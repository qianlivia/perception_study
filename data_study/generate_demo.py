import json
import os
import re

# --- CONFIGURATION ---
FILE_NAMES = ["fe_03_01905_330.02", "fe_03_01695_351.42", "fe_03_01415_141.07", "fe_03_00010_333.58", "fe_03_00159_415.51", "fe_03_00271_344.65", "fe_03_01398_170.67",]
root = "data_study"
root_opus = "data_study_opus"

CONDITIONS = [
    "gt",
    "b_b",
    "c_b",
    "random_same_lexical",
    "random",
]

OUTPUT_HTML = "index.html"


def sanitize_id(filename, condition):
    """Removes periods and special characters that break CSS selectors."""
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', filename)
    return f"{clean_name}_{condition}"


def align_transcript_timings(json_data, file_id, cond):
    """
    Maps timeline boundaries by exploiting the strict alternating structure:
    Even lines = Context gaps, Odd lines = Feedback list entries.
    """
    context_text = json_data.get("context_text", "")
    context_start = json_data.get("context_start", 0)
    context_end = json_data.get("context_end_new", json_data.get("context_end", 0))
    feedbacks = json_data.get("feedback", [])
    
    total_duration = max(0.0, context_end - context_start)
    raw_segments = context_text.split('/')
    lines_payload = []
    current_speaker = "A"
    
    for seg in raw_segments:
        text = seg.strip()
        if not text: continue
            
        if "<A>" in text or "<a>" in text: current_speaker = "A"
        elif "<B>" in text or "<b>" in text: current_speaker = "B"
            
        clean_text = re.sub(r'<[a-zA-Z]>', '', text)
        clean_text = re.sub(r'</[a-zA-Z]>', '', clean_text).strip()
        
        lines_payload.append({
            "speaker": current_speaker,
            "text": clean_text,
            "start": None,
            "end": None,
            "is_feedback": False
        })

    fb_idx = 0
    num_feedbacks = len(feedbacks)
    for idx, line in enumerate(lines_payload):
        if idx % 2 == 1 and fb_idx < num_feedbacks:
            fb = feedbacks[fb_idx]
            line["start"] = max(0.0, fb["start"] - context_start)
            line["end"] = min(total_duration, fb["end"] - context_start)
            line["is_feedback"] = True
            fb_idx += 1

    num_lines = len(lines_payload)
    for idx, line in enumerate(lines_payload):
        if line["start"] is not None: continue
        line["start"] = 0.0 if idx == 0 else lines_payload[idx - 1]["end"]
        if idx + 1 < num_lines and lines_payload[idx + 1]["start"] is not None:
            line["end"] = lines_payload[idx + 1]["start"]
        else:
            line["end"] = total_duration

    return lines_payload


def load_json_data(filepath):
    if not os.path.exists(filepath): return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception: return None


def main():
    compiled_data = {}

    for file_id in FILE_NAMES:
        compiled_data[file_id] = {}
        for cond in CONDITIONS:
            wav_relative_path = f"{root_opus}/{cond}/{file_id}.opus"
            json_real_path = os.path.join(f"{root}/{cond}_transcripts", f"{file_id}.json")
            json_content = load_json_data(json_real_path)
            
            if json_content is not None:
                safe_instance_id = sanitize_id(file_id, cond)
                final_aligned_lines = align_transcript_timings(json_content, file_id, cond)
                compiled_data[file_id][cond] = {
                    "instance_id": safe_instance_id,
                    "audio_url": wav_relative_path,
                    "aligned_lines": final_aligned_lines,
                    "context_start": json_content.get("context_start", 0),
                    "feedback_raw": json_content.get("feedback", [])
                }

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dialogue examples with transcripts</title>
    <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
    <script src="https://unpkg.com/wavesurfer.js@7"></script>
    <script src="https://unpkg.com/wavesurfer.js@7/dist/plugins/regions.min.js"></script>
    <style>
        .wavesurfer-region {{
            background-color: rgba(239, 68, 68, 0.15) !important;
            border-left: 1px solid rgba(239, 68, 68, 0.4) !important;
            border-right: 1px solid rgba(239, 68, 68, 0.4) !important;
            height: 100% !important;
            z-index: 10 !important;
        }}
        .transcript-line {{ transition: all 0.1s ease-in-out; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body class="bg-gray-50 text-gray-800 font-sans p-6">

    <div class="max-w-6xl mx-auto">
        <h1 class="text-3xl font-bold mb-8 text-center text-gray-900">Dialogue examples with transcripts</h1>
        
        <div id="tab-headers" class="flex flex-wrap gap-2 mb-8 border-b border-gray-200 pb-4"></div>
        
        <div id="dashboard-container"></div>
    </div>

    <script>
        const payload = {json.dumps(compiled_data)};
        const container = document.getElementById('dashboard-container');
        const headerContainer = document.getElementById('tab-headers');

        const fileIds = Object.keys(payload);
        
        // Registry arrays to globalize tracking and allow reset loops
        const allWaveSurferInstances = [];

        fileIds.forEach((fileId, fileIndex) => {{
            const exampleNum = fileIndex + 1;
            const exampleId = `example_container_${{fileIndex}}`;
            
            // Create Tab Navigation Button
            const btn = document.createElement('button');
            btn.className = `px-6 py-2 rounded-full font-medium text-sm transition-all shadow-sm tab-btn cursor-pointer`;
            btn.id = `btn_tab_${{fileIndex}}`;
            btn.textContent = `Example ${{exampleNum}}`;
            btn.onclick = () => showTab(fileIndex);
            headerContainer.appendChild(btn);

            // Create Tab View Content wrapper
            const fileSection = document.createElement('div');
            fileSection.id = exampleId;
            fileSection.className = "tab-content space-y-12";
            
            Object.keys(payload[fileId]).forEach((condition) => {{
                const condData = payload[fileId][condition];
                const instanceId = condData.instance_id;
                
                let transcriptSpansHtml = '';
                condData.aligned_lines.forEach((lineObj, index) => {{
                    const textColorClass = lineObj.speaker === "A" ? "text-indigo-400/60" : "text-teal-500/60";
                    const prefix = lineObj.speaker === "A" ? "A: " : "B: ";
                    transcriptSpansHtml += `
                        <span class="transcript-line block py-1 px-2 font-mono text-sm cursor-pointer hover:bg-gray-100 rounded ${{textColorClass}}" 
                              data-start="${{lineObj.start}}" data-speaker="${{lineObj.speaker}}">
                            <strong class="opacity-70">${{prefix}}</strong>${{lineObj.text}}
                        </span>`;
                }});

                fileSection.innerHTML += `
                    <div class="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-8">
                        <div class="flex justify-between items-center mb-3">
                            <span class="text-sm font-bold uppercase tracking-wider text-gray-500">Condition: ${{condition}}</span>
                        </div>
                        <div id="transcript_${{instanceId}}" class="bg-white p-4 rounded border border-gray-200 shadow-inner max-h-72 overflow-y-auto mb-4 space-y-0.5">
                            ${{transcriptSpansHtml}}
                        </div>
                        <div class="flex items-center gap-4 mb-2">
                            <button id="btn_play_${{instanceId}}" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-xs rounded shadow shadow-indigo-200 cursor-pointer">Play</button>
                            <span id="time_${{instanceId}}" class="text-xs font-mono text-gray-500">0:00</span>
                        </div>
                        <div id="wave_${{instanceId}}" data-id="${{instanceId}}" class="w-full bg-white rounded border border-gray-100 p-2 shadow-sm"></div>
                    </div>
                `;
            }});

            container.appendChild(fileSection);

            // Initialize WaveSurfer instances for the specific visible conditions
            Object.keys(payload[fileId]).forEach((condition) => {{
                const condData = payload[fileId][condition];
                const instanceId = condData.instance_id;
                const contextStart = condData.context_start;
                const targetContainer = document.querySelector(`[data-id="${{instanceId}}"]`);

                const ws = WaveSurfer.create({{
                    container: targetContainer,
                    waveColor: '#cbd5e1',
                    progressColor: '#4f46e5',
                    cursorColor: '#4f46e5',
                    height: 80,
                    responsive: true,
                    url: condData.audio_url
                }});

                const wsRegions = ws.registerPlugin(WaveSurfer.Regions.create());
                const spanElements = document.getElementById(`transcript_${{instanceId}}`).querySelectorAll('.transcript-line');

                // Track globally
                allWaveSurferInstances.push(ws);

                spanElements.forEach(el => {{
                    el.onclick = () => {{
                        ws.setTime(parseFloat(el.dataset.start));
                        if (!ws.isPlaying()) ws.play();
                    }};
                }});

                ws.on('ready', () => {{
                    condData.feedback_raw.forEach(fb => {{
                        wsRegions.addRegion({{
                            start: fb.start - contextStart,
                            end: fb.end - contextStart,
                            drag: false, resize: false
                        }});
                    }});
                }});

                ws.on('audioprocess', () => {{
                    const cur = ws.getCurrentTime();
                    document.getElementById(`time_${{instanceId}}`).textContent = new Date(cur * 1000).toISOString().substr(14, 5);
                    
                    condData.aligned_lines.forEach((line, idx) => {{
                        const el = spanElements[idx];
                        if (cur >= line.start && cur <= line.end) {{
                            el.classList.remove('text-indigo-400/60', 'text-teal-500/60');
                            const bg = line.speaker === "A" ? 'bg-indigo-100/90' : 'bg-teal-100/90';
                            const txt = line.speaker === "A" ? 'text-indigo-900' : 'text-teal-900';
                            el.classList.add(bg, txt, 'font-bold', 'rounded', 'scale-[1.005]');
                        }} else {{
                            el.classList.remove('bg-indigo-100/90', 'bg-teal-100/90', 'text-indigo-900', 'text-teal-900', 'font-bold', 'rounded', 'scale-[1.005]');
                            el.classList.add(line.speaker === "A" ? 'text-indigo-400/60' : 'text-teal-500/60');
                        }}
                    }});
                }});

                const playBtn = document.getElementById(`btn_play_${{instanceId}}`);
                playBtn.onclick = () => ws.playPause();
                ws.on('play', () => playBtn.textContent = 'Pause');
                ws.on('pause', () => playBtn.textContent = 'Play');
            }});
        }});

        function showTab(index) {{
            // CRITICAL STEP: Reset and pause all audio instances on tab change
            allWaveSurferInstances.forEach(ws => {{
                if (ws.isPlaying()) {{
                    ws.pause();
                }}
                ws.setTime(0); // Snap playheads back to 0:00 boundary cleanly
            }});

            // Toggle Navigation Header Classes
            document.querySelectorAll('.tab-btn').forEach((b, i) => {{
                if(i === index) {{
                    b.classList.add('bg-indigo-600', 'text-white');
                    b.classList.remove('bg-gray-200', 'text-gray-700');
                }} else {{
                    b.classList.remove('bg-indigo-600', 'text-white');
                    b.classList.add('bg-gray-200', 'text-gray-700');
                }}
            }});

            // Toggle Card Content Frame Visibility Classes
            document.querySelectorAll('.tab-content').forEach((c, i) => {{
                c.classList.toggle('active', i === index);
            }});
        }}

        // Initialize display context on application start
        if(fileIds.length > 0) showTab(0);
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"Generated tab-isolated audio dashboard inside: '{OUTPUT_HTML}'")

if __name__ == "__main__":
    main()
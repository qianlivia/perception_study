import os
from pydub import AudioSegment

input_root = "selected_feedback_rms22"
output_root = "selected_feedback_rms22_high_pass"

# Process all files
for root, _, files in os.walk(input_root):
    for file in files:
        if file.lower().endswith(".wav"):
            path_in = os.path.join(root, file)
            rel_path = os.path.relpath(root, input_root)
            path_out_dir = os.path.join(output_root, rel_path)
            os.makedirs(path_out_dir, exist_ok=True)
            path_out = os.path.join(path_out_dir, file)

            audio = AudioSegment.from_wav(path_in)
            filtered = audio.low_pass_filter(20000)
            filtered.export(path_out, format="wav")

            print(f"Processed {file}")

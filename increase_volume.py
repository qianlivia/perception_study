import os
from pydub import AudioSegment
from pydub.effects import compress_dynamic_range

# Paths
input_root = "selected_for_context_survey"
output_root = "selected_feedback"

# Settings
TARGET_RMS = -18.0      # louder target for short clips
MAX_GAIN_DB = 8.0       # max boost allowed
APPLY_COMPRESSION = True # set to False to skip compression

def normalize_clip(audio, target_rms, max_gain_db, apply_compression=True):
    # 1. Peak normalization: bring loudest sample close to 0 dBFS
    peak_norm = audio.apply_gain(-audio.max_dBFS)

    # 2. Optional gentle compression
    if apply_compression:
        compressed = compress_dynamic_range(
            peak_norm,
            threshold=-20.0,
            ratio=3.0,
            attack=5,
            release=50
        )
    else:
        compressed = peak_norm

    # 3. RMS normalization with capped gain
    change_in_dBFS = target_rms - compressed.dBFS
    if change_in_dBFS > max_gain_db:
        change_in_dBFS = max_gain_db

    normalized = compressed.apply_gain(change_in_dBFS)
    return normalized

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
            processed = normalize_clip(audio, TARGET_RMS, MAX_GAIN_DB, APPLY_COMPRESSION)
            processed.export(path_out, format="wav")

            print(f"Processed {file}: {audio.dBFS:.2f} → {processed.dBFS:.2f} dBFS")

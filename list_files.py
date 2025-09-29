import os
import shutil

all_folder = "/media/liviaq/extraDisk/prosodic_similarity_2/data/feedback_carol/survey/final_files"
excluded_subfolders = ["selected", "selected_for_context_survey", "selected_context", "selected2"]

def find_files(source: str, excluded_subfolders: list = []) -> dict:
    wav_files = dict()
    
    for root, dirs, files in os.walk(source):
        # Exclude specified subfolders
        dirs[:] = [d for d in dirs if d not in excluded_subfolders]
        for file in files:
            if file.endswith(".wav"):
                if file not in wav_files:
                    wav_files[file] = 1
                else:
                    wav_files[file] += 1
    return wav_files

def copy_unique_files(source: str, target: str, excluded_subfolders: list = []):
    wav_files = find_files(source, excluded_subfolders)
    moved_files = []
    for file in wav_files:
        # Copy first occurrence only
        for root, dirs, files in os.walk(source):
            # Exclude specified subfolders
            dirs[:] = [d for d in dirs if d not in excluded_subfolders]
            if file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target, file)
                shutil.copy2(source_file, target_file)
                print(f"Copied: {source_file} to {target_file}")
                moved_files.append(file)
                break  # Stop after copying the first occurrence

    return moved_files

def get_wav_files_by_subfolder(root_folder):
    wav_files_by_subfolder = []
    
    # Loop through only immediate subfolders
    for subfolder in os.listdir(root_folder):
        subfolder_path = os.path.join(root_folder, subfolder)
        if os.path.isdir(subfolder_path):
            wav_files = [
                os.path.join(subfolder, f)
                for f in os.listdir(subfolder_path)
                if f.lower().endswith(".wav")
            ]
            if wav_files:
                wav_files_by_subfolder.append(wav_files)
    
    return wav_files_by_subfolder


source_folder = "/media/liviaq/extraDisk/perception_study/selected_feedback_clipped"
wav_files = find_files(source_folder)
# Sort by count descending
wav_files = dict(sorted(wav_files.items(), key=lambda item: item[1], reverse=True))
for file, count in wav_files.items():
    print(f"{file}: {count}")

wav_files = set(wav_files)  # Remove duplicates
print(wav_files)
print(f"Total .wav files found: {len(wav_files)}")
print()
wav_files_all = find_files(all_folder, excluded_subfolders)
wav_files_all = set(wav_files_all)  # Remove duplicates

print(f"Total .wav files in all folders (excluding {excluded_subfolders}): {len(wav_files_all)}")
print(wav_files_all)

print(wav_files_all - wav_files)

# Copy unique files to a new folder
source_folder = "/media/liviaq/extraDisk/perception_study/selected_feedback_clipped_rms30"
target_folder = "/media/liviaq/extraDisk/perception_study/selected_feedback_clipped_rms30_unique"
os.makedirs(target_folder, exist_ok=True)
moved_files = copy_unique_files(source=source_folder, target=target_folder, excluded_subfolders=excluded_subfolders)
print(moved_files)


root = source_folder
result = get_wav_files_by_subfolder(root)

print(result)
import os
import shutil

source_folder = "/media/liviaq/extraDisk/prosodic_similarity_2/data/feedback_carol/survey/final_files_clipped"
target_folder = "/media/liviaq/extraDisk/perception_study/selected_for_context_survey"

# Walk through source folder
for root, _, files in os.walk(source_folder):
    for f in files:
        source_file = os.path.join(root, f)
        # Walk through target folder to find all matching filenames
        for t_root, _, t_files in os.walk(target_folder):
            if f in t_files:
                target_file = os.path.join(t_root, f)
                shutil.copy2(source_file, target_file)
                print(f"Replaced: {target_file} with {source_file}")
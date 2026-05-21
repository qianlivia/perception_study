import os
import shutil

# ---------------------------
# CONFIG
# ---------------------------

FILE_NAMES = [
    "fe_03_01905_330.02",
    "fe_03_01695_351.42",
    "fe_03_01415_141.07",
    "fe_03_00010_333.58",
    "fe_03_00159_415.51",
    "fe_03_00271_344.65",
    "fe_03_01398_170.67",
]

CONDITIONS = [
    "gt",
    "b_b",
    "c_b",
    "random_same_lexical",
    "random",
]

SRC_ROOT = "data_study"
DEST_ROOT = "data_study_opus"


# ---------------------------
# MAIN
# ---------------------------

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def copy_wavs():
    total = 0

    for cond in CONDITIONS:
        for file_id in FILE_NAMES:

            src_path = os.path.join(
                SRC_ROOT,
                cond,
                f"{file_id}.wav"
            )

            if not os.path.exists(src_path):
                print(f"[MISSING] {src_path}")
                continue

            dest_dir = os.path.join(
                DEST_ROOT,
                cond
            )

            ensure_dir(dest_dir)

            dest_path = os.path.join(
                dest_dir,
                f"{file_id}.wav"
            )

            os.system(
                f'ffmpeg -y -i "{src_path}" '
                f'-c:a libopus -b:a 64k '
                f'"{dest_path.replace(".wav", ".opus")}"'
            )

            print(f"[COPIED] {src_path} -> {dest_path}")

            total += 1

    print(f"\nDone. Copied {total} files.")


if __name__ == "__main__":
    copy_wavs()

# Quick utility snippet to print your precise sparse-checkout mapping configuration
FILE_NAMES = [
    "fe_03_01905_330.02", "fe_03_01695_351.42", "fe_03_01415_141.07", 
    "fe_03_00010_333.58", "fe_03_00159_415.51", "fe_03_00271_344.65", 
    "fe_03_01398_170.67"
]

CONDITIONS = ["gt", "b_b", "c_b", "random_same_lexical", "random"]
root = "data_study"

print("sparse-checkout: |")
print("  index.html")
for f_id in FILE_NAMES:
    print(f"\n  # --- Files for {f_id} ---")
    for cond in CONDITIONS:
        print(f"  {root}/{cond}/{f_id}.wav")
        print(f"  {root}/{cond}_transcripts/{f_id}.json")

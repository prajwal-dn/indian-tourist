# save as download_data.py and run it
from datasets import load_dataset
import json
from pathlib import Path

Path(r"E:\aiassis\knowledge").mkdir(exist_ok=True)

print("Downloading Dolly 15K...")
ds = load_dataset("databricks/dolly-15k", split="train")
data = []
for r in ds:
    data.append({
        "question": r["instruction"],
        "answer": r["response"],
        "category": r["category"]
    })
with open(r"E:\aiassis\knowledge\dolly_15k.json", "w") as f:
    json.dump(data, f, indent=2)
print("Saved dolly_15k.json!")

print("Downloading Alpaca...")
ds2 = load_dataset("yahma/alpaca-cleaned", split="train")
data2 = []
for r in ds2:
    data2.append({
        "question": r["instruction"],
        "answer": r["output"]
    })
with open(r"E:\aiassis\knowledge\alpaca.json", "w") as f:
    json.dump(data2, f, indent=2)
print("Saved alpaca.json!")

print("All done! Restart Nova and it will load all data automatically!")

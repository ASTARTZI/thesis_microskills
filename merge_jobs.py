# merge_jobs.py
from pathlib import Path
import pandas as pd


PROCESSED_DIR = Path("data/processed")
FINAL_DIR = Path("data/final")
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def main():
    csv_files = list(PROCESSED_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in data/processed")
        return

    frames = []
    for file in csv_files:
        df = pd.read_csv(file)
        df["source_file"] = file.name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    print("Combined rows before dedup:", len(combined))

    dedup = combined.drop_duplicates(subset=["id"]).copy()
    print("Rows after dedup:", len(dedup))

    combined_path = FINAL_DIR / "all_jobs_combined.csv"
    dedup_path = FINAL_DIR / "all_jobs_deduplicated.csv"

    combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
    dedup.to_csv(dedup_path, index=False, encoding="utf-8-sig")

    print(f"Saved combined file to: {combined_path}")
    print(f"Saved deduplicated file to: {dedup_path}")


if __name__ == "__main__":
    main()
    
    
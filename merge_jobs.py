from pathlib import Path
import pandas as pd


def main():
    processed_dir = Path("data/processed")
    output_dir = Path("data/final")
    output_dir.mkdir(parents=True, exist_ok=True)

    csv_files = list(processed_dir.glob("jobs_*_el.csv"))

    if not csv_files:
        print("No CSV files found.")
        return

    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        df["retrieval_file"] = file.name
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    print(f"Combined rows before dedup: {len(combined)}")

    # Deduplication
    if "id" in combined.columns:
        dedup = combined.drop_duplicates(subset=["id"])
    else:
        dedup = combined.drop_duplicates()

    print(f"Rows after dedup: {len(dedup)}")

    combined_path = output_dir / "all_jobs_combined.csv"
    dedup_path = output_dir / "all_jobs_deduplicated.csv"

    combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
    dedup.to_csv(dedup_path, index=False, encoding="utf-8-sig")

    print(f"Saved combined file to: {combined_path}")
    print(f"Saved deduplicated file to: {dedup_path}")


if __name__ == "__main__":
    main()
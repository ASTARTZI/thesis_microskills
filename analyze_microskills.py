from pathlib import Path
import pandas as pd
import json
from collections import Counter


INPUT_PATH = Path("data/final/jobs_with_microskills.csv")
OUTPUT_DIR = Path("data/final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_json_list(value):
    if pd.isna(value):
        return []
    value = str(value).strip()
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def main():
    if not INPUT_PATH.exists():
        print(f"Input file not found: {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)

    df["detected_microskills"] = df["detected_microskills"].apply(parse_json_list)
    df["detected_categories"] = df["detected_categories"].apply(parse_json_list)
    df["detected_microskills_count"] = pd.to_numeric(
        df["detected_microskills_count"], errors="coerce"
    ).fillna(0).astype(int)

    total_jobs = len(df)
    jobs_with_microskills = (df["detected_microskills_count"] > 0).sum()
    jobs_without_microskills = (df["detected_microskills_count"] == 0).sum()
    avg_microskills = df["detected_microskills_count"].mean()

    microskill_counter = Counter()
    category_counter = Counter()

    for microskills in df["detected_microskills"]:
        microskill_counter.update(microskills)

    for categories in df["detected_categories"]:
        category_counter.update(categories)

    microskills_df = pd.DataFrame(
        microskill_counter.items(),
        columns=["microskill", "frequency"]
    ).sort_values("frequency", ascending=False)

    categories_df = pd.DataFrame(
        category_counter.items(),
        columns=["category", "frequency"]
    ).sort_values("frequency", ascending=False)

    summary_df = pd.DataFrame([
        {"metric": "total_jobs", "value": total_jobs},
        {"metric": "jobs_with_microskills", "value": jobs_with_microskills},
        {"metric": "jobs_without_microskills", "value": jobs_without_microskills},
        {"metric": "share_with_microskills", "value": round(jobs_with_microskills / total_jobs, 4) if total_jobs else 0},
        {"metric": "average_microskills_per_job", "value": round(avg_microskills, 4)},
    ])

    summary_path = OUTPUT_DIR / "microskills_summary.csv"
    microskills_path = OUTPUT_DIR / "microskills_frequency.csv"
    categories_path = OUTPUT_DIR / "microskills_categories_frequency.csv"

    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    microskills_df.to_csv(microskills_path, index=False, encoding="utf-8-sig")
    categories_df.to_csv(categories_path, index=False, encoding="utf-8-sig")

    print("=== SUMMARY ===")
    print(summary_df)

    print("\n=== TOP MICROSKILLS ===")
    print(microskills_df.head(10))

    print("\n=== TOP CATEGORIES ===")
    print(categories_df.head(10))

    print(f"\nSaved summary to: {summary_path}")
    print(f"Saved microskill frequencies to: {microskills_path}")
    print(f"Saved category frequencies to: {categories_path}")



if __name__ == "__main__":
    main() 
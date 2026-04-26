# textprep.py
from pathlib import Path
import re
import pandas as pd


INPUT_PATH = Path("data/final/all_jobs_deduplicated.csv")
OUTPUT_PATH = Path("data/final/all_jobs_cleaned.csv")


def normalize_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).lower()

    # αλλαγές γραμμής / tabs
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # βασικός καθαρισμός punctuation
    text = re.sub(r"[^\w\sάέήίόύώϊΐϋΰ]", " ", text, flags=re.UNICODE)

    # collapse spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    if not INPUT_PATH.exists():
        print(f"Input file not found: {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)

    if "title" not in df.columns:
        df["title"] = ""
    if "description" not in df.columns:
        df["description"] = ""

    df["combined_text"] = (
        df["title"].fillna("").astype(str) + " " +
        df["description"].fillna("").astype(str)
    )

    df["cleaned_text"] = df["combined_text"].apply(normalize_text)

    out_df = df[["id", "title", "cleaned_text"]].copy()
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Saved cleaned dataset to: {OUTPUT_PATH}")
    print(out_df.head())


if __name__ == "__main__":
    main()
    
    
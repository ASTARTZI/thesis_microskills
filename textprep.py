import re
import pandas as pd
from pathlib import Path


def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).lower()

    # αφαίρεση urls
    text = re.sub(r"http\S+|www\S+", " ", text)

    # αφαίρεση line breaks / tabs
    text = re.sub(r"[\r\n\t]+", " ", text)

    # κράτα γράμματα, αριθμούς, βασικά σύμβολα
    text = re.sub(r"[^\w\s\+#\.]", " ", text)

    # αφαίρεση πολλών κενών
    text = re.sub(r"\s+", " ", text).strip()

    return text


def main():
    input_path = Path("data/final/all_jobs_deduplicated.csv")
    output_path = Path("data/final/all_jobs_cleaned.csv")

    df = pd.read_csv(input_path)

    df["title"] = df["title"].fillna("")
    df["description"] = df["description"].fillna("")

    df["combined_text"] = df["title"] + " " + df["description"]
    df["cleaned_text"] = df["combined_text"].apply(clean_text)

    df.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Saved cleaned dataset to: {output_path}")
    print(df[["id", "title", "cleaned_text"]].head())


if __name__ == "__main__":
    main()
# microskill_matcher.py
from pathlib import Path
import re
import pandas as pd
import json


CLEANED_JOBS_PATH = Path("data/final/all_jobs_cleaned.csv")
LEXICON_PATH = Path("MicroSkillsLexicon.xlsx")
OUTPUT_PATH = Path("data/final/jobs_with_microskills.csv")


def normalize_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = re.sub(r"[^\w\sάέήίόύώϊΐϋΰ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_keywords(value: str) -> list[str]:
    if pd.isna(value):
        return []

    text = str(value).strip()
    if not text:
        return []

    # χωρισμός με κόμμα
    parts = [p.strip().lower() for p in text.split(",") if p.strip()]
    return parts


def load_lexicon(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)

    required_cols = [
        "Categories Micro-skills (GR)",
        "Categories Micro-skills (EN)",
        "Microskills",
        "Definition (GR)",
        "Keywords",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Λείπουν στήλες από το lexicon: {missing}")

    df = df.copy()
    df["Microskills"] = df["Microskills"].fillna("").astype(str).str.strip()
    df["Categories Micro-skills (GR)"] = df["Categories Micro-skills (GR)"].fillna("").astype(str).str.strip()
    df["keyword_list"] = df["Keywords"].apply(parse_keywords)

    # normalize και το όνομα microskill ως πιθανό keyword
    df["microskill_norm"] = df["Microskills"].apply(normalize_text)

    return df


def contains_keyword(text: str, keyword: str) -> bool:
    if not keyword:
        return False

    keyword = normalize_text(keyword)

    # whole phrase match
    pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"
    return re.search(pattern, text, flags=re.UNICODE) is not None


def detect_microskills_in_text(text: str, lexicon_df: pd.DataFrame):
    found_microskills = []
    found_categories = []

    for _, row in lexicon_df.iterrows():
        microskill = row["Microskills"]
        category = row["Categories Micro-skills (GR)"]

        keywords = list(row["keyword_list"])

        # προαιρετικά: βάλε και το ίδιο το microskill σαν keyword
        if row["microskill_norm"]:
            keywords.append(row["microskill_norm"])

        matched = False
        for kw in keywords:
            if contains_keyword(text, kw):
                matched = True
                break

        if matched:
            found_microskills.append(microskill)
            found_categories.append(category)

    # unique, κρατώντας σειρά
    found_microskills = list(dict.fromkeys(found_microskills))
    found_categories = list(dict.fromkeys(found_categories))

    return found_microskills, found_categories


def main():
    print("Loading cleaned jobs dataset...")
    if not CLEANED_JOBS_PATH.exists():
        raise FileNotFoundError(f"Δεν βρέθηκε το αρχείο: {CLEANED_JOBS_PATH}")

    jobs_df = pd.read_csv(CLEANED_JOBS_PATH)

    print("Loading microskills lexicon...")
    if not LEXICON_PATH.exists():
        raise FileNotFoundError(f"Δεν βρέθηκε το lexicon: {LEXICON_PATH}")

    lexicon_df = load_lexicon(LEXICON_PATH)

    print(f"Loaded {len(jobs_df)} jobs")
    print(f"Loaded {len(lexicon_df)} microskills from lexicon")

    results = []

    for idx, row in jobs_df.iterrows():
        text = normalize_text(row.get("cleaned_text", ""))

        detected_microskills, detected_categories = detect_microskills_in_text(text, lexicon_df)

        results.append({
            "id": row.get("id"),
            "title": row.get("title", ""),
            "detected_microskills": json.dumps(detected_microskills, ensure_ascii=False),
            "detected_categories": json.dumps(detected_categories, ensure_ascii=False),
            "detected_microskills_count": len(detected_microskills),
        })

        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(jobs_df)} jobs")

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Saved matcher output to: {OUTPUT_PATH}")
    print(out_df.head(10))


if __name__ == "__main__":
    main()
from pathlib import Path
import re
import pandas as pd
import json


CLEANED_JOBS_PATH = Path("data/final/all_jobs_cleaned.csv")
LEXICON_PATH = Path("MicroSkillsLexicon.xlsx")
OUTPUT_PATH = Path("data/final/jobs_with_microskills.csv")


EXTRA_KEYWORDS_BY_MICROSKILL = {
    "Σύνταξη επαγγελματικών email": [
        "email communication", "emails", "e-mail", "e mails",
        "correspondence", "business correspondence",
        "written correspondence"
    ],

    "Σαφής και συνοπτική επικοινωνία": [
        "communication skills", "excellent communication", "strong communication",
        "written and verbal communication", "verbal and written communication",
        "oral and written communication", "written and oral communication",
        "interpersonal skills", "presentation skills",
        "communicate effectively", "effective communication",
        "client communication", "customer communication",
        "team communication"
    ],

    "Ενεργητική ακρόαση": [
        "active listening", "understand customer needs",
        "understand client needs", "gather requirements",
        "requirements gathering", "stakeholder communication",
        "customer needs", "client needs"
    ],

    "Αποτελεσματική χρήση GPT": [
        "chatgpt", "chat gpt", "openai", "llm",
        "large language model", "gen ai", "genai",
        "generative ai", "artificial intelligence tools",
        "ai tools"
    ],

    "Αυτοματοποίηση επαναλαμβανόμενων εργασιών": [
        "process automation", "task automation", "workflow automation",
        "automate tasks", "automating tasks", "automation",
        "scripting", "scripts", "automated processes"
    ],

    "Οργάνωση ψηφιακού χώρου εργασίας": [
        "file management", "filing", "electronic filing",
        "record keeping", "records management", "documentation",
        "data entry", "data recording", "maintain records",
        "update records", "folder organization", "document management",
        "organize files", "organise files"
    ],

    "Αποτελεσματική αναζήτηση στο διαδίκτυο": [
        "internet research", "online research", "web research",
        "desk research", "market research", "information retrieval",
        "information search", "research skills"
    ],

    "Διαχείριση χρόνου": [
        "time management", "time management skills",
        "prioritization", "prioritisation",
        "prioritization skills", "prioritisation skills",
        "prioritise", "prioritize", "prioritising", "prioritizing",
        "organizational skills", "organisational skills",
        "multitasking", "multi tasking", "deadlines",
        "deadline", "work under pressure", "fast paced",
        "fast-paced", "meet deadlines", "manage workload",
        "workload management"
    ],

    "Διαχείριση προσοχής και συγκέντρωσης": [
        "attention to detail", "detail oriented", "detail-oriented",
        "accuracy", "accurate", "data accuracy",
        "focus on detail", "high attention", "attention",
        "precise", "precision", "careful", "meticulous"
    ],

    "Επιβεβαίωση οδηγιών και απαιτήσεων": [
        "clarify requirements", "requirement clarification",
        "confirm requirements", "confirm instructions",
        "requirements analysis", "business requirements",
        "understand requirements", "collect requirements",
        "analyze requirements", "analyse requirements"
    ],
}


def normalize_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).lower()

    text = text.replace("&", " and ")
    text = text.replace("+", " plus ")

    text = re.sub(r"[-_/]", " ", text)

    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    text = re.sub(r"[^\w\sάέήίόύώϊΐϋΰ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def parse_keywords(value: str) -> list[str]:
    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    parts = re.split(r"[,;|\n]+", text)

    keywords = []

    for part in parts:
        keyword = part.strip().lower()

        if keyword:
            keywords.append(keyword)

    return keywords


def expand_keyword_variants(keyword: str) -> list[str]:
    keyword = normalize_text(keyword)

    if not keyword:
        return []

    variants = {keyword}

    replacements = {
        "organise": "organize",
        "organised": "organized",
        "organising": "organizing",
        "organisation": "organization",
        "organisational": "organizational",

        "prioritise": "prioritize",
        "prioritised": "prioritized",
        "prioritising": "prioritizing",
        "prioritisation": "prioritization",

        "analyse": "analyze",
        "analysing": "analyzing",
        "analysed": "analyzed",

        "e mail": "email",
        "chat gpt": "chatgpt",
        "multi tasking": "multitasking",
        "fast paced": "fastpaced",
    }

    for old, new in replacements.items():
        if old in keyword:
            variants.add(keyword.replace(old, new))

        if new in keyword:
            variants.add(keyword.replace(new, old))

    return sorted(variants)


def load_lexicon(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)

    required_cols = [
        "Categories Micro-skills (GR)",
        "Categories Micro-skills (EN)",
        "Microskills",
        "Definition (GR)",
        "Keywords",
    ]

    missing = [col for col in required_cols if col not in df.columns]

    if missing:
        raise ValueError(f"Λείπουν στήλες από το lexicon: {missing}")

    df = df.copy()

    df["Microskills"] = df["Microskills"].fillna("").astype(str).str.strip()
    df["Categories Micro-skills (GR)"] = (
        df["Categories Micro-skills (GR)"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["keyword_list"] = df["Keywords"].apply(parse_keywords)

    df["keyword_list"] = df.apply(
        lambda row: row["keyword_list"]
        + EXTRA_KEYWORDS_BY_MICROSKILL.get(row["Microskills"], []),
        axis=1,
    )

    df["microskill_norm"] = df["Microskills"].apply(normalize_text)

    df["keyword_list"] = df.apply(
        lambda row: sorted(
            set(
                variant
                for keyword in row["keyword_list"] + [row["microskill_norm"]]
                for variant in expand_keyword_variants(keyword)
                if variant
            )
        ),
        axis=1,
    )

    return df


def contains_keyword(text: str, keyword: str) -> bool:
    if not keyword:
        return False

    keyword = normalize_text(keyword)

    if not keyword:
        return False

    pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

    return re.search(pattern, text, flags=re.UNICODE) is not None


def detect_microskills_in_text(text: str, lexicon_df: pd.DataFrame):
    found_microskills = []
    found_categories = []

    text = normalize_text(text)

    for _, row in lexicon_df.iterrows():
        microskill = row["Microskills"]
        category = row["Categories Micro-skills (GR)"]
        keywords = row["keyword_list"]

        if any(contains_keyword(text, keyword) for keyword in keywords):
            found_microskills.append(microskill)
            found_categories.append(category)

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
        text = row.get("cleaned_text", "")

        detected_microskills, detected_categories = detect_microskills_in_text(
            text,
            lexicon_df
        )

        results.append({
            "id": row.get("id"),
            "title": row.get("title", ""),
            "detected_microskills": json.dumps(
                detected_microskills,
                ensure_ascii=False
            ),
            "detected_categories": json.dumps(
                detected_categories,
                ensure_ascii=False
            ),
            "detected_microskills_count": len(detected_microskills),
        })

        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(jobs_df)} jobs")

    out_df = pd.DataFrame(results)

    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    jobs_with_microskills = (out_df["detected_microskills_count"] > 0).sum()
    share = jobs_with_microskills / len(out_df) if len(out_df) else 0

    print(f"Saved matcher output to: {OUTPUT_PATH}")
    print(
        f"Jobs with at least one microskill: "
        f"{jobs_with_microskills}/{len(out_df)} ({share:.2%})"
    )

    print(out_df.head(10))


if __name__ == "__main__":
    main()
    
    
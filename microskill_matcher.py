from pathlib import Path
import re
import json
import pandas as pd


CLEANED_JOBS_PATH = Path("data/final/all_jobs_cleaned.csv")
LEXICON_PATH = Path("MicroSkillsLexicon.xlsx")
OUTPUT_PATH = Path("data/final/jobs_with_microskills.csv")


MAX_MICROSKILLS_PER_JOB = 6


EN_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "while", "of", "at", "by", "for",
    "with", "without", "about", "against", "between", "into", "through", "during",
    "before", "after", "above", "below", "to", "from", "up", "down", "in", "out",
    "on", "off", "over", "under", "again", "further", "then", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "can", "will", "just", "should", "now", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did", "this", "that",
    "these", "those", "we", "you", "they", "he", "she", "it", "our", "your", "their",
    "his", "her", "its", "as", "per", "via", "etc", "job", "role", "position", "company",
    "team", "work", "working", "skills", "skill", "ability", "knowledge", "experience",
    "responsible", "responsibilities", "candidate", "required", "requirements"
}

GR_STOPWORDS = {
    "ο", "η", "το", "οι", "τα", "του", "της", "των", "τον", "την", "τους", "τις",
    "και", "ή", "σε", "στο", "στη", "στην", "στον", "στα", "στις", "στους", "με",
    "χωρίς", "για", "από", "ως", "που", "πως", "να", "θα", "είναι", "ειναι", "ήταν",
    "ηταν", "έχει", "εχει", "έχουν", "εχουν", "μια", "ένα", "ενα", "ένας", "ενας",
    "αυτή", "αυτη", "αυτό", "αυτο", "αυτές", "αυτα", "αυτοί", "στης", "στην",
    "εργασία", "εργασια", "θέση", "θεση", "εταιρεία", "εταιρεια", "υποψήφιος",
    "υποψηφιος", "δεξιότητες", "δεξιοτητες", "γνώση", "γνωση", "εμπειρία", "εμπειρια"
}

STOPWORDS = EN_STOPWORDS | GR_STOPWORDS


GENERIC_SINGLE_WORDS = {
    "communication", "management", "organization", "organisation", "support",
    "customer", "client", "business", "project", "process", "quality",
    "administration", "administrative", "office", "data", "digital",
    "analysis", "reporting", "planning", "research", "documentation",
    "teamwork", "collaboration", "problem", "solving", "leadership",
    "learning", "adaptability", "flexibility", "creativity", "innovation",
    "επικοινωνία", "επικοινωνια", "διαχείριση", "διαχειριση", "οργάνωση",
    "οργανωση", "υποστήριξη", "υποστηριξη", "πελάτης", "πελατης",
    "έργο", "εργο", "δεδομένα", "δεδομενα"
}


STRONG_SINGLE_WORD_KEYWORDS = {
    "chatgpt", "openai", "genai", "automation", "automate", "automated",
    "scripting", "scripts", "macros", "vba", "rpa", "zapier",
    "deadlines", "deadline", "multitasking", "prioritization",
    "prioritisation", "prioritize", "prioritise",
    "accuracy", "accurate", "meticulous", "precision",
    "correspondence", "email", "emails", "prompting",
    "αυτοματοποίηση", "αυτοματοποιηση", "προθεσμίες", "προθεσμιες"
}


IRREGULAR_EN_LEMMAS = {
    "children": "child",
    "people": "person",
    "men": "man",
    "women": "woman",
    "analyses": "analysis",
    "indices": "index",
}


EXTRA_KEYWORDS_BY_MICROSKILL = {
    "Σύνταξη επαγγελματικών email": [
        "email communication",
        "email writing",
        "professional email",
        "business email",
        "business correspondence",
        "written correspondence",
        "mail correspondence",
        "compose emails",
        "draft emails",
        "reply to emails",
    ],

    "Σαφής και συνοπτική επικοινωνία": [
        "communication skills",
        "excellent communication",
        "strong communication",
        "clear communication",
        "effective communication",
        "communicate effectively",
        "written and verbal communication",
        "verbal and written communication",
        "oral and written communication",
        "interpersonal skills",
        "presentation skills",
        "client communication",
        "customer communication",
        "team communication",
        "stakeholder communication",
        "επικοινωνιακές δεξιότητες",
        "επικοινωνιακες δεξιοτητες",
    ],

    "Ενεργητική ακρόαση": [
        "active listening",
        "listening skills",
        "understand customer needs",
        "understand client needs",
        "identify customer needs",
        "gather requirements",
        "requirements gathering",
        "requirements elicitation",
        "customer needs analysis",
        "client needs analysis",
    ],

    "Αποτελεσματική χρήση GPT": [
        "chatgpt",
        "chat gpt",
        "openai",
        "large language model",
        "prompt engineering",
        "generative ai",
        "ai tools",
        "artificial intelligence tools",
        "microsoft copilot",
        "ai assisted",
    ],

    "Αυτοματοποίηση επαναλαμβανόμενων εργασιών": [
        "process automation",
        "task automation",
        "workflow automation",
        "automate tasks",
        "automating tasks",
        "automated processes",
        "excel macros",
        "power automate",
        "robotic process automation",
        "streamline processes",
        "workflow improvement",
        "αυτοματοποίηση εργασιών",
        "αυτοματοποιηση εργασιων",
    ],

    "Οργάνωση ψηφιακού χώρου εργασίας": [
        "file management",
        "electronic filing",
        "digital filing",
        "record keeping",
        "records management",
        "document management",
        "data entry",
        "data recording",
        "maintain records",
        "update records",
        "folder organization",
        "folder organisation",
        "organize files",
        "organise files",
        "maintain database",
        "update database",
        "crm update",
        "erp update",
        "διαχείριση αρχείων",
        "διαχειριση αρχειων",
        "οργάνωση αρχείων",
        "οργανωση αρχειων",
    ],

    "Αποτελεσματική αναζήτηση στο διαδίκτυο": [
        "internet research",
        "online research",
        "web research",
        "desk research",
        "market research",
        "information retrieval",
        "information search",
        "research skills",
        "competitive research",
        "αναζήτηση πληροφοριών",
        "αναζητηση πληροφοριων",
    ],

    "Διαχείριση χρόνου": [
        "time management",
        "time management skills",
        "prioritization skills",
        "prioritisation skills",
        "prioritize tasks",
        "prioritise tasks",
        "organizational skills",
        "organisational skills",
        "meet deadlines",
        "tight deadlines",
        "work under pressure",
        "fast paced environment",
        "manage workload",
        "workload management",
        "planning skills",
        "task planning",
        "διαχείριση χρόνου",
        "διαχειριση χρονου",
    ],

    "Διαχείριση προσοχής και συγκέντρωσης": [
        "attention to detail",
        "detail oriented",
        "detail-oriented",
        "detail orientation",
        "data accuracy",
        "high attention to detail",
        "focus on detail",
        "quality focus",
        "quality oriented",
        "error checking",
        "checking accuracy",
        "προσοχή στη λεπτομέρεια",
        "προσοχη στη λεπτομερεια",
    ],

    "Επιβεβαίωση οδηγιών και απαιτήσεων": [
        "clarify requirements",
        "requirement clarification",
        "confirm requirements",
        "confirm instructions",
        "requirements analysis",
        "business requirements",
        "understand requirements",
        "collect requirements",
        "analyze requirements",
        "analyse requirements",
        "validate requirements",
        "verify requirements",
        "follow instructions",
        "follow procedures",
        "requirements documentation",
        "confirm details",
        "επιβεβαίωση απαιτήσεων",
        "επιβεβαιωση απαιτησεων",
    ],
}


SEMANTIC_GROUPS_BY_MICROSKILL = {
    "Σαφής και συνοπτική επικοινωνία": [
        ["communication", "client"],
        ["communication", "customer"],
        ["communication", "stakeholder"],
        ["interpersonal", "skills"],
        ["presentation", "skills"],
    ],

    "Ενεργητική ακρόαση": [
        ["understand", "needs"],
        ["gather", "requirements"],
        ["identify", "needs"],
    ],

    "Αυτοματοποίηση επαναλαμβανόμενων εργασιών": [
        ["automate", "processes"],
        ["automation", "workflow"],
        ["streamline", "processes"],
    ],

    "Οργάνωση ψηφιακού χώρου εργασίας": [
        ["document", "management"],
        ["record", "keeping"],
        ["data", "entry"],
        ["maintain", "database"],
        ["update", "records"],
    ],

    "Διαχείριση χρόνου": [
        ["manage", "workload"],
        ["meet", "deadlines"],
        ["work", "pressure"],
        ["prioritize", "tasks"],
    ],

    "Διαχείριση προσοχής και συγκέντρωσης": [
        ["attention", "detail"],
        ["data", "accuracy"],
        ["error", "checking"],
    ],

    "Επιβεβαίωση οδηγιών και απαιτήσεων": [
        ["confirm", "requirements"],
        ["clarify", "requirements"],
        ["follow", "instructions"],
        ["verify", "details"],
    ],
}


def normalize_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = str(text).lower()
    text = text.replace("&", " and ")
    text = text.replace("+", " plus ")
    text = re.sub(r"[-_/]", " ", text)
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    text = re.sub(r"[^\w\sάέήίόύώϊΐϋΰ]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def simple_english_lemma(token: str) -> str:
    if token in IRREGULAR_EN_LEMMAS:
        return IRREGULAR_EN_LEMMAS[token]

    if len(token) <= 3:
        return token

    if token.endswith("ies") and len(token) > 4:
        return token[:-3] + "y"

    if token.endswith("ing") and len(token) > 5:
        base = token[:-3]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base

    if token.endswith("ed") and len(token) > 4:
        base = token[:-2]
        if len(base) >= 2 and base[-1] == base[-2]:
            base = base[:-1]
        return base

    if token.endswith("es") and len(token) > 4:
        return token[:-2]

    if token.endswith("s") and len(token) > 4 and not token.endswith("ss"):
        return token[:-1]

    return token


def simple_greek_lemma(token: str) -> str:
    if len(token) <= 4:
        return token

    suffixes = [
        "ώντας", "οντας", "ήσεις", "ησεις", "ήσεων", "ησεων",
        "ότητα", "οτητα", "ότητες", "οτητες", "τικών", "τικων",
        "ικούς", "ικους", "ικής", "ικης", "ικό", "ικο", "ικά", "ικα",
        "ίες", "ιες", "ους", "ες", "ων", "ης", "ας", "ος", "ου", "οι", "ια", "α"
    ]

    for suffix in suffixes:
        if token.endswith(suffix) and len(token) - len(suffix) >= 4:
            return token[:-len(suffix)]

    return token


def lemmatize_token(token: str) -> str:
    if re.search(r"[a-z]", token):
        return simple_english_lemma(token)

    if re.search(r"[α-ωάέήίόύώϊΐϋΰ]", token):
        return simple_greek_lemma(token)

    return token


def preprocess_text(text: str, remove_stopwords: bool = True, lemmatize: bool = True) -> str:
    text = normalize_text(text)
    tokens = text.split()

    processed_tokens = []

    for token in tokens:
        if remove_stopwords and token in STOPWORDS:
            continue

        if lemmatize:
            token = lemmatize_token(token)

        if token and len(token) > 1:
            processed_tokens.append(token)

    return " ".join(processed_tokens)


def parse_keywords(value: str) -> list[str]:
    if pd.isna(value):
        return []

    text = str(value).strip()

    if not text:
        return []

    parts = re.split(r"[,;|\n]+", text)

    return [part.strip().lower() for part in parts if part.strip()]


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
        "e mails": "emails",
        "chat gpt": "chatgpt",
        "gen ai": "genai",
        "multi tasking": "multitasking",
        "fast paced": "fastpaced",
        "detail oriented": "detailoriented",
    }

    for old, new in replacements.items():
        if old in keyword:
            variants.add(keyword.replace(old, new))

        if new in keyword:
            variants.add(keyword.replace(new, old))

    processed_variants = {preprocess_text(v) for v in variants if v}

    return sorted({v for v in variants | processed_variants if v})


def is_useful_keyword(keyword: str) -> bool:
    keyword = preprocess_text(keyword)

    if not keyword:
        return False

    tokens = keyword.split()

    if len(tokens) == 1:
        token = tokens[0]

        if token in STRONG_SINGLE_WORD_KEYWORDS:
            return True

        if token in GENERIC_SINGLE_WORDS:
            return False

        if token in STOPWORDS:
            return False

        if len(token) < 8:
            return False

        return False

    meaningful_tokens = [
        token for token in tokens
        if token not in STOPWORDS and token not in GENERIC_SINGLE_WORDS
    ]

    if len(meaningful_tokens) == 0:
        return False

    if len(keyword) < 7:
        return False

    too_generic_phrases = {
        "communication skill",
        "management skill",
        "organizational skill",
        "administrative support",
        "customer support",
        "team work",
        "problem solving",
        "project management",
        "data management",
        "quality control",
    }

    if keyword in too_generic_phrases:
        return False

    return True


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
        df["Categories Micro-skills (GR)"].fillna("").astype(str).str.strip()
    )

    df["keyword_list"] = df["Keywords"].apply(parse_keywords)

    df["keyword_list"] = df.apply(
        lambda row: row["keyword_list"]
        + EXTRA_KEYWORDS_BY_MICROSKILL.get(row["Microskills"], []),
        axis=1,
    )

    df["keyword_list"] = df["keyword_list"].apply(
        lambda keywords: sorted(
            set(
                variant
                for keyword in keywords
                for variant in expand_keyword_variants(keyword)
                if is_useful_keyword(variant)
            )
        )
    )

    df["semantic_groups"] = df["Microskills"].apply(
        lambda m: [
            [preprocess_text(term) for term in group if preprocess_text(term)]
            for group in SEMANTIC_GROUPS_BY_MICROSKILL.get(m, [])
        ]
    )

    return df


def build_matcher_entries(lexicon_df: pd.DataFrame) -> list[dict]:
    entries = []
    seen = set()

    for _, row in lexicon_df.iterrows():
        microskill = row["Microskills"]
        category = row["Categories Micro-skills (GR)"]

        for keyword in row["keyword_list"]:
            keyword = preprocess_text(keyword)

            if not keyword:
                continue

            key = (keyword, microskill)

            if key in seen:
                continue

            seen.add(key)

            entries.append({
                "keyword": keyword,
                "microskill": microskill,
                "category": category,
            })

    entries.sort(key=lambda x: len(x["keyword"]), reverse=True)

    return entries


def build_semantic_entries(lexicon_df: pd.DataFrame) -> list[dict]:
    entries = []

    for _, row in lexicon_df.iterrows():
        microskill = row["Microskills"]
        category = row["Categories Micro-skills (GR)"]

        for group in row["semantic_groups"]:
            group = [term for term in group if term]

            if len(group) >= 2:
                entries.append({
                    "group": group,
                    "microskill": microskill,
                    "category": category,
                })

    return entries


def keyword_matches_text(keyword: str, padded_text: str, tokens: set[str]) -> bool:
    keyword_tokens = keyword.split()

    if len(keyword_tokens) == 1:
        return keyword_tokens[0] in tokens

    return f" {keyword} " in padded_text


def detect_microskills_in_text(
    text: str,
    keyword_entries: list[dict],
    semantic_entries: list[dict]
):
    processed_text = preprocess_text(text)
    padded_text = f" {processed_text} "
    tokens = set(processed_text.split())

    scores = {}

    for entry in keyword_entries:
        keyword = entry["keyword"]

        if keyword_matches_text(keyword, padded_text, tokens):
            microskill = entry["microskill"]
            category = entry["category"]

            if microskill not in scores:
                scores[microskill] = {
                    "category": category,
                    "score": 0,
                    "keywords": [],
                    "semantic_groups": [],
                }

            keyword_score = 2 if len(keyword.split()) >= 2 else 1
            scores[microskill]["score"] += keyword_score

            if len(scores[microskill]["keywords"]) < 5:
                scores[microskill]["keywords"].append(keyword)

    for entry in semantic_entries:
        group = entry["group"]

        if all(term in tokens for term in group):
            microskill = entry["microskill"]
            category = entry["category"]

            if microskill not in scores:
                scores[microskill] = {
                    "category": category,
                    "score": 0,
                    "keywords": [],
                    "semantic_groups": [],
                }

            scores[microskill]["score"] += 1

            group_text = " + ".join(group)

            if len(scores[microskill]["semantic_groups"]) < 5:
                scores[microskill]["semantic_groups"].append(group_text)

    ranked = sorted(
        scores.items(),
        key=lambda item: (
            item[1]["score"],
            len(item[1]["keywords"]),
            len(item[1]["semantic_groups"]),
        ),
        reverse=True,
    )

    ranked = ranked[:MAX_MICROSKILLS_PER_JOB]

    found_microskills = [microskill for microskill, _ in ranked]
    found_categories = list(
        dict.fromkeys(data["category"] for _, data in ranked)
    )

    evidence = {
        microskill: {
            "score": data["score"],
            "keywords": data["keywords"],
            "semantic_groups": data["semantic_groups"],
        }
        for microskill, data in ranked
    }

    return found_microskills, found_categories, evidence


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

    keyword_entries = build_matcher_entries(lexicon_df)
    semantic_entries = build_semantic_entries(lexicon_df)

    print(f"Prepared {len(keyword_entries)} strict keyword/variant matcher entries")
    print(f"Prepared {len(semantic_entries)} semantic matcher entries")

    results = []

    for idx, row in jobs_df.iterrows():
        text = row.get("processed_text", row.get("cleaned_text", ""))

        detected_microskills, detected_categories, evidence = detect_microskills_in_text(
            text,
            keyword_entries,
            semantic_entries,
        )

        results.append({
            "id": row.get("id"),
            "title": row.get("title", ""),
            "detected_microskills": json.dumps(detected_microskills, ensure_ascii=False),
            "detected_categories": json.dumps(detected_categories, ensure_ascii=False),
            "detected_evidence": json.dumps(evidence, ensure_ascii=False),
            "detected_microskills_count": len(detected_microskills),
        })

        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(jobs_df)} jobs")

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    jobs_with_microskills = (out_df["detected_microskills_count"] > 0).sum()
    share = jobs_with_microskills / len(out_df) if len(out_df) else 0
    avg = out_df["detected_microskills_count"].mean() if len(out_df) else 0
    max_count = out_df["detected_microskills_count"].max() if len(out_df) else 0

    print(f"Saved matcher output to: {OUTPUT_PATH}")
    print(
        f"Jobs with at least one microskill: "
        f"{jobs_with_microskills}/{len(out_df)} ({share:.2%})"
    )
    print(f"Average microskills per job: {avg:.2f}")
    print(f"Max microskills in one job: {max_count}")

    print(out_df.head(10))


if __name__ == "__main__":
    main()
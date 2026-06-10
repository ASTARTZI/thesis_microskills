from pathlib import Path
import re
import pandas as pd


# Αρχείο εισόδου με τις αποδιπλοποιημένες αγγελίες.
INPUT_PATH = Path("data/final/all_jobs_deduplicated.csv")

# Αρχείο εξόδου όπου θα αποθηκευτεί το καθαρισμένο dataset.
OUTPUT_PATH = Path("data/final/all_jobs_cleaned.csv")


# Αγγλικά stopwords που αφαιρούνται κατά την προεπεξεργασία του κειμένου.
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
    "his", "her", "its", "as", "per", "via", "etc", "job", "role", "position", "company"
}

# Ελληνικά stopwords που δεν προσφέρουν ουσιαστική πληροφορία για την ανάλυση.
GR_STOPWORDS = {
    "ο", "η", "το", "οι", "τα", "του", "της", "των", "τον", "την", "τους", "τις",
    "και", "ή", "σε", "στο", "στη", "στην", "στον", "στα", "στις", "στους", "με",
    "χωρίς", "για", "από", "ως", "που", "πως", "να", "θα", "είναι", "ειναι", "ήταν",
    "ηταν", "έχει", "εχει", "έχουν", "εχουν", "μια", "ένα", "ενα", "ένας", "ενας",
    "αυτή", "αυτη", "αυτό", "αυτο", "αυτές", "αυτα", "αυτοί", "στης", "στην",
    "εργασία", "θέση", "εταιρεία", "εταιρεια", "υποψήφιος", "υποψηφιος"
}

# Ενώνει τα αγγλικά και ελληνικά stopwords σε ένα κοινό σύνολο.
STOPWORDS = EN_STOPWORDS | GR_STOPWORDS


# Χειροκίνητες αντιστοιχίσεις για συγκεκριμένους αγγλικούς ανώμαλους τύπους.
IRREGULAR_EN_LEMMAS = {
    "children": "child",
    "people": "person",
    "men": "man",
    "women": "woman",
    "data": "data",
    "analyses": "analysis",
    "indices": "index",
}


def normalize_text(text: str) -> str:
    # Κανονικοποιεί το αρχικό κείμενο: πεζά γράμματα, αφαίρεση ειδικών χαρακτήρων
    # και αντικατάσταση πολλαπλών κενών με ένα ενιαίο κενό.
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


def detect_language(text: str) -> str:
    # Εντοπίζει πρόχειρα τη γλώσσα της αγγελίας με βάση την αναλογία
    # ελληνικών και λατινικών χαρακτήρων.
    text = str(text)

    greek_chars = len(re.findall(r"[α-ωάέήίόύώϊΐϋΰ]", text.lower()))
    latin_chars = len(re.findall(r"[a-z]", text.lower()))

    if greek_chars == 0 and latin_chars == 0:
        return "unknown"

    total = greek_chars + latin_chars
    greek_ratio = greek_chars / total
    latin_ratio = latin_chars / total

    if greek_ratio >= 0.60:
        return "greek"

    if latin_ratio >= 0.60:
        return "english"

    return "mixed"


def simple_english_lemma(token: str) -> str:
    # Εφαρμόζει απλό lemmatization/stemming σε αγγλικές λέξεις,
    # ώστε διαφορετικές μορφές της ίδιας λέξης να αντιμετωπίζονται πιο ομοιόμορφα.
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
    # Εφαρμόζει απλή αποκοπή ελληνικών καταλήξεων,
    # για να μειωθεί η επίδραση διαφορετικών κλιτών μορφών.
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
    # Επιλέγει την κατάλληλη απλή κανονικοποίηση ανάλογα με το αν το token είναι αγγλικό ή ελληνικό.
    if re.search(r"[a-z]", token):
        return simple_english_lemma(token)

    if re.search(r"[α-ωάέήίόύώϊΐϋΰ]", token):
        return simple_greek_lemma(token)

    return token


def preprocess_text(text: str, remove_stopwords: bool = True, lemmatize: bool = True) -> str:
    # Εκτελεί πλήρη προεπεξεργασία κειμένου:
    # καθαρισμό, διαχωρισμό σε tokens, αφαίρεση stopwords και απλό lemmatization.
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


def main():
    # Ελέγχει αν υπάρχει το αρχείο εισόδου με τις αποδιπλοποιημένες αγγελίες.
    if not INPUT_PATH.exists():
        print(f"Input file not found: {INPUT_PATH}")
        return

    # Φορτώνει το dataset των αγγελιών.
    df = pd.read_csv(INPUT_PATH)

    # Αν λείπουν οι βασικές στήλες, δημιουργούνται κενές ώστε να μη σταματήσει η εκτέλεση.
    if "title" not in df.columns:
        df["title"] = ""

    if "description" not in df.columns:
        df["description"] = ""

    # Ενώνει τίτλο και περιγραφή σε ένα ενιαίο κείμενο για ανάλυση.
    df["combined_text"] = (
        df["title"].fillna("").astype(str)
        + " "
        + df["description"].fillna("").astype(str)
    )

    # Δημιουργεί δύο εκδοχές του κειμένου:
    # cleaned_text για καθαρισμένη μορφή και processed_text για χρήση σε matching/ανάλυση.
    df["cleaned_text"] = df["combined_text"].apply(normalize_text)
    df["processed_text"] = df["combined_text"].apply(preprocess_text)

    # Προσθέτει ένδειξη γλώσσας για κάθε αγγελία.
    df["detected_language"] = df["combined_text"].apply(detect_language)

    # Κρατά μόνο τις στήλες που χρειάζονται στα επόμενα στάδια της ανάλυσης.
    out_df = df[
        ["id", "title", "cleaned_text", "processed_text", "detected_language"]
    ].copy()

    # Αποθηκεύει το καθαρισμένο dataset σε CSV αρχείο.
    out_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Saved cleaned dataset to: {OUTPUT_PATH}")
    print(out_df.head())


if __name__ == "__main__":
    # Εκτελεί τη διαδικασία καθαρισμού όταν το αρχείο τρέχει απευθείας.
    main()
from pathlib import Path
import pandas as pd
import json
from collections import Counter


# Ορίζει το αρχείο εισόδου που περιέχει τις αγγελίες με τα microskills που έχουν ήδη ανιχνευθεί.
INPUT_PATH = Path("data/final/jobs_with_microskills.csv")

# Ορίζει τον φάκελο εξόδου όπου θα αποθηκευτούν τα τελικά αρχεία σύνοψης και συχνοτήτων.
OUTPUT_DIR = Path("data/final")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_json_list(value):
    # Μετατρέπει μία τιμή που είναι αποθηκευμένη ως JSON string σε κανονική λίστα Python.
    # Αν η τιμή είναι κενή, λανθασμένη ή δεν μπορεί να διαβαστεί, επιστρέφει κενή λίστα.
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
    # Ελέγχει αν υπάρχει το αρχείο εισόδου πριν ξεκινήσει η ανάλυση.
    if not INPUT_PATH.exists():
        print(f"Input file not found: {INPUT_PATH}")
        return

    # Φορτώνει το τελικό αρχείο αγγελιών σε DataFrame.
    df = pd.read_csv(INPUT_PATH)

    # Μετατρέπει τις στήλες με microskills και κατηγορίες από JSON strings σε λίστες.
    df["detected_microskills"] = df["detected_microskills"].apply(parse_json_list)
    df["detected_categories"] = df["detected_categories"].apply(parse_json_list)

    # Μετατρέπει το πλήθος των microskills σε ακέραιο αριθμό, χειριζόμενο τυχόν μη έγκυρες τιμές.
    df["detected_microskills_count"] = pd.to_numeric(
        df["detected_microskills_count"], errors="coerce"
    ).fillna(0).astype(int)

    # Υπολογίζει βασικά συνολικά στατιστικά για τις αγγελίες και τα ανιχνευμένα microskills.
    total_jobs = len(df)
    jobs_with_microskills = (df["detected_microskills_count"] > 0).sum()
    jobs_without_microskills = (df["detected_microskills_count"] == 0).sum()
    avg_microskills = df["detected_microskills_count"].mean()

    # Δημιουργεί μετρητές για τη συχνότητα εμφάνισης κάθε microskill και κάθε κατηγορίας.
    microskill_counter = Counter()
    category_counter = Counter()

    # Μετρά πόσες φορές εμφανίζεται κάθε microskill στο σύνολο των αγγελιών.
    for microskills in df["detected_microskills"]:
        microskill_counter.update(microskills)

    # Μετρά πόσες φορές εμφανίζεται κάθε κατηγορία microskills στο σύνολο των αγγελιών.
    for categories in df["detected_categories"]:
        category_counter.update(categories)

    # Δημιουργεί πίνακα με τη συχνότητα των microskills, ταξινομημένο από το συχνότερο προς το λιγότερο συχνό.
    microskills_df = pd.DataFrame(
        microskill_counter.items(),
        columns=["microskill", "frequency"]
    ).sort_values("frequency", ascending=False)

    # Δημιουργεί αντίστοιχο πίνακα συχνοτήτων για τις κατηγορίες microskills.
    categories_df = pd.DataFrame(
        category_counter.items(),
        columns=["category", "frequency"]
    ).sort_values("frequency", ascending=False)

    # Δημιουργεί συνοπτικό πίνακα με βασικούς δείκτες για την παρουσία microskills στις αγγελίες.
    summary_df = pd.DataFrame([
        {"metric": "total_jobs", "value": total_jobs},
        {"metric": "jobs_with_microskills", "value": jobs_with_microskills},
        {"metric": "jobs_without_microskills", "value": jobs_without_microskills},
        {"metric": "share_with_microskills", "value": round(jobs_with_microskills / total_jobs, 4) if total_jobs else 0},
        {"metric": "average_microskills_per_job", "value": round(avg_microskills, 4)},
    ])

    # Ορίζει τα ονόματα των αρχείων εξόδου.
    summary_path = OUTPUT_DIR / "microskills_summary.csv"
    microskills_path = OUTPUT_DIR / "microskills_frequency.csv"
    categories_path = OUTPUT_DIR / "microskills_categories_frequency.csv"

    # Αποθηκεύει τα αποτελέσματα σε CSV αρχεία με ελληνική/Unicode συμβατότητα.
    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    microskills_df.to_csv(microskills_path, index=False, encoding="utf-8-sig")
    categories_df.to_csv(categories_path, index=False, encoding="utf-8-sig")

    # Εμφανίζει στη γραμμή εντολών τη σύνοψη και τα 10 συχνότερα microskills και κατηγορίες.
    print("=== SUMMARY ===")
    print(summary_df)

    print("\n=== TOP MICROSKILLS ===")
    print(microskills_df.head(10))

    print("\n=== TOP CATEGORIES ===")
    print(categories_df.head(10))

    # Ενημερώνει τον χρήστη για τα αρχεία που δημιουργήθηκαν.
    print(f"\nSaved summary to: {summary_path}")
    print(f"Saved microskill frequencies to: {microskills_path}")
    print(f"Saved category frequencies to: {categories_path}")


if __name__ == "__main__":
    # Εκτελεί τη βασική ροή του αρχείου όταν τρέχει απευθείας από τη γραμμή εντολών.
    main()
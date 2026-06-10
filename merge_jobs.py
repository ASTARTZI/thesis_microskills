# merge_jobs.py

from pathlib import Path
import pandas as pd


# Φάκελος που περιέχει τα επιμέρους αρχεία αγγελιών μετά τη συλλογή δεδομένων.
PROCESSED_DIR = Path("data/processed")

# Φάκελος όπου θα αποθηκευτούν τα τελικά ενοποιημένα αρχεία.
FINAL_DIR = Path("data/final")
FINAL_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # Εντοπίζει όλα τα αρχεία CSV που έχουν παραχθεί από τη διαδικασία συλλογής αγγελιών.
    csv_files = list(PROCESSED_DIR.glob("*.csv"))

    # Ελέγχει αν υπάρχουν αρχεία προς συγχώνευση.
    if not csv_files:
        print("No CSV files found in data/processed")
        return

    frames = []

    # Φορτώνει κάθε αρχείο CSV και προσθέτει πληροφορία για το αρχείο προέλευσής του.
    for file in csv_files:
        df = pd.read_csv(file)
        df["source_file"] = file.name
        frames.append(df)

    # Ενοποιεί όλα τα DataFrames σε ένα ενιαίο σύνολο δεδομένων.
    combined = pd.concat(frames, ignore_index=True)
    print("Combined rows before dedup:", len(combined))

    # Αφαιρεί διπλότυπες αγγελίες με βάση το μοναδικό αναγνωριστικό τους (id).
    dedup = combined.drop_duplicates(subset=["id"]).copy()
    print("Rows after dedup:", len(dedup))

    # Ορίζει τα ονόματα των τελικών αρχείων εξόδου.
    combined_path = FINAL_DIR / "all_jobs_combined.csv"
    dedup_path = FINAL_DIR / "all_jobs_deduplicated.csv"

    # Αποθηκεύει τόσο το πλήρες όσο και το αποδιπλοποιημένο σύνολο δεδομένων.
    combined.to_csv(combined_path, index=False, encoding="utf-8-sig")
    dedup.to_csv(dedup_path, index=False, encoding="utf-8-sig")

    print(f"Saved combined file to: {combined_path}")
    print(f"Saved deduplicated file to: {dedup_path}")


if __name__ == "__main__":
    # Εκτελεί τη διαδικασία συγχώνευσης και αποδιπλοποίησης των αγγελιών.
    main()
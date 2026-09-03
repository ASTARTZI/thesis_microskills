import json
import pandas as pd
from pathlib import Path


def save_jobs_json(items, path: Path):
    # Αποθηκεύει τις αγγελίες σε αρχείο JSON,
    # διατηρώντας τη δομή των δεδομένων όπως επιστράφηκαν από το API.
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def save_jobs_csv(items, path: Path):
    # Ελέγχει αν υπάρχουν δεδομένα προς αποθήκευση.
    # Αν η λίστα είναι κενή, η διαδικασία τερματίζεται.
    if not items:
        print("No items to save.")
        return

    # Μετατρέπει τη λίστα των αγγελιών σε DataFrame
    # και την αποθηκεύει σε μορφή CSV για περαιτέρω επεξεργασία.
    df = pd.DataFrame(items)
    df.to_csv(path, index=False, encoding="utf-8-sig")
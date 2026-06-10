from pathlib import Path
from requests.exceptions import ReadTimeout, RequestException

from collector import TrackerClient, build_request_body
from extractor import save_jobs_json, save_jobs_csv


# Ορίζει σε ποια γλώσσα θα πραγματοποιηθεί η αναζήτηση των αγγελιών.
SEARCH_LANGUAGE_MODE = "bilingual"
# Επιλογές:
# "english"   -> ψάχνει μόνο αγγλικά keywords
# "greek"     -> ψάχνει μόνο ελληνικά keywords
# "bilingual" -> ψάχνει αγγλικά + ελληνικά μαζί


# Ομάδες λέξεων-κλειδιών που χρησιμοποιούνται για τη συλλογή αγγελιών.
# Κάθε ομάδα έχει μία ετικέτα και αντίστοιχα keywords στα αγγλικά και στα ελληνικά.
KEYWORD_GROUPS = [
    {
        "label": "assistant",
        "english": ["assistant"],
        "greek": ["βοηθός", "βοηθος"],
    },
    {
        "label": "administrator",
        "english": ["administrator", "administrative"],
        "greek": ["διοικητικός", "διοικητικος", "γραμματειακή υποστήριξη", "γραμματειακη υποστηριξη"],
    },
    {
        "label": "office",
        "english": ["office"],
        "greek": ["γραφείο", "γραφειο"],
    },
    {
        "label": "coordinator",
        "english": ["coordinator"],
        "greek": ["συντονιστής", "συντονιστης", "συντονίστρια", "συντονιστρια"],
    },
    {
        "label": "support",
        "english": ["support"],
        "greek": ["υποστήριξη", "υποστηριξη"],
    },
    {
        "label": "customer_service",
        "english": ["customer service", "customer support"],
        "greek": ["εξυπηρέτηση πελατών", "εξυπηρετηση πελατων", "υποστήριξη πελατών", "υποστηριξη πελατων"],
    },
    {
        "label": "sales",
        "english": ["sales"],
        "greek": ["πωλήσεις", "πωλησεις", "πωλητής", "πωλητης", "πωλήτρια", "πωλητρια"],
    },
    {
        "label": "marketing",
        "english": ["marketing"],
        "greek": ["μάρκετινγκ", "μαρκετινγκ"],
    },
    {
        "label": "hr",
        "english": ["hr", "human resources"],
        "greek": ["ανθρώπινο δυναμικό", "ανθρωπινο δυναμικο"],
    },
    {
        "label": "recruiter",
        "english": ["recruiter", "recruitment"],
        "greek": ["προσλήψεις", "προσληψεις", "υπεύθυνος προσλήψεων", "υπευθυνος προσληψεων"],
    },
    {
        "label": "analyst",
        "english": ["analyst"],
        "greek": ["αναλυτής", "αναλυτης", "αναλύτρια", "αναλυτρια"],
    },
    {
        "label": "project_manager",
        "english": ["project manager", "project management"],
        "greek": ["διαχειριστής έργου", "διαχειριστης εργου", "υπεύθυνος έργου", "υπευθυνος εργου"],
    },
    {
        "label": "operations",
        "english": ["operations"],
        "greek": ["λειτουργίες", "λειτουργιες", "επιχειρησιακές λειτουργίες", "επιχειρησιακες λειτουργιες"],
    },
    {
        "label": "secretary",
        "english": ["secretary"],
        "greek": ["γραμματέας", "γραμματεας", "γραμματειακή", "γραμματειακη"],
    },
    {
        "label": "communication",
        "english": ["communication"],
        "greek": ["επικοινωνία", "επικοινωνια"],
    },
    {
        "label": "data_entry",
        "english": ["data entry"],
        "greek": ["καταχώρηση δεδομένων", "καταχωρηση δεδομενων"],
    },
    {
        "label": "developer",
        "english": ["developer"],
        "greek": ["προγραμματιστής", "προγραμματιστης", "προγραμματίστρια", "προγραμματιστρια"],
    },
    {
        "label": "software_engineer",
        "english": ["software engineer", "software developer"],
        "greek": ["μηχανικός λογισμικού", "μηχανικος λογισμικου", "προγραμματιστής λογισμικού", "προγραμματιστης λογισμικου"],
    },
]


# Κωδικός χώρας για την αναζήτηση αγγελιών στην Ελλάδα.
LOCATION_CODE = "EL"

# Μέγιστος αριθμός σελίδων που θα ανακτηθούν ανά ομάδα keywords.
MAX_PAGES = 3


def get_keywords_for_group(group: dict) -> list[str]:
    # Επιστρέφει τα keywords μιας ομάδας ανάλογα με τη γλωσσική ρύθμιση αναζήτησης.
    if SEARCH_LANGUAGE_MODE == "english":
        return group["english"]

    if SEARCH_LANGUAGE_MODE == "greek":
        return group["greek"]

    if SEARCH_LANGUAGE_MODE == "bilingual":
        return group["english"] + group["greek"]

    # Αν έχει δοθεί λάθος τιμή στη ρύθμιση γλώσσας, σταματά η εκτέλεση με επεξηγηματικό μήνυμα.
    raise ValueError(
        "Λάθος SEARCH_LANGUAGE_MODE. "
        "Χρησιμοποίησε: english, greek ή bilingual."
    )


def main():
    # Δημιουργεί τους φακέλους για τα ακατέργαστα και τα επεξεργασμένα δεδομένα, αν δεν υπάρχουν ήδη.
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    # Δημιουργεί client για την επικοινωνία με το Tracker API.
    client = TrackerClient()

    # Κρατά τις ομάδες keywords που απέτυχαν, ώστε να εμφανιστούν στο τέλος.
    failed_groups = []

    # Εκτελεί αναζήτηση για κάθε ομάδα λέξεων-κλειδιών.
    for group in KEYWORD_GROUPS:
        label = group["label"]
        keywords = get_keywords_for_group(group)

        print(f"\nRunning keyword group: {label}")
        print(f"Search language mode: {SEARCH_LANGUAGE_MODE}")
        print(f"Keywords: {keywords}")

        # Δημιουργεί το σώμα του αιτήματος προς το API με keywords και χώρα αναζήτησης.
        body = build_request_body(
            keywords=keywords,
            keywords_logic="or",
            location_code=[LOCATION_CODE],
        )

        print("Request body:", body)

        try:
            # Ανακτά τις αγγελίες από το API για τη συγκεκριμένη ομάδα keywords.
            items = client.fetch_all_jobs(body=body, max_pages=MAX_PAGES)
            print(f"Total fetched items: {len(items)}")

            # Δημιουργεί κοινό όνομα αρχείου με βάση την ομάδα, τη γλώσσα και τη χώρα.
            file_stub = f"jobs_{label}_{SEARCH_LANGUAGE_MODE}_{LOCATION_CODE.lower()}"

            json_path = Path("data/raw") / f"{file_stub}.json"
            csv_path = Path("data/processed") / f"{file_stub}.csv"

            # Αποθηκεύει τα αποτελέσματα τόσο σε JSON όσο και σε CSV μορφή.
            save_jobs_json(items, json_path)
            save_jobs_csv(items, csv_path)

            print(f"Saved raw JSON to: {json_path}")
            print(f"Saved CSV to: {csv_path}")

        except ReadTimeout:
            # Διαχειρίζεται περιπτώσεις όπου το API καθυστερεί υπερβολικά να απαντήσει.
            print(f"TIMEOUT στο keyword group: {label}")
            failed_groups.append(label)
            continue

        except RequestException as e:
            # Διαχειρίζεται γενικά σφάλματα HTTP ή σύνδεσης με το API.
            print(f"Request error στο keyword group '{label}': {e}")
            failed_groups.append(label)
            continue

        except Exception as e:
            # Διαχειρίζεται απρόβλεπτα σφάλματα, ώστε να συνεχίσει η εκτέλεση στις επόμενες ομάδες.
            print(f"Unexpected error στο keyword group '{label}': {e}")
            failed_groups.append(label)
            continue

    print("\n=== RUN FINISHED ===")

    # Εμφανίζει συγκεντρωτικά ποιες ομάδες ολοκληρώθηκαν ή απέτυχαν.
    if failed_groups:
        print("Keyword groups που απέτυχαν:")
        for group in failed_groups:
            print("-", group)
    else:
        print("Όλα τα keyword groups ολοκληρώθηκαν επιτυχώς.")


if __name__ == "__main__":
    # Εκτελεί τη βασική διαδικασία συλλογής αγγελιών όταν το αρχείο τρέχει απευθείας.
    main()
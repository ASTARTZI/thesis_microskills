from pathlib import Path
from requests.exceptions import ReadTimeout, RequestException

from collector import TrackerClient, build_request_body
from extractor import save_jobs_json, save_jobs_csv


SEARCH_LANGUAGE_MODE = "bilingual"
# Επιλογές:
# "english"   -> ψάχνει μόνο αγγλικά keywords
# "greek"     -> ψάχνει μόνο ελληνικά keywords
# "bilingual" -> ψάχνει αγγλικά + ελληνικά μαζί


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


LOCATION_CODE = "EL"
MAX_PAGES = 3


def get_keywords_for_group(group: dict) -> list[str]:
    if SEARCH_LANGUAGE_MODE == "english":
        return group["english"]

    if SEARCH_LANGUAGE_MODE == "greek":
        return group["greek"]

    if SEARCH_LANGUAGE_MODE == "bilingual":
        return group["english"] + group["greek"]

    raise ValueError(
        "Λάθος SEARCH_LANGUAGE_MODE. "
        "Χρησιμοποίησε: english, greek ή bilingual."
    )


def main():
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    client = TrackerClient()
    failed_groups = []

    for group in KEYWORD_GROUPS:
        label = group["label"]
        keywords = get_keywords_for_group(group)

        print(f"\nRunning keyword group: {label}")
        print(f"Search language mode: {SEARCH_LANGUAGE_MODE}")
        print(f"Keywords: {keywords}")

        body = build_request_body(
            keywords=keywords,
            keywords_logic="or",
            location_code=[LOCATION_CODE],
        )

        print("Request body:", body)

        try:
            items = client.fetch_all_jobs(body=body, max_pages=MAX_PAGES)
            print(f"Total fetched items: {len(items)}")

            file_stub = f"jobs_{label}_{SEARCH_LANGUAGE_MODE}_{LOCATION_CODE.lower()}"

            json_path = Path("data/raw") / f"{file_stub}.json"
            csv_path = Path("data/processed") / f"{file_stub}.csv"

            save_jobs_json(items, json_path)
            save_jobs_csv(items, csv_path)

            print(f"Saved raw JSON to: {json_path}")
            print(f"Saved CSV to: {csv_path}")

        except ReadTimeout:
            print(f"TIMEOUT στο keyword group: {label}")
            failed_groups.append(label)
            continue

        except RequestException as e:
            print(f"Request error στο keyword group '{label}': {e}")
            failed_groups.append(label)
            continue

        except Exception as e:
            print(f"Unexpected error στο keyword group '{label}': {e}")
            failed_groups.append(label)
            continue

    print("\n=== RUN FINISHED ===")

    if failed_groups:
        print("Keyword groups που απέτυχαν:")
        for group in failed_groups:
            print("-", group)
    else:
        print("Όλα τα keyword groups ολοκληρώθηκαν επιτυχώς.")


if __name__ == "__main__":
    main()
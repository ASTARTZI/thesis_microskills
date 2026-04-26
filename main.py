from pathlib import Path
from requests.exceptions import ReadTimeout, RequestException

from collector import TrackerClient, build_request_body
from extractor import save_jobs_json, save_jobs_csv


KEYWORDS = [
    "assistant",
    "administrator",
    "office",
    "coordinator",
    "support",
    "customer service",
    "sales",
    "marketing",
    "hr",
    "recruiter",
    "analyst",
    "project manager",
    "operations",
    "secretary",
    "communication",
    "data entry",
    "developer",
    "software engineer",
]

LOCATION_CODE = "EL"
MAX_PAGES = 3


def slugify_keyword(text: str) -> str:
    return (
        text.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace(".", "dot")
    )


def main():
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    client = TrackerClient()

    failed_keywords = []

    for keyword in KEYWORDS:
        print(f"\nRunning keyword: {keyword}")

        body = build_request_body(
            keywords=[keyword],
            keywords_logic="or",
            location_code=[LOCATION_CODE],
        )

        print("Request body:", body)

        try:
            items = client.fetch_all_jobs(body=body, max_pages=MAX_PAGES)
            print(f"Total fetched items: {len(items)}")

            file_stub = f"jobs_{slugify_keyword(keyword)}_{LOCATION_CODE.lower()}"

            json_path = Path("data/raw") / f"{file_stub}.json"
            csv_path = Path("data/processed") / f"{file_stub}.csv"

            save_jobs_json(items, json_path)
            save_jobs_csv(items, csv_path)

            print(f"Saved raw JSON to: {json_path}")
            print(f"Saved CSV to: {csv_path}")

        except ReadTimeout:
            print(f"TIMEOUT στο keyword: {keyword}")
            failed_keywords.append(keyword)
            continue

        except RequestException as e:
            print(f"Request error στο keyword '{keyword}': {e}")
            failed_keywords.append(keyword)
            continue

        except Exception as e:
            print(f"Unexpected error στο keyword '{keyword}': {e}")
            failed_keywords.append(keyword)
            continue

    print("\n=== RUN FINISHED ===")
    if failed_keywords:
        print("Keywords που απέτυχαν:")
        for kw in failed_keywords:
            print("-", kw)
    else:
        print("Όλα τα keywords ολοκληρώθηκαν επιτυχώς.")


if __name__ == "__main__":
    main()
    
    
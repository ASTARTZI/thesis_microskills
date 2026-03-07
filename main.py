import json
from pathlib import Path

from collector import TrackerClient, build_request_body
from extractor import jobs_to_dataframe
from keywords import TECH_KEYWORDS


def save_keyword_results(client: TrackerClient, keyword: str) -> None:
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")

    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    body = build_request_body(
        keywords=[keyword],
        keywords_logic="or",
        location_code=["EL"],
    )

    print(f"\nRunning keyword: {keyword}")
    print("Request body:", body)

    items = client.fetch_all_jobs(body=body, max_pages=1)
    print(f"Total fetched items: {len(items)}")

    keyword_part = keyword.replace(" ", "_").replace(".", "dot").lower()
    location_part = "_".join(body.get("location_code", ["all"])).lower()

    raw_path = raw_dir / f"jobs_{keyword_part}_{location_part}.json"
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    df = jobs_to_dataframe(items)
    csv_path = processed_dir / f"jobs_{keyword_part}_{location_part}.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    print(f"Saved raw JSON to: {raw_path}")
    print(f"Saved CSV to: {csv_path}")


def main() -> None:
    client = TrackerClient(page_size=100)

    for keyword in TECH_KEYWORDS:
        try:
            save_keyword_results(client, keyword)
        except Exception as e:
            print(f"Error for keyword '{keyword}': {e}")


if __name__ == "__main__":
    main()
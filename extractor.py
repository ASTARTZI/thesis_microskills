from typing import Any, Dict, List
import pandas as pd


def jobs_to_dataframe(items: List[Dict[str, Any]]) -> pd.DataFrame:
    rows = []

    for item in items:
        rows.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "description": item.get("description"),
            "experience_level": item.get("experience_level"),
            "type": item.get("type"),
            "location": item.get("location"),
            "location_code": item.get("location_code"),
            "upload_date": item.get("upload_date"),
            "source": item.get("source"),
            "source_id": item.get("source_id"),
            "organization": item.get("organization"),
            "skills": item.get("skills", []),
            "occupations": item.get("occupations", []),
        })

    return pd.DataFrame(rows)
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# =========================
# PATHS
# =========================

SUMMARY_PATH = Path("data/final/microskills_summary.csv")
MICROSKILLS_FREQ_PATH = Path("data/final/microskills_frequency.csv")
CATEGORIES_FREQ_PATH = Path("data/final/microskills_categories_frequency.csv")
MATCHER_OUTPUT_PATH = Path("data/final/jobs_with_microskills.csv")
CLEANED_JOBS_PATH = Path("data/final/all_jobs_cleaned.csv")

OUTPUT_DIR = Path("data/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# LOAD DATA
# =========================

summary_df = pd.read_csv(SUMMARY_PATH)
microskills_df = pd.read_csv(MICROSKILLS_FREQ_PATH)
categories_df = pd.read_csv(CATEGORIES_FREQ_PATH)
matcher_df = pd.read_csv(MATCHER_OUTPUT_PATH)
cleaned_df = pd.read_csv(CLEANED_JOBS_PATH)


# =========================
# 1. JOBS WITH / WITHOUT MICROSKILLS
# =========================

jobs_with = int(
    summary_df.loc[
        summary_df["metric"] == "jobs_with_microskills",
        "value"
    ].values[0]
)

jobs_without = int(
    summary_df.loc[
        summary_df["metric"] == "jobs_without_microskills",
        "value"
    ].values[0]
)

plt.figure(figsize=(7, 7))

plt.pie(
    [jobs_with, jobs_without],
    labels=["With Microskills", "Without Microskills"],
    autopct="%1.1f%%"
)

plt.title("Jobs With and Without Detected Microskills")

plt.savefig(
    OUTPUT_DIR / "jobs_with_without_microskills.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: jobs_with_without_microskills.png")


# =========================
# 2. TOP 10 MICROSKILLS
# =========================

TOP_N = 10

top_micro_df = microskills_df.head(TOP_N)

plt.figure(figsize=(12, 7))

plt.barh(
    top_micro_df["microskill"],
    top_micro_df["frequency"]
)

plt.xlabel("Frequency")
plt.ylabel("Microskill")
plt.title("Top 10 Detected Microskills")

plt.gca().invert_yaxis()

plt.savefig(
    OUTPUT_DIR / "top_10_microskills.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: top_10_microskills.png")


# =========================
# 3. TOP CATEGORIES
# =========================

plt.figure(figsize=(12, 7))

plt.barh(
    categories_df["category"],
    categories_df["frequency"]
)

plt.xlabel("Frequency")
plt.ylabel("Category")
plt.title("Microskill Categories Frequency")

plt.gca().invert_yaxis()

plt.savefig(
    OUTPUT_DIR / "microskill_categories.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: microskill_categories.png")


# =========================
# 4. DISTRIBUTION OF MICROSKILLS PER JOB
# =========================

plt.figure(figsize=(10, 6))

plt.hist(
    matcher_df["detected_microskills_count"],
    bins=range(0, 8)
)

plt.xlabel("Detected Microskills per Job")
plt.ylabel("Number of Jobs")
plt.title("Distribution of Microskills per Job")

plt.savefig(
    OUTPUT_DIR / "microskills_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: microskills_distribution.png")


# =========================
# 5. LANGUAGE DISTRIBUTION
# =========================

language_counts = cleaned_df["detected_language"].value_counts()

plt.figure(figsize=(7, 7))

plt.pie(
    language_counts.values,
    labels=language_counts.index,
    autopct="%1.1f%%"
)

plt.title("Language Distribution of Job Ads")

plt.savefig(
    OUTPUT_DIR / "language_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: language_distribution.png")

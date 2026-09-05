from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# PATHS

# Αρχεία εισόδου που έχουν παραχθεί από τα προηγούμενα στάδια της ανάλυσης.
SUMMARY_PATH = Path("data/final/microskills_summary.csv")
MICROSKILLS_FREQ_PATH = Path("data/final/microskills_frequency.csv")
CATEGORIES_FREQ_PATH = Path("data/final/microskills_categories_frequency.csv")
MATCHER_OUTPUT_PATH = Path("data/final/jobs_with_microskills.csv")
CLEANED_JOBS_PATH = Path("data/final/all_jobs_cleaned.csv")

# Φάκελος όπου θα αποθηκευτούν τα γραφήματα της ανάλυσης.
OUTPUT_DIR = Path("data/visualizations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# LOAD DATA

# Φορτώνει τα αρχεία με τα συνοπτικά αποτελέσματα, τις συχνότητες και τα καθαρισμένα δεδομένα.
summary_df = pd.read_csv(SUMMARY_PATH)
microskills_df = pd.read_csv(MICROSKILLS_FREQ_PATH)
categories_df = pd.read_csv(CATEGORIES_FREQ_PATH)
matcher_df = pd.read_csv(MATCHER_OUTPUT_PATH)
cleaned_df = pd.read_csv(CLEANED_JOBS_PATH)


# JOBS WITH / WITHOUT MICROSKILLS

# Ανακτά από το summary το πλήθος αγγελιών στις οποίες ανιχνεύθηκαν microskills.
jobs_with = int(
    summary_df.loc[
        summary_df["metric"] == "jobs_with_microskills",
        "value"
    ].values[0]
)

# Ανακτά από το summary το πλήθος αγγελιών χωρίς ανιχνευμένα microskills.
jobs_without = int(
    summary_df.loc[
        summary_df["metric"] == "jobs_without_microskills",
        "value"
    ].values[0]
)

# Δημιουργεί κυκλικό γράφημα με το ποσοστό αγγελιών με και χωρίς microskills.
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


# TOP 10 MICROSKILLS

# Ορίζει πόσα από τα συχνότερα microskills θα εμφανιστούν στο γράφημα.
TOP_N = 10

# Επιλέγει τα 10 συχνότερα microskills.
top_micro_df = microskills_df.head(TOP_N)

# Δημιουργεί οριζόντιο ραβδόγραμμα για τα συχνότερα microskills.
plt.figure(figsize=(12, 7))

plt.barh(
    top_micro_df["microskill"],
    top_micro_df["frequency"]
)

plt.xlabel("Frequency")
plt.ylabel("Microskill")
plt.title("Top 10 Detected Microskills")

# Αντιστρέφει τον άξονα ώστε το συχνότερο microskill να εμφανίζεται πρώτο.
plt.gca().invert_yaxis()

plt.savefig(
    OUTPUT_DIR / "top_10_microskills.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: top_10_microskills.png")


# TOP CATEGORIES

# Δημιουργεί γράφημα συχνοτήτων για τις κατηγορίες microskills.
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


# DISTRIBUTION OF MICROSKILLS PER JOB

# Υπολογίζει πόσες αγγελίες έχουν 0, 1, 2, 3 κτλ. microskills.
microskills_per_job_counts = (
    matcher_df["detected_microskills_count"]
    .value_counts()
    .sort_index()
)

# Δημιουργεί ραβδόγραμμα που δείχνει πόσα microskills ανιχνεύθηκαν ανά αγγελία.
plt.figure(figsize=(10, 6))

plt.bar(
    microskills_per_job_counts.index,
    microskills_per_job_counts.values
)

plt.xlabel("Detected Microskills per Job")
plt.ylabel("Number of Jobs")
plt.title("Distribution of Microskills per Job")

# Εμφανίζει στον οριζόντιο άξονα τις διακριτές τιμές των microskills ανά αγγελία.
plt.xticks(microskills_per_job_counts.index)

plt.savefig(
    OUTPUT_DIR / "microskills_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Saved: microskills_distribution.png")


# LANGUAGE DISTRIBUTION

# Υπολογίζει πόσες αγγελίες ανήκουν σε κάθε γλωσσική κατηγορία.
language_counts = cleaned_df["detected_language"].value_counts()

# Δημιουργεί κυκλικό γράφημα για την κατανομή γλώσσας των αγγελιών.
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
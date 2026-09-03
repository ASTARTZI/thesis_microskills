import streamlit as st
import pandas as pd


# Ορίζει τις βασικές ρυθμίσεις της σελίδας της εφαρμογής.
# Καθορίζει τον τίτλο που εμφανίζεται στον browser και το πλάτος της σελίδας.
st.set_page_config(
    page_title="MicroSkills Lexicon Explorer",
    layout="wide"
)


# Ορίζει την εμφάνιση της εφαρμογής.
# Χρησιμοποιείται συνδυασμός σκούρου μπλε και μαύρου χρώματος
# με κυκλικές διαβαθμίσεις ώστε να δημιουργείται εφέ σταγόνων στο background.
st.markdown(
    """
    <style>

    /* Κύριο background της εφαρμογής */
    .stApp {
        background:
            radial-gradient(
                circle at 15% 20%,
                rgba(16, 52, 96, 0.45) 0%,
                rgba(16, 52, 96, 0.18) 18%,
                transparent 35%
            ),
            radial-gradient(
                circle at 85% 15%,
                rgba(0, 38, 77, 0.45) 0%,
                rgba(0, 38, 77, 0.15) 20%,
                transparent 38%
            ),
            radial-gradient(
                circle at 75% 70%,
                rgba(11, 61, 105, 0.40) 0%,
                rgba(11, 61, 105, 0.12) 22%,
                transparent 40%
            ),
            radial-gradient(
                circle at 20% 80%,
                rgba(0, 22, 45, 0.60) 0%,
                rgba(0, 22, 45, 0.18) 25%,
                transparent 42%
            ),
            linear-gradient(
                135deg,
                #02050a 0%,
                #06111f 35%,
                #02050a 65%,
                #071827 100%
            );

        background-attachment: fixed;
        color: #f5f7fa;
    }


    /* Αλλάζει το χρώμα των βασικών τίτλων */
    h1, h2, h3 {
        color: #f5f7fa !important;
    }


    /* Αλλάζει το χρώμα του απλού κειμένου */
    p, span, label {
        color: #e8edf4;
    }


    /* Μορφοποιεί τον βασικό τίτλο της εφαρμογής */
    .main-title {
        font-size: 46px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }


    /* Μορφοποιεί την περιγραφή κάτω από τον τίτλο */
    .main-subtitle {
        font-size: 18px;
        color: #b9c9dc;
        margin-bottom: 35px;
    }


    /* Μορφοποιεί τα containers των metrics */
    [data-testid="stMetric"] {
        background: rgba(4, 13, 24, 0.70);
        border: 1px solid rgba(70, 115, 165, 0.25);
        border-radius: 14px;
        padding: 18px;
        backdrop-filter: blur(8px);
    }


    /* Μορφοποιεί τα αναπτυσσόμενα πλαίσια των micro-skills */
    [data-testid="stExpander"] {
        background: rgba(3, 10, 20, 0.72);
        border: 1px solid rgba(65, 105, 150, 0.28);
        border-radius: 10px;
    }


    /* Μορφοποιεί το πεδίο αναζήτησης */
    [data-testid="stTextInput"] input {
        background-color: rgba(5, 13, 24, 0.90);
        color: white;
        border: 1px solid rgba(70, 110, 155, 0.50);
        border-radius: 8px;
    }


    /* Μορφοποιεί το selectbox */
    [data-baseweb="select"] > div {
        background-color: rgba(5, 13, 24, 0.90);
        border-color: rgba(70, 110, 155, 0.50);
    }


    /* Μορφοποιεί τις διαχωριστικές γραμμές */
    hr {
        border-color: rgba(110, 145, 185, 0.25);
    }


    /* Μορφοποιεί το footer */
    .custom-footer {
        text-align: center;
        color: #9eb2c9;
        font-size: 14px;
        padding-top: 18px;
        padding-bottom: 15px;
    }


    /* Μορφοποιεί τον τίτλο μέσα στο footer */
    .custom-footer strong {
        color: #d9e5f2;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# Εμφανίζει τον βασικό τίτλο της εφαρμογής.
st.markdown(
    """
    <div class="main-title">
        MicroSkills Lexicon Explorer
    </div>
    """,
    unsafe_allow_html=True
)


# Εμφανίζει μια σύντομη περιγραφή της εφαρμογής.
st.markdown(
    """
    <div class="main-subtitle">
        Διαδραστική παρουσίαση των micro-skills
        του MicroSkills Lexicon ανά θεματική κατηγορία.
    </div>
    """,
    unsafe_allow_html=True
)


# Φορτώνει τα δεδομένα από το αρχείο MicroSkillsLexicon.xlsx.
# Χρησιμοποιείται cache ώστε το αρχείο να μη διαβάζεται ξανά σε κάθε ανανέωση της σελίδας.
@st.cache_data
def load_lexicon():

    # Διαβάζει το φύλλο Cleaned_Lexicon από το αρχείο Excel.
    df = pd.read_excel(
        "MicroSkillsLexicon.xlsx",
        sheet_name="Cleaned_Lexicon"
    )

    # Ορίζει τις στήλες του λεξικού που χρειάζονται για την εφαρμογή.
    columns = [
        "Categories Micro-skills (GR)",
        "Categories Micro-skills (EN)",
        "Microskills",
        "Definition (GR)",
        "Keywords"
    ]

    # Διατηρεί μόνο τις απαραίτητες στήλες του λεξικού.
    df = df[columns].copy()

    # Αφαιρεί εγγραφές που δεν έχουν κατηγορία ή όνομα micro-skill.
    df = df.dropna(
        subset=[
            "Categories Micro-skills (GR)",
            "Microskills"
        ]
    )

    # Αν κάποια micro-skill δεν έχει διαθέσιμο ορισμό,
    # εμφανίζεται ένα κατάλληλο μήνυμα στη θέση του.
    df["Definition (GR)"] = df["Definition (GR)"].fillna(
        "Δεν υπάρχει διαθέσιμος ορισμός."
    )

    # Αν κάποια micro-skill δεν έχει διαθέσιμες λέξεις-κλειδιά,
    # εμφανίζεται ένα κατάλληλο μήνυμα στη θέση τους.
    df["Keywords"] = df["Keywords"].fillna(
        "Δεν υπάρχουν διαθέσιμες λέξεις-κλειδιά."
    )

    return df


# Προσπαθεί να φορτώσει το MicroSkills Lexicon.
# Αν παρουσιαστεί κάποιο σφάλμα, εμφανίζεται σχετικό μήνυμα στην εφαρμογή.
try:
    df = load_lexicon()

except Exception as e:

    st.error(
        "Δεν ήταν δυνατή η φόρτωση του MicroSkillsLexicon.xlsx"
    )

    st.code(str(e))

    st.stop()


# Υπολογίζει τον συνολικό αριθμό διαφορετικών micro-skills του λεξικού.
total_skills = df["Microskills"].nunique()


# Υπολογίζει τον συνολικό αριθμό θεματικών κατηγοριών του λεξικού.
total_categories = df[
    "Categories Micro-skills (GR)"
].nunique()


# Δημιουργεί δύο στήλες για την παρουσίαση των βασικών στοιχείων του λεξικού.
col1, col2 = st.columns(2)


# Εμφανίζει τον συνολικό αριθμό micro-skills.
with col1:
    st.metric(
        "Συνολικές Micro-skills",
        total_skills
    )


# Εμφανίζει τον συνολικό αριθμό θεματικών κατηγοριών.
with col2:
    st.metric(
        "Θεματικές Κατηγορίες",
        total_categories
    )


# Προσθέτει διαχωριστική γραμμή ανάμεσα στις ενότητες.
st.divider()


# Εμφανίζει την ενότητα αναζήτησης micro-skills.
st.subheader(
    "Αναζήτηση Micro-skill"
)


# Δημιουργεί πεδίο εισαγωγής κειμένου για την αναζήτηση micro-skills.
search = st.text_input(
    "Αναζήτησε micro-skill ή λέξη-κλειδί",
    placeholder="π.χ. email, communication, GPT, time..."
)


# Εκτελεί την αναζήτηση μόνο όταν ο χρήστης έχει εισαγάγει κάποιον όρο.
if search:

    search_lower = search.lower()

    # Αναζητά τον όρο στο όνομα της micro-skill,
    # στις λέξεις-κλειδιά και στον ορισμό της.
    results = df[
        df["Microskills"]
        .astype(str)
        .str.lower()
        .str.contains(search_lower, na=False)

        |

        df["Keywords"]
        .astype(str)
        .str.lower()
        .str.contains(search_lower, na=False)

        |

        df["Definition (GR)"]
        .astype(str)
        .str.lower()
        .str.contains(search_lower, na=False)
    ]

    # Εμφανίζει πόσα αποτελέσματα βρέθηκαν.
    st.write(
        f"Βρέθηκαν **{len(results)} αποτελέσματα**"
    )


    # Εμφανίζει κάθε micro-skill που βρέθηκε.
    for _, row in results.iterrows():

        with st.expander(
            row["Microskills"]
        ):

            st.write(
                f"**Κατηγορία:** "
                f"{row['Categories Micro-skills (GR)']}"
            )

            st.write(
                f"**Category:** "
                f"{row['Categories Micro-skills (EN)']}"
            )

            st.write(
                "**Ορισμός:**"
            )

            st.write(
                row["Definition (GR)"]
            )

            st.write(
                "**Λέξεις-κλειδιά:**"
            )

            st.write(
                row["Keywords"]
            )


# Προσθέτει διαχωριστική γραμμή πριν από την ενότητα των κατηγοριών.
st.divider()


# Εμφανίζει τον τίτλο της ενότητας με τις θεματικές κατηγορίες.
st.header(
    "Θεματικές Κατηγορίες"
)


# Υπολογίζει πόσες micro-skills περιλαμβάνει κάθε θεματική κατηγορία.
category_counts = (
    df.groupby(
        "Categories Micro-skills (GR)"
    )["Microskills"]
    .nunique()
    .sort_values(
        ascending=False
    )
)


# Μετατρέπει τα αποτελέσματα των κατηγοριών σε πίνακα δεδομένων.
category_table = category_counts.reset_index()


# Μετονομάζει τις στήλες του πίνακα.
category_table.columns = [
    "Θεματική Κατηγορία",
    "Αριθμός Micro-skills"
]


# Εμφανίζει τον πίνακα με όλες τις θεματικές κατηγορίες
# και τον αριθμό των micro-skills που περιλαμβάνει η καθεμία.
st.dataframe(
    category_table,
    use_container_width=True,
    hide_index=True
)


# Προσθέτει διαχωριστική γραμμή πριν από την επιλογή κατηγορίας.
st.divider()


# Δημιουργεί λίστα με όλες τις διαθέσιμες θεματικές κατηγορίες.
categories = (
    df["Categories Micro-skills (GR)"]
    .dropna()
    .unique()
)


# Δημιουργεί πεδίο επιλογής ώστε ο χρήστης να επιλέξει μία θεματική κατηγορία.
selected_category = st.selectbox(
    "Επίλεξε μία κατηγορία για να δεις όλες τις micro-skills:",
    categories
)


# Φιλτράρει το λεξικό και κρατά μόνο τις micro-skills
# που ανήκουν στην κατηγορία που επέλεξε ο χρήστης.
category_df = df[
    df["Categories Micro-skills (GR)"]
    == selected_category
].copy()


# Εντοπίζει την αγγλική ονομασία της επιλεγμένης κατηγορίας.
english_category = (
    category_df[
        "Categories Micro-skills (EN)"
    ]
    .iloc[0]
)


# Εμφανίζει το όνομα της επιλεγμένης κατηγορίας.
st.subheader(
    selected_category
)


# Εμφανίζει την αγγλική ονομασία της επιλεγμένης κατηγορίας.
st.write(
    f"**English:** {english_category}"
)


# Εμφανίζει τον αριθμό των micro-skills που περιλαμβάνει η επιλεγμένη κατηγορία.
st.write(
    f"Η κατηγορία περιλαμβάνει "
    f"**{category_df['Microskills'].nunique()} micro-skills**."
)


# Εμφανίζει τον τίτλο της λίστας με τις micro-skills της επιλεγμένης κατηγορίας.
st.markdown(
    "### Micro-skills της κατηγορίας"
)


# Διατρέχει όλες τις micro-skills της επιλεγμένης κατηγορίας.
for number, (_, row) in enumerate(
    category_df.iterrows(),
    start=1
):

    # Εμφανίζει κάθε micro-skill σε ξεχωριστή αναπτυσσόμενη ενότητα.
    with st.expander(
        f"{number}. {row['Microskills']}"
    ):

        st.write(
            "**Ορισμός**"
        )

        st.write(
            row["Definition (GR)"]
        )

        st.write(
            "**Λέξεις-κλειδιά**"
        )

        st.write(
            row["Keywords"]
        )


# Προσθέτει διαχωριστική γραμμή πριν από την πλήρη λίστα.
st.divider()


# Εμφανίζει την ενότητα με την πλήρη λίστα των micro-skills.
st.header(
    "Πλήρης λίστα Micro-skills"
)


# Δημιουργεί checkbox ώστε ο χρήστης να επιλέξει
# αν θέλει να εμφανίσει ολόκληρο το MicroSkills Lexicon.
show_all = st.checkbox(
    "Εμφάνιση όλων των micro-skills"
)


# Εμφανίζει την πλήρη λίστα μόνο όταν το checkbox είναι ενεργοποιημένο.
if show_all:

    full_table = df[
        [
            "Categories Micro-skills (GR)",
            "Microskills",
            "Definition (GR)",
            "Keywords"
        ]
    ].copy()

    full_table.columns = [
        "Κατηγορία",
        "Micro-skill",
        "Ορισμός",
        "Keywords"
    ]

    st.dataframe(
        full_table,
        use_container_width=True,
        hide_index=True
    )


# Προσθέτει διαχωριστική γραμμή πριν από το footer.
st.divider()


# Εμφανίζει το footer της εφαρμογής.
st.markdown(
    """
    <div class="custom-footer">
        <strong>© Thesis MicroSkills</strong><br>
        MicroMatch: Ανίχνευση Μικρο-Δεξιοτήτων μέσα από Κείμενα<br>
        Martha Astartzi
    </div>
    """,
    unsafe_allow_html=True
)
from pathlib import Path
from itertools import combinations
from collections import Counter
import ast

import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx


# Ορίζει το αρχείο εισόδου που περιέχει τις αγγελίες μαζί με τις micro-skills
# που έχει ήδη ανιχνεύσει το MicroMatch Framework.
INPUT_FILE = Path("data/final/jobs_with_microskills.csv")

# Δημιουργεί ξεχωριστό φάκελο στον οποίο θα αποθηκευτούν
# τα αποτελέσματα της ανάλυσης δικτύου.
OUTPUT_DIR = Path("network_results")

# Ορίζει πόσα από τα ισχυρότερα ζεύγη micro-skills
# θα εμφανιστούν στα αποτελέσματα.
TOP_EDGES_TO_PRINT = 10

# Ορίζει πόσες από τις πιο κεντρικές micro-skills
# θα εμφανιστούν στα αποτελέσματα.
TOP_NODES_TO_PRINT = 10

# Κρατάει στο τελικό γράφημα μόνο συνδέσεις που έχουν εμφανιστεί
# τουλάχιστον 20 φορές, ώστε το δίκτυο να παραμένει ευανάγνωστο.
MIN_EDGE_WEIGHT_FOR_GRAPH = 20

# Περιορίζει τον αριθμό των κόμβων που εμφανίζονται στο δίκτυο,
# ώστε η οπτικοποίηση να μην γίνει υπερβολικά πυκνή.
MAX_NODES_IN_GRAPH = 25


def parse_microskills(value):
    # Μετατρέπει την τιμή της στήλης detected_microskills
    # από κείμενο σε πραγματική λίστα Python.

    # Αν η τιμή είναι κενή, επιστρέφει κενή λίστα.
    if pd.isna(value):
        return []

    text = str(value).strip()

    # Αν το πεδίο είναι κενό ή περιέχει ήδη κενή λίστα,
    # δεν υπάρχουν micro-skills προς επεξεργασία.
    if not text or text == "[]":
        return []

    try:
        # Μετατρέπει με ασφάλεια το κείμενο τύπου
        # ["skill 1", "skill 2"] σε Python list.
        parsed = ast.literal_eval(text)

        if isinstance(parsed, list):
            return [
                str(skill).strip()
                for skill in parsed
                if str(skill).strip()
            ]

    except Exception:
        # Αν υπάρξει πρόβλημα στη μετατροπή,
        # επιστρέφει κενή λίστα ώστε να συνεχιστεί η επεξεργασία.
        return []

    return []


def main():
    # Δημιουργεί τον φάκελο αποτελεσμάτων αν δεν υπάρχει ήδη.
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Loading dataset...")

    # Διαβάζει το αρχείο με τις τελικές αγγελίες και τις ανιχνευμένες micro-skills.
    df = pd.read_csv(INPUT_FILE)

    # Ελέγχει ότι υπάρχει η απαραίτητη στήλη με τις micro-skills.
    if "detected_microskills" not in df.columns:
        raise ValueError(
            "Δεν βρέθηκε η στήλη 'detected_microskills' στο CSV."
        )

    print(f"Total jobs: {len(df)}")

    # Μετατρέπει τη στήλη detected_microskills σε λίστα
    # ώστε να μπορούν να αναλυθούν οι micro-skills ανά αγγελία.
    df["microskills_list"] = df["detected_microskills"].apply(
        parse_microskills
    )

    # Μετράει σε πόσες αγγελίες εμφανίζεται κάθε micro-skill.
    skill_counter = Counter()

    for skills in df["microskills_list"]:

        # Αφαιρεί πιθανές διπλές εμφανίσεις της ίδιας micro-skill
        # μέσα στην ίδια αγγελία.
        unique_skills = sorted(set(skills))

        for skill in unique_skills:
            skill_counter[skill] += 1

    # Δημιουργεί πίνακα με τη συχνότητα εμφάνισης κάθε micro-skill.
    skill_frequency_df = pd.DataFrame(
        skill_counter.items(),
        columns=[
            "microskill",
            "job_frequency"
        ]
    ).sort_values(
        by="job_frequency",
        ascending=False
    )

    # Αποθηκεύει τις συχνότητες των micro-skills σε CSV.
    skill_frequency_df.to_csv(
        OUTPUT_DIR / "microskills_node_frequency.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Μετράει πόσες φορές εμφανίζεται μαζί κάθε ζεύγος micro-skills.
    edge_counter = Counter()

    for skills in df["microskills_list"]:

        # Κάθε micro-skill λαμβάνεται μία φορά ανά αγγελία.
        unique_skills = sorted(set(skills))

        # Δημιουργεί όλους τους δυνατούς συνδυασμούς δύο micro-skills.
        for skill_a, skill_b in combinations(unique_skills, 2):
            edge_counter[(skill_a, skill_b)] += 1

    # Δημιουργεί πίνακα με όλα τα ζεύγη micro-skills
    # και τον αριθμό των κοινών εμφανίσεών τους.
    edges_df = pd.DataFrame(
        [
            {
                "microskill_1": pair[0],
                "microskill_2": pair[1],
                "cooccurrence_count": count
            }
            for pair, count in edge_counter.items()
        ]
    )

    # Αν δεν υπάρχουν ζεύγη micro-skills, η ανάλυση τερματίζεται.
    if edges_df.empty:
        print("Δεν βρέθηκαν συν-εμφανίσεις micro-skills.")
        return

    # Ταξινομεί τα ζεύγη από το συχνότερο προς το λιγότερο συχνό.
    edges_df = edges_df.sort_values(
        by="cooccurrence_count",
        ascending=False
    )

    # Αποθηκεύει όλα τα ζεύγη micro-skills σε αρχείο CSV.
    edges_df.to_csv(
        OUTPUT_DIR / "microskills_cooccurrence_edges.csv",
        index=False,
        encoding="utf-8-sig"
    )

    # Δημιουργεί το πλήρες γράφημα δικτύου.
    # Κάθε κόμβος αντιστοιχεί σε μία micro-skill.
    G = nx.Graph()

    # Προσθέτει όλες τις micro-skills ως κόμβους του δικτύου.
    for skill, frequency in skill_counter.items():
        G.add_node(
            skill,
            frequency=frequency
        )

    # Προσθέτει σύνδεση μεταξύ δύο micro-skills όταν εμφανίζονται
    # μαζί στην ίδια αγγελία.
    for (skill_a, skill_b), weight in edge_counter.items():
        G.add_edge(
            skill_a,
            skill_b,
            weight=weight
        )

    # Υπολογίζει το συνολικό βάρος των συνδέσεων κάθε micro-skill.
    # Μεγαλύτερη τιμή σημαίνει ότι η micro-skill εμφανίζεται συχνά
    # μαζί με άλλες micro-skills.
    weighted_degree = dict(
        G.degree(weight="weight")
    )

    # Υπολογίζει την κεντρικότητα βαθμού κάθε micro-skill.
    # Η τιμή δείχνει με πόσες διαφορετικές micro-skills συνδέεται ένας κόμβος.
    degree_centrality = nx.degree_centrality(G)

    centrality_rows = []

    # Δημιουργεί αναλυτικό πίνακα με τις βασικές μετρικές
    # για κάθε micro-skill του δικτύου.
    for node in G.nodes():
        centrality_rows.append(
            {
                "microskill": node,
                "job_frequency": G.nodes[node]["frequency"],
                "number_of_connections": G.degree(node),
                "weighted_degree": weighted_degree[node],
                "degree_centrality": degree_centrality[node]
            }
        )

    # Ταξινομεί τις micro-skills με βάση το συνολικό βάρος
    # των συνδέσεών τους.
    centrality_df = pd.DataFrame(
        centrality_rows
    ).sort_values(
        by="weighted_degree",
        ascending=False
    )

    # Αποθηκεύει τις μετρικές κεντρικότητας σε CSV.
    centrality_df.to_csv(
        OUTPUT_DIR / "microskills_centrality.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\n")
    print("=" * 70)
    print("TOP 10 MICRO-SKILL PAIRS")
    print("=" * 70)

    # Εμφανίζει τα δέκα ζεύγη micro-skills
    # με τις περισσότερες κοινές εμφανίσεις.
    print(
        edges_df.head(
            TOP_EDGES_TO_PRINT
        ).to_string(index=False)
    )

    print("\n")
    print("=" * 70)
    print("TOP 10 MOST CENTRAL MICRO-SKILLS")
    print("=" * 70)

    # Εμφανίζει τις δέκα micro-skills
    # με το μεγαλύτερο συνολικό βάρος συνδέσεων.
    print(
        centrality_df[
            [
                "microskill",
                "job_frequency",
                "number_of_connections",
                "weighted_degree"
            ]
        ]
        .head(TOP_NODES_TO_PRINT)
        .to_string(index=False)
    )

    # Κρατάει μόνο τις ισχυρότερες συνδέσεις
    # για να δημιουργηθεί ένα πιο καθαρό και ευανάγνωστο δίκτυο.
    strong_edges = [
        (u, v, data)
        for u, v, data in G.edges(data=True)
        if data["weight"] >= MIN_EDGE_WEIGHT_FOR_GRAPH
    ]

    # Δημιουργεί νέο, μικρότερο δίκτυο
    # μόνο με τις ισχυρότερες συνδέσεις.
    H = nx.Graph()

    for u, v, data in strong_edges:
        H.add_edge(
            u,
            v,
            weight=data["weight"]
        )

    # Αν υπάρχουν πάρα πολλοί κόμβοι,
    # κρατάει μόνο τους πιο σημαντικούς.
    if len(H.nodes()) > MAX_NODES_IN_GRAPH:

        node_strength = dict(
            H.degree(weight="weight")
        )

        top_nodes = sorted(
            node_strength,
            key=node_strength.get,
            reverse=True
        )[:MAX_NODES_IN_GRAPH]

        H = H.subgraph(top_nodes).copy()

    print("\n")
    print(f"Graph nodes: {H.number_of_nodes()}")
    print(f"Graph edges: {H.number_of_edges()}")

    # Δημιουργεί την οπτικοποίηση του δικτύου
    # μόνο αν υπάρχουν κόμβοι μετά τα φίλτρα.
    if H.number_of_nodes() > 0:

        plt.figure(figsize=(16, 12))

        # Υπολογίζει αυτόματα τη θέση των κόμβων στο γράφημα.
        # Το seed χρησιμοποιείται ώστε το διάγραμμα να παραμένει ίδιο
        # σε κάθε εκτέλεση του κώδικα.
        pos = nx.spring_layout(
            H,
            seed=42,
            k=1.2
        )

        node_sizes = []

        # Το μέγεθος κάθε κόμβου εξαρτάται από το πόσες φορές
        # εμφανίζεται η συγκεκριμένη micro-skill στις αγγελίες.
        for node in H.nodes():
            frequency = skill_counter.get(node, 1)

            node_sizes.append(
                300 + frequency * 12
            )

        edge_widths = []

        # Το πάχος κάθε σύνδεσης εξαρτάται από το πόσες φορές
        # εμφανίζεται μαζί το συγκεκριμένο ζεύγος micro-skills.
        for u, v in H.edges():
            weight = H[u][v]["weight"]

            edge_widths.append(
                max(0.5, weight / 15)
            )

        # Σχεδιάζει τους κόμβους του δικτύου.
        nx.draw_networkx_nodes(
            H,
            pos,
            node_size=node_sizes,
            alpha=0.85
        )

        # Σχεδιάζει τις συνδέσεις μεταξύ των micro-skills.
        nx.draw_networkx_edges(
            H,
            pos,
            width=edge_widths,
            alpha=0.35
        )

        # Προσθέτει τα ονόματα των micro-skills πάνω στους κόμβους.
        nx.draw_networkx_labels(
            H,
            pos,
            font_size=8
        )

        plt.title(
            "Micro-Skills Co-occurrence Network"
        )

        plt.axis("off")

        plt.tight_layout()

        # Αποθηκεύει το τελικό διάγραμμα δικτύου ως εικόνα υψηλής ανάλυσης.
        plt.savefig(
            OUTPUT_DIR / "microskills_cooccurrence_network.png",
            dpi=300,
            bbox_inches="tight"
        )

        plt.close()

        print("\nSaved network graph:")
        print(
            OUTPUT_DIR / "microskills_cooccurrence_network.png"
        )

    # Επιλέγει τα δέκα ισχυρότερα ζεύγη micro-skills
    # για τη δημιουργία επιπλέον ραβδογράμματος.
    top_edges = edges_df.head(10).copy()

    # Ενώνει τα ονόματα των δύο micro-skills
    # ώστε κάθε ζεύγος να εμφανίζεται ως μία ετικέτα.
    top_edges["pair"] = (
        top_edges["microskill_1"]
        + " + "
        + top_edges["microskill_2"]
    )

    # Ταξινομεί τα ζεύγη κατάλληλα ώστε το ισχυρότερο
    # να εμφανίζεται στην κορυφή του οριζόντιου ραβδογράμματος.
    top_edges = top_edges.sort_values(
        by="cooccurrence_count",
        ascending=True
    )

    plt.figure(figsize=(12, 8))

    # Δημιουργεί οριζόντιο ραβδόγραμμα
    # με τα δέκα συχνότερα ζεύγη micro-skills.
    plt.barh(
        top_edges["pair"],
        top_edges["cooccurrence_count"]
    )

    plt.xlabel(
        "Number of Job Advertisements"
    )

    plt.ylabel(
        "Micro-Skill Pair"
    )

    plt.title(
        "Top 10 Micro-Skill Co-occurrences"
    )

    plt.tight_layout()

    # Αποθηκεύει το ραβδόγραμμα των ισχυρότερων ζευγών.
    plt.savefig(
        OUTPUT_DIR / "top_10_microskill_pairs.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("Saved top-pairs chart:")
    print(
        OUTPUT_DIR / "top_10_microskill_pairs.png"
    )

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    # Εκτελεί την κύρια διαδικασία της ανάλυσης
    # όταν το αρχείο τρέχει απευθείας.
    main()
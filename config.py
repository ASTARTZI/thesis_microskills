import os
from dotenv import load_dotenv

# Φορτώνει τις μεταβλητές περιβάλλοντος από το αρχείο .env.
# Με αυτόν τον τρόπο τα ευαίσθητα στοιχεία σύνδεσης δεν αποθηκεύονται μέσα στον κώδικα.
load_dotenv()

# Διαβάζει τις παραμέτρους σύνδεσης με το Tracker API από το αρχείο .env.
TRACKER_API = os.getenv("TRACKER_API")
TRACKER_USERNAME = os.getenv("TRACKER_USERNAME")
TRACKER_PASSWORD = os.getenv("TRACKER_PASSWORD")

# Ορίζει το προεπιλεγμένο μέγεθος σελίδας για τα αποτελέσματα του API.
# Αν δεν υπάρχει τιμή στο .env, χρησιμοποιείται το 100.
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "100"))

# Έλεγχος ότι έχει οριστεί το URL του API.
# Αν λείπει, η εκτέλεση διακόπτεται με κατάλληλο μήνυμα σφάλματος.
if not TRACKER_API:
    raise RuntimeError("Missing TRACKER_API in .env")

# Έλεγχος ότι έχει οριστεί το όνομα χρήστη για την αυθεντικοποίηση.
if not TRACKER_USERNAME:
    raise RuntimeError("Missing TRACKER_USERNAME in .env")

# Έλεγχος ότι έχει οριστεί ο κωδικός πρόσβασης για την αυθεντικοποίηση.
if not TRACKER_PASSWORD:
    raise RuntimeError("Missing TRACKER_PASSWORD in .env")
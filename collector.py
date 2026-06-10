import urllib3

# Απενεργοποιεί τις προειδοποιήσεις για μη ασφαλή HTTPS αιτήματα.
# Χρησιμοποιείται εδώ επειδή το API έχει προσωρινό θέμα με το πιστοποιητικό.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests
import time

from config import (
    TRACKER_API,
    TRACKER_USERNAME,
    TRACKER_PASSWORD,
    DEFAULT_PAGE_SIZE,
)


@dataclass
class TrackerClient:
    # Κλάση-πελάτης για την επικοινωνία με το Tracker API.
    # Περιλαμβάνει τα στοιχεία σύνδεσης, το μέγεθος σελίδας και τη διαχείριση του token.
    api: str = TRACKER_API
    username: str = TRACKER_USERNAME
    password: str = TRACKER_PASSWORD
    page_size: int = DEFAULT_PAGE_SIZE

    # Αποθηκεύει προσωρινά το token, ώστε να μη γίνεται login σε κάθε αίτημα.
    _token: Optional[str] = None
    _token_ts: float = 0.0
    _token_ttl_seconds: int = 20 * 60

    def get_token(self, force: bool = False) -> str:
        # Επιστρέφει ένα ενεργό token αυθεντικοποίησης.
        # Αν υπάρχει ήδη πρόσφατο token, το ξαναχρησιμοποιεί· αλλιώς κάνει νέο login.
        now = time.time()

        if (
            not force
            and self._token is not None
            and (now - self._token_ts) < self._token_ttl_seconds
        ):
            return self._token

        response = requests.post(
            f"{self.api}/login",
            json={
                "username": self.username,
                "password": self.password,
            },
            timeout=30,
            verify=False,  # Προσωρινά λόγω προβλήματος με το SSL certificate.
        )
        response.raise_for_status()

        # Καθαρίζει το token που επιστρέφει το API και το αποθηκεύει για επόμενη χρήση.
        token = response.text.strip().replace('"', "")
        self._token = token
        self._token_ts = now
        return token

    def post_jobs(self, body: Dict[str, Any], page: int = 1) -> Dict[str, Any]:
        # Στέλνει αίτημα στο endpoint των αγγελιών για μία συγκεκριμένη σελίδα αποτελεσμάτων.
        token = self.get_token()

        response = requests.post(
            f"{self.api}/jobs",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {token}",
            },
            params={
                "page": page,
                "page_size": self.page_size,
            },
            data=body,
            timeout=120,
            verify=False,  # Προσωρινά λόγω προβλήματος με το SSL certificate.
        )
        response.raise_for_status()
        return response.json()

    def fetch_all_jobs(
        self,
        body: Dict[str, Any],
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        # Ανακτά όλες τις αγγελίες που αντιστοιχούν στα κριτήρια αναζήτησης,
        # διατρέχοντας όλες τις σελίδες αποτελεσμάτων του API.
        first_page = self.post_jobs(body=body, page=1)

        total_count = first_page.get("count", 0)
        items = first_page.get("items", [])

        # Αν το API δεν επιστρέψει αποτελέσματα, επιστρέφει αμέσως κενή λίστα.
        if total_count == 0:
            return items

        # Υπολογίζει τον συνολικό αριθμό σελίδων με βάση το πλήθος αποτελεσμάτων.
        total_pages = (total_count + self.page_size - 1) // self.page_size

        # Περιορίζει προαιρετικά τις σελίδες που θα ανακτηθούν, χρήσιμο για δοκιμές.
        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        # Φέρνει διαδοχικά τις υπόλοιπες σελίδες και προσθέτει τις αγγελίες στη λίστα.
        for page in range(2, total_pages + 1):
            data = self.post_jobs(body=body, page=page)
            items.extend(data.get("items", []))
            print(f"Fetched page {page}/{total_pages} - total items so far: {len(items)}")

        return items


def build_request_body(
    keywords: Optional[List[str]] = None,
    keywords_logic: str = "or",
    location_code: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    skill_ids: Optional[List[str]] = None,
    skill_ids_logic: str = "or",
    occupation_ids: Optional[List[str]] = None,
    occupation_ids_logic: str = "or",
    min_upload_date: Optional[str] = None,
    max_upload_date: Optional[str] = None,
) -> Dict[str, Any]:
    # Δημιουργεί δυναμικά το σώμα του αιτήματος προς το API,
    # προσθέτοντας μόνο τα φίλτρα που έχουν δοθεί από τον χρήστη/κώδικα.
    body: Dict[str, Any] = {}

    # Προσθέτει λέξεις-κλειδιά αναζήτησης και τη λογική σύνδεσής τους.
    if keywords:
        body["keywords"] = keywords
        body["keywords_logic"] = keywords_logic

    # Προσθέτει φίλτρο χώρας ή γεωγραφικής τοποθεσίας.
    if location_code:
        body["location_code"] = location_code

    # Προσθέτει φίλτρο προέλευσης των αγγελιών, αν έχει οριστεί.
    if sources:
        body["sources"] = sources

    # Προσθέτει φίλτρα δεξιοτήτων και τη λογική σύνδεσής τους.
    if skill_ids:
        body["skill_ids"] = skill_ids
        body["skill_ids_logic"] = skill_ids_logic

    # Προσθέτει φίλτρα επαγγελμάτων και τη λογική σύνδεσής τους.
    if occupation_ids:
        body["occupation_ids"] = occupation_ids
        body["occupation_ids_logic"] = occupation_ids_logic

    # Προσθέτει κατώτατο όριο ημερομηνίας ανάρτησης αγγελίας.
    if min_upload_date:
        body["min_upload_date"] = min_upload_date

    # Προσθέτει ανώτατο όριο ημερομηνίας ανάρτησης αγγελίας.
    if max_upload_date:
        body["max_upload_date"] = max_upload_date

    return body
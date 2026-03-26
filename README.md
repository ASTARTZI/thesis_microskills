Για συγχρονισμό του vs code με το github
git add .
git commit -m "update"
git push

Για αντικατάσταση όλων των αρχείων και ανανέωση τους από το vs code στο github
git push -u origin main --force

-----------------------------------------------------
.\.venv\Scripts\python.exe .\main.py
.\.venv\Scripts\python.exe .\merge_jobs.py
.\.venv\Scripts\python.exe .\textprep.py
.\.venv\Scripts\python.exe .\microskill_matcher.py
.\.venv\Scripts\python.exe .\analyze_microskills.py
------------------------------------------------------

main.py → κατεβάζει αγγελίες
merge_jobs.py → ενώνει και αφαιρεί διπλότυπα
textprep.py → καθαρίζει το κείμενο
microskill_matcher.py → βρίσκει μικροδεξιότητες
analyze_microskills.py → βγάζει σύνοψη και συχνότητες

Για να τρέξει όλο το project
.\.venv\Scripts\python.exe .\main.py; .\.venv\Scripts\python.exe .\merge_jobs.py; .\.venv\Scripts\python.exe .\textprep.py; .\.venv\Scripts\python.exe .\microskill_matcher.py; .\.venv\Scripts\python.exe .\analyze_microskills.py

================================================================================
CLAUDE CONTEXT FILE — MIMIC-IV CAPSTONE PROJECT
Last Updated: 2026-04-13
================================================================================

PURPOSE OF THIS FILE
- Full context for Claude to resume work seamlessly after context compaction
- Step-by-step record of everything done so far
- Reference for next steps and project goals
- Read this file first at the start of every new session

================================================================================
SECTION 1: WHO IS THE USER
================================================================================
- Name: Dharani (DePaul email: dkommire@depaul.edu)
- Program: MS in Data Science, DePaul University
- This is a capstone project
- Python experience: ~6 years technically, but new to clinical databases and BigQuery
- Learning style: ADHD — needs step-by-step explanations so they can explain
  the work to professors and recruiters
- Previously worked in Google Colab, now fully moved to VS Code

================================================================================
SECTION 2: THE PROJECT GOAL
================================================================================
Build a 30-DAY HOSPITAL READMISSION PREDICTION DASHBOARD using MIMIC-IV v3.1

- Database: MIMIC-IV v3.1 (real de-identified clinical records from Beth Israel
  Deaconess Medical Center, Boston MA)
- Hosted on: Google BigQuery (physionet-data project)
- Billing project: project-74029ab6-0065-4d76-bbc
- PhysioNet username: dekay2627
- Authenticated Google account: dkommire@depaul.edu

The 5-phase plan:
  Phase 1: Define the cohort + target variable (readmitted_30d = 0 or 1)
  Phase 2: Feature engineering (demographics, labs, diagnoses, LOS, etc.)
  Phase 3: EDA on the cohort
  Phase 4: Build & evaluate ML models (Logistic Regression → Random Forest → XGBoost)
  Phase 5: Streamlit interactive dashboard

Current status: EDA notebook (eda.ipynb) is being built and debugged.
Phases 1-5 have NOT been started yet. EDA comes first.

================================================================================
SECTION 3: ENVIRONMENT SETUP (ALREADY DONE — DO NOT REDO)
================================================================================
- OS: Windows 11
- Python: 3.13 (Microsoft Store version at AppData\Local\Packages\...)
  AND Anaconda Python 3.12 at C:\Users\dhara\anaconda3\
  NOTE: Jupyter notebook uses ANACONDA kernel — packages must be installed there
- gcloud CLI: INSTALLED at C:\Users\dhara\AppData\Local\Google\Cloud SDK\
- Authentication: DONE — dkommire@depaul.edu authenticated via:
    gcloud auth login (done)
    gcloud auth application-default login (done)
    Credentials saved to: C:\Users\dhara\AppData\Roaming\gcloud\application_default_credentials.json
- GCP project set: gcloud config set project project-74029ab6-0065-4d76-bbc
- PhysioNet BigQuery access: RE-GRANTED on 2026-04-09 (email confirmation received)
- physionet-data starred in BigQuery console

Packages installed (in Anaconda environment):
  - google-cloud-bigquery (installed via pip inside Jupyter cell using sys.executable)
  - db-dtypes
  - pyarrow
  - pandas (already present)
  - matplotlib (already present)
  - seaborn (already present)

IMPORTANT: When Jupyter throws ModuleNotFoundError for google.cloud, run this
in a notebook cell to install into the correct environment:
  import sys
  !{sys.executable} -m pip install google-cloud-bigquery db-dtypes pyarrow

================================================================================
SECTION 4: DATABASE STRUCTURE
================================================================================
Dataset path: physionet-data.mimiciv_3_1_hosp
ICU path:     physionet-data.mimiciv_3_1_icu

Key tables and sizes:
  labevents         — 158,374,764 rows  (16,052 MB) — every lab test result
  emar_detail       —  87,371,064 rows  (7,408 MB)  — medication admin detail
  poe               —  52,212,109 rows  (4,767 MB)  — provider order entries
  emar              —  42,808,593 rows  (4,886 MB)  — medication admin records
  prescriptions     —  20,292,611 rows  (3,327 MB)  — medication orders
  pharmacy          —  17,847,567 rows  (3,244 MB)  — pharmacy records
  diagnoses_icd     —   6,364,488 rows  (245 MB)    — ICD diagnosis codes per visit
  microbiologyevents—   3,988,224 rows  (763 MB)    — microbiology cultures
  transfers         —   2,413,581 rows  (150 MB)    — patient movement
  procedures_icd    —     859,655 rows  (40 MB)     — procedures per visit
  admissions        —     546,028 rows  (77 MB)     — one row per hospital visit
  patients          —     364,627 rows  (14 MB)     — one row per unique patient
  d_icd_diagnoses   —     112,107 rows  (9 MB)      — ICD code lookup dictionary
  d_labitems        —       1,650 rows  (0.1 MB)    — lab item lookup dictionary

================================================================================
SECTION 5: KEY FINDINGS FROM EDA SO FAR
================================================================================
- Total unique patients:  364,627
- Total admissions:       546,028
- Avg admissions/patient: 1.50
- Gender: 52.6% Female (avg age 48.4), 47.4% Male (avg age 49.4)
- Largest race group: WHITE at 38% — 62% are non-white or unknown
- Most common admission type: Emergency
- Most common insurance: Medicare
- Length of stay: heavily right-skewed, most stays are short (1-3 days)
- In-hospital mortality: ~5-6% of admissions
- 30-day readmission rate: ~12-15% (final number pending Section 8 completion)

================================================================================
SECTION 6: FILES IN THE PROJECT
================================================================================
Location: C:\Users\dhara\OneDrive\Desktop\Project 1\

  main.py               — original connection test + quick EDA script (working)
  eda.ipynb             — full EDA Jupyter notebook (IN PROGRESS)
  demographics_overview.png — saved chart from main.py run
  Claude_Readme.txt     — THIS FILE

eda.ipynb structure:
  Cell 1  (pip install)    — installs google-cloud-bigquery into Jupyter kernel
  Cell 2  (setup)          — imports, BigQuery client, q() helper function
  Cell 3  (markdown)       — Section 2 description
  Cell 4  (tables)         — database table inventory
  Cell 5  (markdown)       — Section 3 description
  Cell 6  (scale)          — patient + admission counts
  Cell 7  (markdown)
  Cell 8  (gender)         — gender breakdown table + pie chart
  Cell 9  (markdown)
  Cell 10 (age)            — age histogram + age bucket bar chart
  Cell 11 (markdown)
  Cell 12 (race)           — race/ethnicity table + horizontal bar chart
  Cell 13 (markdown)       — Section 4 description
  Cell 14 (visit counts)   — how many times patients return
  Cell 15 (markdown)
  Cell 16 (LOS)            — length of stay histogram
  Cell 17 (markdown)
  Cell 18 (adm type/insur) — admission type + insurance bar charts ← BUG FIXED
  Cell 19 (markdown)       — Section 5 description
  Cell 20 (diagnoses top20)— top 20 ICD diagnoses chart
  Cell 21 (markdown)
  Cell 22 (diag/admission) — diagnoses per admission histogram
  Cell 23 (markdown)       — Section 6 description
  Cell 24 (labs)           — top 20 lab tests chart
  Cell 25 (markdown)       — Section 7 description
  Cell 26 (mortality)      — mortality + discharge location chart ← BUG FIXED
  Cell 27 (markdown)       — Section 8 description
  Cell 28 (readmission)    — 30-day readmission target variable preview
  Cell 29 (markdown)       — Summary table + next steps

================================================================================
SECTION 7: BUGS FIXED AND KNOWN ISSUES
================================================================================
FIXED:
- ModuleNotFoundError for google.cloud: fixed by installing via sys.executable
  inside notebook cell (Anaconda kernel vs system Python mismatch)
- 403 Access Denied on BigQuery: fixed by re-requesting BigQuery access on
  PhysioNet and starring physionet-data project in BigQuery console
- Wrong dataset name (mimiciv_hosp → mimiciv_v3_1_hosp → mimiciv_3_1_hosp)
- Cell 4c TypeError (insurance None values): fix = .fillna('Unknown').astype(str)
  on the barh() call for df_insurance['insurance']
- Cell 7 TypeError (discharge_location None values): same fix — .fillna('Unknown').astype(str)

PATTERN TO REMEMBER:
- MIMIC-IV has NULL values in many string columns (insurance, discharge_location, etc.)
- Always use .fillna('Unknown').astype(str) before passing a string column to barh()
- NotebookEdit tool does NOT reliably update open notebooks in VS Code —
  tell user to manually edit cells, or close/reopen notebook

================================================================================
SECTION 8: NEXT STEPS (IN ORDER)
================================================================================
1. Finish running all cells in eda.ipynb — confirm Section 8 (readmission preview)
   produces the 30-day readmission rate number

2. Begin Phase 1 — Build the cohort table:
   - Adults only (age >= 18)
   - Discharged alive (hospital_expire_flag = 0)
   - Target variable: readmitted_30d (1 if next admission within 30 days, else 0)
   - SQL uses LEAD() window function over subject_id ordered by admittime
   - Result: one row per eligible admission with label attached

3. Begin Phase 2 — Feature engineering:
   - Demographics: age, gender, race
   - Admission features: admission_type, insurance, los_days
   - Diagnosis features: num_diagnoses, presence of key ICD codes
   - Prior utilization: number of prior admissions
   - Lab features: abnormal flag counts for common labs

4. Phase 3 — EDA on cohort (readmission rate by subgroup)

5. Phase 4 — Modeling:
   - Logistic Regression (baseline)
   - Random Forest
   - XGBoost
   - Evaluate with AUC-ROC, precision-recall, feature importance

6. Phase 5 — Streamlit dashboard:
   - Input patient characteristics
   - Output readmission risk score
   - Show top contributing features

================================================================================
END OF FILE
================================================================================

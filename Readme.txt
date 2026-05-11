================================================================================
CLAUDE CONTEXT FILE — MIMIC-IV CAPSTONE PROJECT
Last Updated: 2026-04-27 (evening update)
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

Current status:
  - EDA notebook (eda.ipynb): COMPLETE (BigQuery EDA on full 364k patient dataset)
  - Pipeline switched from BigQuery to LOCAL DuckDB (CSV files in data/)
  - Phase 1 (Cohort): COMPLETE — cohort.ipynb built cohort, target variable built
    outputs/cohort_10k.csv (9,996 patients: subject_id, age_group, gender)
  - Phase 2 (Feature engineering): COMPLETE — final_dataset.parquet produced
    23,896 rows x 719 columns (14 clinical features + 705 CCSR binary flags)
    Saved to: outputs/final_dataset.parquet and outputs/final_dataset.csv
  - Phase 3 (EDA on final dataset): COMPLETE — eda_final_dataset.ipynb (10 sections)
    All charts saved to outputs/eda_plots/
  - Phases 4-5: NOT started (modeling and dashboard)

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
  - google-cloud-bigquery, db-dtypes (BigQuery — no longer used)
  - pyarrow (still used for parquet output)
  - duckdb (local SQL engine — all queries now run via duckdb.connect())
  - pandas, matplotlib, seaborn (already present)
  - requests (for AHRQ file downloads)

NOTE: Pipeline migrated off BigQuery. All data now lives in:
  data/admissions.csv, data/patients.csv, data/diagnoses_icd.csv
  CCSR mappings: ccsr/icd10_ccsr/ (DXCCSR_v2025-1) and ccsr/icd9_ccs/ (CCS 2015)

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
FROM eda.ipynb (full MIMIC-IV BigQuery EDA):
- Total unique patients:  364,627
- Total admissions:       546,028
- Avg admissions/patient: 1.50
- Gender: 52.6% Female (avg age 48.4), 47.4% Male (avg age 49.4)
- Largest race group: WHITE at 38% — 62% are non-white or unknown
- Most common admission type: Emergency
- Most common insurance: Medicare
- Length of stay: heavily right-skewed, most stays are short (1-3 days)
- In-hospital mortality: ~5-6% of admissions

FROM eda_final_dataset.ipynb (final modeling dataset, 23,896 rows):
- Dataset shape: 23,896 rows x 719 columns
- Column layout: cols 0-1 are IDs, cols 2-13 are clinical features,
  cols 14-718 are CCSR binary diagnosis flags (705 total)
- Target: readmitted_30d — exact rate produced by running Section 3
- CCSR column names have embedded single quotes and spaces
  e.g. "'1    '" instead of "1" — MUST be cleaned before modeling
- discharge_location contains DIED rows — must be excluded or
  handled as a separate class before binary classification
- race has many unique values — consolidation needed before encoding
- hospital_expire_flag lives in data/admissions.csv (not in df by default)
  Section 10 joins it on hadm_id to build three-class outcome
- Three outcome classes (from Section 10):
    Class 0: Not Readmitted (discharged alive, no readmission within 30d)
    Class 1: Readmitted within 30 days
    Class 2: Died in hospital
- Top CCSR conditions vary by outcome class (chart: three_class_top_conditions.png)

================================================================================
SECTION 6: FILES IN THE PROJECT
================================================================================
Location: C:\Users\dhara\OneDrive\Desktop\Project 1\

  main.py                           — original connection test + quick EDA script
  eda.ipynb                         — BigQuery EDA on full MIMIC-IV dataset (COMPLETE)
  cohort.ipynb                      — Phase 1 cohort + target variable (COMPLETE)
  ccsr_features.ipynb               — Phase 2 CCSR feature engineering (COMPLETE)
  eda_final_dataset.ipynb           — Phase 3 EDA on final modeling dataset (COMPLETE)
  demographics_overview.png         — chart from main.py
  Readme.txt                        — THIS FILE
  data/                             — admissions.csv, patients.csv, diagnoses_icd.csv
  outputs/cohort_10k.csv            — 9,996 patients (subject_id, age_group, gender)
  outputs/ccsr_features.parquet     — CCSR binary feature matrix (intermediate)
  outputs/ccsr_features_preview.csv — preview of CCSR features
  outputs/final_dataset.parquet     — FINAL modeling dataset (23,896 x 719) USE THIS
  outputs/final_dataset.csv         — same as above in CSV format
  outputs/eda_plots/                — all EDA charts (15+ PNG files)
    missing_values.png, target_distribution.png
    age_at_admission_dist.png, los_days_dist.png, prior_admissions_count_dist.png
    gender_counts.png, admission_type_counts.png, insurance_counts.png
    race_counts.png, discharge_location_counts.png, marital_status_counts.png
    gender_readmission_rate.png, admission_type_readmission_rate.png, ...
    ccsr_top20_prevalence.png, numeric_correlations.png
    three_class_top_conditions.png
  ccsr/icd10_ccsr/                  — extracted DXCCSR_v2025-1 mapping files
  ccsr/icd9_ccs/                    — extracted CCS 2015 ICD-9 mapping files

eda_final_dataset.ipynb structure (23 cells):
  Section 1:  Setup and Load — imports, loads final_dataset.parquet as df
  Section 2:  Missing Value Analysis — table + missing_values.png
  Section 3:  Target Variable Distribution — target_distribution.png
  Section 4:  Clinical Feature Distributions — histograms split by readmission
  Section 5:  Categorical Feature Analysis — value counts + bar charts
  Section 6:  Readmission Rate by Category — rate per group + charts
  Section 7:  CCSR Feature Summary — top 20/bottom 10 prevalence, ccsr_top20_prevalence.png
  Section 8:  Class Imbalance and Correlation Check — numeric_correlations.png
  Section 9:  EDA Summary Report — computed summary block with all key numbers
  Section 10: Three-Class Outcome Analysis — joins hospital_expire_flag from
              data/admissions.csv, builds outcome_class (0/1/2), top conditions
              per class, three_class_top_conditions.png

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

KNOWN ISSUES IN final_dataset.parquet (must fix in preprocessing before modeling):
1. CCSR column names have embedded single quotes and spaces
   e.g. "'1    '" — strip quotes and spaces before encoding
2. discharge_location = 'DIED' rows exist — exclude before binary classification
   or keep only for three-class model
3. race column has many unique values — consolidate rare categories
4. hospital_expire_flag is NOT in final_dataset.parquet —
   must join from data/admissions.csv on hadm_id when needed

================================================================================
SECTION 8: NEXT STEPS (IN ORDER)
================================================================================
Phases 1, 2, 3 are COMPLETE. Starting from Phase 4.

1. Preprocessing notebook (new: preprocessing.ipynb):
   - Load outputs/final_dataset.parquet
   - Fix CCSR column names: strip embedded single quotes and spaces
   - Drop or flag rows where discharge_location = 'DIED'
   - Consolidate rare race categories (e.g. group anything under 1% as 'Other')
   - Encode categorical columns (gender, admission_type, insurance, race,
     discharge_location, marital_status) using LabelEncoder or pd.get_dummies
   - Scale numeric columns (age_at_admission, los_days, prior_admissions_count)
   - Save cleaned dataset to outputs/final_dataset_clean.parquet

2. Phase 4 — Modeling notebook (new: modeling.ipynb):
   - Load outputs/final_dataset_clean.parquet
   - Train/test split (80/20, stratified on readmitted_30d)
   - Baseline: Logistic Regression
   - Random Forest with feature importance
   - XGBoost
   - Evaluate each with: AUC-ROC, precision, recall, F1, confusion matrix
   - Handle class imbalance with class_weight='balanced' or SMOTE
   - Save best model to outputs/best_model.pkl

3. Phase 5 — Streamlit dashboard (new: app.py or dashboard.py):
   - Input: patient characteristics (age, gender, admission type, diagnoses)
   - Output: readmission risk score (probability)
   - Show top contributing CCSR features for the prediction
   - Run locally with: streamlit run app.py

================================================================================
SECTION 9: MODELING RESULTS
================================================================================
Date completed: 2026-05-11

Notebook: modeling_v2.ipynb — COMPLETE

Models trained:
  - Logistic Regression (baseline)
  - Random Forest
  - XGBoost (best model)

Best model: XGBoost
  ROC-AUC: 0.7562

Output files produced:
  outputs/lr_model.pkl              — trained Logistic Regression model
  outputs/rf_model.pkl              — trained Random Forest model
  outputs/xgb_model.pkl             — trained XGBoost model (best)
  outputs/best_model_info.json      — metadata for best model
  outputs/roc_curves.png            — ROC curves for all three models
  outputs/calibration_curves.png    — calibration curves for all three models
  outputs/fairness_audit.csv        — readmission rate by demographic group

Next step: SHAP explainability and Streamlit dashboard

================================================================================
END OF FILE
================================================================================

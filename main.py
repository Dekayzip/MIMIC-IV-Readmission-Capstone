from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# SETUP: Open a connection to BigQuery
#
# Think of `client` like a phone line to Google's servers.
# Every query we run goes through this object.
# The project ID tells Google which account to bill for compute time.
# ---------------------------------------------------------------------------
PROJECT_ID = "project-74029ab6-0065-4d76-bbc"
DATASET    = "physionet-data.mimiciv_3_1_hosp"

client = bigquery.Client(project=PROJECT_ID)

def run_query(sql):
    """Helper so we don't repeat client.query(...).to_dataframe() everywhere."""
    return client.query(sql).to_dataframe()


# ===========================================================================
# SECTION 1: How big is this database?
# ===========================================================================
print("=" * 55)
print("MIMIC-IV v3.1  —  First Look")
print("=" * 55)

# --- 1a. Total unique patients ---
# The `patients` table has one row per patient (subject_id is the unique ID).
# COUNT(*) counts every row = total patients.
df_patients = run_query(f"""
    SELECT COUNT(*) AS total_patients
    FROM `{DATASET}.patients`
""")
total_patients = df_patients["total_patients"][0]
print(f"\nTotal unique patients : {total_patients:,}")

# --- 1b. Total hospital admissions ---
# The `admissions` table has one row per hospital VISIT (hadm_id).
# One patient can have many visits, so this number is larger than patients.
df_admissions = run_query(f"""
    SELECT COUNT(*) AS total_admissions
    FROM `{DATASET}.admissions`
""")
total_admissions = df_admissions["total_admissions"][0]
print(f"Total admissions      : {total_admissions:,}")
print(f"Avg admissions/patient: {total_admissions / total_patients:.2f}")


# ===========================================================================
# SECTION 2: Who are the patients? (Demographics)
# ===========================================================================

# --- 2a. Gender breakdown ---
# `anchor_age` = patient's age in the anchor year (a privacy-preserving
# reference year). We use it as a proxy for age at first admission.
df_gender = run_query(f"""
    SELECT
        gender,
        COUNT(*) AS count,
        ROUND(AVG(anchor_age), 1) AS avg_age
    FROM `{DATASET}.patients`
    GROUP BY gender
    ORDER BY count DESC
""")
print("\n--- Gender Breakdown ---")
print(df_gender.to_string(index=False))

# --- 2b. Race / Ethnicity breakdown ---
# `race` comes from the admissions table (self-reported at admission).
# A patient can report different races across visits — we take their
# most frequently reported value to assign one label per person.
df_race = run_query(f"""
    WITH patient_race AS (
        SELECT
            subject_id,
            race,
            COUNT(*) AS times_reported,
            ROW_NUMBER() OVER (
                PARTITION BY subject_id
                ORDER BY COUNT(*) DESC
            ) AS rn
        FROM `{DATASET}.admissions`
        GROUP BY subject_id, race
    )
    SELECT
        race,
        COUNT(*) AS patient_count,
        ROUND(COUNT(*) * 100.0 / {total_patients}, 1) AS pct
    FROM patient_race
    WHERE rn = 1
    GROUP BY race
    ORDER BY patient_count DESC
""")
print("\n--- Race / Ethnicity Breakdown (per patient) ---")
print(df_race.to_string(index=False))

# --- 2c. Age distribution buckets ---
# We bin patients into age groups so we can see the shape of the population.
# CASE WHEN is SQL's version of if/elif.
df_age = run_query(f"""
    SELECT
        CASE
            WHEN anchor_age < 30  THEN '< 30'
            WHEN anchor_age < 45  THEN '30–44'
            WHEN anchor_age < 60  THEN '45–59'
            WHEN anchor_age < 75  THEN '60–74'
            ELSE                       '75+'
        END AS age_group,
        COUNT(*) AS count
    FROM `{DATASET}.patients`
    GROUP BY age_group
    ORDER BY MIN(anchor_age)
""")
print("\n--- Age Group Distribution ---")
print(df_age.to_string(index=False))


# ===========================================================================
# SECTION 3: What tables exist in this dataset?
# ===========================================================================
# INFORMATION_SCHEMA.TABLES is a special BigQuery table that lists every
# table in a dataset — like a table of contents for the database.
df_tables = run_query(f"""
    SELECT table_id AS table_name, row_count, size_bytes
    FROM `physionet-data.mimiciv_3_1_hosp.__TABLES__`
    ORDER BY row_count DESC
""")
df_tables["size_mb"] = (df_tables["size_bytes"].astype(float) / 1e6).round(1)
df_tables = df_tables[["table_name", "row_count", "size_mb"]]
print("\n--- Tables in mimiciv_3_1_hosp ---")
print(df_tables.to_string(index=False))


# ===========================================================================
# SECTION 4: Visualizations
# ===========================================================================
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("MIMIC-IV v3.1  —  Patient Demographics Overview", fontsize=14, fontweight="bold")

# -- Plot 1: Gender pie chart --
axes[0].pie(
    df_gender["count"],
    labels=df_gender["gender"],
    autopct="%1.1f%%",
    colors=["#4C72B0", "#DD8452"],
    startangle=90
)
axes[0].set_title("Gender Distribution")

# -- Plot 2: Age group bar chart --
axes[1].bar(df_age["age_group"], df_age["count"], color="#4C72B0", edgecolor="white")
axes[1].set_title("Age Group Distribution")
axes[1].set_xlabel("Age Group")
axes[1].set_ylabel("Number of Patients")
axes[1].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))

# -- Plot 3: Top 8 race/ethnicity horizontal bar --
top_race = df_race.head(8)
axes[2].barh(top_race["race"], top_race["patient_count"], color="#4C72B0", edgecolor="white")
axes[2].set_title("Top 8 Race / Ethnicity")
axes[2].set_xlabel("Number of Patients")
axes[2].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
axes[2].invert_yaxis()

plt.tight_layout()
plt.savefig("demographics_overview.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nChart saved to demographics_overview.png")
print("\nDone.")

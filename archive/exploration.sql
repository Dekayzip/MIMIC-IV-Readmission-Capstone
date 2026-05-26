-- ============================================================
-- TWO DATAFRAMES: Visit 1 and Visit 2 for returning patients
-- ============================================================
--
-- Strategy:
--   1. Use ROW_NUMBER() to label each visit per patient (1, 2, 3...)
--   2. Use COUNT() OVER to know how many total visits each patient had
--   3. Keep only patients with 2+ visits (returning_patients CTE)
--   4. Pull features from admissions + patients + diagnoses_icd
--   5. Run query twice — once filtered to visit_num = 1,
--                        once filtered to visit_num = 2
--
-- Features per visit:
--   From admissions   : hadm_id, admittime, dischtime, los_days,
--                       admission_type, insurance, race,
--                       discharge_location, hospital_expire_flag
--   From patients     : gender, anchor_age
--   From diagnoses_icd: num_diagnoses (count of ICD codes that visit)
-- ============================================================


-- ============================================================
-- SHARED BASE (used by both queries below as a CTE)
-- ============================================================
-- WITH ranked_visits AS (
--     SELECT
--         a.subject_id,
--         a.hadm_id,
--         a.admittime,
--         a.dischtime,
--         DATE_DIFF(DATE(a.dischtime), DATE(a.admittime), DAY) AS los_days,
--         a.admission_type,
--         a.insurance,
--         a.race,
--         a.discharge_location,
--         a.hospital_expire_flag,
--         ROW_NUMBER() OVER (
--             PARTITION BY a.subject_id
--             ORDER BY a.admittime
--         ) AS visit_num,
--         COUNT(*) OVER (
--             PARTITION BY a.subject_id
--         ) AS total_visits
--     FROM `physionet-data.mimiciv_3_1_hosp.admissions` a
-- ),
-- returning_patients AS (
--     SELECT * FROM ranked_visits
--     WHERE total_visits >= 2       -- only patients who came back
-- )


-- ============================================================
-- DATAFRAME 1 — First visit for every returning patient
-- ============================================================
WITH ranked_visits AS (
    SELECT
        a.subject_id,
        a.hadm_id,
        a.admittime,
        a.dischtime,
        DATE_DIFF(DATE(a.dischtime), DATE(a.admittime), DAY) AS los_days,
        a.admission_type,
        a.insurance,
        a.race,
        a.discharge_location,
        a.hospital_expire_flag,
        ROW_NUMBER() OVER (PARTITION BY a.subject_id ORDER BY a.admittime) AS visit_num,
        COUNT(*)     OVER (PARTITION BY a.subject_id)                      AS total_visits
    FROM `physionet-data.mimiciv_3_1_hosp.admissions` a
),
returning_patients AS (
    SELECT * FROM ranked_visits WHERE total_visits >= 2
)
SELECT
    r.subject_id,
    r.hadm_id,
    r.admittime,
    r.dischtime,
    r.los_days,
    r.admission_type,
    r.insurance,
    r.race,
    r.discharge_location,
    r.hospital_expire_flag,
    p.gender,
    p.anchor_age,
    COALESCE(d.num_diagnoses, 0) AS num_diagnoses
FROM returning_patients r
JOIN `physionet-data.mimiciv_3_1_hosp.patients` p
    ON r.subject_id = p.subject_id
LEFT JOIN (
    SELECT hadm_id, COUNT(*) AS num_diagnoses
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    GROUP BY hadm_id
) d ON r.hadm_id = d.hadm_id
WHERE r.visit_num = 1       -- ← FIRST visit only
ORDER BY r.subject_id;


-- ============================================================
-- DATAFRAME 2 — Second visit for every returning patient
-- (identical query, only the WHERE changes)
-- ============================================================
WITH ranked_visits AS (
    SELECT
        a.subject_id,
        a.hadm_id,
        a.admittime,
        a.dischtime,
        DATE_DIFF(DATE(a.dischtime), DATE(a.admittime), DAY) AS los_days,
        a.admission_type,
        a.insurance,
        a.race,
        a.discharge_location,
        a.hospital_expire_flag,
        ROW_NUMBER() OVER (PARTITION BY a.subject_id ORDER BY a.admittime) AS visit_num,
        COUNT(*)     OVER (PARTITION BY a.subject_id)                      AS total_visits
    FROM `physionet-data.mimiciv_3_1_hosp.admissions` a
),
returning_patients AS (
    SELECT * FROM ranked_visits WHERE total_visits >= 2
)
SELECT
    r.subject_id,
    r.hadm_id,
    r.admittime,
    r.dischtime,
    r.los_days,
    r.admission_type,
    r.insurance,
    r.race,
    r.discharge_location,
    r.hospital_expire_flag,
    p.gender,
    p.anchor_age,
    COALESCE(d.num_diagnoses, 0) AS num_diagnoses
FROM returning_patients r
JOIN `physionet-data.mimiciv_3_1_hosp.patients` p
    ON r.subject_id = p.subject_id
LEFT JOIN (
    SELECT hadm_id, COUNT(*) AS num_diagnoses
    FROM `physionet-data.mimiciv_3_1_hosp.diagnoses_icd`
    GROUP BY hadm_id
) d ON r.hadm_id = d.hadm_id
WHERE r.visit_num = 2       -- ← SECOND visit only
ORDER BY r.subject_id;

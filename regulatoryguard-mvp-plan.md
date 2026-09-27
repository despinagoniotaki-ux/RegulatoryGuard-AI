# RegulatoryGuard AI — MVP Architecture Plan

## Top-Level Overview

**Goal:** Ship a working hackathon MVP of RegulatoryGuard AI — a three-tier, low-cost pre-clinical data compliance engine built on the IBM Bob 2.0 framework.

**Scope:**
- Fix the schema mismatch in `process_data.py` so it correctly reads `regulatory_rules.json`
- Build a Streamlit dashboard (`app.py`) that wires all three tiers together
- Integrate a Bob 2.0 subagent to generate natural-language compliance narratives
- Apply the RegulatoryGuardAI brand design system to the Streamlit UI
- Surface `RegulatoryGuard.png` as the logo in the dashboard header

**Non-goals:**
- No cloud deployment (local run only for hackathon demo)
- No database backend — all I/O is flat files (CSV / JSON)
- No authentication or multi-user handling
- No changes to `convert_rules_dynamic.py` (it works correctly)
- No changes to `RegulatoryGuardAI_generate_mock_data.py` (mock data already generated)

**Approach:** Fix → Wire → Narrate → Style. Each sub-task is independently reviewable.

---

## Critical Pre-existing Bug

`process_data.py` references `rules["dosing_deviation_thresholds"]` and `rules["action_protocols"]` — **keys that do not exist** in the actual `regulatory_rules.json`. The real schema uses a `rules` array where each entry has `Minor_Variance_Limit_Percent`, `Major_Variance_Limit_Percent`, and `Action_Required` per `Assay_Parameter`. This must be fixed in Sub-task 1 before anything else can run.

---

## File Map

| File | Role | Tier |
|---|---|---|
| `RegulatoryGuardAI_Rules_Example.csv` | Source-of-truth rules authored by the science team | 1 |
| `convert_rules_dynamic.py` | Converts the CSV rules file into `regulatory_rules.json` | 1 |
| `regulatory_rules.json` | Compiled governance rulebook (6 assay parameters with variance thresholds) | 1 → 2 |
| `RegulatoryGuardAI_Test_Records/RegulatoryGuardAI_mock_preclinical_data.csv` | 3,200 mock animal dosing records with `Animal_ID`, `Cohort`, `Target_Dose_mg_kg`, `Actual_Dose_mg_kg`, `Notes` | 2 |
| `process_data.py` | Pandas engine that computes `Deviation_Pct` and maps to `Status` / `System_Action` per record | 2 |
| `app.py` (to be created) | Streamlit dashboard orchestrating all three tiers | 3 |
| `RegulatoryGuardAI_site_guides.html` | Brand design system — colour tokens, typography, badge rules | 3 |
| `RegulatoryGuard.png` | Brand logo displayed in dashboard header | 3 |
| `requirements.txt` (to be created) | Python dependency manifest | 0 |

---

## Sub-Tasks

---

### Sub-task 1 — Fix the `process_data.py` Schema Mismatch

**Status:** `[ ] pending`

**Intent:**
`process_data.py` will crash at runtime because it looks for `rules["dosing_deviation_thresholds"]` and `rules["action_protocols"]` — keys that were never written to `regulatory_rules.json`. The actual JSON stores rules as a flat array keyed by `Assay_Parameter`. The fix must make the engine read the real schema without altering the JSON structure.

Because the mock data contains a single measurement type (dosing deviation in mg/kg), `process_data.py` must pick the `Body Weight Change` rule row (or the first matching rule) as the deviation thresholds to apply — or better, apply the **most conservative threshold** across all loaded rules so the engine is generalisable.

**Expected Outcomes:**
- `process_data.py` runs without KeyError
- Reads `Minor_Variance_Limit_Percent` and `Major_Variance_Limit_Percent` from `rules["rules"][0]` (or a named lookup)
- Assigns `Status` values: `"APPROVED"`, `"REVIEW REQUIRED"`, `"EXCEEDS LIMIT"`
- Assigns `System_Action` from the rule's `Action_Required` field
- Running `python process_data.py` produces a valid `audit_ready_report.csv`

**Cohort-to-Rule Mapping (confirmed by user):**

| Cohort | Assay Parameter Rule Applied |
|---|---|
| Group_1_Low | Body Weight Change |
| Group_2_Mid | Serum Glucose |
| Group_3_High | Heart Rate |
| Group_4_Control | Alanine Aminotransferase (ALT) |

This mapping is hardcoded as a Python dict inside `process_data.py` so the demo shows genuine multi-parameter compliance coverage across all four cohorts.

**Todo List:**
1. In `process_data.py`, remove the two broken `rules["dosing_deviation_thresholds"]` / `rules["action_protocols"]` lookups
2. Build a `rules_by_parameter` dict from `rules["rules"]` keyed by `Assay_Parameter`
3. Add a `COHORT_RULE_MAP` dict: `{"Group_1_Low": "Body Weight Change", "Group_2_Mid": "Serum Glucose", "Group_3_High": "Heart Rate", "Group_4_Control": "Alanine Aminotransferase (ALT)"}`
4. Apply the vectorised deviation calc row-by-row using the cohort's mapped rule thresholds (`Minor_Variance_Limit_Percent`, `Major_Variance_Limit_Percent`)
5. Replace the three hard-coded status strings with `"APPROVED"`, `"REVIEW REQUIRED"`, `"EXCEEDS LIMIT"` (matching badge labels in the brand guide)
6. Set `System_Action` from the rule's `Action_Required` field for minor/major; use `"Exclude"` for exceeds-limit
7. Add `Applied_Rule` as an output column (the `Assay_Parameter` name used) so the dashboard can show which rule flagged each record
8. Update the `__main__` block to reference the correct mock data path: `RegulatoryGuardAI_Test_Records/RegulatoryGuardAI_mock_preclinical_data.csv`

**Relevant Context:**
- `process_data.py` lines 9-11 (the broken key lookups)
- `regulatory_rules.json` rules array — 6 parameters each with `Minor_Variance_Limit_Percent`, `Major_Variance_Limit_Percent`, `Action_Required`
- Badge label strings defined in `RegulatoryGuardAI_site_guides.html` lines 118-120

---

### Sub-task 2 — Create `requirements.txt`

**Status:** `[ ] pending`

**Intent:**
No dependency manifest exists. Without it the hackathon judges cannot install and run the project. This sub-task creates the minimal `requirements.txt` for the three-tier stack.

**Expected Outcomes:**
- `requirements.txt` exists at the project root
- Lists only the non-stdlib packages: `pandas`, `streamlit`, `requests`
- No IBM SDK dependency (Bob 2.0 is called via raw `requests`)

**Todo List:**
1. Confirm all `import` statements across `convert_rules_dynamic.py`, `process_data.py`, and planned `app.py`
2. Write `requirements.txt` with minimum version pins: `pandas>=2.0`, `streamlit>=1.35`, `requests>=2.31`

**Relevant Context:**
- `process_data.py` imports: `pandas`, `json` (stdlib)
- `convert_rules_dynamic.py` imports: `csv`, `json`, `sys`, `os` (all stdlib)
- `app.py` will need: `streamlit`, `pandas`, `requests` — no SDK

---

### Sub-task 3 — Build the Streamlit Dashboard `app.py`

**Status:** `[ ] pending`

**Intent:**
Wire all three tiers into a single runnable Streamlit app. Tier 1 (rule ingestion) is pre-run; `app.py` loads the compiled `regulatory_rules.json`. Tier 2 (deterministic math) is called via `process_preclinical_data()` from `process_data.py`. Tier 3 (narrative) is a Bob 2.0 subagent call that receives the processed summary and returns a natural-language compliance paragraph.

**Expected Outcomes:**
- `app.py` exists at the project root
- Page header shows `RegulatoryGuard.png` logo + "RegulatoryGuard AI" title in brand navy
- Summary KPI row: total records, % approved, % review, % exceeds
- Full compliance results table with traffic-light `Status` column badges (green/yellow/red)
- "Run Compliance Check" primary button triggers Tier 2 processing
- "Generate Narrative" button calls the Bob 2.0 subagent and displays the returned text in a styled card
- "Export eCTD Package" secondary button downloads `audit_ready_report.csv`
- All colours sourced from the brand tokens in `RegulatoryGuardAI_site_guides.html`

**Todo List:**
1. Import `streamlit`, `pandas`, `requests`, `os`, `io`, and `process_preclinical_data` from `process_data`
2. Set Streamlit page config: `page_title="RegulatoryGuard AI"`, `layout="wide"`, `page_icon` = shield emoji
3. Inject the brand CSS (font, colour tokens, badge classes) via `st.markdown(..., unsafe_allow_html=True)`
4. Render the header: `st.image("RegulatoryGuard.png", width=160)` + `st.title` in brand navy
5. Add sidebar section **"Upload Data"**: `st.sidebar.file_uploader("Pre-clinical Data CSV", type="csv")` and `st.sidebar.file_uploader("Rules JSON", type="json")`; both must be uploaded before the run button activates (gate with `if data_file and rules_file`)
6. Add sidebar section **"Bob 2.0 Narrative"**: `st.sidebar.text_input("Endpoint URL", placeholder="https://…/v1/text/generation")` and `st.sidebar.text_input("API Key", type="password")` — both optional
7. "Run Compliance Check" button → call `process_preclinical_data()` with the uploaded file buffers → store result DataFrame in `st.session_state["results"]`
8. Render KPI columns using `st.metric`: Total Records, ✅ Approved, ⚠️ Review Required, 🚫 Exceeds Limit
9. Render the data table: HTML-render the `Status` column with the brand badge classes; other columns in `st.dataframe`
10. "Generate Narrative" button → build summary dict from session state → call `generate_narrative()` with sidebar endpoint/key → display result in styled ice-blue card
11. "Export eCTD Package" button → `st.download_button` for the result DataFrame as CSV

**Relevant Context:**
- Brand CSS tokens: `RegulatoryGuardAI_site_guides.html` lines 11-29
- Badge classes: lines 74-82
- Button styles: lines 84-86
- Logo file: `RegulatoryGuard.png` at project root
- Processed data columns: `Animal_ID`, `Cohort`, `Target_Dose_mg_kg`, `Actual_Dose_mg_kg`, `Notes`, `Deviation_Pct`, `Status`, `System_Action`, `Applied_Rule`

---

### Sub-task 4 — Integrate the Bob 2.0 Subagent Narrative Engine

**Status:** `[ ] pending`

**Intent:**
The hackathon requirement is to demonstrate IBM Bob 2.0. The narrative tier receives a structured compliance summary from Tier 2 and returns an audit-ready natural-language paragraph suitable for an eCTD Section 2.6 narrative. This is the highest-value AI differentiator in the demo.

**Expected Outcomes:**
- A `generate_narrative(summary_dict)` function exists (either in `app.py` or a separate `narrative.py`)
- The function builds a structured prompt from: total records, counts per status, flagged cohort names, max deviation %
- It calls the Bob 2.0 API / subagent and returns a string
- The returned text appears in the Streamlit UI inside a styled container
- If the Bob 2.0 API key is not set, the function returns a clearly marked placeholder string so the UI still renders

**API approach (confirmed by user):** Bob 2.0 REST API called directly via Python `requests` with a `Bearer` token. No extra SDK dependency. The endpoint URL and API key are **optional** — collected from the user via Streamlit sidebar text inputs at runtime. If either field is blank the function skips the API call and renders a clearly-labelled placeholder narrative so the app is fully usable without credentials.

**Todo List:**
1. Add two `st.sidebar.text_input` fields: "Bob 2.0 Endpoint URL" (placeholder: `https://…/v1/text/generation`) and "Bob 2.0 API Key" (type `password`)
2. Write `generate_narrative(summary_dict, endpoint, api_key)` in `app.py` using `requests.post`
3. If either `endpoint` or `api_key` is empty, skip the API call and return a clearly-labelled placeholder narrative string (no `st.warning` blocking the UI)
4. Build the prompt f-string from summary dict keys: `total`, `approved_count`, `review_count`, `exceeds_count`, `top_flagged_cohort`, `max_deviation_pct`, `applied_rules`
5. Set `Authorization: Bearer {api_key}` header and `Content-Type: application/json`
6. Wrap the `requests.post` call in `try/except requests.RequestException` with a user-visible `st.error` on failure
7. Style the returned narrative (or placeholder) in a `st.markdown` block inside a `div` with `background: #E0F2FE` and `border: 1px solid #0284C7`

**Relevant Context:**
- Summary dict keys: `total`, `approved_count`, `review_count`, `exceeds_count`, `top_flagged_cohort`, `max_deviation_pct`, `applied_rules`
- Brand card style: `background: #E0F2FE`, `border: 1px solid #0284C7`, `border-radius: 14px`, `padding: 26px`
- No environment variable needed — credentials come entirely from the sidebar inputs

---

### Sub-task 5 — End-to-End Smoke Test and Demo Readiness

**Status:** `[ ] pending`

**Intent:**
Verify that a judge can clone the repo, install dependencies, and run the full pipeline from a single command. Catch any remaining path or import errors before the demo.

**Expected Outcomes:**
- `python convert_rules_dynamic.py RegulatoryGuardAI_Rules_Example.csv` produces `regulatory_rules.json` without error
- `python process_data.py` produces `audit_ready_report.csv` with all 3,200 records and correct `Status` values
- `streamlit run app.py` launches without import errors and renders the dashboard
- All three status buckets (APPROVED / REVIEW REQUIRED / EXCEEDS LIMIT) are visible in the results table
- The "Export eCTD Package" button downloads a valid CSV
- A short `README.md` exists with one-command run instructions

**Todo List:**
1. Run `python convert_rules_dynamic.py RegulatoryGuardAI_Rules_Example.csv` — verify output JSON matches expected schema
2. Run `python process_data.py` — inspect `audit_ready_report.csv` for correct `Status` distribution (~90% APPROVED, ~7% REVIEW, ~3% EXCEEDS)
3. Run `streamlit run app.py` — walk through all UI interactions
4. Write `README.md` with: project description, setup steps (`pip install -r requirements.txt`), and run command
5. Verify `RegulatoryGuard.png` loads correctly in the header (no broken image)

**Relevant Context:**
- Mock data distribution (from generator): ~90% deviation < 5%, ~7% 5–10%, ~3% > 10%
- Expected audit report columns: `Animal_ID`, `Cohort`, `Target_Dose_mg_kg`, `Actual_Dose_mg_kg`, `Notes`, `Deviation_Pct`, `Status`, `System_Action`

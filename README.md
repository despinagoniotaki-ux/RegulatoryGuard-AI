# RegulatoryGuard AI

> **IBM Bob 2.0 Hackathon MVP** — An accessible AI engine that automates the tracking, review, and justification of preclinical data anomalies to accelerate regulatory approvals for clinical trials without high software costs.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Powered by IBM Bob 2.0](https://img.shields.io/badge/Powered%20by-IBM%20Bob%202.0-0284C7)](https://www.ibm.com/watsonx)

---

## Overview

**RegulatoryGuard AI** is a three-tier, flat-file pre-clinical data compliance engine built for the IBM Bob 2.0 Hackathon. It automates the detection of dosing variance deviations across animal cohorts, surfaces compliance verdicts in a modern Streamlit dashboard, and generates eCTD-ready narratives via the IBM Bob 2.0 large language model API.

### Architecture

| Tier | Component | Role |
|---|---|---|
| **1 — Rules** | `RegulatoryGuardAI_Rules_Example.csv` → `regulatory_rules.json` | Science-team-authored variance thresholds per assay parameter |
| **2 — Engine** | `process_data.py` | Pandas engine: computes deviation %, assigns traffic-light status, maps cohort → rule |
| **3 — UI & AI** | `app.py` + Bob 2.0 API | Streamlit dashboard + AI narrative generation |

### Traffic-light Compliance Verdicts

| Status | Meaning |
|---|---|
| 🟢 **INCLUDE** | Deviation ≤ minor variance limit |
| 🟡 **REVIEW** | Deviation between minor and major limit |
| 🔴 **EXCLUDE** | Deviation exceeds major variance limit |

### Key Capabilities

- Multi-project workspace with unique 15-digit project IDs
- Per-record 15-digit IDs (first 6 digits derived from the project ID)
- Import delta detection — new records vs. previously seen records highlighted
- Custom rules upload (CSV or JSON) overriding the default rulebook
- Bob 2.0 AI narrative generation with graceful placeholder fallback
- One-click eCTD-ready CSV export

---

## Installation & Setup

### Prerequisites

- Python **3.10 or later**
- `pip` (comes with Python) or `conda`
- Git (optional — you can also download the ZIP)
- ~200 MB free disk space

### Step-by-step

**1. Clone the repository**

```bash
git clone https://github.com/despinagoniotaki-ux/RegulatoryGuard-AI.git
cd RegulatoryGuard-AI
```

**2. Create and activate a virtual environment**

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

The following packages will be installed:
- `streamlit >= 1.35`
- `pandas >= 2.0`
- `numpy >= 1.26`
- `requests >= 2.31`
- `python-dotenv >= 1.0`

**4. Configure watsonx.ai credentials**

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

Then open `.env` in any text editor and set:

```env
WATSONX_PROJECT_ID=your-watsonx-project-id-here
WATSONX_API_KEY=your-ibm-cloud-api-key-here
```

- **Project ID** — found in your [watsonx.ai](https://dataplatform.cloud.ibm.com/) project settings under *Manage → General*.
- **API Key** — create one at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys).

The app reads these values at startup and pre-fills the sidebar fields automatically. You can always override them in the sidebar without editing `.env`.

**5. Compile the default rulebook** *(only needed once, or after editing the CSV)*

```bash
python convert_rules_dynamic.py RegulatoryGuardAI_Rules_Example.csv
```

This produces `regulatory_rules.json` at the project root.

> **Already done?** A pre-compiled `regulatory_rules.json` is included in the repo — you can skip step 5 unless you modify the rules CSV.

---

## Launching the Dashboard

From the project root (with the virtual environment active):

```bash
streamlit run app.py
```

Streamlit will print something like:

```
  You can now view your Streamlit app in your browser.
  Local URL:  http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

> **Port conflict?** Use `streamlit run app.py --server.port 8080` to run on a different port.

---

## Dashboard Walkthrough

### Sidebar

| Section | Purpose |
|---|---|
| 🗂 **Project** | Create a new project (name + description → unique 15-digit ID assigned automatically) or switch to an existing one. |
| 📋 **Compliance Rules** | Download the template rules CSV; upload a custom rules file (CSV or JSON). |
| 📂 **Dataset** | Load the built-in mock dataset or upload your own pre-clinical CSV. |
| 🤖 **Bob 2.0 Narrative** | watsonx.ai Project ID and IBM Cloud API Key for AI narrative generation (pre-filled from `.env`). |

### Executive Summary

After running the compliance check, four KPI cards appear at the top of the main panel:

- **Total Records** — number of rows analysed in this import, with new-record delta
- **✓ Include** — records within all acceptance limits (green)
- **⚠ Review** — records between minor and major variance limits (yellow)
- **✕ Exclude** — records exceeding the major variance limit (red)

### Distribution Charts

- **Status Distribution** — bar chart of INCLUDE / REVIEW / EXCLUDE counts
- **Deviation % by Cohort** — mean deviation per cohort group
- **Deviation % Histogram** — frequency distribution across deviation buckets

### Interactive Data Viewer

Filter the results table by **Status**, **Cohort**, or **free-text search** across Animal ID and Notes fields. Each row includes: `Record_ID`, `Animal_ID`, `Cohort`, `Target_Dose_mg_kg`, `Actual_Dose_mg_kg`, `Deviation_Pct`, `Status`, `System_Action`, `Applied_Rule`, and `Delta` (NEW / EXISTING).

---

## Using Custom Rules

### Download the Template

Click **"⬇ Download Rules Template"** in the sidebar to get `RegulatoryGuardAI_Rules_Example.csv`.

### CSV Column Reference

| Column | Type | Description |
|---|---|---|
| `Assay_Parameter` | text | Name of the assay (must match cohort mapping) |
| `Unit` | text | Unit of measurement (for display only) |
| `Minor_Variance_Limit_Percent` | number | Upper boundary of the INCLUDE zone (%) |
| `Major_Variance_Limit_Percent` | number | Upper boundary of the REVIEW zone; beyond this = EXCLUDE (%) |
| `Action_Required` | text | Action text shown in the REVIEW row |

### Upload Your Rules

1. Edit the CSV template with your thresholds and save it.
2. In the sidebar under **📋 Compliance Rules**, use the *Upload custom rules* file picker.
3. A success message confirms how many rules were loaded.
4. Click **"▶ Run Compliance Check"** — the engine will now use your rules.

> You can also upload a JSON file (`.json`) that already follows the `regulatory_rules.json` schema.

### Default Cohort-to-Rule Mapping

| Cohort | Assay Parameter Applied |
|---|---|
| `Group_1_Low` | Body Weight Change |
| `Group_2_Mid` | Serum Glucose |
| `Group_3_High` | Heart Rate |
| `Group_4_Control` | Alanine Aminotransferase (ALT) |

Cohorts not in this mapping fall back to the rule with the most conservative (lowest) minor variance limit.

---

## Bob 2.0 Narrative Generation

RegulatoryGuard AI integrates **IBM Bob 2.0** to automatically produce an eCTD Section 2.6-style compliance narrative from the processed compliance summary.

### How It Works

1. **IAM token exchange** — the app POSTs your API key to `https://iam.cloud.ibm.com/identity/token` to obtain a short-lived bearer token.
2. **Inference call** — `POST https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29` using model `ibm/granite-13b-instruct-v2` via the standard `requests` library (no extra SDK required).

### What the Narrative Includes

- Total number of records analysed
- Per-status counts and percentages
- Maximum deviation observed and which cohort it occurred in
- Which assay rules were applied
- A professional summary sentence suitable for eCTD submission

> **No credentials?** If either sidebar field is left blank, the app will display a clearly labelled placeholder narrative — the rest of the dashboard remains fully functional.

---

## Running the Pipeline Standalone

Each tier can be run independently from the command line.

```bash
# Tier 1 — Compile rules
python convert_rules_dynamic.py RegulatoryGuardAI_Rules_Example.csv
# Output: regulatory_rules.json

# Tier 2 — Run compliance engine
python process_data.py
# Reads:  RegulatoryGuardAI_Test_Records/RegulatoryGuardAI_mock_preclinical_data.csv
#         regulatory_rules.json
# Output: audit_ready_report.csv

# Full pipeline (one-liner)
python convert_rules_dynamic.py RegulatoryGuardAI_Rules_Example.csv && python process_data.py
```

> **Expected distribution** for the mock dataset: ~90% INCLUDE, ~7% REVIEW, ~3% EXCLUDE across 3,200 records.

---

## Exporting Results

Click **"⬇ Export eCTD Package (CSV)"** below the data table to download the full processed dataset as `audit_ready_report_<project_id>.csv`. The CSV is ready for direct attachment to an eCTD submission package or import into a LIMS / EDC system.

---

## FAQ & Troubleshooting

**The dashboard shows "No active project" after I create one**
The project is stored in Streamlit session state. If the page fully reloads (e.g. after a code change), session state is cleared. Simply re-create the project in the sidebar — this is expected behaviour for the MVP's in-memory persistence.

**`ModuleNotFoundError: No module named 'streamlit'`**
Your virtual environment is not active, or you forgot to run `pip install -r requirements.txt`. Re-activate the environment (`source .venv/bin/activate`) and reinstall.

**Rules uploaded but compliance check still uses old thresholds**
After uploading new rules, click **"▶ Run Compliance Check"** again. Uploading the file updates the rules in session state; the engine only uses them on the next run.

**watsonx.ai narrative returns an error or empty text**
- Check that `WATSONX_PROJECT_ID` and `WATSONX_API_KEY` in `.env` are correct (no extra spaces or quotes).
- Confirm the API key is valid at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys).
- Verify the project ID matches the one in your watsonx.ai project under *Manage → General*.
- Check that your network allows outbound HTTPS to `iam.cloud.ibm.com` and `us-south.ml.cloud.ibm.com`.

**How do I add my own cohort-to-rule mappings?**
Open `app.py` and find the `COHORT_RULE_MAP` dictionary near the top. Add entries in the format `"Your_Cohort_Name": "Assay_Parameter_Name"`. The assay parameter name must exactly match the `Assay_Parameter` column value in your rules CSV.

**Port 8501 is already in use**
```bash
streamlit run app.py --server.port 8080
```

---

## License

MIT © 2025 Despoina Goniotaki, Evrydiki Goniotaki (RegulatoryGuard-AI) — see [LICENSE](LICENSE) for details.

---

*RegulatoryGuard AI · IBM Bob 2.0 Hackathon Submission · [Lablab.ai](https://lablab.ai)*

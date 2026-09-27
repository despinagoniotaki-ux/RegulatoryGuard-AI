"""
RegulatoryGuard AI — Streamlit Dashboard (app.py)
MVP for IBM Bob 2.0 Hackathon
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import io
import re
import random
import string
import hashlib
from datetime import datetime

# ─── Load .env (silently ignored if python-dotenv is not installed) ───────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_ENV_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
_ENV_API_KEY    = os.getenv("WATSONX_API_KEY", "")

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RegulatoryGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Brand CSS (tokens from RegulatoryGuardAI_site_guides.html) ───────────────
BRAND_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

:root {
  --brand-dark:       #0A192F;
  --brand-blue:       #0284C7;
  --brand-light-blue: #E0F2FE;
  --bg-surface:       #F8FAFC;
  --bg-card:          #FFFFFF;
  --text-primary:     #0F172A;
  --text-secondary:   #475569;
  --line:             #E2E8F0;
  --status-green:     #10B981;
  --status-yellow:    #F59E0B;
  --status-red:       #EF4444;
}

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', 'Segoe UI', Helvetica, Arial, sans-serif !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--brand-dark) !important;
  border-right: 1px solid rgba(255,255,255,0.07);
}
section[data-testid="stSidebar"] * {
  color: #CBD5E1 !important;
}
section[data-testid="stSidebar"] .sidebar-section-title {
  color: #94A3B8 !important;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .10em;
  text-transform: uppercase;
  margin: 20px 0 8px;
}
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {
  background: rgba(255,255,255,0.92) !important;
  border: 1px solid rgba(255,255,255,0.30) !important;
  color: #0A2540 !important;
  border-radius: 7px !important;
}
section[data-testid="stSidebar"] input::placeholder,
section[data-testid="stSidebar"] textarea::placeholder {
  color: #64748B !important;
  opacity: 1 !important;
}

/* ── Sidebar file uploader ── */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
  background: rgba(255,255,255,0.92) !important;
  border: 1px dashed rgba(10,37,64,0.35) !important;
  border-radius: 7px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] div {
  color: #0A2540 !important;
}

/* ── Main container ── */
.block-container { padding-top: 1.6rem !important; padding-bottom: 3rem !important; }

/* ── Dashboard header ── */
.rg-header {
  display: flex;
  align-items: center;
  gap: 18px;
  background: linear-gradient(135deg, #0A192F 0%, #0c2340 60%, #0e2d57 100%);
  border-radius: 16px;
  padding: 22px 28px;
  margin-bottom: 26px;
}
.rg-header-text h1 {
  margin: 0; font-size: 26px; font-weight: 800;
  color: #FFFFFF; letter-spacing: -.02em; line-height: 1.2;
}
.rg-header-text p  { margin: 4px 0 0; color: #94A3B8; font-size: 14px; }

/* ── Metric / KPI cards ── */
.kpi-row { display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap; }
.kpi-card {
  flex: 1; min-width: 160px;
  background: var(--bg-card);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 18px 20px;
}
.kpi-card .kpi-label { font-size: 12px; font-weight: 600; color: var(--text-secondary); letter-spacing: .06em; text-transform: uppercase; }
.kpi-card .kpi-value { font-size: 32px; font-weight: 800; color: var(--text-primary); line-height: 1.2; margin: 4px 0 2px; }
.kpi-card .kpi-sub   { font-size: 12px; color: var(--text-secondary); }

.kpi-card.green { border-left: 4px solid var(--status-green); }
.kpi-card.yellow{ border-left: 4px solid var(--status-yellow); }
.kpi-card.red   { border-left: 4px solid var(--status-red);   }
.kpi-card.blue  { border-left: 4px solid var(--brand-blue);   }

/* ── Traffic-light badge ── */
.badge {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 4px 12px; border-radius: 999px;
  font-size: 12px; font-weight: 600; white-space: nowrap;
}
.badge.green  { background: rgba(16,185,129,.1); color: #047857; border: 1px solid rgba(16,185,129,.3); }
.badge.yellow { background: rgba(245,158,11,.1);  color: #B45309; border: 1px solid rgba(245,158,11,.3); }
.badge.red    { background: rgba(239,68,68,.1);   color: #B91C1C; border: 1px solid rgba(239,68,68,.3); }
.dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block; }
.green-dot  { background: var(--status-green); }
.yellow-dot { background: var(--status-yellow); }
.red-dot    { background: var(--status-red); }

/* ── Section headings ── */
.section-heading {
  font-size: 15px; font-weight: 700; color: var(--text-primary);
  border-bottom: 1px solid var(--line); padding-bottom: 8px; margin: 24px 0 14px;
  letter-spacing: -.01em;
}

/* ── Narrative card ── */
.narrative-card {
  background: var(--brand-light-blue);
  border: 1px solid #0284C7;
  border-radius: 14px;
  padding: 22px 26px;
  font-size: 14px;
  line-height: 1.75;
  color: var(--text-primary);
  max-height: 360px;
  overflow-y: auto;
}
.narrative-card .narrative-label {
  font-size: 11px; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: var(--brand-blue); margin-bottom: 10px;
}

/* ── Delta badge ── */
.delta-new   { background: rgba(2,132,199,.12);   color: #0369a1; border-radius: 4px; padding: 2px 7px; font-size: 11px; font-weight: 600; }
.delta-same  { background: rgba(71,85,105,.10);   color: #475569; border-radius: 4px; padding: 2px 7px; font-size: 11px; }

/* ── Surface panel ── */
.surface-panel {
  background: var(--bg-surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 20px 22px;
  margin-bottom: 16px;
}

/* ── PII warning banner ── */
.pii-warning {
  background: #FFF7ED;
  border: 1px solid #F97316;
  border-left: 4px solid #F97316;
  border-radius: 10px;
  padding: 14px 18px;
  margin-bottom: 14px;
  font-size: 13px;
  color: #7C2D12;
}
.pii-warning strong { color: #9A3412; }

/* ── Streamlit override: primary button ── */
.stButton>button {
  background: var(--brand-blue) !important;
  color: #fff !important;
  border: none !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
  font-size: 14px !important;
}
.stButton>button:hover { background: #0369A1 !important; }

/* ── Streamlit override: download button ── */
.stDownloadButton>button {
  background: transparent !important;
  color: var(--brand-blue) !important;
  border: 2px solid var(--brand-blue) !important;
  border-radius: 8px !important;
  font-weight: 600 !important;
}

/* ── Table tweaks ── */
.dataframe-container { border-radius: 10px; overflow: hidden; }
[data-testid="stDataFrame"] { border-radius: 10px; }

/* ── Phase 3 — Human Review Portal ── */
.review-portal-header {
  display: flex; align-items: center; gap: 10px;
  background: linear-gradient(90deg, #1e3a5f 0%, #0c2340 100%);
  border-radius: 12px; padding: 16px 22px; margin-bottom: 18px;
}
.review-portal-header h2 {
  margin: 0; font-size: 17px; font-weight: 700; color: #FFFFFF; letter-spacing: -.01em;
}
.review-portal-header p {
  margin: 3px 0 0; font-size: 12px; color: #94A3B8;
}
.review-stat-pill {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 600;
}
.review-stat-pill.yellow { background: rgba(245,158,11,.15); color: #B45309; border: 1px solid rgba(245,158,11,.4); }
.review-stat-pill.red    { background: rgba(239,68,68,.15);  color: #B91C1C; border: 1px solid rgba(239,68,68,.4); }
.review-stat-pill.blue   { background: rgba(2,132,199,.12);  color: #0369a1; border: 1px solid rgba(2,132,199,.3); }
.finalize-info {
  background: #F0FDF4; border: 1px solid #86EFAC; border-left: 4px solid #22C55E;
  border-radius: 10px; padding: 14px 18px; margin-bottom: 14px; font-size: 13px; color: #14532D;
}
.finalize-info strong { color: #15803D; }
</style>
"""
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ── Persistent jump-to nav bar ────────────────────────────────────────────────
# Injected via components.html so Streamlit cannot strip or collapse it.
# The script writes the bar directly into the parent document <body> and uses
# position:fixed so it stays visible no matter how far the user scrolls.
import streamlit.components.v1 as _components
_components.html("""
<script>
(function() {
  var parent = window.parent.document;
  var BAR_ID = 'rg-jump-nav';
  if (parent.getElementById(BAR_ID)) return;   // already injected — skip on reruns

  // --- styles ---
  var style = parent.createElement('style');
  style.textContent = [
    '#rg-jump-nav {',
    '  position: fixed; top: 0; left: 0; right: 0; z-index: 99999;',
    '  display: flex; align-items: center; gap: 6px; flex-wrap: nowrap;',
    '  background: rgba(248,250,252,0.96);',
    '  border-bottom: 1px solid #E2E8F0;',
    '  padding: 7px 18px;',
    '  box-shadow: 0 1px 6px rgba(0,0,0,0.08);',
    '  backdrop-filter: blur(8px);',
    '  font-family: "Plus Jakarta Sans", "Segoe UI", sans-serif;',
    '}',
    '#rg-jump-nav .rg-nav-label {',
    '  font-size: 11px; font-weight: 700; color: #475569;',
    '  text-transform: uppercase; letter-spacing: .06em; margin-right: 4px; white-space: nowrap;',
    '}',
    '#rg-jump-nav a {',
    '  font-size: 12px; font-weight: 600; color: #0284C7;',
    '  text-decoration: none; padding: 4px 10px; border-radius: 6px;',
    '  border: 1px solid rgba(2,132,199,0.25); background: rgba(2,132,199,0.06);',
    '  white-space: nowrap; transition: background 0.15s;',
    '}',
    '#rg-jump-nav a:hover { background: rgba(2,132,199,0.18); }'
  ].join('');
  parent.head.appendChild(style);

  // --- bar ---
  var bar = parent.createElement('div');
  bar.id = BAR_ID;
  bar.innerHTML = [
    '<span class="rg-nav-label">Jump to</span>',
    '<a href="#exec-summary">&#128202; Executive Summary</a>',
    '<a href="#distribution">&#128200; Distribution</a>',
    '<a href="#data-viewer">&#128270; Data Viewer</a>',
    '<a href="#narrative">&#129302; Narrative</a>',
    '<a href="#review-portal">&#128269; Review Portal</a>',
    '<a href="#export">&#128230; Export</a>'
  ].join('');
  parent.body.insertBefore(bar, parent.body.firstChild);

  // Push Streamlit's main content down so the bar doesn't cover it
  var appView = parent.querySelector('.appview-container') || parent.querySelector('.main');
  if (appView) appView.style.paddingTop = '42px';
})();
</script>
""", height=0)

# ─── Helpers / IDs ────────────────────────────────────────────────────────────

def _rand_digits(n: int) -> str:
    return "".join(random.choices(string.digits, k=n))

def new_project_id() -> str:
    return _rand_digits(15)

def new_record_id(project_id: str) -> str:
    """6 first digits = last 6 digits of project_id"""
    prefix = project_id[-6:]
    suffix = _rand_digits(9)
    return prefix + suffix

def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

# ─── Session state initialisation ─────────────────────────────────────────────

def _init_state():
    defaults = {
        "projects":         {},          # {project_id: {name, description, datasets:[]}}
        "active_project":   None,
        "results_df":       None,
        "previous_df":      None,
        "import_history":   [],          # list of import metadata dicts
        "narrative_text":   None,
        "rules_json":       None,
        "raw_data_df":      None,
        # Phase 3 — keyed by Record_ID: {"action": str, "comment": str}
        "review_decisions": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ─── GDPR / PII Detection ─────────────────────────────────────────────────────

# Column name patterns that suggest PII/sensitive data (case-insensitive).
# Uses (?<![a-z0-9]) / (?![a-z0-9]) as word boundaries so that underscore-
# delimited names like "patient_name" or "first_name" are also matched.
_PII_COLUMN_PATTERNS = [
    r"(?<![a-z0-9])name(?![a-z0-9])",
    r"first.?name", r"last.?name", r"full.?name", r"sur.?name",
    r"(?<![a-z0-9])ssn(?![a-z0-9])", r"social.?security", r"ssin",
    r"passport", r"national.?id", r"personal.?id",
    r"(?<![a-z0-9])nid(?![a-z0-9])",
    r"(?<![a-z0-9])dob(?![a-z0-9])", r"date.?of.?birth", r"birth.?date",
    r"(?<![a-z0-9])email(?![a-z0-9])", r"e.?mail",
    r"(?<![a-z0-9])phone(?![a-z0-9])", r"mobile", r"telephone",
    r"address", r"(?<![a-z0-9])street(?![a-z0-9])",
    r"(?<![a-z0-9])zip(?![a-z0-9])", r"postcode", r"postal",
    r"ip.?address",
    r"patient.?id", r"subject.?id", r"participant.?id",
    r"medical.?record", r"(?<![a-z0-9])mrn(?![a-z0-9])",
    r"(?<![a-z0-9])gender(?![a-z0-9])", r"(?<![a-z0-9])sex(?![a-z0-9])",
    r"(?<![a-z0-9])race(?![a-z0-9])", r"ethnicity",
    r"diagnosis", r"(?<![a-z0-9])condition(?![a-z0-9])",
    r"birthday", r"(?<![a-z0-9])age(?![a-z0-9])",
    r"(?<![a-z0-9])salary(?![a-z0-9])", r"income", r"financial",
    r"biometric", r"fingerprint",
]

# Cell-level regex patterns for common PII formats
_PII_CELL_PATTERNS = {
    "SSN":          re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "Email":        re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    "Phone (US)":   re.compile(r"\b(?:\+?1[\s\-.]?)?\(?\d{3}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}\b"),
    "Date of Birth":re.compile(r"\b(?:19|20)\d{2}[\/\-]\d{2}[\/\-]\d{2}\b"),
    "Passport/ID":  re.compile(r"\b[A-Z]{1,2}\d{6,9}\b"),
    "Postcode (UK)":re.compile(r"\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b"),
    "IP Address":   re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def scan_pii(df: pd.DataFrame) -> dict:
    """
    Scan a DataFrame for potential PII.

    Returns a dict:
        {
          "flagged_columns": [list of column names matching PII patterns],
          "cell_findings":   {column: {pii_type: count, ...}, ...},
          "has_pii": bool,
        }
    """
    flagged_columns = []
    for col in df.columns:
        col_lower = str(col).lower()
        for pat in _PII_COLUMN_PATTERNS:
            if re.search(pat, col_lower):
                flagged_columns.append(col)
                break

    cell_findings: dict = {}
    # Scan string columns for PII patterns in a sample (up to 500 rows for speed)
    sample = df.head(500)
    for col in df.columns:
        col_str = sample[col].astype(str)
        col_hits: dict = {}
        for pii_type, pattern in _PII_CELL_PATTERNS.items():
            matches = col_str.str.count(pattern).sum()
            if matches > 0:
                col_hits[pii_type] = int(matches)
        if col_hits:
            cell_findings[col] = col_hits

    has_pii = bool(flagged_columns or cell_findings)
    return {
        "flagged_columns": flagged_columns,
        "cell_findings":   cell_findings,
        "has_pii":         has_pii,
    }


def render_pii_warning(pii_result: dict) -> None:
    """Render a GDPR/PII warning banner in the Streamlit UI."""
    if not pii_result["has_pii"]:
        return

    col_list = ", ".join(f"<code>{c}</code>" for c in pii_result["flagged_columns"]) or "—"
    cell_parts = []
    for col, hits in pii_result["cell_findings"].items():
        for pii_type, count in hits.items():
            cell_parts.append(f"<code>{col}</code>: {count}× {pii_type}")
    cell_detail = "; ".join(cell_parts) if cell_parts else "—"

    st.markdown(f"""
    <div class="pii-warning">
      <strong>⚠ GDPR / Sensitive Data Alert</strong><br>
      The uploaded dataset may contain <strong>personally identifiable information (PII)</strong>
      or sensitive data that is subject to GDPR, HIPAA, or equivalent data-protection regulations.<br><br>
      <strong>Flagged column names:</strong> {col_list}<br>
      <strong>Flagged cell patterns:</strong> {cell_detail}<br><br>
      Please ensure you have a lawful basis for processing this data, that data subjects have been
      informed, and that this system is operated in a GDPR-compliant environment.
      Do <em>not</em> upload real personal data unless your organisation's data-processing agreement
      covers this application.
    </div>
    """, unsafe_allow_html=True)


# ─── Data validation ───────────────────────────────────────────────────────────

REQUIRED_DATA_COLUMNS = {"Animal_ID", "Cohort", "Target_Dose_mg_kg", "Actual_Dose_mg_kg"}
REQUIRED_RULES_COLUMNS = {"Assay_Parameter", "Minor_Variance_Limit_Percent", "Major_Variance_Limit_Percent"}

def validate_data_df(df: pd.DataFrame) -> list[str]:
    """Return list of validation error strings; empty list = valid."""
    errors = []
    missing = REQUIRED_DATA_COLUMNS - set(df.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
    if len(df) == 0:
        errors.append("The uploaded file contains no data rows.")
    for col in ("Target_Dose_mg_kg", "Actual_Dose_mg_kg"):
        if col in df.columns and not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"Column '{col}' must be numeric.")
    return errors

def validate_rules_json(rules: dict) -> list[str]:
    """Return list of validation error strings; empty list = valid."""
    errors = []
    if "rules" not in rules:
        errors.append("Rules file must contain a top-level 'rules' key.")
        return errors
    if not isinstance(rules["rules"], list) or len(rules["rules"]) == 0:
        errors.append("The 'rules' list is empty or not a list.")
        return errors
    for i, rule in enumerate(rules["rules"]):
        missing = REQUIRED_RULES_COLUMNS - set(rule.keys())
        if missing:
            errors.append(f"Rule #{i+1} is missing fields: {', '.join(sorted(missing))}")
    return errors


# ─── Process data (vectorized — replaces iterrows loop) ───────────────────────

COHORT_RULE_MAP = {
    "Group_1_Low":     "Body Weight Change",
    "Group_2_Mid":     "Serum Glucose",
    "Group_3_High":    "Heart Rate",
    "Group_4_Control": "Alanine Aminotransferase (ALT)",
}

@st.cache_data(show_spinner=False)
def process_preclinical_data(df_hash: str, df: pd.DataFrame, rules_json: dict, project_id: str) -> pd.DataFrame:
    """
    Fully vectorized compliance processing. df_hash is a stable cache key
    derived from the DataFrame content; it is not used inside the function.
    """
    rules_by_param = {r["Assay_Parameter"]: r for r in rules_json["rules"]}
    fallback_rule   = min(rules_json["rules"], key=lambda r: r["Minor_Variance_Limit_Percent"])

    df = df.copy()
    df["Deviation_Pct"] = (
        (df["Actual_Dose_mg_kg"] - df["Target_Dose_mg_kg"]) / df["Target_Dose_mg_kg"]
    ).abs().mul(100).round(2)

    # Map each row's cohort to its rule parameters (vectorized via map)
    df["_param_name"] = df["Cohort"].map(COHORT_RULE_MAP).fillna(fallback_rule["Assay_Parameter"])

    minor_map = {r["Assay_Parameter"]: r["Minor_Variance_Limit_Percent"] for r in rules_json["rules"]}
    major_map = {r["Assay_Parameter"]: r["Major_Variance_Limit_Percent"] for r in rules_json["rules"]}
    action_map = {r["Assay_Parameter"]: r["Action_Required"] for r in rules_json["rules"]}

    df["_minor"] = df["_param_name"].map(minor_map)
    df["_major"] = df["_param_name"].map(major_map)

    # Vectorized status assignment using numpy.select
    conditions = [
        df["Deviation_Pct"] <= df["_minor"],
        df["Deviation_Pct"] <= df["_major"],
    ]
    df["Status"] = np.select(
        conditions,
        ["INCLUDE", "REVIEW"],
        default="EXCLUDE",
    )
    df["System_Action"] = np.select(
        conditions,
        ["Approved – within acceptable range", df["_param_name"].map(action_map)],
        default="Exclude – exceeds major variance limit",
    )
    df["Applied_Rule"] = df["_param_name"]

    # Drop temp columns
    df.drop(columns=["_param_name", "_minor", "_major"], inplace=True)

    # Stamp each record
    df["Record_ID"] = [new_record_id(project_id) for _ in range(len(df))]
    df["Import_TS"] = now_ts()

    return df


def compute_delta(new_df: pd.DataFrame, prev_df: pd.DataFrame) -> pd.DataFrame:
    """Tag rows that are new vs previously seen (by Animal_ID)."""
    if prev_df is None or prev_df.empty:
        new_df = new_df.copy()
        new_df["Delta"] = "NEW"
        return new_df
    prev_ids = set(prev_df["Animal_ID"].astype(str))
    new_df = new_df.copy()
    new_df["Delta"] = new_df["Animal_ID"].astype(str).apply(
        lambda x: "NEW" if x not in prev_ids else "EXISTING"
    )
    return new_df


def _df_hash(df: pd.DataFrame) -> str:
    """Stable hash of DataFrame content for use as a cache key."""
    return hashlib.md5(pd.util.hash_pandas_object(df, index=True).values.tobytes()).hexdigest()


# ─── Bob 2.0 narrative ────────────────────────────────────────────────────────

_WATSONX_IAM_URL = "https://iam.cloud.ibm.com/identity/token"

# Region → inference base URL map.  Key must match the selectbox option exactly.
_WATSONX_REGIONS = {
    "Dallas (us-south)":   "https://us-south.ml.cloud.ibm.com",
    "London (eu-gb)":      "https://eu-gb.ml.cloud.ibm.com",
    "Frankfurt (eu-de)":   "https://eu-de.ml.cloud.ibm.com",
    "Tokyo (jp-tok)":      "https://jp-tok.ml.cloud.ibm.com",
    "Sydney (au-syd)":     "https://au-syd.ml.cloud.ibm.com",
}
_WATSONX_INFERENCE_PATH = "/ml/v1/text/generation?version=2023-05-29"


def _get_iam_token(api_key: str) -> str:
    """Exchange an IBM Cloud API key for a short-lived IAM bearer token."""
    import requests as _req
    resp = _req.post(
        _WATSONX_IAM_URL,
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=20,
    )
    if not resp.ok:
        raise RuntimeError(
            f"IAM token exchange failed — HTTP {resp.status_code}: {resp.text[:300]}"
        )
    token = resp.json().get("access_token")
    if not token:
        raise RuntimeError("IAM response did not contain an access_token.")
    return token


def generate_narrative(summary: dict, project_id: str, api_key: str, region: str) -> str:
    if not project_id or not api_key:
        return (
            "**[Placeholder — watsonx.ai credentials not configured]**\n\n"
            f"A compliance review of {summary.get('total', 0):,} pre-clinical dosing records was completed. "
            f"{summary.get('include_count', 0):,} records ({summary.get('include_pct', 0):.1f}%) met all acceptance criteria and are cleared for inclusion in the eCTD submission. "
            f"{summary.get('review_count', 0):,} records ({summary.get('review_pct', 0):.1f}%) require scientific review prior to inclusion. "
            f"{summary.get('exclude_count', 0):,} records ({summary.get('exclude_pct', 0):.1f}%) exceeded major variance thresholds and are flagged for exclusion. "
            f"The highest deviation observed was {summary.get('max_deviation_pct', 0):.2f}% in cohort **{summary.get('top_flagged_cohort', 'N/A')}**. "
            f"Rules applied: {', '.join(summary.get('applied_rules', []))}. "
            "This report is auto-generated by RegulatoryGuard AI for traceability purposes."
        )

    base_url  = _WATSONX_REGIONS.get(region, _WATSONX_REGIONS["London (eu-gb)"])
    infer_url = base_url + _WATSONX_INFERENCE_PATH

    # EU-GB fallback: if the London endpoint is unreachable (IBM infrastructure issue),
    # automatically retry via Frankfurt (eu-de) which is also an EU data-residency region.
    _EU_GB_FALLBACK = _WATSONX_REGIONS["Frankfurt (eu-de)"] + _WATSONX_INFERENCE_PATH

    prompt = (
        "You are a regulatory affairs scientist preparing an eCTD Section 2.6 compliance narrative.\n\n"
        f"Pre-clinical dosing compliance summary:\n"
        f"- Total records analysed: {summary['total']:,}\n"
        f"- INCLUDE (within limits): {summary['include_count']:,} ({summary['include_pct']:.1f}%)\n"
        f"- REVIEW REQUIRED: {summary['review_count']:,} ({summary['review_pct']:.1f}%)\n"
        f"- EXCLUDE (exceeds limit): {summary['exclude_count']:,} ({summary['exclude_pct']:.1f}%)\n"
        f"- Maximum deviation observed: {summary['max_deviation_pct']:.2f}%\n"
        f"- Most flagged cohort: {summary['top_flagged_cohort']}\n"
        f"- Assay rules applied: {', '.join(summary['applied_rules'])}\n\n"
        "Write a detailed, professional compliance narrative (4–6 sentences) suitable for inclusion "
        "in a regulatory submission. Cover the overall compliance rate, flagged cohorts, deviation "
        "magnitude, applicable rules, and any risk mitigation considerations. Do not use markdown formatting."
    )

    payload = {
        "model_id": "meta-llama/llama-3-3-70b-instruct",
        "input":      prompt,
        "parameters": {"decoding_method": "greedy", "max_new_tokens": 1024},
        "project_id": project_id,
    }

    import requests as _req

    def _do_post(url: str) -> "_req.Response":
        return _req.post(
            url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type":  "application/json",
                "Accept":        "application/json",
            },
            json=payload,
            timeout=60,
        )

    try:
        token = _get_iam_token(api_key)
    except RuntimeError as exc:
        st.error(f"❌ IAM authentication failed: {exc}")
        return ""

    try:
        resp = _do_post(infer_url)

        # If the primary endpoint returns a server-side error (5xx) AND we are on eu-gb,
        # transparently retry via the Frankfurt fallback before surfacing an error.
        if not resp.ok and resp.status_code >= 500 and region == "London (eu-gb)":
            st.warning(
                f"⚠️ London (eu-gb) endpoint returned HTTP {resp.status_code} — "
                "IBM infrastructure issue detected. Retrying via Frankfurt (eu-de) fallback…"
            )
            resp = _do_post(_EU_GB_FALLBACK)

        if not resp.ok:
            status = resp.status_code
            if status >= 500:
                detail_msg = (
                    f"HTTP {status} — this is an IBM server-side error (not a credentials problem). "
                    "The watsonx.ai endpoint may be temporarily down. Try again in a few minutes, "
                    "or switch the region selector to **Frankfurt (eu-de)**."
                )
            else:
                detail_msg = (
                    f"HTTP {status} — check your Project ID and that your API key has "
                    f"access to the **{region}** instance."
                )
            st.error(f"❌ watsonx.ai returned {detail_msg}\nDetail: {resp.text[:400]}")
            return ""

        data = resp.json()
        # watsonx.ai response shape: {"results": [{"generated_text": "..."}]}
        if "results" in data and data["results"]:
            return data["results"][0].get("generated_text", "").strip()
        return data.get("generated_text", str(data))
    except _req.exceptions.Timeout:
        st.error("❌ watsonx.ai request timed out (60 s). The service may be busy — try again.")
        return ""
    except _req.exceptions.ConnectionError as exc:
        st.error(f"❌ Could not reach watsonx.ai ({infer_url}). Check your network or selected region. Detail: {exc}")
        return ""
    except Exception as exc:
        st.error(f"❌ Unexpected error calling watsonx.ai: {exc}")
        return ""


# ─── Load rules (JSON or CSV→JSON) ────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_rules_from_json(json_bytes: bytes) -> dict:
    return json.loads(json_bytes.decode("utf-8"))

@st.cache_data(show_spinner=False)
def load_rules_from_csv(csv_bytes: bytes) -> dict:
    """Convert uploaded CSV rules to the regulatory_rules.json schema in-memory."""
    import csv as csvmod
    reader = csvmod.DictReader(io.StringIO(csv_bytes.decode("utf-8")))
    rules_list = []
    for row in reader:
        processed = {}
        for k, v in row.items():
            k, v = k.strip(), v.strip()
            try:
                processed[k] = float(v) if "." in v else int(v)
            except ValueError:
                processed[k] = v
        rules_list.append(processed)
    return {"rules_metadata": {"source_file": "uploaded", "total_parameters": len(rules_list)}, "rules": rules_list}


# ─── Badge HTML helper ─────────────────────────────────────────────────────────

def status_badge(status: str) -> str:
    cls = {"INCLUDE": "green", "REVIEW": "yellow", "EXCLUDE": "red"}.get(status, "")
    dot_cls = {"INCLUDE": "green-dot", "REVIEW": "yellow-dot", "EXCLUDE": "red-dot"}.get(status, "")
    # Use eCTD-spec labels in display
    labels = {
        "INCLUDE": "✓ INCLUDE",
        "REVIEW":  "⚠ REVIEW_REQUIRED",
        "EXCLUDE": "✕ EXCLUDE_EXCEPTIONAL",
    }
    label = labels.get(status, status)
    return f'<span class="badge {cls}"><span class="dot {dot_cls}"></span>{label}</span>'


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    # Logo in sidebar
    if os.path.exists("RegulatoryGuard.png"):
        st.image("RegulatoryGuard.png", width=160)
    st.markdown("---")

    # ── Project management ──
    st.markdown('<div class="sidebar-section-title">🗂 Project</div>', unsafe_allow_html=True)

    project_mode = st.radio("", ["New project", "Existing project"], label_visibility="collapsed")

    if project_mode == "New project":
        proj_name = st.text_input("Project name", placeholder="e.g. Study 2024-A")
        proj_desc = st.text_area("Description", placeholder="Brief description…", height=72)
        if st.button("Create Project", use_container_width=True):
            if proj_name.strip():
                pid = new_project_id()
                st.session_state["projects"][pid] = {
                    "name": proj_name.strip(),
                    "description": proj_desc.strip(),
                    "datasets": [],
                }
                st.session_state["active_project"] = pid
                st.success(f"Project created — ID: `{pid}`")
            else:
                st.warning("Please enter a project name.")
    else:
        if st.session_state["projects"]:
            options = {f"{v['name']} ({k})": k for k, v in st.session_state["projects"].items()}
            chosen_label = st.selectbox("Select project", list(options.keys()))
            # Guard against stale selectbox value after concurrent state change
            st.session_state["active_project"] = options.get(chosen_label)
        else:
            st.info("No projects yet. Create one first.")

    st.markdown("---")

    # ── Rules section ──
    st.markdown('<div class="sidebar-section-title">📋 Compliance Rules</div>', unsafe_allow_html=True)

    # Download template — graceful degradation if file missing
    _rules_template_path = "RegulatoryGuardAI_Rules_Example.csv"
    if os.path.exists(_rules_template_path):
        try:
            with open(_rules_template_path, "rb") as _f:
                st.download_button(
                    label="⬇ Download Rules Template",
                    data=_f.read(),
                    file_name="RegulatoryGuardAI_Rules_Example.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        except OSError:
            st.warning("Rules template file could not be read.")
    else:
        st.caption("Rules template not found on disk.")

    uploaded_rules = st.file_uploader(
        "Upload custom rules (CSV or JSON)",
        type=["csv", "json"],
        help="Upload a custom rules file to override the default rulebook.",
    )
    if uploaded_rules:
        raw = uploaded_rules.read()
        try:
            if uploaded_rules.name.endswith(".csv"):
                loaded_rules = load_rules_from_csv(raw)
            else:
                loaded_rules = load_rules_from_json(raw)

            # Validate schema before accepting
            rule_errors = validate_rules_json(loaded_rules)
            if rule_errors:
                for err in rule_errors:
                    st.error(f"Rules file error: {err}")
            else:
                st.session_state["rules_json"] = loaded_rules
                n_rules = len(loaded_rules["rules"])
                st.success(f"✓ {n_rules} rules loaded from `{uploaded_rules.name}`")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            st.error(f"Could not parse rules file '{uploaded_rules.name}'. Please check the file format.")

    # Load default rules if none set
    if st.session_state["rules_json"] is None and os.path.exists("regulatory_rules.json"):
        try:
            with open("regulatory_rules.json") as _jf:
                st.session_state["rules_json"] = json.load(_jf)
        except (OSError, json.JSONDecodeError):
            st.error("Default rules file 'regulatory_rules.json' could not be loaded.")

    st.markdown("---")

    # ── Data section ──
    st.markdown('<div class="sidebar-section-title">📂 Dataset</div>', unsafe_allow_html=True)

    load_mock = st.button("Load Mock Dataset", use_container_width=True)
    if load_mock:
        mock_path = "RegulatoryGuardAI_Test_Records/RegulatoryGuardAI_mock_preclinical_data.csv"
        if os.path.exists(mock_path):
            try:
                df_mock = pd.read_csv(mock_path)
                data_errors = validate_data_df(df_mock)
                if data_errors:
                    for err in data_errors:
                        st.error(f"Mock dataset error: {err}")
                else:
                    st.session_state["raw_data_df"] = df_mock
                    st.success(f"✓ Mock dataset loaded ({len(df_mock):,} records)")
            except Exception:
                st.error("Mock dataset could not be read. The file may be corrupted.")
        else:
            st.error(
                "Mock dataset file not found. "
                "Expected: RegulatoryGuardAI_Test_Records/RegulatoryGuardAI_mock_preclinical_data.csv"
            )

    uploaded_data = st.file_uploader(
        "Upload pre-clinical data (CSV)",
        type=["csv"],
        help="CSV with columns: Animal_ID, Cohort, Target_Dose_mg_kg, Actual_Dose_mg_kg, Notes",
    )
    if uploaded_data:
        try:
            df_up = pd.read_csv(uploaded_data)
        except Exception:
            st.error(f"Could not read '{uploaded_data.name}'. Please ensure it is a valid UTF-8 CSV file.")
            df_up = None

        if df_up is not None:
            data_errors = validate_data_df(df_up)
            if data_errors:
                for err in data_errors:
                    st.error(f"Upload error: {err}")
                st.caption(f"Expected columns: {', '.join(sorted(REQUIRED_DATA_COLUMNS))}")
            else:
                # PII scan
                pii_result = scan_pii(df_up)
                if pii_result["has_pii"]:
                    # Store PII findings so the main area can render the warning
                    st.session_state["_pii_result"] = pii_result
                    st.warning(
                        "⚠ Potential PII detected in upload. "
                        "Review the data-protection notice shown in the main panel."
                    )
                else:
                    st.session_state.pop("_pii_result", None)
                st.session_state["raw_data_df"] = df_up
                st.success(f"✓ Uploaded `{uploaded_data.name}` ({len(df_up):,} records)")

    st.markdown("---")

    # ── Bob 2.0 ──
    st.markdown('<div class="sidebar-section-title">🤖 Bob 2.0 Narrative</div>', unsafe_allow_html=True)
    bob_project_id = st.text_input(
        "watsonx.ai Project ID",
        value=_ENV_PROJECT_ID,
        help="Your IBM watsonx.ai project ID. Set WATSONX_PROJECT_ID in .env to pre-fill.",
    )
    bob_api_key = st.text_input(
        "IBM Cloud API Key",
        value=_ENV_API_KEY,
        type="password",
        help="Your IBM Cloud API key. Set WATSONX_API_KEY in .env to pre-fill.",
    )
    _region_options = list(_WATSONX_REGIONS.keys())
    bob_region = st.selectbox(
        "watsonx.ai Region",
        _region_options,
        index=_region_options.index("London (eu-gb)"),
        help="Select the IBM Cloud region where your watsonx.ai instance is deployed.",
    )
    with st.expander("🔧 Troubleshoot connection", expanded=False):
        st.markdown(
            "**Common causes of narrative errors:**\n"
            "- Wrong region — your watsonx.ai instance must be in the selected region\n"
            "- API key doesn't have `Watson Machine Learning` service access\n"
            "- Project ID mismatch — copy it from **watsonx.ai → your project → Manage → General**\n"
            "- IAM token endpoint unreachable (check firewall / proxy)\n\n"
            "If credentials are correct but the error persists, verify the region is set to **London (eu-gb)**."
        )


# ─── Main header ──────────────────────────────────────────────────────────────

logo_b64 = ""
if os.path.exists("RegulatoryGuard.png"):
    import base64
    try:
        with open("RegulatoryGuard.png", "rb") as _img:
            logo_b64 = base64.b64encode(_img.read()).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="width:64px;height:64px;object-fit:contain;border-radius:10px;">'
    except OSError:
        logo_html = "🛡️"
else:
    logo_html = "🛡️"

active_pid = st.session_state.get("active_project")
if active_pid:
    proj_info = st.session_state["projects"].get(active_pid, {})
    header_sub = f'Project: <strong>{proj_info.get("name","—")}</strong> &nbsp;·&nbsp; ID: <code style="font-size:11px;">{active_pid}</code>'
else:
    header_sub = "No active project — create or select one in the sidebar."

st.markdown(f"""
<div class="rg-header">
  {logo_html}
  <div class="rg-header-text">
    <h1>RegulatoryGuard AI</h1>
    <p>{header_sub}</p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── GDPR consent notice (always visible) ─────────────────────────────────────

with st.expander("🔒 Data Privacy & GDPR Notice", expanded=False):
    st.markdown("""
    **RegulatoryGuard AI — Data Protection Notice**

    This tool is designed for pre-clinical, non-personal research data only. Before uploading any data, please confirm:

    - ✅ The dataset does **not** contain personal data about identifiable individuals (names, SSNs, dates of birth, email addresses, etc.).
    - ✅ Your organisation has an applicable Data Processing Agreement (DPA) in place if real personal data must be processed.
    - ✅ All data subjects have been appropriately informed in accordance with **GDPR Articles 13 & 14**.
    - ✅ You have a lawful basis (Article 6) for any processing that may occur.

    Data uploaded to this session is held **in-memory only** and is not persisted to disk or transmitted to third parties,
    except when the Bob 2.0 narrative endpoint is configured (statistical summaries only — no raw records are sent).

    For questions about data protection, contact your organisation's Data Protection Officer (DPO).
    """)

# ─── PII warning banner (shown if scan flagged the current dataset) ───────────

_pii_result = st.session_state.get("_pii_result")
if _pii_result:
    render_pii_warning(_pii_result)

# ─── Active project guard ──────────────────────────────────────────────────────

if not active_pid:
    st.info("👈 Create or select a project in the sidebar to begin.")
    st.stop()


# ─── Run compliance check ─────────────────────────────────────────────────────

raw_df = st.session_state.get("raw_data_df")
rules  = st.session_state.get("rules_json")

col_run, col_export, col_narrative, _ = st.columns([1.6, 1.4, 1.4, 3])

with col_run:
    run_clicked = st.button("▶  Run Compliance Check", use_container_width=True)

if run_clicked:
    if raw_df is None:
        st.warning("Please load or upload a dataset first.")
    elif rules is None:
        st.warning("No rules loaded. Check that 'regulatory_rules.json' exists or upload a custom rules file.")
    else:
        # Validate data before processing
        data_errors = validate_data_df(raw_df)
        if data_errors:
            for err in data_errors:
                st.error(f"Data validation failed: {err}")
        else:
            with st.spinner("Running compliance engine…"):
                prev_df = st.session_state.get("results_df")

                # Use content hash as cache key so re-runs on unchanged data are instant
                cache_key = _df_hash(raw_df)
                result = process_preclinical_data(cache_key, raw_df, rules, active_pid)
                result = compute_delta(result, prev_df)

                # Archive previous import
                if prev_df is not None and not prev_df.empty:
                    st.session_state["previous_df"] = prev_df.copy()

                st.session_state["results_df"] = result
                st.session_state["narrative_text"] = None  # reset on new run

                # Record import metadata — guard against project being removed
                if active_pid in st.session_state["projects"]:
                    import_meta = {
                        "import_id":   new_record_id(active_pid),
                        "timestamp":   now_ts(),
                        "records":     len(result),
                        "new_records": int((result["Delta"] == "NEW").sum()),
                        "project_id":  active_pid,
                    }
                    st.session_state["import_history"].append(import_meta)
                    st.session_state["projects"][active_pid]["datasets"].append(import_meta)

            st.success(f"✓ Compliance check complete — {len(result):,} records processed.")

results_df = st.session_state.get("results_df")

# ─── Executive summary ────────────────────────────────────────────────────────

if results_df is not None and not results_df.empty:

    total   = len(results_df)
    n_inc   = int((results_df["Status"] == "INCLUDE").sum())
    n_rev   = int((results_df["Status"] == "REVIEW").sum())
    n_exc   = int((results_df["Status"] == "EXCLUDE").sum())
    n_new   = int((results_df["Delta"] == "NEW").sum()) if "Delta" in results_df.columns else total

    pct_inc = n_inc / total * 100
    pct_rev = n_rev / total * 100
    pct_exc = n_exc / total * 100

    max_dev = results_df["Deviation_Pct"].max()
    top_cohort = (
        results_df[results_df["Status"] == "EXCLUDE"]["Cohort"].value_counts().idxmax()
        if n_exc > 0 else "—"
    )

    st.markdown('<div id="exec-summary"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Executive Summary</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card blue">
        <div class="kpi-label">Total Records</div>
        <div class="kpi-value">{total:,}</div>
        <div class="kpi-sub">+{n_new:,} new this import</div>
      </div>
      <div class="kpi-card green">
        <div class="kpi-label">✓ Include</div>
        <div class="kpi-value">{n_inc:,}</div>
        <div class="kpi-sub">{pct_inc:.1f}% of total</div>
      </div>
      <div class="kpi-card yellow">
        <div class="kpi-label">⚠ Review</div>
        <div class="kpi-value">{n_rev:,}</div>
        <div class="kpi-sub">{pct_rev:.1f}% of total</div>
      </div>
      <div class="kpi-card red">
        <div class="kpi-label">✕ Exclude</div>
        <div class="kpi-value">{n_exc:,}</div>
        <div class="kpi-sub">{pct_exc:.1f}% of total</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Distribution charts ────────────────────────────────────────────────────
    st.markdown('<div id="distribution"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Distribution Analysis</div>', unsafe_allow_html=True)

    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
        st.markdown("**Status Distribution**")
        chart_data = pd.DataFrame({
            "Status": ["INCLUDE", "REVIEW", "EXCLUDE"],
            "Count":  [n_inc, n_rev, n_exc],
        })
        st.bar_chart(chart_data.set_index("Status")["Count"])

    with chart_col2:
        st.markdown("**Deviation % by Cohort**")
        cohort_dev = results_df.groupby("Cohort")["Deviation_Pct"].mean().reset_index()
        cohort_dev.columns = ["Cohort", "Mean Deviation %"]
        st.bar_chart(cohort_dev.set_index("Cohort"))

    with chart_col3:
        st.markdown("**Deviation % Histogram**")
        bins = pd.cut(results_df["Deviation_Pct"], bins=[0, 2, 5, 10, 15, 100],
                      labels=["0–2%", "2–5%", "5–10%", "10–15%", ">15%"])
        hist_data = bins.value_counts().sort_index()
        st.bar_chart(hist_data)

    # ── Delta summary ──────────────────────────────────────────────────────────
    if "Delta" in results_df.columns and n_new < total:
        n_existing = total - n_new
        st.markdown(
            f'<div class="surface-panel">'
            f'<strong>Import delta:</strong> &nbsp;'
            f'<span class="delta-new">+{n_new} NEW</span> &nbsp; '
            f'<span class="delta-same">{n_existing} EXISTING</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Filtered data viewer ───────────────────────────────────────────────────
    st.markdown('<div id="data-viewer"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Interactive Data Viewer</div>', unsafe_allow_html=True)

    filter_col1, filter_col2, filter_col3 = st.columns([1.5, 1.5, 2])
    with filter_col1:
        status_filter = st.multiselect(
            "Filter by status",
            ["INCLUDE", "REVIEW", "EXCLUDE"],
            default=["INCLUDE", "REVIEW", "EXCLUDE"],
        )
    with filter_col2:
        cohort_filter = st.multiselect(
            "Filter by cohort",
            sorted(results_df["Cohort"].unique().tolist()),
            default=sorted(results_df["Cohort"].unique().tolist()),
        )
    with filter_col3:
        search_term = st.text_input("Search Animal ID / Notes", placeholder="e.g. A0042 or 'handling'")

    filtered = results_df[
        results_df["Status"].isin(status_filter) &
        results_df["Cohort"].isin(cohort_filter)
    ]
    if search_term:
        mask = (
            filtered["Animal_ID"].astype(str).str.contains(search_term, case=False, na=False) |
            filtered.get("Notes", pd.Series(dtype=str)).astype(str).str.contains(search_term, case=False, na=False)
        )
        filtered = filtered[mask]

    total_filtered = len(filtered)
    PAGE_SIZE = 200
    max_page   = max(1, (total_filtered - 1) // PAGE_SIZE + 1)

    page_col, caption_col = st.columns([1, 4])
    with page_col:
        page_num = st.number_input(
            "Page",
            min_value=1,
            max_value=max_page,
            value=1,
            step=1,
            help=f"Showing {PAGE_SIZE} rows per page",
        )
    with caption_col:
        st.caption(
            f"Showing {min(PAGE_SIZE, total_filtered):,} of {total_filtered:,} filtered records "
            f"(page {page_num}/{max_page}) — {total:,} total"
        )

    page_start  = (page_num - 1) * PAGE_SIZE
    page_slice  = filtered.iloc[page_start : page_start + PAGE_SIZE]

    # Render with HTML badges for Status column (paginated — avoids rendering all 3000+ rows)
    display_cols = ["Record_ID", "Animal_ID", "Cohort", "Target_Dose_mg_kg", "Actual_Dose_mg_kg",
                    "Deviation_Pct", "Status", "System_Action", "Applied_Rule"]
    if "Delta" in filtered.columns:
        display_cols.append("Delta")
    display_cols = [c for c in display_cols if c in page_slice.columns]

    badge_df = page_slice[display_cols].copy()
    badge_df["Status"] = badge_df["Status"].apply(status_badge)

    st.markdown(
        badge_df.to_html(escape=False, index=False, classes="dataframe", border=0),
        unsafe_allow_html=True,
    )

    # ── Export ─────────────────────────────────────────────────────────────────
    st.markdown("---")
    export_col1, export_col2 = st.columns([1, 5])
    with export_col1:
        csv_bytes = results_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇ Export eCTD Package (CSV)",
            data=csv_bytes,
            file_name=f"audit_ready_report_{active_pid}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # ── Bob 2.0 narrative panel ────────────────────────────────────────────────
    st.markdown('<div id="narrative"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Bob 2.0 Narrative Generation</div>', unsafe_allow_html=True)

    applied_rules_list = sorted(results_df["Applied_Rule"].unique().tolist()) if "Applied_Rule" in results_df.columns else []

    summary = {
        "total":            total,
        "include_count":    n_inc,
        "review_count":     n_rev,
        "exclude_count":    n_exc,
        "include_pct":      pct_inc,
        "review_pct":       pct_rev,
        "exclude_pct":      pct_exc,
        "max_deviation_pct": float(max_dev),
        "top_flagged_cohort": top_cohort,
        "applied_rules":    applied_rules_list,
    }

    with col_narrative:
        gen_clicked = st.button("🤖  Generate Narrative", use_container_width=True)

    if gen_clicked or (st.session_state.get("narrative_text") and gen_clicked is False):
        if gen_clicked:
            with st.spinner("Generating compliance narrative…"):
                narrative = generate_narrative(summary, bob_project_id, bob_api_key, bob_region)
                st.session_state["narrative_text"] = narrative

    narrative_text = st.session_state.get("narrative_text")
    if narrative_text:
        is_placeholder = narrative_text.startswith("**[Placeholder")
        label = "Placeholder Narrative (configure Bob 2.0 credentials for AI generation)" if is_placeholder else "Bob 2.0 — AI-Generated Compliance Narrative"
        st.markdown(f"""
        <div class="narrative-card">
          <div class="narrative-label">{label}</div>
          {narrative_text}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="surface-panel" style="text-align:center; color:#94A3B8; padding: 32px;">
          Click <strong>"🤖 Generate Narrative"</strong> to produce an eCTD-ready compliance paragraph.
        </div>
        """, unsafe_allow_html=True)

    # ── Phase 3: Human-in-the-Loop Review Portal ──────────────────────────────
    st.markdown('<div id="review-portal"></div>', unsafe_allow_html=True)
    st.markdown("---")

    # Identify flagged records (REVIEW_REQUIRED = yellow, EXCLUDE_EXCEPTIONAL = red)
    flagged_mask = results_df["Status"].isin(["REVIEW", "EXCLUDE"])
    flagged_df   = results_df[flagged_mask].copy().reset_index(drop=True)
    n_flagged    = len(flagged_df)
    n_review_req = int((flagged_df["Status"] == "REVIEW").sum())
    n_exc_excpt  = int((flagged_df["Status"] == "EXCLUDE").sum())

    # Live decision counts from session state
    _decisions = st.session_state["review_decisions"]
    _all_acts  = [v["action"] for v in _decisions.values()]
    _n_pending   = n_flagged - sum(1 for a in _all_acts if a != "Pending") - max(0, n_flagged - len(_decisions))
    _n_approved  = _all_acts.count("Approve Exception")
    _n_rejected  = _all_acts.count("Reject / Isolate")
    _n_override  = _all_acts.count("Override")
    _n_decided   = _n_approved + _n_rejected + _n_override

    st.markdown(f"""
    <div class="review-portal-header">
      <div>
        <h2>🔍 Phase 3 — Human-in-the-Loop Review Portal</h2>
        <p>
          Select a decision for each flagged record — changes are saved instantly. &nbsp;
          <span class="review-stat-pill yellow">⚠ {n_review_req} REVIEW_REQUIRED</span> &nbsp;
          <span class="review-stat-pill red">✕ {n_exc_excpt} EXCLUDE_EXCEPTIONAL</span> &nbsp;
          <span class="review-stat-pill blue">✓ {_n_decided}/{n_flagged} decided</span>
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if n_flagged == 0:
        st.success("✓ No flagged records — all records are within acceptance limits.")
    else:
        # ── Filter controls ────────────────────────────────────────────────────
        rp_col1, rp_col2, rp_col3 = st.columns([1.4, 1.4, 2])
        with rp_col1:
            rp_status_filter = st.multiselect(
                "Filter by flag type",
                ["REVIEW_REQUIRED", "EXCLUDE_EXCEPTIONAL"],
                default=["REVIEW_REQUIRED", "EXCLUDE_EXCEPTIONAL"],
                key="rp_status_filter",
            )
        with rp_col2:
            rp_cohort_filter = st.multiselect(
                "Filter by cohort",
                sorted(flagged_df["Cohort"].unique().tolist()),
                default=sorted(flagged_df["Cohort"].unique().tolist()),
                key="rp_cohort_filter",
            )
        with rp_col3:
            rp_search = st.text_input(
                "Search Animal ID / Notes",
                placeholder="e.g. A0042",
                key="rp_search",
            )

        # Apply filters
        _d2i = {"REVIEW_REQUIRED": "REVIEW", "EXCLUDE_EXCEPTIONAL": "EXCLUDE"}
        _int_filter = [_d2i[s] for s in rp_status_filter if s in _d2i]
        portal_df = flagged_df[
            flagged_df["Status"].isin(_int_filter) &
            flagged_df["Cohort"].isin(rp_cohort_filter)
        ].copy()
        if rp_search:
            _smask = (
                portal_df["Animal_ID"].astype(str).str.contains(rp_search, case=False, na=False) |
                portal_df.get("Notes", pd.Series(dtype=str)).astype(str).str.contains(rp_search, case=False, na=False)
            )
            portal_df = portal_df[_smask]

        st.caption(f"Showing **{len(portal_df):,}** of {n_flagged:,} flagged record(s).")

        _action_options = ["Pending", "Approve Exception", "Reject / Isolate", "Override"]
        _action_colors  = {
            "Pending":           "#94A3B8",
            "Approve Exception": "#10B981",
            "Reject / Isolate":  "#EF4444",
            "Override":          "#F59E0B",
        }

        # ── Per-row review cards ───────────────────────────────────────────────
        # Each card holds: context info (read-only) | action dropdown | comment box
        # Any widget change triggers an immediate st.rerun() via on_change callback,
        # persisting that record's decision before the page refreshes.

        def _save_decision(record_id: str, action_key: str, comment_key: str) -> None:
            """on_change callback — fires instantly when dropdown or text changes."""
            st.session_state["review_decisions"][record_id] = {
                "action":    st.session_state[action_key],
                "comment":   st.session_state.get(comment_key, ""),
                "saved_at":  datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

        for _, row in portal_df.iterrows():
            rid        = row["Record_ID"]
            animal     = row["Animal_ID"]
            cohort     = row["Cohort"]
            dev_pct    = row["Deviation_Pct"]
            flag_type  = "⚠ REVIEW_REQUIRED" if row["Status"] == "REVIEW" else "✕ EXCLUDE_EXCEPTIONAL"
            flag_color = "#F59E0B" if row["Status"] == "REVIEW" else "#EF4444"
            sys_action = row.get("System_Action", "—")
            rule       = row.get("Applied_Rule", "—")

            saved      = _decisions.get(rid, {})
            cur_action = saved.get("action", "Pending")
            cur_comment= saved.get("comment", "")
            saved_at   = saved.get("saved_at", "")

            # Unique widget keys per record
            _ak = f"ra_{rid}"   # action key
            _ck = f"rc_{rid}"   # comment key

            # Initialise widget state on first render (prevents stale default)
            if _ak not in st.session_state:
                st.session_state[_ak] = cur_action
            if _ck not in st.session_state:
                st.session_state[_ck] = cur_comment

            _action_color = _action_colors.get(cur_action, "#94A3B8")
            _border_style = f"border-left: 4px solid {flag_color};"

            with st.container():
                st.markdown(
                    f'<div style="background:#F8FAFC; {_border_style} border-radius:10px; '
                    f'padding:14px 18px 6px 18px; margin-bottom:4px;">'
                    f'<span style="font-size:13px; font-weight:700; color:{flag_color};">{flag_type}</span>'
                    f'&nbsp;&nbsp;'
                    f'<span style="font-size:13px; font-weight:600; color:#0F172A;">Animal: {animal}</span>'
                    f'&nbsp;·&nbsp;'
                    f'<span style="font-size:12px; color:#475569;">Cohort: {cohort}</span>'
                    f'&nbsp;·&nbsp;'
                    f'<span style="font-size:12px; color:#475569;">Deviation: <strong>{dev_pct:.2f}%</strong></span>'
                    f'&nbsp;·&nbsp;'
                    f'<span style="font-size:11px; color:#94A3B8;">Rule: {rule}</span>'
                    f'&nbsp;·&nbsp;'
                    f'<span style="font-size:11px; color:#94A3B8;">System: {sys_action}</span>'
                    + (f'&nbsp;&nbsp;<span style="font-size:10px; color:#22C55E;">✓ saved {saved_at}</span>' if saved_at else "")
                    + '</div>',
                    unsafe_allow_html=True,
                )

                c_action, c_comment = st.columns([1, 3])

                with c_action:
                    st.selectbox(
                        "Decision",
                        options=_action_options,
                        key=_ak,
                        label_visibility="collapsed",
                        on_change=_save_decision,
                        args=(rid, _ak, _ck),
                    )

                with c_comment:
                    _comment_placeholder = (
                        "Required: add audit justification for Approve Exception / Override…"
                        if cur_action in ("Approve Exception", "Override")
                        else "Optional: add investigator note for audit trail…"
                    )
                    st.text_input(
                        "Comment",
                        key=_ck,
                        placeholder=_comment_placeholder,
                        label_visibility="collapsed",
                        on_change=_save_decision,
                        args=(rid, _ak, _ck),
                    )

                # Inline warning if comment is missing for decisions that require it
                if cur_action in ("Approve Exception", "Override") and not cur_comment.strip():
                    st.warning(
                        f"⚠ A reviewer comment is required for **{cur_action}** decisions.",
                        icon=None,
                    )

            st.markdown("<div style='margin-bottom:6px'></div>", unsafe_allow_html=True)

        # ── Live decision summary bar ──────────────────────────────────────────
        st.markdown(
            f"**Decision progress:** &nbsp;"
            f'<span class="review-stat-pill blue">{n_flagged - _n_decided} Pending</span> &nbsp;'
            f'<span class="review-stat-pill yellow">{_n_approved} Approved</span> &nbsp;'
            f'<span class="review-stat-pill red">{_n_rejected} Rejected</span> &nbsp;'
            f'<span class="review-stat-pill blue">{_n_override} Override</span>',
            unsafe_allow_html=True,
        )

    # ── Finalize & Export eCTD Audit Package ──────────────────────────────────
    st.markdown('<div id="export"></div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<div class="section-heading">📦 Finalize & Export eCTD Audit Package</div>', unsafe_allow_html=True)

    # Recalculate after any decisions saved this run
    _decisions_now    = st.session_state["review_decisions"]
    _n_with_decision  = sum(1 for v in _decisions_now.values() if v.get("action", "Pending") != "Pending")
    _n_still_pending  = n_flagged - _n_with_decision
    _missing_comment  = [
        rid for rid, v in _decisions_now.items()
        if v.get("action") in ("Approve Exception", "Override") and not v.get("comment", "").strip()
    ]

    if _n_still_pending > 0 or _missing_comment:
        _issues = []
        if _n_still_pending > 0:
            _issues.append(f"{_n_still_pending} record(s) still Pending")
        if _missing_comment:
            _issues.append(f"{len(_missing_comment)} decision(s) missing a required comment")
        st.markdown(
            f'<div class="finalize-info" style="background:#FFF7ED;border-color:#F97316;color:#7C2D12;">'
            f'<strong>⚠ {" · ".join(_issues)}.</strong> '
            f'You may still export — incomplete records will appear as-is in the audit package. '
            f'For a submission-ready eCTD package, resolve all outstanding items above.'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="finalize-info">'
            '<strong>✓ All flagged records have been reviewed and commented.</strong> '
            'Ready to finalize the eCTD audit package for Section 4.2.3 submission.'
            '</div>',
            unsafe_allow_html=True,
        )

    finalize_col, _ = st.columns([1.8, 4])
    with finalize_col:
        finalize_clicked = st.button(
            "📦  Finalize & Export eCTD Audit Package",
            use_container_width=True,
            key="finalize_export_btn",
        )

    if finalize_clicked:
        _export_ts       = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        _decisions_store = st.session_state["review_decisions"]

        audit_df = results_df.copy()

        # Surface eCTD-spec label in the export
        audit_df["Compliance_Status"] = audit_df["Status"].map(
            {"INCLUDE": "INCLUDE", "REVIEW": "REVIEW_REQUIRED", "EXCLUDE": "EXCLUDE_EXCEPTIONAL"}
        ).fillna(audit_df["Status"])

        # Merge human review decisions (all records; INCLUDE rows get "N/A")
        def _get_field(rid, field, fallback):
            v = _decisions_store.get(rid, {})
            return v.get(field, fallback)

        audit_df["Review_Action"]    = audit_df.apply(
            lambda r: _get_field(r["Record_ID"], "action", "N/A" if r["Status"] == "INCLUDE" else "Pending"), axis=1
        )
        audit_df["Reviewer_Comment"] = audit_df["Record_ID"].apply(
            lambda rid: _get_field(rid, "comment", "")
        )
        audit_df["Review_Timestamp"] = audit_df["Record_ID"].apply(
            lambda rid: _get_field(rid, "saved_at", "")
        )
        audit_df["Export_Timestamp"] = _export_ts
        audit_df["Package_Version"]  = f"eCTD-s4.2.3-{active_pid}"

        _audit_csv = audit_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="⬇  Download final_audited_preclinical_report.csv",
            data=_audit_csv,
            file_name="final_audited_preclinical_report.csv",
            mime="text/csv",
            use_container_width=False,
            key="download_audit_csv",
        )
        st.success(
            f"✓ eCTD audit package ready — {len(audit_df):,} records, "
            f"exported at {_export_ts}. Download the file above."
        )

    # ── Import history ─────────────────────────────────────────────────────────
    if st.session_state["import_history"]:
        with st.expander("📜 Import History"):
            hist_df = pd.DataFrame(st.session_state["import_history"])
            st.dataframe(hist_df, use_container_width=True)

else:
    # No results yet — show call-to-action
    st.markdown("""
    <div class="surface-panel" style="text-align:center; padding: 52px 32px;">
      <div style="font-size:40px; margin-bottom:12px;">🛡️</div>
      <div style="font-size:18px; font-weight:700; color:#0F172A; margin-bottom:8px;">
        Ready to run compliance analysis
      </div>
      <div style="color:#475569; max-width:480px; margin:0 auto;">
        Load the mock dataset or upload your own pre-clinical CSV, then click
        <strong>"▶ Run Compliance Check"</strong> to begin.
      </div>
    </div>
    """, unsafe_allow_html=True)

    with col_export:
        st.download_button(
            "⬇ Export eCTD Package",
            data=b"No results yet.",
            file_name="audit_ready_report.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=True,
        )


# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:48px; padding-top:18px;
            border-top:1px solid #E2E8F0; font-size:12px; color:#94A3B8;">
  RegulatoryGuard AI &nbsp;·&nbsp; IBM Bob 2.0 Hackathon MVP &nbsp;·&nbsp;
  Pre-clinical compliance engine
</div>
""", unsafe_allow_html=True)

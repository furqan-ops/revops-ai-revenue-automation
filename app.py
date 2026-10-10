import streamlit as st
import json
import time
import traceback
from datetime import date
from pathlib import Path
from backend_scoring import process_lead

st.set_page_config(
    page_title="Lead Scoring Pipeline - RevOps Workspace",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injected CSS translating v0 globals.css design decisions into Streamlit
st.markdown("""
<style>
    /* Global Base */
    .stApp {
        background-color: #f7f8fa !important;
        color: #111827 !important;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    }

    /* Completely hide Streamlit default header, toolbar, and sidebar */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    div[data-testid="collapsedControl"] {
        display: none !important;
    }
    div[data-testid="stToolbar"] {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }

    .block-container {
        max-width: 1240px !important;
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* Topbar Shell */
    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 14px 24px;
        margin-bottom: 24px;
        box-shadow: 0 1px 2px rgba(17, 24, 39, 0.02);
    }
    .brand-mark {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-wordmark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 5px 9px;
        border-radius: 6px;
        background: #111827;
        color: #ffffff;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: -0.01em;
    }
    .brand-title {
        font-weight: 650;
        font-size: 15px;
        color: #111827;
        letter-spacing: -0.01em;
        line-height: 1.2;
    }
    .brand-context {
        display: block;
        color: #9ca3af;
        font-size: 11px;
        margin-top: 2px;
    }
    .topbar-meta {
        color: #6b7280;
        font-size: 12px;
        font-weight: 500;
    }

    /* Page Heading */
    .page-heading {
        margin-bottom: 24px;
    }
    .eyebrow {
        margin: 0 0 4px 0;
        color: #6b7280;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .heading-title {
        font-size: 24px;
        line-height: 1.2;
        letter-spacing: -0.03em;
        font-weight: 650;
        color: #111827;
        margin: 0;
    }
    .subheading {
        margin-top: 6px;
        color: #6b7280;
        font-size: 13px;
        line-height: 1.5;
    }

    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 24px;
    }
    .stat-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px 18px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 1px 2px rgba(17, 24, 39, 0.02);
    }
    .stat-card::before {
        content: '';
        position: absolute;
        inset: 0 auto 0 0;
        width: 3px;
    }
    .stat-card-1::before { background: #2563eb; }
    .stat-card-2::before { background: #7c3aed; }
    .stat-card-3::before { background: #059669; }
    .stat-card-label {
        color: #6b7280;
        font-size: 12px;
        margin: 0;
    }
    .stat-card-val {
        display: block;
        margin: 6px 0 4px 0;
        font-size: 24px;
        line-height: 1;
        font-variant-numeric: tabular-nums;
        font-weight: 650;
        color: #111827;
    }
    .stat-card-helper {
        color: #9ca3af;
        font-size: 11px;
    }

    /* Pipeline Stepper */
    .pipeline-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 20px 22px;
        margin-bottom: 24px;
        box-shadow: 0 1px 2px rgba(17, 24, 39, 0.02);
    }
    .pipeline-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .pipeline-header h2 {
        font-size: 16px;
        font-weight: 650;
        letter-spacing: -0.01em;
        margin: 0;
        color: #111827;
    }
    .pipeline-header div[data-testid="stDownloadButton"] button {
        background-color: #ffffff !important;
        color: #374151 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 12px !important;
        padding: 6px 14px !important;
        transition: all 0.15s !important;
    }
    .pipeline-header div[data-testid="stDownloadButton"] button:hover {
        background-color: #f9fafb !important;
        border-color: #9ca3af !important;
        color: #111827 !important;
    }
    .steps-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
    }
    .step-item {
        display: flex;
        align-items: center;
        position: relative;
        flex: 1;
    }
    .step-item:not(:last-child)::after {
        content: '';
        height: 1px;
        background: #d1d5db;
        position: absolute;
        left: 32px;
        right: 12px;
        top: 13px;
        z-index: 0;
    }
    .step-circle {
        width: 27px;
        height: 27px;
        border: 1px solid #d1d5db;
        color: #6b7280;
        background: #ffffff;
        border-radius: 50%;
        display: grid;
        place-items: center;
        font-size: 11px;
        font-weight: 600;
        position: relative;
        z-index: 1;
        flex: 0 0 auto;
    }
    .step-circle.complete {
        color: #047857;
        background: #ecfdf5;
        border-color: #a7f3d0;
    }
    .step-circle.pending {
        color: #9ca3af;
        background: #f3f4f6;
        border-color: #e5e7eb;
    }
    .step-info {
        display: flex;
        flex-direction: column;
        gap: 2px;
        margin-left: 9px;
        background: #ffffff;
        padding-right: 12px;
        position: relative;
        z-index: 1;
    }
    .step-info b {
        font-size: 12px;
        font-weight: 600;
        color: #111827;
        white-space: nowrap;
    }
    .step-info small {
        color: #6b7280;
        font-size: 11px;
        white-space: nowrap;
    }

    /* Panels / Cards */
    .panel {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 22px 24px;
        box-shadow: 0 1px 2px rgba(17, 24, 39, 0.02);
        height: 100%;
    }
    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .panel-header h2 {
        font-size: 16px;
        font-weight: 650;
        letter-spacing: -0.01em;
        margin: 0;
        color: #111827;
    }

    /* Empty state box */
    .empty-state-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 220px;
        text-align: center;
        color: #6b7280;
        border: 1px dashed #d1d5db;
        border-radius: 6px;
        background: #fafbfc;
        padding: 24px;
    }
    .empty-state-box p {
        margin: 0;
        font-size: 13px;
    }

    /* Score Header */
    .score-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 4px 0 20px 0;
    }
    .score-value {
        display: flex;
        align-items: baseline;
        gap: 4px;
        font-variant-numeric: tabular-nums;
    }
    .score-value strong {
        font-size: 40px;
        letter-spacing: -0.06em;
        line-height: 1;
        color: #111827;
        font-weight: 700;
    }
    .score-value span {
        color: #9ca3af;
        font-size: 14px;
    }
    .tier-pill {
        border-radius: 999px;
        padding: 4px 9px;
        font-size: 11px;
        font-weight: 650;
    }
    .tier-1 { color: #047857; background: #ecfdf5; }
    .tier-2 { color: #b45309; background: #fffbeb; }
    .tier-3 { color: #374151; background: #f3f4f6; }

    /* Breakdown Progress Bars */
    .breakdown-row {
        margin-bottom: 14px;
    }
    .breakdown-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 6px;
        color: #4b5563;
        font-size: 12px;
    }
    .breakdown-label b {
        font-weight: 600;
        color: #111827;
        font-variant-numeric: tabular-nums;
    }
    .progress-track {
        height: 6px;
        background: #eef0f3;
        border-radius: 999px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background: #2563eb;
        border-radius: inherit;
    }

    /* Rationale & Callout */
    .rationale-block {
        margin-top: 22px;
        padding-top: 16px;
        border-top: 1px solid #f0f1f3;
    }
    .rationale-block h3 {
        font-size: 13px;
        font-weight: 650;
        color: #111827;
        margin: 0 0 6px 0;
    }
    .rationale-block p {
        color: #4b5563;
        font-size: 13px;
        line-height: 1.55;
        margin: 0;
    }
    .approach-callout {
        margin-top: 16px;
        padding: 13px 15px;
        border-left: 2px solid #d1d5db;
        background: #f9fafb;
        border-radius: 0 6px 6px 0;
    }
    .approach-callout h3 {
        font-size: 13px;
        font-weight: 650;
        color: #111827;
        margin: 0 0 4px 0;
    }
    .approach-callout p {
        color: #4b5563;
        font-size: 13px;
        line-height: 1.55;
        margin: 0;
    }

    /* Records & Tabs Container */
    .records-panel {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 22px 24px;
        box-shadow: 0 1px 2px rgba(17, 24, 39, 0.02);
        margin-top: 24px;
    }

    /* Tables */
    .table-row {
        display: grid;
        grid-template-columns: 180px 1fr;
        padding: 10px 0;
        border-bottom: 1px solid #f0f1f3;
    }
    .table-row:last-child {
        border-bottom: 0;
    }
    .table-row span {
        color: #6b7280;
        font-size: 12px;
    }
    .table-row b {
        font-weight: 500;
        font-size: 13px;
        color: #111827;
    }

    /* Code Panels */
    .code-panel {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        overflow: hidden;
        background: #f8fafc;
        margin-bottom: 12px;
    }
    .code-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 14px;
        background: #f3f4f6;
        border-bottom: 1px solid #e5e7eb;
    }
    .code-header b {
        font-size: 12px;
        color: #111827;
    }
    .code-header span {
        color: #6b7280;
        font-size: 11px;
        margin-left: 8px;
    }
    .code-header small {
        background: #e5e7eb;
        color: #4b5563;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 11px;
    }
    .code-panel pre {
        padding: 12px 14px;
        margin: 0;
        overflow-x: auto;
        color: #374151;
        font: 12px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace;
    }

    /* Slack Preview */
    .slack-message {
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        padding: 18px 20px;
        background: #ffffff;
    }
    .slack-top {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
    }
    .slack-top b {
        font-size: 13px;
        color: #111827;
    }
    .slack-top span {
        color: #6b7280;
        font-size: 11px;
    }
    .slack-body {
        color: #374151;
        font-size: 13px;
        line-height: 1.6;
    }
    .slack-link {
        display: inline-block;
        color: #2563eb;
        font-size: 13px;
        margin-top: 12px;
        text-decoration: underline;
        font-weight: 500;
    }
    .slack-empty {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #6b7280;
        font-size: 13px;
        padding: 16px;
        border: 1px solid #e5e7eb;
        border-radius: 6px;
        background: #f9fafb;
    }

    /* Streamlit widget restyling */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border: 1px solid #d1d5db !important;
        border-radius: 6px !important;
        color: #111827 !important;
        font-size: 13px !important;
    }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12) !important;
    }
    div[data-testid="stButton"] button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: 0 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        padding: 9px 16px !important;
        transition: background 0.15s !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #1d4ed8 !important;
    }

    /* Active tab styling: Blue accent #2563EB text, border, and highlight indicator (zero red) */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #6b7280 !important;
        padding: 10px 16px !important;
        background: transparent !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #2563eb !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #2563eb !important;
        border-bottom-color: #2563eb !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #2563eb !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-highlight"] {
        background-color: #2563eb !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-border"] {
        background-color: #e5e7eb !important;
    }

    /* Form Label Styling */
    label[data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin-bottom: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# Data loading - strictly identical to baseline
ROOT_DIR = Path(__file__).parent
DATA_FILE = ROOT_DIR / "mock_data" / "test_leads.json"
FIRM_FILE = ROOT_DIR / "mock_data" / "firmographics_db.json"
WORKFLOW_FILE = ROOT_DIR / "workflows" / "step5_full_revops_pipeline.json"

@st.cache_data
def load_datasets():
    leads = []
    firms = {}
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            leads = json.load(f)
    if FIRM_FILE.exists():
        with open(FIRM_FILE, "r", encoding="utf-8") as f:
            firms = json.load(f)
    return leads, firms

leads_data, firms_data = load_datasets()

# 1. Topbar with Wordmark RevOps, Date, and no demo/operational pills (Item 1)
current_date_str = date.today().strftime("%B %d, %Y")

st.markdown(f"""
<header class="topbar">
    <div class="brand-mark">
        <span class="brand-wordmark">RevOps</span>
        <div>
            <div class="brand-title">Lead Scoring Pipeline</div>
            <span class="brand-context">Revenue operations workspace</span>
        </div>
    </div>
    <div class="topbar-meta">
        <span>{current_date_str}</span>
    </div>
</header>
""", unsafe_allow_html=True)

# 2. Page Heading (Item 2)
st.markdown("""
<section class="page-heading">
    <p class="eyebrow">Revenue operations</p>
    <h1 class="heading-title">Inbound lead scoring</h1>
    <p class="subheading">Scores inbound leads on four weighted criteria and routes each one to Slack, the SDR queue, or the audit log.</p>
</section>
""", unsafe_allow_html=True)

# Scenario selection & form setup
scenario_options = [
    "Tier 1: Enterprise Buyer — Sarah Jenkins (CloudScale Systems)",
    "Tier 2: Mid-Market Prospect — David Miller (Growth Digital Agency)",
    "Tier 3: Disqualified Inquiry — Alex K (Freelance / Personal Gmail)"
]

# Track scenario selection to sync form fields
if "selected_scenario_idx" not in st.session_state:
    st.session_state["selected_scenario_idx"] = 0

# Track neutral start state (Item 3)
# Policy: Keep the last result until the user clicks 'Run scoring' again, allowing review while modifying inputs.
if "has_run" not in st.session_state:
    st.session_state["has_run"] = False
if "last_result" not in st.session_state:
    st.session_state["last_result"] = None
if "measured_duration_ms" not in st.session_state:
    st.session_state["measured_duration_ms"] = None
if "validation_status" not in st.session_state:
    st.session_state["validation_status"] = None
if "field_errors" not in st.session_state:
    st.session_state["field_errors"] = {}

# 3. Workspace Grid (Two Columns: Lead input on Left, Scoring result on Right)
col_left, col_right = st.columns([1.05, 0.95], gap="large")

with col_left:
    # Lead input header with 'Sample leads' label (Item 4 & 6)
    st.markdown("""
    <div class="panel-header" style="margin-bottom: 8px;">
        <h2>Lead input</h2>
        <span class="stat-card-helper">Sample leads</span>
    </div>
    """, unsafe_allow_html=True)

    selected_scenario_str = st.selectbox(
        "Select Scenario:",
        scenario_options,
        index=st.session_state["selected_scenario_idx"],
        label_visibility="collapsed"
    )
    new_scenario_idx = scenario_options.index(selected_scenario_str)

    # Sync fields if user switches scenario dropdown
    if new_scenario_idx != st.session_state["selected_scenario_idx"]:
        st.session_state["selected_scenario_idx"] = new_scenario_idx
        scenario_lead = leads_data[new_scenario_idx]["payload"] if leads_data else {}
        st.session_state["field_first_name"] = scenario_lead.get("first_name", "")
        st.session_state["field_last_name"] = scenario_lead.get("last_name", "")
        st.session_state["field_work_email"] = scenario_lead.get("work_email", "")
        st.session_state["field_job_title"] = scenario_lead.get("job_title", "")
        st.session_state["field_company_name"] = scenario_lead.get("company_name", "")
        st.session_state["field_company_size"] = scenario_lead.get("company_size", "")
        st.session_state["field_company_website"] = scenario_lead.get("company_website", "")
        st.session_state["field_message"] = scenario_lead.get("message", "")
        st.session_state["field_errors"] = {}
        st.session_state["validation_status"] = None

    current_lead = leads_data[st.session_state["selected_scenario_idx"]]["payload"] if leads_data else {}

    # Initialize field state if first load
    if "field_first_name" not in st.session_state:
        st.session_state["field_first_name"] = current_lead.get("first_name", "")
        st.session_state["field_last_name"] = current_lead.get("last_name", "")
        st.session_state["field_work_email"] = current_lead.get("work_email", "")
        st.session_state["field_job_title"] = current_lead.get("job_title", "")
        st.session_state["field_company_name"] = current_lead.get("company_name", "")
        st.session_state["field_company_size"] = current_lead.get("company_size", "")
        st.session_state["field_company_website"] = current_lead.get("company_website", "")
        st.session_state["field_message"] = current_lead.get("message", "")

    form_c1, form_c2 = st.columns(2)
    with form_c1:
        first_name = st.text_input("First name", value=st.session_state["field_first_name"])
        st.session_state["field_first_name"] = first_name
        if "first_name" in st.session_state["field_errors"]:
            st.markdown(f"<p style='color: #dc2626; font-size: 11px; margin-top: -8px; margin-bottom: 6px;'>{st.session_state['field_errors']['first_name']}</p>", unsafe_allow_html=True)

        work_email = st.text_input("Work email", value=st.session_state["field_work_email"])
        st.session_state["field_work_email"] = work_email
        if "work_email" in st.session_state["field_errors"]:
            st.markdown(f"<p style='color: #dc2626; font-size: 11px; margin-top: -8px; margin-bottom: 6px;'>{st.session_state['field_errors']['work_email']}</p>", unsafe_allow_html=True)

        company_name = st.text_input("Company name", value=st.session_state["field_company_name"])
        st.session_state["field_company_name"] = company_name

        company_size = st.text_input("Company size", value=st.session_state["field_company_size"])
        st.session_state["field_company_size"] = company_size

    with form_c2:
        last_name = st.text_input("Last name", value=st.session_state["field_last_name"])
        st.session_state["field_last_name"] = last_name
        if "last_name" in st.session_state["field_errors"]:
            st.markdown(f"<p style='color: #dc2626; font-size: 11px; margin-top: -8px; margin-bottom: 6px;'>{st.session_state['field_errors']['last_name']}</p>", unsafe_allow_html=True)

        job_title = st.text_input("Job title", value=st.session_state["field_job_title"])
        st.session_state["field_job_title"] = job_title

        company_website = st.text_input("Website", value=st.session_state["field_company_website"])
        st.session_state["field_company_website"] = company_website

    message = st.text_area("Inbound message", value=st.session_state["field_message"], height=100)
    st.session_state["field_message"] = message
    if "message" in st.session_state["field_errors"]:
        st.markdown(f"<p style='color: #dc2626; font-size: 11px; margin-top: -8px; margin-bottom: 6px;'>{st.session_state['field_errors']['message']}</p>", unsafe_allow_html=True)

    action_c1, action_c2 = st.columns([1.5, 1])
    with action_c2:
        run_scoring = st.button("Run scoring", use_container_width=True)

    # Item 5: Validation checks run only upon clicking "Run scoring"
    if run_scoring:
        errors = {}
        if not first_name.strip():
            errors["first_name"] = "First name is required."
        if not last_name.strip():
            errors["last_name"] = "Last name is required."
        email_clean = work_email.strip()
        if not email_clean or "@" not in email_clean:
            errors["work_email"] = "Work email must contain '@' followed by a domain with a dot."
        else:
            domain_part = email_clean.split("@")[-1]
            if "." not in domain_part or not domain_part.split(".")[-1]:
                errors["work_email"] = "Work email must contain '@' followed by a domain with a dot."
        if not message.strip():
            errors["message"] = "Inbound message is required."

        st.session_state["field_errors"] = errors

        if errors:
            st.session_state["validation_status"] = "invalid"
        else:
            st.session_state["validation_status"] = "valid"
            # Build current lead input dictionary
            lead_input_dict = {
                "first_name": first_name.strip(),
                "last_name": last_name.strip(),
                "work_email": work_email.strip(),
                "job_title": job_title.strip(),
                "company_name": company_name.strip(),
                "company_size": company_size.strip(),
                "company_website": company_website.strip(),
                "message": message.strip()
            }

            # Item 11: Error handling wrapping process_lead()
            try:
                t_start = time.perf_counter()
                computed_res = process_lead(lead_input_dict, firms_data)
                measured_ms = (time.perf_counter() - t_start) * 1000
                st.session_state["last_result"] = computed_res
                st.session_state["measured_duration_ms"] = measured_ms
                st.session_state["has_run"] = True
            except Exception as e:
                traceback.print_exc()
                st.error("Scoring could not be completed. Check the inputs and try again.")

    with action_c1:
        if st.session_state["validation_status"] == "valid":
            st.markdown("<p style='color: #059669; font-size: 11px; margin-top: 10px; font-weight: 500;'>All inputs valid</p>", unsafe_allow_html=True)
        elif st.session_state["validation_status"] == "invalid":
            st.markdown("<p style='color: #dc2626; font-size: 11px; margin-top: 10px; font-weight: 500;'>Please correct errors above</p>", unsafe_allow_html=True)

res = st.session_state.get("last_result")
has_run = st.session_state.get("has_run", False) and res is not None

# Right Column: Scoring result panel (Neutral state or populated, Item 3, 5, 6, 9)
with col_right:
    if not has_run:
        st.markdown("""
        <div class="panel">
            <div class="panel-header">
                <h2>Scoring result</h2>
                <span class="stat-card-helper">Rule-based scoring</span>
            </div>
            <div class="empty-state-box">
                <p>Select a lead and run scoring to see the result.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="panel">
            <div class="panel-header">
                <h2>Scoring result</h2>
                <span class="stat-card-helper">Rule-based scoring</span>
            </div>
            <div class="score-header">
                <div class="score-value">
                    <strong>{res['total_score']}</strong><span>/ 100</span>
                </div>
                <span class="tier-pill {res['tier_class']}">{res['tier']}</span>
            </div>
            <div class="breakdown">
                <div class="breakdown-row">
                    <div class="breakdown-label">
                        <span>Firmographic fit</span><b>{res['f_score']} / 30</b>
                    </div>
                    <div class="progress-track"><div class="progress-fill" style="width: {(res['f_score']/30)*100}%;"></div></div>
                </div>
                <div class="breakdown-row">
                    <div class="breakdown-label">
                        <span>Persona and authority</span><b>{res['a_score']} / 30</b>
                    </div>
                    <div class="progress-track"><div class="progress-fill" style="width: {(res['a_score']/30)*100}%;"></div></div>
                </div>
                <div class="breakdown-row">
                    <div class="breakdown-label">
                        <span>Problem alignment</span><b>{res['p_score']} / 30</b>
                    </div>
                    <div class="progress-track"><div class="progress-fill" style="width: {(res['p_score']/30)*100}%;"></div></div>
                </div>
                <div class="breakdown-row">
                    <div class="breakdown-label">
                        <span>Budget and timing</span><b>{res['b_score']} / 10</b>
                    </div>
                    <div class="progress-track"><div class="progress-fill" style="width: {(res['b_score']/10)*100}%;"></div></div>
                </div>
            </div>
            <div class="rationale-block">
                <h3>Rationale</h3>
                <p>{res['rationale']}</p>
            </div>
            <div class="approach-callout">
                <h3>Suggested first-call approach</h3>
                <p>"{res['sales_hook']}"</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 4. Stat cards (Item 6)
latency_display = f"{st.session_state['measured_duration_ms']:.2f} ms" if (has_run and st.session_state.get('measured_duration_ms') is not None) else "&mdash;"

st.markdown(f"""
<section class="stats-grid" style="margin-top: 24px;">
    <article class="stat-card stat-card-1">
        <p class="stat-card-label">Test leads</p>
        <strong class="stat-card-val">3</strong>
        <span class="stat-card-helper">Built-in sample set</span>
    </article>
    <article class="stat-card stat-card-2">
        <p class="stat-card-label">Scoring time</p>
        <strong class="stat-card-val">{latency_display}</strong>
        <span class="stat-card-helper">Scoring function only, local run.</span>
    </article>
    <article class="stat-card stat-card-3">
        <p class="stat-card-label">Tier 1 share</p>
        <strong class="stat-card-val">33%</strong>
        <span class="stat-card-helper">1 of 3 test leads</span>
    </article>
</section>
""", unsafe_allow_html=True)

# 5. Pipeline Stepper Card with step-specific status text & download button (Item 7 & 9)
enrichment_text = "Firmographics matched" if (has_run and res.get('email_domain') in firms_data) else "Fallback profile used"
step1_sub = "Lead received" if has_run else "Waiting"
step2_sub = enrichment_text if has_run else "Waiting"
step3_sub = f"Score {res['total_score']}" if has_run else "Waiting"
step4_sub = "Payloads built" if has_run else "Waiting"
step5_sub = f"{res['action']}" if has_run else "Waiting"

circle_cls = "complete" if has_run else "pending"
circle_icon = "&#10003;" if has_run else ""

st.markdown("""
<section class="pipeline-card">
    <div class="pipeline-header">
        <div>
            <p class="eyebrow" style="margin: 0 0 2px 0;">Workflow status</p>
            <h2>Pipeline status</h2>
        </div>
""", unsafe_allow_html=True)

# Secondary download button aligned inside pipeline status header (Item 9)
c_hdr_left, c_hdr_btn = st.columns([3, 1])
with c_hdr_btn:
    if WORKFLOW_FILE.exists():
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow_content = f.read()
        st.download_button(
            label="Download workflow JSON",
            data=workflow_content,
            file_name="master_revops_pipeline.json",
            mime="application/json",
            use_container_width=True
        )

st.markdown(f"""
    </div>
    <div class="steps-container">
        <div class="step-item">
            <span class="step-circle {circle_cls}">{circle_icon or '1'}</span>
            <div class="step-info">
                <b>Inbound intake</b>
                <small style="color: {'#6b7280' if has_run else '#9ca3af'};">{step1_sub}</small>
            </div>
        </div>
        <div class="step-item">
            <span class="step-circle {circle_cls}">{circle_icon or '2'}</span>
            <div class="step-info">
                <b>Enrichment</b>
                <small style="color: {'#6b7280' if has_run else '#9ca3af'};">{step2_sub}</small>
            </div>
        </div>
        <div class="step-item">
            <span class="step-circle {circle_cls}">{circle_icon or '3'}</span>
            <div class="step-info">
                <b>AI scoring</b>
                <small style="color: {'#6b7280' if has_run else '#9ca3af'};">{step3_sub}</small>
            </div>
        </div>
        <div class="step-item">
            <span class="step-circle {circle_cls}">{circle_icon or '4'}</span>
            <div class="step-info">
                <b>CRM sync</b>
                <small style="color: {'#6b7280' if has_run else '#9ca3af'};">{step4_sub}</small>
            </div>
        </div>
        <div class="step-item">
            <span class="step-circle {circle_cls}">{circle_icon or '5'}</span>
            <div class="step-info">
                <b>Routing and alerts</b>
                <small style="color: {'#6b7280' if has_run else '#9ca3af'};">{step5_sub}</small>
            </div>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# 6. Records Section (Tabs) (Item 3 & 8)
tab_enrichment, tab_crm, tab_slack = st.tabs(["Company enrichment", "CRM records", "Slack alert"])

with tab_enrichment:
    if not has_run:
        st.markdown("""
        <div class="records-panel" style="text-align: center; color: #6b7280; padding: 36px 24px;">
            <p style="margin: 0; font-size: 13px;">Run scoring to see results here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="records-panel">
            <div class="table-row">
                <span>Company</span><b>{res['enriched'].get('name', 'N/A')}</b>
            </div>
            <div class="table-row">
                <span>Industry</span><b>{res['enriched'].get('industry', 'N/A')}</b>
            </div>
            <div class="table-row">
                <span>Headcount</span><b>{res['enriched'].get('employee_count', 'N/A')} ({res['enriched'].get('employee_range', '')})</b>
            </div>
            <div class="table-row">
                <span>Annual revenue</span><b>{res['enriched'].get('estimated_annual_revenue', 'N/A')}</b>
            </div>
            <div class="table-row">
                <span>Headquarters</span><b>{res['enriched'].get('headquarters', 'N/A')}</b>
            </div>
            <div class="table-row">
                <span>Tech stack</span><b>{", ".join(res['enriched'].get('tech_stack', [])) if res['enriched'].get('tech_stack') else "None detected"}</b>
            </div>
            <div class="table-row">
                <span>Domain type</span><b>{"Consumer email" if res['is_free'] else "Corporate business domain"}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

with tab_crm:
    if not has_run:
        st.markdown("""
        <div class="records-panel" style="text-align: center; color: #6b7280; padding: 36px 24px;">
            <p style="margin: 0; font-size: 13px;">Run scoring to see results here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="records-panel">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
                <div class="code-panel">
                    <div class="code-header">
                        <div><b>Contact</b><span>/crm/v3/objects/contacts</span></div>
                        <small>{len(res['contact_payload'])} properties</small>
                    </div>
                    <pre>{json.dumps(res['contact_payload'], indent=2)}</pre>
                </div>
                <div class="code-panel">
                    <div class="code-header">
                        <div><b>Company</b><span>/crm/v3/objects/companies</span></div>
                        <small>{len(res['company_payload'])} properties</small>
                    </div>
                    <pre>{json.dumps(res['company_payload'], indent=2)}</pre>
                </div>
            </div>
            <p style="color: #6b7280; font-size: 12px; margin-top: 14px; margin-bottom: 0;">
                Linked via contact-to-company association endpoint (/crm/v3/associations/contacts/companies).
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab_slack:
    if not has_run:
        st.markdown("""
        <div class="records-panel" style="text-align: center; color: #6b7280; padding: 36px 24px;">
            <p style="margin: 0; font-size: 13px;">Run scoring to see results here.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        if res['total_score'] >= 80:
            st.markdown(f"""
            <div class="records-panel"><div class="slack-message">
                <div class="slack-top"><b>#sales-inbound-leads</b><span>Inbound Router Bot &middot; just now</span></div>
                <div class="slack-body">
                    <p><strong>[ALERT] New {res['tier']} lead:</strong> {res['first_name']} {res['last_name']} at {res['enriched'].get('name')}</p>
                    <p><strong>Score:</strong> {res['total_score']}/100 &middot; <strong>Role:</strong> {res['job_title']}</p>
                    <p><strong>Projected ARR:</strong> {res['deal_arr']} &middot; <strong>Assigned AE:</strong> Alex Vance (Round-Robin)</p>
                    <p><em>"{res['sales_hook']}"</em></p>
                    <a class="slack-link" href="#crm-records">View deal in HubSpot CRM (#hs_deal_894129)</a>
                </div>
            </div></div>
            """, unsafe_allow_html=True)
        elif res['total_score'] >= 50:
            st.markdown(f"""
            <div class="records-panel"><div class="slack-empty">
                <span>{res['sdr_queue_text']}</span>
            </div></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="records-panel"><div class="slack-empty">
                <span>{res['audit_log_text']}</span>
            </div></div>
            """, unsafe_allow_html=True)

# 7. Small gray footer (Item 10)
st.markdown("""
<footer style="margin-top: 48px; padding-top: 16px; border-top: 1px solid #e5e7eb; text-align: center; color: #9ca3af; font-size: 12px;">
    v1.0 &middot; Rule-based scoring engine
</footer>
""", unsafe_allow_html=True)

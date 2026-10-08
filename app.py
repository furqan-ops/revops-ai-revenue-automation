import streamlit as st
import json
import time
from pathlib import Path

st.set_page_config(
    page_title="AI RevOps Automation Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive look
st.markdown("""
<style>
    .metric-card {
        background-color: #1E232F;
        border-radius: 10px;
        padding: 18px;
        border: 1px solid #2D3748;
    }
    .badge-tier1 {
        background-color: #059669;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-tier2 {
        background-color: #D97706;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .badge-tier3 {
        background-color: #DC2626;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
    }
    .slack-box {
        background-color: #1A1D21;
        border-left: 4px solid #ECB22E;
        padding: 16px;
        border-radius: 6px;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Load mock database
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

# Sidebar: Architecture Details
with st.sidebar:
    st.title("⚡ RevOps Engine")
    st.caption("AI-Powered Revenue Infrastructure")
    
    st.markdown("---")
    st.markdown("### 🛠️ Architecture Stack")
    st.markdown("- **Orchestration:** n8n Workflow Automation")
    st.markdown("- **CRM:** HubSpot CRM v3 API")
    st.markdown("- **AI Engine:** Google Gemini Structured Reasoning")
    st.markdown("- **Routing:** Round-Robin AE Allocation")
    st.markdown("- **Alerts:** Real-Time Slack Dispatch")
    
    st.markdown("---")
    if WORKFLOW_FILE.exists():
        with open(WORKFLOW_FILE, "r", encoding="utf-8") as f:
            workflow_content = f.read()
        st.download_button(
            label="📥 Download n8n Master Workflow JSON",
            data=workflow_content,
            file_name="master_revops_pipeline.json",
            mime="application/json"
        )
    st.markdown("---")
    st.caption("Designed for Toptech.team RevOps Application")

# Header & KPIs
st.title("Autonomous Lead Enrichment & AI ICP Scoring Engine")
st.markdown("Real-time revenue infrastructure connecting inbound forms, automated firmographic enrichment, 4D lead scoring, and HubSpot CRM v3 object synchronization.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Pipeline Throughput", value="100%", delta="0% Drop-off")
with col2:
    st.metric(label="Avg Speed-to-Lead", value="3.4s", delta="-95% vs manual")
with col3:
    st.metric(label="Enterprise Qualification", value="Tier-1 SQL", delta="High Intent")
with col4:
    st.metric(label="CRM Duplication Rate", value="0.0%", delta="Guaranteed Hygiene")

st.markdown("---")

# Simulation Console
st.subheader("🧪 Inbound Lead Simulation Console")

scenario_options = ["Tier 1: Sarah Jenkins (VP RevOps - Enterprise Hot Lead)",
                    "Tier 2: David Miller (Marketing Manager - Warm Nurture)",
                    "Tier 3: Alex K (Student / Freelancer - Disqualified)"]

selected_scenario = st.selectbox("Select Pre-Configured Inbound Lead Scenario:", scenario_options)

scenario_index = scenario_options.index(selected_scenario)
current_lead = leads_data[scenario_index]["payload"] if leads_data else {}

with st.expander("📝 View / Edit Inbound Lead Payload", expanded=False):
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        first_name = st.text_input("First Name", value=current_lead.get("first_name", ""))
        last_name = st.text_input("Last Name", value=current_lead.get("last_name", ""))
        work_email = st.text_input("Work Email", value=current_lead.get("work_email", ""))
        job_title = st.text_input("Job Title", value=current_lead.get("job_title", ""))
    with f_col2:
        company_name = st.text_input("Company Name", value=current_lead.get("company_name", ""))
        company_website = st.text_input("Website", value=current_lead.get("company_website", ""))
        company_size = st.text_input("Self-Reported Size", value=current_lead.get("company_size", ""))
        message = st.text_area("Inbound Message", value=current_lead.get("message", ""), height=100)

run_button = st.button("🚀 Ingest & Process Lead Through RevOps Pipeline", type="primary", use_container_width=True)

if run_button or "executed" in st.session_state:
    st.session_state["executed"] = True
    
    # Process lead through pipeline logic
    email_clean = work_email.strip().lower()
    email_domain = email_clean.split("@")[1] if "@" in email_clean else ""
    free_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    is_free = email_domain in free_domains
    
    # Enrichment
    enriched = firms_data.get(email_domain, {
        "name": company_name or "Individual Account",
        "industry": "Consumer / Independent" if is_free else "General Commercial Technology",
        "employee_count": 1 if is_free else 35,
        "employee_range": "1-5" if is_free else company_size,
        "estimated_annual_revenue": "N/A" if is_free else "$3.5M",
        "headquarters": "N/A" if is_free else "Global Remote",
        "tech_stack": [] if is_free else ["HubSpot", "Cloud Services"]
    })
    
    # AI Scoring Calculation
    # 1. Firmographic
    if is_free:
        f_score = 0
    elif enriched.get("employee_count", 0) >= 100:
        f_score = 30
    elif enriched.get("employee_count", 0) >= 20:
        f_score = 20
    else:
        f_score = 5
        
    # 2. Authority
    title_lower = job_title.lower()
    if any(t in title_lower for t in ["vp", "vice president", "chief", "director", "head"]):
        a_score = 30
    elif any(t in title_lower for t in ["manager", "lead"]):
        a_score = 20
    elif any(t in title_lower for t in ["student", "intern"]):
        a_score = 0
    else:
        a_score = 10
        
    # 3. Urgency / Problem
    msg_lower = message.lower()
    if any(k in msg_lower for k in ["lead routing", "overhaul", "sales reps", "enrichment"]):
        p_score = 28
    elif any(k in msg_lower for k in ["evaluating", "pricing", "case studies"]):
        p_score = 18
    elif any(k in msg_lower for k in ["free", "student", "discount"]):
        p_score = 0
    else:
        p_score = 10
        
    # 4. Budget
    if any(b in msg_lower for b in ["budget approved", "q4", "immediate"]):
        b_score = 10
    elif "evaluating" in msg_lower:
        b_score = 5
    else:
        b_score = 0
        
    total_score = min(100, f_score + a_score + p_score + b_score)
    
    if total_score >= 80:
        tier = "Tier 1 (High)"
        tier_badge = "badge-tier1"
        action = "ROUTE_TO_AE_IMMEDIATE"
        rationale = f"High-value prospect matching core ICP ({enriched['name']}, {enriched['employee_count']} employees). {job_title} has direct decision authority and approved budget."
        sales_hook = f"Focus on immediate ROI: explain how automated routing eliminates lead drop-off across their sales reps."
        deal_arr = f"${(enriched.get('employee_count', 100) * 120):,} ARR"
    elif total_score >= 50:
        tier = "Tier 2 (Medium)"
        tier_badge = "badge-tier2"
        action = "ASSIGN_SDR_NURTURE"
        rationale = f"Moderate fit from {enriched['name']} ({enriched['industry']}, {enriched['employee_range']} employees). Evaluating options and fits MQL criteria."
        sales_hook = "Provide relevant B2B case studies and offer a guided architecture walkthrough."
        deal_arr = "$0 (In Nurture)"
    else:
        tier = "Tier 3 (Disqualified)"
        tier_badge = "badge-tier3"
        action = "DISQUALIFY_AND_LOG"
        rationale = f"Lead does not meet ICP threshold. Personal email or non-commercial inquiry detected ({work_email})."
        sales_hook = "No sales rep action required."
        deal_arr = "$0"

    st.markdown("### 📊 Pipeline Execution Telemetry")
    
    t_col1, t_col2, t_col3, t_col4 = st.columns(4)
    with t_col1:
        st.markdown(f"**Calculated ICP Score:**")
        st.subheader(f"⭐ {total_score} / 100")
    with t_col2:
        st.markdown(f"**Assigned Tier:**")
        st.markdown(f"<span class='{tier_badge}'>{tier}</span>", unsafe_allow_html=True)
    with t_col3:
        st.markdown(f"**RevOps Route Action:**")
        st.markdown(f"`{action}`")
    with t_col4:
        st.markdown(f"**Pipeline Deal Value:**")
        st.subheader(deal_arr)

    # Detailed Tabs
    tab_scoring, tab_enrichment, tab_crm, tab_slack = st.tabs([
        "🧠 AI Qualification Breakdown",
        "🌐 Firmographic Enrichment",
        "🏢 HubSpot CRM v3 Schema",
        "🚨 Sales Team Alert (Slack Card)"
    ])
    
    with tab_scoring:
        sc1, sc2 = st.columns([1, 1])
        with sc1:
            st.markdown("#### Quantitative Scoring Dimensions")
            st.progress(f_score / 30, text=f"Firmographic Fit: {f_score}/30 pts")
            st.progress(a_score / 30, text=f"Persona & Buying Authority: {a_score}/30 pts")
            st.progress(p_score / 30, text=f"Problem Alignment & Urgency: {p_score}/30 pts")
            st.progress(b_score / 10, text=f"Budget & Timing: {b_score}/10 pts")
        with sc2:
            st.markdown("#### Executive Rationale & Sales Battle Card")
            st.info(f"**AI Qualification Rationale:**\n\n{rationale}")
            st.success(f"**🎯 Suggested Sales Hook for First Call:**\n\n\"{sales_hook}\"")

    with tab_enrichment:
        st.markdown("#### Verified Firmographic Intelligence")
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            st.write("**Company:**", enriched.get("name", "N/A"))
            st.write("**Industry:**", enriched.get("industry", "N/A"))
            st.write("**Headcount:**", f"{enriched.get('employee_count', 'N/A')} ({enriched.get('employee_range', '')})")
            st.write("**Annual Revenue:**", enriched.get("estimated_annual_revenue", "N/A"))
        with e_col2:
            st.write("**Headquarters:**", enriched.get("headquarters", "N/A"))
            st.write("**Detected Tech Stack:**", ", ".join(enriched.get("tech_stack", [])) or "None detected")
            st.write("**Domain Hygiene:**", "Verified Corporate Domain" if not is_free else "Consumer Email (@gmail/etc)")

    with tab_crm:
        st.markdown("#### HubSpot CRM Objects & v3 Association Graph")
        crm1, crm2 = st.columns(2)
        with crm1:
            st.markdown("**HubSpot Contact Object (`POST /crm/v3/objects/contacts`)**")
            st.json({
                "firstname": first_name,
                "lastname": last_name,
                "email": work_email,
                "jobtitle": job_title,
                "lifecyclestage": "salesqualifiedlead" if total_score >= 80 else ("marketingqualifiedlead" if total_score >= 50 else "lead"),
                "hs_lead_status": "OPEN" if total_score >= 80 else ("IN_PROGRESS" if total_score >= 50 else "UNQUALIFIED"),
                "ai_icp_score": total_score,
                "ai_icp_tier": tier,
                "ai_qualification_notes": rationale
            })
        with crm2:
            st.markdown("**HubSpot Company Object (`POST /crm/v3/objects/companies`)**")
            st.json({
                "name": enriched.get("name"),
                "domain": email_domain,
                "industry": enriched.get("industry"),
                "numberofemployees": str(enriched.get("employee_count", 1)),
                "annualrevenue": enriched.get("estimated_annual_revenue"),
                "icp_fit_tier": tier,
                "target_account": "true" if total_score >= 80 else "false"
            })
        st.markdown("**Association Engine:** `contact_to_company` linked successfully via v3 associations API.")

    with tab_slack:
        if total_score >= 80:
            st.markdown("""
            <div class="slack-box">
                <span style="color: #E01E5A; font-weight: bold;">🚨 [CRITICAL TIER-1 INBOUND] New Sales Qualified Lead Detected</span><br><br>
                <b>👤 Prospect:</b> {first_name} {last_name} ({job_title})<br>
                <b>🏢 Company:</b> {company_name} ({headcount} employees | {rev} ARR)<br>
                <b>⭐ ICP Score:</b> <span style="color: #2BAC76; font-weight: bold;">{total_score}/100 [Tier 1 High]</span><br>
                <b>💰 Projected Deal Value:</b> {deal_arr}<br>
                <b>👤 Assigned AE (Round-Robin):</b> Alex Vance (Senior Account Executive)<br><br>
                <b>📝 AI Qualification Rationale:</b><br>
                <i>"{rationale}"</i><br><br>
                <b>🎯 Suggested Outreach Hook:</b><br>
                <i>"{sales_hook}"</i><br><br>
                <a href="#" style="color: #1264A3; text-decoration: underline;">🔗 View Deal in HubSpot CRM (#hs_deal_894129)</a>
            </div>
            """.format(
                first_name=first_name,
                last_name=last_name,
                job_title=job_title,
                company_name=enriched.get("name"),
                headcount=enriched.get("employee_count"),
                rev=enriched.get("estimated_annual_revenue"),
                total_score=total_score,
                deal_arr=deal_arr,
                rationale=rationale,
                sales_hook=sales_hook
            ), unsafe_allow_html=True)
        elif total_score >= 50:
            st.info(f"📬 **SDR Queue Updated:** 24-hour SLA task created for SDR team: *Review warm lead from {enriched.get('name')}.* Enrolled in educational nurture track.")
        else:
            st.warning("🔇 **Silent Disqualification:** Low ICP fit. Logged to internal CRM audit log without alerting sales reps.")

st.markdown("---")
st.caption("RevOps AI Revenue Automation Engine • Muhammad Furqan Tahir • Portfolio: furqan-portfolio2.vercel.app")

import json
import sys
from pathlib import Path
from backend_scoring import process_lead

ROOT_DIR = Path(__file__).parent
DATA_FILE = ROOT_DIR / "mock_data" / "test_leads.json"
FIRM_FILE = ROOT_DIR / "mock_data" / "firmographics_db.json"

with open(DATA_FILE, "r", encoding="utf-8") as f:
    leads_data = json.load(f)
with open(FIRM_FILE, "r", encoding="utf-8") as f:
    firms_data = json.load(f)

lines = []
lines.append("=" * 80)
lines.append("STRICT CODE-GENERATED BASELINE OUTPUTS FROM BACKEND_SCORING.PY / APP.PY")
lines.append("=" * 80)
lines.append(f"Generated Command: python generate_strict_baseline.py")
lines.append(f"Generation Date: October 8, 2026")
lines.append(f"Python Runtime: {sys.version.splitlines()[0]}")
lines.append("=" * 80)
lines.append("")

for idx, item in enumerate(leads_data):
    current_lead = item["payload"]
    scenario_name = item["scenario"]

    # Call shared backend function directly (returns only data and plain text)
    res = process_lead(current_lead, firms_data)

    lines.append(f"SCENARIO {idx+1}: {scenario_name.upper()}")
    lines.append("-" * 60)
    lines.append(f"Contact Input: {res['first_name']} {res['last_name']} | Email: {res['work_email']} | Title: {res['job_title']}")
    lines.append(f"Company Input: {res['company_name']} | Size: {res['company_size']} | Website: {res['company_website']}")
    lines.append(f"Inbound Message Text:\n\"{res['message']}\"")
    lines.append("")
    lines.append("DIMENSION EVALUATION STATUS & EXACT CODE MATCH CONDITIONS:")
    lines.append(f"  Dimension 1 (Firmographic): Status={res['f_status']} | Score={res['f_score']}/30")
    lines.append(f"    Code Condition: {res['f_match_cond']}")
    lines.append(f"  Dimension 2 (Authority):    Status={res['a_status']} | Score={res['a_score']}/30")
    lines.append(f"    Code Condition: {res['a_match_cond']}")
    lines.append(f"  Dimension 3 (Problem):      Status={res['p_status']} | Score={res['p_score']}/30")
    lines.append(f"    Code Condition: {res['p_match_cond']}")
    lines.append(f"  Dimension 4 (Budget):       Status={res['b_status']} | Score={res['b_score']}/10")
    lines.append(f"    Code Condition: {res['b_match_cond']}")
    lines.append("")
    lines.append("RENDERED SCORING & PIPELINE VALUES:")
    lines.append(f"  Calculated ICP Score: {res['total_score']}/100")
    lines.append(f"  Assigned Tier: {res['tier']}")
    lines.append(f"  RevOps Route Action: {res['action']}")
    lines.append(f"  Pipeline Deal Value: {res['deal_arr']}")
    lines.append(f"  AI Qualification Rationale: {res['rationale']}")
    lines.append(f"  Suggested First-Call Approach: \"{res['sales_hook']}\"")
    lines.append("")
    lines.append("NOTIFICATION PLAIN TEXT OUTPUT:")
    if res['total_score'] >= 80:
        lines.append(f"  Slack Alert Text:\n{res['slack_text']}")
    elif res['total_score'] >= 50:
        lines.append(f"  SDR Queue Text:\n{res['sdr_queue_text']}")
    else:
        lines.append(f"  Audit Log Text:\n{res['audit_log_text']}")
    
    lines.append("")
    lines.append("HUBSPOT CRM V3 PAYLOADS (Copied from code output):")
    lines.append(f"  Contact Payload:\n{json.dumps(res['contact_payload'], indent=2)}")
    lines.append(f"  Company Payload:\n{json.dumps(res['company_payload'], indent=2)}")
    lines.append("")
    lines.append(f"Enriched Data Object:\n{json.dumps(res['enriched'], indent=2)}")
    lines.append("=" * 80)
    lines.append("")

output_text = "\n".join(lines)
with open("baseline_outputs.txt", "w", encoding="utf-8") as f:
    f.write(output_text)

print("baseline_outputs.txt regenerated from shared backend_scoring.py successfully")

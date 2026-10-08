import os
import json
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

DATA_FILE = Path(__file__).parent / "mock_data" / "test_leads.json"

ICP_RUBRIC_PROMPT = """
You are an expert enterprise RevOps Revenue Automation Analyst.
Evaluate the inbound lead dossier against our B2B Ideal Customer Profile (ICP).

SCORING CRITERIA (0 - 100 points total):
1. Firmographic Fit (0-30 pts):
   - 30 pts: B2B SaaS, DevOps, Cloud Infrastructure, Tech, 50-1000 employees.
   - 15-20 pts: Mid-market agencies, professional services, 20-50 employees.
   - 0 pts: Personal, student, or non-commercial accounts.
2. Persona & Buying Authority (0-30 pts):
   - 30 pts: VP, Director, Head of RevOps / Sales / Growth / Engineering.
   - 15-20 pts: Managers, Team Leads.
   - 0 pts: Students, interns, or non-decision makers.
3. Problem Alignment & Urgency (0-30 pts):
   - 25-30 pts: Explicit pain in lead routing, CRM manual work, team expansion.
   - 10-20 pts: General evaluation, exploratory interest.
   - 0 pts: Seeking free tools or discounts.
4. Budget & Timing (0-10 pts):
   - 10 pts: Active budget, current quarter project (e.g. Q4, immediate).
   - 5 pts: Future evaluation.
   - 0 pts: No commercial intent.

Return ONLY a valid JSON object matching this schema:
{
  "icp_score": <int 0-100>,
  "tier": "<'Tier 1 (High)' | 'Tier 2 (Medium)' | 'Tier 3 (Disqualified)'>",
  "buying_intent": "<'High' | 'Medium' | 'Low'>",
  "dimension_breakdown": {
    "firmographic_fit": <int 0-30>,
    "persona_authority": <int 0-30>,
    "problem_alignment": <int 0-30>,
    "budget_timing": <int 0-10>
  },
  "key_pain_points": ["<point 1>", "<point 2>"],
  "qualification_rationale": "<2 concise sentences summarizing why this score was awarded>",
  "suggested_sales_hook": "<1 customized sentence for SDR outreach>",
  "recommended_action": "<'ROUTE_TO_AE_IMMEDIATE' | 'ASSIGN_SDR_NURTURE' | 'DISQUALIFY_AND_LOG'>"
}
"""

def score_with_gemini(lead_payload: dict, api_key: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    
    body = {
        "contents": [
            {
                "parts": [
                    {"text": ICP_RUBRIC_PROMPT},
                    {"text": f"INBOUND LEAD DOSSIER TO EVALUATE:\n{json.dumps(lead_payload, indent=2)}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }
    
    req = Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urlopen(req, timeout=15) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            candidate_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return json.loads(candidate_text)
    except HTTPError as e:
        print(f"Gemini API Error: {e.code} - {e.reason}")
        print(e.read().decode("utf-8"))
        return None
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Gemini AI Lead Scoring directly")
    parser.add_argument("--tier", type=int, default=1, choices=[1, 2, 3], help="Lead scenario (1=Hot, 2=Warm, 3=Disqualified)")
    parser.add_argument("--key", default=os.getenv("GEMINI_API_KEY", ""), help="Gemini API Key")
    args = parser.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        leads = json.load(f)

    target_lead = leads[args.tier - 1]
    print(f"\nEvaluating: {target_lead['scenario']} ({target_lead['payload']['work_email']})")

    if not args.key:
        print("⚠️ No GEMINI_API_KEY provided. Showing rubric structure.")
        print("Set your key via: set GEMINI_API_KEY=your_key or pass --key your_key")
    else:
        print("🤖 Calling Google Gemini 2.5 Flash with structured schema...")
        result = score_with_gemini(target_lead["payload"], args.key)
        if result:
            print("\n✅ AI Qualification Result:")
            print(json.dumps(result, indent=2))

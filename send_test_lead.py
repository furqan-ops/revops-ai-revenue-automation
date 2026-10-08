import json
import sys
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from pathlib import Path

DEFAULT_WEBHOOK_URL = "http://localhost:5678/webhook-test/inbound-lead"
DATA_FILE = Path(__file__).parent / "mock_data" / "test_leads.json"

def load_leads():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def send_lead(webhook_url: str, scenario_index: int):
    leads = load_leads()
    if scenario_index < 0 or scenario_index >= len(leads):
        print(f"Error: scenario index must be between 0 and {len(leads) - 1}")
        return

    selected = leads[scenario_index]
    payload = selected["payload"]

    print(f"\n==========================================")
    print(f"🚀 Sending Scenario: [{selected['scenario'].upper()}]")
    print(f"📝 Description: {selected['description']}")
    print(f"🎯 Target URL: {webhook_url}")
    print(f"📦 Lead Email: {payload['work_email']} ({payload['first_name']} {payload['last_name']})")
    print(f"==========================================\n")

    json_data = json.dumps(payload).encode("utf-8")
    req = Request(
        webhook_url,
        data=json_data,
        headers={"Content-Type": "application/json", "User-Agent": "LeadGen-Test-Client/1.0"},
        method="POST"
    )

    try:
        with urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_body = response.read().decode("utf-8")
            print(f"✅ Webhook Success! HTTP {status_code}")
            print(f"📬 Response: {response_body}\n")
    except HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        print(f"Response: {e.read().decode('utf-8')}\n")
    except URLError as e:
        print(f"❌ Connection Failed: {e.reason}")
        print("💡 Tip: Make sure your n8n Docker container is running and the Webhook node is in 'Listening' mode.\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send mock lead to n8n webhook")
    parser.add_argument("--url", default=DEFAULT_WEBHOOK_URL, help="n8n Webhook URL (default: http://localhost:5678/webhook-test/inbound-lead)")
    parser.add_argument("--tier", type=int, default=1, choices=[1, 2, 3], help="Lead Tier scenario to send: 1 (Hot), 2 (Warm), 3 (Disqualified)")
    
    args = parser.parse_args()
    send_lead(args.url, args.tier - 1)

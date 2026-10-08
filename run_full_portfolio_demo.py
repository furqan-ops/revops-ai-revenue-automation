import json
import time
import argparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from pathlib import Path

DEFAULT_WEBHOOK_URL = "http://localhost:5678/webhook-test/inbound-lead"
DATA_FILE = Path(__file__).parent / "mock_data" / "test_leads.json"

def run_scenario(lead_item: dict, webhook_url: str):
    scenario = lead_item["scenario"]
    payload = lead_item["payload"]
    description = lead_item["description"]

    print(f"\n{'='*65}")
    print(f"🎬 TEST SCENARIO: {scenario.upper()}")
    print(f"📌 {description}")
    print(f"👤 Contact: {payload['first_name']} {payload['last_name']} ({payload['job_title']})")
    print(f"🏢 Company: {payload['company_name']} | Email: {payload['work_email']}")
    print(f"🎯 Webhook: {webhook_url}")
    print(f"{'='*65}")

    data = json.dumps(payload).encode("utf-8")
    req = Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "RevOps-Demo-Suite/1.0"},
        method="POST"
    )

    start_time = time.time()
    try:
        with urlopen(req, timeout=15) as res:
            elapsed = (time.time() - start_time) * 1000
            status_code = res.getcode()
            res_body = res.read().decode("utf-8")
            print(f"✅ [HTTP {status_code}] Webhook Ingested in {elapsed:.1f}ms")
            print(f"📦 Immediate Response: {res_body}")
    except HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        print(e.read().decode("utf-8"))
    except URLError as e:
        print(f"❌ Connection Error: {e.reason}")
        print("💡 Ensure n8n is running in Docker and 'Inbound Webhook' node is in 'Listen for test event' mode.")

def main():
    parser = argparse.ArgumentParser(description="Autonomous RevOps Inbound Lead Engine - End-to-End Demo Suite")
    parser.add_argument("--url", default=DEFAULT_WEBHOOK_URL, help="n8n webhook URL")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3], help="Run specific tier (1=Hot, 2=Warm, 3=Disqualified). If omitted, runs all.")
    args = parser.parse_args()

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        leads = json.load(f)

    if args.tier:
        run_scenario(leads[args.tier - 1], args.url)
    else:
        print("\n🚀 RUNNING FULL END-TO-END REVOPS DEMO SUITE (ALL 3 TIERS)")
        for i, lead in enumerate(leads, 1):
            run_scenario(lead, args.url)
            if i < len(leads):
                print("\n⏳ Pausing 2 seconds before next test scenario...")
                time.sleep(2)

if __name__ == "__main__":
    main()

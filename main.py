import argparse
import json
import os
import sys

from core.cdp import CDPTab
from core.ai_engine import NineRouterAI
from core.glints_engine import GlintsEngine
from core.jobstreet_engine import JobStreetEngine
from core.salary_parser import SalaryParser

def load_json(path: str, fallback_path: str = None) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if fallback_path and os.path.exists(fallback_path):
        print(f"[*] Note: '{path}' not found. Loading template '{fallback_path}'.")
        with open(fallback_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise FileNotFoundError(f"Configuration file '{path}' not found.")

def main():
    parser = argparse.ArgumentParser(description="JobHunter AI - Autonomous AI-in-the-Loop Job Application Engine")
    parser.add_argument("--config", default="config.json", help="Path to config.json (defaults to config.example.json if missing)")
    parser.add_argument("--profile", default="candidate_profile.json", help="Path to candidate_profile.json")
    parser.add_argument("--test-ai", action="store_true", help="Test 9Router / OpenAI LLM connection and model generation")
    parser.add_argument("--test-cdp", action="store_true", help="Test Chrome CDP connection on port 9222")
    parser.add_argument("--scan", choices=["glints", "jobstreet"], help="Scan fresh opportunities on platform")
    parser.add_argument("--keyword", default="Developer", help="Search keyword for scanning")
    parser.add_argument("--audit", help="Audit specific job ID on selected platform")
    parser.add_argument("--platform", choices=["glints", "jobstreet"], default="glints", help="Target platform for audit/apply")
    args = parser.parse_args()

    cfg = load_json(args.config, fallback_path="config.example.json")
    profile = load_json(args.profile, fallback_path="candidate_profile.example.json")

    print(f"==================================================")
    print(f"   JOBHUNTER AI - SUPERVISED APPLICATION ENGINE   ")
    print(f"==================================================")
    print(f"Candidate: {profile.get('profile', {}).get('full_name')} ({profile.get('profile', {}).get('headline')})")

    ai = NineRouterAI(cfg, profile)

    if args.test_ai:
        print("\n[*] Testing 9Router AI connection...")
        try:
            res = ai.test_connection()
            print(f"[+] 9Router Connected! Models available: {res['models_available']}")
            print(f"[+] Active Model: {res['model_used']}")
            print(f"[+] Test Generation: \"{res['test_reply']}\"")
        except Exception as e:
            print(f"[-] 9Router Test Failed: {e}")
        return

    if args.test_cdp:
        cdp_url = cfg.get("browser", {}).get("cdp_url", "http://127.0.0.1:9222")
        print(f"\n[*] Testing Chrome CDP connection at {cdp_url}...")
        try:
            tab = CDPTab("", cdp_base_url=cdp_url)
            title = tab.js("document.title")
            print(f"[+] CDP Connected successfully! Active Tab Title: '{title}'")
            tab.close()
        except Exception as e:
            print(f"[-] CDP Test Failed: {e}")
        return

    cdp_url = cfg.get("browser", {}).get("cdp_url", "http://127.0.0.1:9222")
    tab = CDPTab(args.platform, cdp_base_url=cdp_url)

    if args.scan:
        print(f"\n[*] Scanning fresh {args.scan.upper()} jobs with keyword: '{args.keyword}'...")
        if args.scan == "glints":
            engine = GlintsEngine(tab, ai, profile)
            jobs = engine.scan_opportunities(keyword=args.keyword, page=1)
            print(f"[+] Found {len(jobs)} opportunities:")
            for j in jobs[:10]:
                print(f"  - [{j['id']}] {j['text']}")
        elif args.scan == "jobstreet":
            engine = JobStreetEngine(tab, ai, profile)
            jobs = engine.scan_jobs(query=args.keyword, page=1)
            print(f"[+] Found {len(jobs)} opportunities:")
            for j in jobs[:10]:
                print(f"  - [{j['id']}] {j['title']} @ {j['company']} ({j['location']}) | {j['salary']}")

    if args.audit:
        print(f"\n[*] Auditing {args.platform.upper()} job ID: {args.audit}...")
        if args.platform == "glints":
            engine = GlintsEngine(tab, ai, profile)
            info = engine.inspect_job(args.audit)
            print(f"[+] Title   : {info.get('title')}")
            print(f"[+] Company : {info.get('company')}")
            print(f"[+] Salary  : {info.get('salary')}")
            print(f"[+] CanApply: {info.get('canApply')}")
            parsed_sal = SalaryParser.parse_range(info.get('salary', ''))
            print(f"[+] Parsed Salary: {parsed_sal}")
            print("\n[*] Generating tailored anti-slop cover letter draft...")
            cl = ai.generate_cover_letter(info.get('title', ''), info.get('company', ''), info.get('desc', ''))
            print(f"\n--- TAILORED COVER LETTER ---\n{cl}\n----------------------------")
        elif args.platform == "jobstreet":
            engine = JobStreetEngine(tab, ai, profile)
            info = engine.inspect_job(args.audit)
            print(f"[+] Title   : {info.get('title')}")
            print(f"[+] Company : {info.get('company')}")
            print(f"[+] Salary  : {info.get('salary')}")
            print(f"[+] Apply   : {info.get('applyType')} (QuickApply: {info.get('isQuickApply')})")

    tab.close()

if __name__ == "__main__":
    main()

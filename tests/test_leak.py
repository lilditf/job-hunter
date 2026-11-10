import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IGNORE_DIRS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv"}

GENERIC_PII_PATTERNS = [
    r"\b08[1-9][0-9]{7,10}\b",
    r"C:\\Users\\(?!<user>)",
    r"C:\\laragon\\www\\cv",
    r"[a-zA-Z0-9._%+-]+@(?!example\.com|users\.noreply\.github\.com)[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
]

PLACEHOLDER_ALLOWLIST = {
    "081234567890",
    "alex.pratama@example.com",
    "user@example.com",
    "37768503+lilditf@users.noreply.github.com",
}

def load_local_sensitive_terms() -> list[str]:
    terms = []
    profile_path = os.path.join(REPO_ROOT, "candidate_profile.json")
    if os.path.exists(profile_path):
        try:
            with open(profile_path, "r", encoding="utf-8") as f:
                data = json.load(f).get("profile", {})
            for key in ["first_name", "last_name", "full_name", "email", "phone"]:
                val = data.get(key)
                if val and val not in PLACEHOLDER_ALLOWLIST:
                    terms.append(re.escape(str(val)))
            dom = data.get("domicile", {})
            for key in ["city", "district"]:
                val = dom.get(key)
                if val and len(val) > 3:
                    terms.append(re.escape(str(val)))
            for proj in data.get("projects", []):
                name = proj.get("name")
                if name and len(name) > 3:
                    terms.append(re.escape(str(name)))
        except Exception:
            pass
    return terms

def scan_repository():
    violations = []
    dynamic_terms = load_local_sensitive_terms()
    all_patterns = GENERIC_PII_PATTERNS + dynamic_terms

    print(f"[*] Scanning repository for PII and sensitive personal leaks at: {REPO_ROOT}")
    print(f"[*] Loaded {len(GENERIC_PII_PATTERNS)} generic PII rules + {len(dynamic_terms)} dynamic profile terms.\n")

    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            if f.endswith((".pyc", ".png", ".jpg", ".jpeg", ".pdf", ".ico")):
                continue
            fpath = os.path.join(root, f)
            rel_path = os.path.relpath(fpath, REPO_ROOT)

            if rel_path.replace("\\", "/") in ("tests/test_leak.py", "candidate_profile.json", "config.json", ".env"):
                continue

            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                    for line_num, line in enumerate(fh, 1):
                        if any(allowed in line for allowed in PLACEHOLDER_ALLOWLIST):
                            continue
                        for pat in all_patterns:
                            if re.search(pat, line, re.IGNORECASE):
                                violations.append((rel_path, line_num, pat, line.strip()[:100]))
            except Exception as e:
                print(f"[!] Error reading {rel_path}: {e}")

    if violations:
        print("[-] FAILED: Sensitive personal data detected in repository files:")
        for rel_path, line_num, pat, preview in violations:
            print(f"  - {rel_path}:{line_num} (Pattern: {pat}) -> {preview}")
        sys.exit(1)
    else:
        print("[+] SUCCESS: ZERO sensitive personal data or PII leaks found! Repository is 100% clean.")
        sys.exit(0)

if __name__ == "__main__":
    scan_repository()

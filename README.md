<div align="center">

# 🎯 JobHunter AI

**AI-in-the-Loop Job Application Engine & Anti-Slop Copywriting Agent**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Chrome CDP](https://img.shields.io/badge/Automation-Chrome%20CDP-4285F4.svg?logo=googlechrome&logoColor=white)](https://chromedevtools.github.io/devtools-protocol/)
[![9Router Ready](https://img.shields.io/badge/LLM%20Router-9Router%20Compatible-10B981.svg)](https://github.com/decolua/9router)
[![Anti-AI Slop](https://img.shields.io/badge/Copywriting-Anti--AI%20Slop-F59E0B.svg)](skills/anti-ai-slop-copywriting.md)

*Apply smarter, not louder. Automate form navigation while an AI agent audits job descriptions, calibrates salaries, and drafts factual, human-grade responses—with zero hallucination and zero corporate buzzwords.*

</div>

---

## 🚨 Why Blind Auto-Apply Fails (And Why This Exists)

Traditional "1-click auto-apply" bots destroy candidate reputations. They click random radio buttons, fabricate technical qualifications, spray identical generic cover letters, and trigger ATS blacklists.

**JobHunter AI** replaces blind bots with **AI-in-the-Loop Supervision**:
1. **Browser Automation via Real Chrome CDP**: Connects to your authenticated local Chrome profile (`--remote-debugging-port=9222`). No brittle headless scrapers, no suspicious login traffic.
2. **Pre-Submit Qualification Audit**: Inspects job descriptions, parses salary bands (`SalaryParser`), and filters out low-ball offers or mismatched certification requirements.
3. **Fact-Grounded Form Reasoning**: Routes screening questions (`select`, `radio`, `textarea`) to your LLM via **9Router**, ensuring every response strictly aligns with your verified `candidate_profile.json`.
4. **Anti-AI-Slop Copywriting**: Automatically strips banned AI clichés (*"passionate"*, *"cutting-edge"*, *"leveraging"*, *"robust"*, *"seamless"*) and enforces concrete engineering metrics.

---

## 🏗️ Architecture Overview

```text
┌───────────────────────────┐       ┌─────────────────────────────────┐
│  candidate_profile.json   │       │  9Router Local Proxy (:20128)   │
│  (Skills, Projects, Bio)  │       │  (Gemini / Claude / GLM / Grok) │
└─────────────┬─────────────┘       └────────────────┬────────────────┘
              │                                      │ OpenAI-compatible API
              ▼                                      ▼
     ┌────────────────────────────────────────────────────────┐
     │                  JobHunter Core Engine                 │
     │  • SalaryParser (IDR / MYR / SGD / USD calibration)    │
     │  • NineRouterAI (Anti-Slop Cover Letter & Q&A Solver)  │
     └──────────────────────────┬─────────────────────────────┘
                                │ WebSocket (CDP Port 9222)
                                ▼
     ┌────────────────────────────────────────────────────────┐
     │        Authenticated Chrome Instance (Port 9222)       │
     │   [JobStreet]   [Glints]   [LinkedIn]   [Indeed]       │
     └────────────────────────────────────────────────────────┘
```

---

## 🌐 Supported & Recommended Platforms

| Platform | Target Market | Optimal Strategy |
|---|---|---|
| **JobStreet** | Indonesia, Malaysia, Singapore | Target `Lamaran Cepat` / Quick Apply listings. Inject customized role-specific cover letters and accurate screening dropdowns. |
| **Glints** | Southeast Asia Startups & Tech | Automated skill-tier matrix calibration (`ADVANCED`, `INTERMEDIATE`, `BASIC`) and verified project essay generation. |
| **LinkedIn** | Remote & ASEAN Multinationals | Easy Apply modal traversal; handles multi-step work authorization, experience duration, and regional currency conversion (MYR/SGD). |
| **Indeed** | Direct Corporate & Enterprise | Profile resume synchronization via CDP `DOM.setFileInputFiles` and multi-step screening automation. |

---

## 🧠 Recommended AI Models (via 9Router)

JobHunter AI uses **9Router** (`http://localhost:20128/v1`) as its unified OpenAI-compatible base URL, allowing you to switch providers effortlessly:

| Task | Recommended Model ID | Why It Excels |
|---|---|---|
| **Screening Q&A & Radio Calibration** | `ag/gemini-3.8-flash-low` | Sub-2s latency, strict JSON adherence, zero overthinking on simple boolean/radio choices. |
| **High-Speed Fallback Solver** | `gh/claude-haiku-5.5` | Ultra-reliable structured formatting for multi-select forms. |
| **Human-Grade Cover Letters** | `ag/claude-sonnet-5-5-low` | Natural engineering register; strictly obeys negative constraints against AI slop. |
| **Indonesian / Bilingual Nuance** | `privatemode/glm-5.3-flash` | Strong bilingual fluency for formal Indonesian and English enterprise postings. |

> **Critical 9Router Implementation Detail**: All API calls in `core/ai_engine.py` explicitly pass `"stream": false` to prevent SSE chunks from breaking JSON response parsing.

---

## 🛡️ Anti-AI-Slop & Recommended Skills

Included inside the [`skills/`](skills/) directory are ready-to-use agent instructions compatible with **Hermes Agent**, **Claude Code**, **Cursor**, and **Windsurf**:

1. **[`skills/anti-ai-slop-copywriting.md`](skills/anti-ai-slop-copywriting.md)**:
   * Enforces the formula: **Action Verb + Specific System + Measurable Proof + Tech Stack**.
   * Strictly blacklists buzzwords (*passionate, innovative, cutting-edge, dynamic, seamless, robust, leveraging, crafting*).
   * Inspired by modern practitioner copywriting standards and [anti-slop engineering principles](https://github.com/blader/humanizer).
2. **[`skills/job-application-agent.md`](skills/job-application-agent.md)**:
   * Prevents agents from lying about domicile, years of experience, or unlisted certifications.
   * Implements salary floor protection and vertical honesty (e.g., admitting zero direct hospital SIMRS experience while pivoting to verified transactional ACID ERP skills).

### Recommended External Skills & Tools to Pair With This Repo
* **[9Router](https://github.com/decolua/9router)**: Local AI gateway pooling Antigravity, GitHub Copilot, Grok, and Mistral into one `localhost:20128/v1` endpoint.
* **[Humanizer / Anti-AI-Slop Rules](https://github.com/blader/humanizer)**: Strip statistical LLM phrasing patterns before sending outreach emails.
* **[Hermes Agent](https://github.com/NousResearch/hermes-agent)**: Autonomous terminal agent capable of loading `skills/` directly as procedural memory.

---

## ⚡ Quick Start (5 Minutes)

### 1. Clone & Install
```bash
git clone https://github.com/lilditf/job-hunter.git
cd job-hunter
pip install -r requirements.txt
```

### 2. Configure Profile & 9Router
```bash
cp config.example.json config.json
cp candidate_profile.example.json candidate_profile.json
```
Edit `candidate_profile.json` with your real skills, experience, and portfolio URLs. *(Note: `candidate_profile.json` and `config.json` are strictly ignored by `.gitignore` so your personal data is never pushed).*

### 3. Launch Chrome with Remote Debugging
```powershell
# Windows PowerShell
Start-Process "C:\Program Files\Google\Chrome\Application\chrome.exe" "--remote-debugging-port=9222", "--remote-allow-origins=*", "--user-data-dir=$env:LOCALAPPDATA\Google\Chrome\JobHunterProfile"
```
Log into your JobStreet, Glints, and LinkedIn accounts in that browser window.

### 4. Verify Connections & Run
```bash
# 1. Test 9Router AI Engine
python main.py --test-ai

# 2. Test Chrome CDP Connection
python main.py --test-cdp

# 3. Scan fresh jobs
python main.py --platform glints --scan glints --keyword "Fullstack"

# 4. Audit a specific job & generate an anti-slop cover letter
python main.py --platform glints --audit <JOB_ID>
```

For full cross-platform setup instructions (macOS/Linux/Windows) and 9Router troubleshooting, read the complete **[SETUP_GUIDE.md](SETUP_GUIDE.md)**.

---

## 🔒 Privacy & Security Guarantee

This repository enforces a **Zero-Leakage Invariant**:
* No personal names, phone numbers, residential addresses, resumes, or credentials are stored in source code.
* Run `python tests/test_leak.py` before committing to ensure no private identifiers slipped into tracked files.

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

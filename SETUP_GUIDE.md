# Complete Setup Guide: JobHunter AI & 9Router

This guide covers everything required to deploy and run **JobHunter AI** with local browser automation (Chrome CDP) and 9Router LLM routing.

---

## 1. Prerequisites

* **Operating System**: Windows 10/11, macOS, or Linux.
* **Python**: Version 3.10 or higher.
* **Google Chrome**: Official Chrome browser installed.
* **9Router**: Local LLM proxy router (or any OpenAI-compatible API endpoint).

---

## 2. Setting Up Chrome Remote Debugging (Port 9222)

JobHunter AI connects to your real, authenticated Chrome instance via the Chrome DevTools Protocol (CDP). This preserves your active logins across job portals without requiring automated login scripts or CAPTCHA bypasses.

### Windows (PowerShell)
```powershell
Start-Process -FilePath "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  -ArgumentList "--remote-debugging-port=9222", `
                "--remote-allow-origins=*", `
                "--user-data-dir=$env:LOCALAPPDATA\Google\Chrome\JobHunterProfile", `
                "--profile-directory=Default", `
                "--no-first-run"
```

### macOS (Terminal)
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir="$HOME/Library/Application Support/Google/Chrome/JobHunterProfile"
```

### Linux (Bash)
```bash
google-chrome \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir="$HOME/.config/google-chrome-jobhunter"
```

> **Verification**: Open your browser and navigate to `http://127.0.0.1:9222/json/version`. If a JSON payload with browser details appears, your debug port is running.

---

## 3. Setting Up 9Router as Local AI Engine

[9Router](https://github.com/decolua/9router) acts as a local gateway routing requests to 40+ AI model providers (including Google Antigravity, GitHub Copilot, Mistral, xAI Grok, and Anthropic) with zero extra token costs.

1. **Launch 9Router**:
   Ensure 9Router is running on its default port: `http://localhost:20128`.
2. **Verify Connected Models & Retrieve API Key**:
   * Open your 9Router Dashboard at `http://localhost:20128` and navigate to the **API Keys** tab.
   * Copy your active API key (or default `sk_9router` if authentication is disabled).
   * Test the endpoint in your terminal:
   ```bash
   curl -s -H "Authorization: Bearer YOUR_9ROUTER_KEY" http://localhost:20128/v1/models | grep '"id"'
   ```
3. **Recommended Model Configurations**:
   * **Fast Form & Question Reasoning**:
     * `ag/gemini-3.8-flash-low` or `ag/gemini-3.8-flash` (~1.2s latency, high schema compliance).
     * `gh/claude-haiku-5.5` (ultra-fast, excellent for multi-choice evaluation).
   * **Anti-Slop Copywriting & Cover Letters**:
     * `ag/claude-sonnet-5-5-low` (human-grade tone, adheres to negative constraints).
     * `privatemode/glm-5.3-flash` (balanced reasoning for bilingual applications).

---

## 4. Configuration & Candidate Profile Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/lilditf/job-hunter.git
   cd job-hunter
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize Configuration**:
   ```bash
   cp config.example.json config.json
   cp candidate_profile.example.json candidate_profile.json
   ```

4. **Customize `candidate_profile.json`**:
   Fill in your factual details:
   * Real technical skills categorized into `ADVANCED`, `INTERMEDIATE`, and `BASIC`.
   * Verified projects with live URLs.
   * Domicile and relocation preferences.
   * Salary expectations (minimum and maximum acceptable gross).

---

## 5. Running the Engine

### Step 1: Test Connectivity
```bash
# Test 9Router LLM generation
python main.py --test-ai

# Test Chrome CDP browser connection
python main.py --test-cdp
```

### Step 2: Scan Opportunities
```bash
# Scan fresh IT jobs on Glints
python main.py --platform glints --scan glints --keyword "Frontend"

# Scan fresh IT jobs on JobStreet
python main.py --platform jobstreet --scan jobstreet --keyword "Fullstack Developer"
```

### Step 3: Audit a Specific Opportunity
```bash
# Inspect job requirements, parse salary, and generate tailored cover letter
python main.py --platform glints --audit <JOB_ID>
```

---

## 6. Recommended Platforms & Strategy

| Platform | Primary Strengths | Best Strategy |
|---|---|---|
| **JobStreet** | Deep penetration in Indonesia, Malaysia, Singapore. High enterprise job volume. | Focus on `Lamaran Cepat` (Quick Apply). Use custom cover letters for technical roles. |
| **Glints** | Startup & tech company hub. Real-time recruiter chat and multi-step screening. | Complete skill ratings accurately. Answer domain textareas with verified project references. |
| **LinkedIn** | High-paying remote & ASEAN multinational roles (Hybrid / Remote). | Target `Easy Apply` badges. Ensure headline and summary match target role before applying. |
| **Indeed** | Direct corporate listings and Smart Apply questionnaires. | Keep resume PDF up to date on account profile; calibrate salary questions to employer range. |

---
name: job-application-agent
description: Supervise job application screening forms, questionnaires, and multi-step dialogs with factual precision and AI-in-the-loop oversight.
---

# Job Application Agent - Operational Protocol

Use this skill when driving automated job hunting on JobStreet, Glints, LinkedIn, or Indeed.

## Philosophy: Why Blind Full-Automation Fails

Naive automated job scripts rely on hardcoded CSS selectors or random radio button clicks. In real hiring pipelines:
1. Screening questions change dynamically per job (domicile checks, proprietary frameworks, salary minimums).
2. Random or false answers get the candidate blacklisted across company ATS systems.
3. Over-qualifying or under-qualifying triggers instant auto-rejections.

This agent operates on an **AI-in-the-Loop** model:
- The browser drives the navigation and discovers the form DOM.
- The LLM reasons over the question context and the candidate's verified profile.
- Radio buttons, selects, and textareas are answered with 100% factual fidelity.

---

## Screening Form Decision Rules

### 1. Domicile & Location Inquiries
* Candidate domicile is configured in `candidate_profile.json` under `profile.domicile.city`.
* If a question asks *"Are you currently residing / living in [City X]?"*:
  - If City X matches the candidate's home city: Select **YES / Ya**.
  - If City X is different: Select **NO / Tidak** (Never fabricate current living address).
* If asked *"Are you willing to relocate or work On-Site / WFO / Hybrid?"*:
  - Check `profile.domicile.willing_to_relocate` and `willing_to_wfo`. If true, answer **YES / Bersedia**.

### 2. Salary Inquiries
* Check `rules.min_salary_idr` in `config.json`.
* If the job explicitly offers below the minimum threshold, abort or skip the listing.
* For undisclosed salaries, calibrate to the midpoint of the candidate's acceptable range (`expected_salary_min_idr` to `expected_salary_max_idr`).
* For ASEAN/regional positions (e.g. Malaysia, Singapore), convert to target currency (`expected_salary_asean_myr`).

### 3. Skill & Experience Ratings
* When rating skills (`ADVANCED`, `INTERMEDIATE`, `BASIC`, `NO_EXPERIENCE`):
  - Strictly match against the candidate's skill arrays in `candidate_profile.json`.
  - For unlisted stacks, select `BASIC` or `NO_EXPERIENCE` honestly.
* For years of experience dropdowns, calculate exact duration from verified career records.

### 4. Notice Period & Availability
* Check `profile.work_status.notice_period`.
* For immediate availability / freelance status, select **Immediately / Segera / < 1 month**.

import time
from .cdp import CDPTab
from .ai_engine import NineRouterAI

class JobStreetEngine:
    """Manages JobStreet multi-step fast apply via CDP and AI supervision."""

    def __init__(self, tab: CDPTab, ai: NineRouterAI, profile: dict):
        self.tab = tab
        self.ai = ai
        self.profile = profile

    def scan_jobs(self, query: str = "Web Developer", page: int = 1) -> list[dict]:
        url = f"https://id.jobstreet.com/id/jobs?keywords={query.replace(' ', '+')}&sortmode=ListedDate&page={page}"
        self.tab.navigate(url, wait_seconds=4)
        return self.tab.js("""(() => {
            const articles = Array.from(document.querySelectorAll('article[data-job-id]'));
            return articles.map(a => ({
                id: a.getAttribute('data-job-id'),
                title: a.querySelector('[data-automation="jobTitle"]')?.innerText.trim() || '',
                company: a.querySelector('[data-automation="jobCompany"]')?.innerText.trim() || '',
                location: a.querySelector('[data-automation="jobLocation"]')?.innerText.trim() || '',
                salary: a.querySelector('[data-automation="jobSalary"]')?.innerText.trim() || 'Undisclosed'
            }));
        })()""") or []

    def inspect_job(self, job_id: str) -> dict:
        self.tab.navigate(f"https://id.jobstreet.com/id/job/{job_id}", wait_seconds=3)
        return self.tab.js("""(() => {
            const btn = document.querySelector('[data-automation="job-detail-apply"]');
            const applyType = btn ? btn.innerText.trim() : 'None';
            const title = document.querySelector('h1')?.innerText.trim() || '';
            const company = document.querySelector('[data-automation="advertiser-name"]')?.innerText.trim() || '';
            const salary = document.querySelector('[data-automation="job-detail-salary"]')?.innerText.trim() || 'Undisclosed';
            const desc = document.querySelector('[data-automation="jobAdDetails"]')?.innerText.trim() || '';
            return {
                id: '""" + job_id + """',
                title,
                company,
                salary,
                applyType,
                isQuickApply: applyType.toLowerCase().includes('cepat') || applyType.toLowerCase().includes('quick'),
                desc
            };
        })()""")

    def start_application(self, job_id: str) -> dict:
        info = self.inspect_job(job_id)
        if not info.get("isQuickApply"):
            return {"status": "EXTERNAL_REDIRECT", "reason": "Requires external ATS registration"}

        # Click quick apply button
        self.tab.js("document.querySelector('[data-automation=\"job-detail-apply\"]').click()")
        time.sleep(3)
        return self.inspect_step(job_id, info)

    def inspect_step(self, job_id: str, job_info: dict) -> dict:
        """Inspects current question step (cover letter, selects, radios, checkboxes)."""
        return self.tab.js("""(() => {
            const isFinished = !!document.querySelector('[data-automation="application-confirmation-header"]');
            if (isFinished) return { status: 'SUBMITTED' };

            const selects = Array.from(document.querySelectorAll('select')).map((s, idx) => ({
                idx,
                label: s.closest('label, div')?.innerText.slice(0, 120) || '',
                options: Array.from(s.options).map(o => o.text.trim())
            }));

            const radios = Array.from(document.querySelectorAll('input[type="radio"]')).map((r, idx) => ({
                idx,
                name: r.name,
                value: r.value,
                label: r.closest('label')?.innerText.trim() || r.value
            }));

            const hasCoverLetter = !!document.querySelector('textarea, [data-automation="cover-letter-text"]');
            const btnContinue = document.querySelector('[data-automation="continue-button"], button[type="submit"]')?.innerText.trim() || null;

            return {
                status: 'IN_PROGRESS',
                hasCoverLetter,
                selects,
                radios,
                button: btnContinue
            };
        })()""")

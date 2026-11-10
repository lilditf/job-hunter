import time
import json
from .cdp import CDPTab
from .ai_engine import NineRouterAI

class GlintsEngine:
    """Manages Glints multi-step application wizard via CDP and AI oversight."""

    def __init__(self, tab: CDPTab, ai: NineRouterAI, profile: dict):
        self.tab = tab
        self.ai = ai
        self.profile = profile

    def scan_opportunities(self, keyword: str = "Developer", page: int = 1) -> list[dict]:
        url = f"https://glints.com/id/opportunities/jobs/explore?keyword={keyword}&page={page}"
        self.tab.navigate(url, wait_seconds=4)
        cards = self.tab.js("""(() => {
            const anchors = Array.from(document.querySelectorAll('a[href*="/opportunities/jobs/"]'));
            const map = new Map();
            for (const a of anchors) {
                const m = a.href.match(/\\/opportunities\\/jobs\\/([a-f0-9\\-]+)/);
                if (m && !map.has(m[1])) {
                    const card = a.closest('[class*=\"JobCard\"], [class*=\"CardContainer\"]') || a;
                    const text = card.innerText.split('\\n').map(s => s.trim()).filter(Boolean).slice(0, 5).join(' | ');
                    map.set(m[1], { id: m[1], url: a.href, text: text });
                }
            }
            return Array.from(map.values());
        })()""") or []
        return cards

    def inspect_job(self, job_id: str) -> dict:
        self.tab.navigate(f"https://glints.com/id/opportunities/jobs/{job_id}", wait_seconds=3)
        return self.tab.js("""(() => {
            const title = document.querySelector('h1')?.innerText.trim() || '';
            const company = document.querySelector('a[href*="/companies/"]')?.innerText.trim() || '';
            const salary = document.querySelector('[class*=\"SalaryJobOverview\"], [class*=\"SalaryWrapper\"]')?.innerText.trim() || 'Undisclosed';
            const desc = document.querySelector('[class*=\"JobDescriptionContainer\"], [class*=\"OpportunityDetail\"]')?.innerText.trim() || '';
            const canApply = !!Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'LAMAR' && b.offsetParent !== null);
            return { title, company, salary, desc, canApply };
        })()""")

    def start_application(self, job_id: str) -> dict:
        info = self.inspect_job(job_id)
        if not info.get("canApply"):
            return {"status": "CANNOT_APPLY", "reason": "No active Lamar button"}

        # Click LAMAR
        self.tab.js("""(() => {
            const btn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'LAMAR' && b.offsetParent !== null);
            if (btn) btn.click();
        })()""")
        time.sleep(2)
        return self.inspect_modal_state(job_id, info)

    def inspect_modal_state(self, job_id: str, job_info: dict) -> dict:
        """Inspects questions, selects, radios, and textareas inside the Glints modal."""
        state = self.tab.js("""(() => {
            const modal = document.querySelector('div[class*=\"Modal\"], div[role=\"dialog\"]');
            if (!modal) return { open: false };
            
            const textareas = Array.from(modal.querySelectorAll('textarea')).map((t, idx) => ({
                idx,
                placeholder: t.placeholder,
                current_value: t.value,
                label: t.closest('div')?.innerText.slice(0, 150) || ''
            }));
            
            const radioGroups = [];
            const rEls = Array.from(modal.querySelectorAll('input[type="radio"]'));
            const names = Array.from(new Set(rEls.map(r => r.name).filter(Boolean)));
            for (const name of names) {
                const group = rEls.filter(r => r.name === name);
                radioGroups.push({
                    name,
                    checked: group.find(r => r.checked)?.value || null,
                    options: group.map(r => ({ value: r.value, label: r.closest('label')?.innerText.trim() || r.value }))
                });
            }

            const buttons = Array.from(modal.querySelectorAll('button')).filter(b => b.offsetParent !== null).map(b => b.innerText.trim());
            return { open: true, textareas, radioGroups, buttons };
        })()""")
        return {"job_id": job_id, "job_info": job_info, "modal_state": state}

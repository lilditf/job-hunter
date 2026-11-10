import json
import requests

FORBIDDEN_SLOP_WORDS = [
    "passionate", "innovative", "cutting-edge", "seamless", "robust",
    "powerful", "dynamic", "leveraging", "crafting", "next-gen",
    "revolutionize", "game-changer", "synergy", "excited to apply"
]

class NineRouterAI:
    """Client for 9Router / OpenAI-compatible endpoints powering AI-in-the-Loop."""

    def __init__(self, config: dict, profile: dict):
        ai_cfg = config.get("ai", {})
        self.base_url = ai_cfg.get("base_url", "http://localhost:20128/v1").rstrip("/")
        self.api_key = ai_cfg.get("api_key", "sk_9router")
        self.model_fast = ai_cfg.get("model_fast", "ag/gemini-3.8-flash-low")
        self.model_creative = ai_cfg.get("model_creative", "ag/claude-sonnet-5-5-low")
        self.timeout = ai_cfg.get("timeout_seconds", 45)
        self.temperature = ai_cfg.get("temperature", 0.2)
        self.profile = profile

    def _chat(self, model: str, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # Always pass stream=False explicitly for 9Router compatibility
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature,
            "stream": False
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"9Router Error HTTP {resp.status_code}: {resp.text[:300]}")
        
        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise RuntimeError("9Router returned empty choices.")
        content = choices[0].get("message", {}).get("content", "").strip()
        if not content:
            raise RuntimeError(f"9Router model '{model}' returned blank content. Try switching provider/model.")
        return content

    def generate_cover_letter(self, job_title: str, company: str, job_desc: str, language: str = "id") -> str:
        """Generates a human-grade, anti-AI-slop cover letter grounded in candidate profile."""
        sys_prompt = (
            "You are a concise, direct technical recruiter and career writer. "
            "Write a tailored cover letter strictly following these anti-slop rules:\n"
            f"1. FORBIDDEN WORDS (never use): {', '.join(FORBIDDEN_SLOP_WORDS)}.\n"
            "2. Formula: Concrete Action Verb + Specific Project/System + Measurable Proof/Metric + Tech Stack.\n"
            "3. Never fabricate skills, degrees, or employment history not in the provided candidate JSON.\n"
            "4. Keep length between 100 and 160 words. Direct and professional.\n"
            f"5. Output language: {'Bahasa Indonesia' if language == 'id' else 'English'}.\n"
            "Return ONLY the cover letter body text."
        )
        usr_prompt = (
            f"Target Role: {job_title} at {company}\n\n"
            f"Job Description:\n{job_desc[:2000]}\n\n"
            f"Candidate Profile JSON:\n{json.dumps(self.profile, indent=2)}"
        )
        return self._chat(self.model_creative, sys_prompt, usr_prompt, max_tokens=1000)

    def evaluate_screening_questions(self, job_title: str, company: str, questions: list[dict]) -> dict:
        """
        Evaluates form questions (radio, select, textarea) against the candidate profile.
        Returns a structured JSON mapping question index to factual answer.
        """
        sys_prompt = (
            "You are an AI-in-the-Loop Job Application Supervisor. "
            "Analyze the screening form questions and provide 100% honest, factual answers based ONLY on the candidate JSON.\n"
            "Rules:\n"
            "- If asked whether the candidate currently lives in a city different from domicile.city, answer NO/Tidak.\n"
            "- If asked about willingness to relocate or work WFO/Hybrid, check domicile.willing_to_relocate and willing_to_wfo.\n"
            "- If asked about an unlisted skill (not in skills.ADVANCED/INTERMEDIATE/BASIC), answer NO / 0 years / No experience.\n"
            "- For textareas/essays, write 2-4 crisp sentences citing verified projects from the profile without AI buzzwords.\n"
            "Return strictly valid JSON: {\"radio\": {\"0\": \"VALUE\"}, \"select\": {\"0\": \"EXACT_OPTION_TEXT\"}, \"textarea\": {\"0\": \"text\"}}"
        )
        usr_prompt = (
            f"Job: {job_title} @ {company}\n\n"
            f"Candidate Profile:\n{json.dumps(self.profile, indent=2)}\n\n"
            f"Form Questions:\n{json.dumps(questions, indent=2)}"
        )
        raw = self._chat(self.model_fast, sys_prompt, usr_prompt, max_tokens=1500)
        # Extract JSON block if wrapped in markdown fences
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)

    def test_connection(self) -> dict:
        """Tests 9Router /v1/models and generates a short verification reply."""
        models_resp = requests.get(
            f"{self.base_url}/models",
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10
        )
        models_count = len(models_resp.json().get("data", [])) if models_resp.status_code == 200 else 0
        reply = self._chat(self.model_fast, "Reply with OK only.", "Test connection.", max_tokens=64)
        return {"models_available": models_count, "test_reply": reply, "model_used": self.model_fast}

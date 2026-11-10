import re

class SalaryParser:
    """Robust salary range extraction and expectation calibrator."""

    @staticmethod
    def parse_range(salary_str: str) -> dict:
        """Parses raw text like 'Rp 6.000.000 – Rp 8.000.000 per month' or 'RM 4,500'."""
        if not salary_str or "undisclosed" in salary_str.lower() or "kompetitif" in salary_str.lower():
            return {"min": None, "max": None, "currency": "IDR", "period": "month", "raw": salary_str}

        cleaned = salary_str.replace(",", "").replace(".", "")
        currency = "IDR"
        if "rm" in salary_str.lower() or "myr" in salary_str.lower():
            currency = "MYR"
        elif "sgd" in salary_str.lower() or "s$" in salary_str.lower():
            currency = "SGD"
        elif "$" in salary_str or "usd" in salary_str.lower():
            currency = "USD"

        # Match numbers with 6+ digits for IDR, or 3-5 digits for MYR/SGD/USD
        numbers = [int(m) for m in re.findall(r"\d+", cleaned)]
        
        # Filter sensible salary amounts
        if currency == "IDR":
            numbers = [n for n in numbers if n >= 1000000]
        else:
            numbers = [n for n in numbers if 500 <= n <= 50000]

        if not numbers:
            return {"min": None, "max": None, "currency": currency, "raw": salary_str}

        if len(numbers) >= 2:
            return {
                "min": min(numbers[0], numbers[1]),
                "max": max(numbers[0], numbers[1]),
                "currency": currency,
                "raw": salary_str
            }
        return {"min": numbers[0], "max": numbers[0], "currency": currency, "raw": salary_str}

    @staticmethod
    def calibrate_expectation(parsed: dict, user_min: int, user_max: int) -> int:
        """Returns the optimal calibrated salary expectation within offer bounds."""
        if parsed["min"] and parsed["max"]:
            # Pick upper-midpoint within the employer's stated budget
            midpoint = (parsed["min"] + parsed["max"]) // 2
            return max(user_min, min(parsed["max"], midpoint))
        elif parsed["min"]:
            return max(user_min, parsed["min"])
        return (user_min + user_max) // 2

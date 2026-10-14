import re
from dataclasses import dataclass


@dataclass
class ScoredEmail:
    email: str=None
    score: int=0


class EmailFilterEngine:
    def email_score(self, email: str) -> int:
        totalScore = 0
        for keyword, score in GLOBAL_ROLE_WEIGHTS.items():
            pattern = re.escape(keyword)
            if re.search(pattern, email):
                totalScore += score
        return totalScore

    def is_restricted_email(self, email: str) -> bool:
        for keyword in RESTRICTED_EMAIL_KEYWORDS:
            pattern = re.escape(keyword)
            if re.search(pattern, email):
                return True
        return False

    async def email_filter(self, emails: list[str], limit: int) -> list[str]:
        emails: list[str] = await self.get_washout_emails(emails)
        selected_emails: list[ScoredEmail] = []

        for email in emails:
            if self.is_restricted_email(email):
                continue
            totalScore = self.email_score(email)
            if totalScore < 0:
                continue
            scored_email = ScoredEmail()
            scored_email.score = totalScore
            scored_email.email = email
            selected_emails.append(scored_email)

        selected_emails.sort(key=lambda email: email.score, reverse=True)

        return [email.email for email in selected_emails[:limit]]

    async def remove_duplicate_emails(self, emails: list[str]) -> list[str]:
        # 1. Clean whitespace and lowercase every email
        # 2. Filter out empty strings or None values
        cleaned = [
            email.strip().lower()
            for email in emails
            if email and isinstance(email, str) and email.strip()
        ]

        # 3. dict.fromkeys() removes duplicates in O(N) time and maintains order
        return list(dict.fromkeys(cleaned))

    async def get_washout_emails(self, emails: list[str]) -> list[str]:
        valid_business_emails: set[str] = set()

        for email in emails:
            clean_email = email.strip().lower()

            # Basic structural validation
            if clean_email.count("@") != 1:
                continue

            local_part, domain = clean_email.split("@")

            if not local_part or not domain:
                continue

            # Reject blocked consumer email domains
            if self.is_restricted_email(domain):
                continue

            # Preserve order while removing duplicates
            valid_business_emails.add(clean_email)

        return await self.remove_duplicate_emails(emails=list(valid_business_emails))


GLOBAL_ROLE_WEIGHTS = {
    # Regulatory compliance and financial crime
    "chiefcompliance": 100,
    "compliance": 95,
    "regulatory": 95,
    "regaffairs": 95,
    "financialcrime": 90,
    "aml": 90,
    "sanctions": 90,
    "kyc": 85,
    "risk": 90,
    "governance": 85,
    "companysecretary": 85,
    "dpo": 80,
    "privacy": 75,
    "fraud": 75,
    # Legal, audit and financial leadership
    "legal": 80,
    "audit": 80,
    "internalcontrol": 80,
    "cfo": 75,
    "ceo": 65,
    "director": 60,
    "board": 60,
    # Financial operations
    "accounts": 55,
    "finance": 55,
    "billing": 45,
    "invoice": 45,
    "payments": 45,
    "underwriting": 40,
    "claims": 40,
    "insurance": 35,
    # General business contacts
    "stakeholderrelations": 35,
    "enquir": 30,
    "query": 30,
    "contact": 25,
    "info": 20,
    "ops": 20,
    "support": 15,
    "help": 10,
    # Security and abuse reporting
    "security": 15,
    "abuse": 10,
    # Media and marketing
    "media": -20,
    "marketing": -40,
    "newsletter": -50,
    "promo": -60,
    # Automated or undeliverable addresses
    "press": -2000,
    "noreply": -2000,
    "no-reply": -2000,
    "daemon": -2000,
    "bounce": -2000,
}

RESTRICTED_EMAIL_KEYWORDS = {
    # Press and media
    "press",
    "media",
    "newsletter",
    "marketing",
    "promo",
    # Automated or undeliverable addresses
    "noreply",
    "no-reply",
    "donotreply",
    "do-not-reply",
    "daemon",
    "bounce",
    "mailer-daemon",
    "postmaster",
    # Automated system notifications
    "notifications",
    "notification",
    "automated",
    "autobot",
    # Test and temporary addresses
    "test",
    "example",
    "dummy",
    "temporary",
    "temp",
}

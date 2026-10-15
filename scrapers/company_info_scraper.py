from urllib.parse import urlsplit

from playwright.async_api import Page, BrowserContext
import re
from services.email_filter_engine import EmailFilterEngine

FALLBACK_ROUTES = [
    # Contact pages
    " contact",
    "contact-us",
    "contactus",
    "get-in-touch",
    "locations",
    # About pages
    "about",
    "about-us",
    "aboutus",
    "company",
    "who-we-are",
    # Support & Legal (good email sources)
    "support",
    "customer-support",
    "privacy-policy",
    "imprint",
]

DISALLOWED_CONSUMER_DOMAINS = {
    "gmail.com",
    "yahoo.com",
    "ymail.com",
    "hotmail.com",
    "outlook.com",
    "live.com",
    "icloud.com",
    "aol.com",
    "protonmail.com",
    "proton.me",
    "zoho.com",
    "mail.com",
    "gmx.com",
}


class CompanyInfoScraper:
    async def getEmailsFromText(self, text: str):
        email_regx = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        raw_emails: list[str] = re.findall(email_regx, text)
        emails = list({email.strip().lower() for email in raw_emails})
        return emails

    async def get_emails_from_mailto(self, page: Page) -> list[str]:
        # 1. Grab all href attributes starting with "mailto:"
        mailto_hrefs = await page.eval_on_selector_all(
            'a[href^="mailto:"]',
            "(elements) => elements.map(el => el.getAttribute('href'))",
        )

        emails = set()
        for href in mailto_hrefs:
            if not href:
                continue

            # Remove "mailto:" prefix (case-insensitive)
            cleaned = re.sub(r"^mailto:\s*", "", href, flags=re.IGNORECASE)

            # Strip query parameters like "?subject=Hello&body=..."
            cleaned = cleaned.split("?")[0].strip().lower()

            # Handle multiple comma-separated emails inside one mailto
            for candidate in cleaned.split(","):
                candidate = candidate.strip()
                if candidate and re.match(
                    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", candidate
                ):
                    emails.add(candidate)

        return list(emails)

    def is_consumer_domain(self, domain: str) -> bool:
        """Check whether a domain belongs to a blocked email provider."""
        return domain in DISALLOWED_CONSUMER_DOMAINS or any(
            domain.endswith("." + blocked_domain)
            for blocked_domain in DISALLOWED_CONSUMER_DOMAINS
        )

   

    async def get_emails_list(self, page: Page, context: BrowserContext, maxLimit:int=5):
        email_filter_engine = EmailFilterEngine() 
        body = page.locator("body")
        await body.first.wait_for(state="attached", timeout=12000)
        body_text = await body.first.inner_text()
        body_emails = (await self.getEmailsFromText(body_text)) + (await self.get_emails_from_mailto(page))
         
        if len(body_emails) > 0:
            return await email_filter_engine.email_filter(body_emails, limit=maxLimit)

        # check in nav links
        links = page.locator("nav a")
        if await links.count() > 0:
           await links.first.wait_for(state="attached", timeout=12000)
           
        # Human-readable keywords for visible hidden link text
        TARGET_KEYWORDS = [
            r"contact",
            r"get\s+in\s+touch",
            r"locations?",
            r"about",
            r"who\s+we\s+are",
            r"company",
            r"support",
            r"privacy(\s+policy)?",
            r"imprint",
        ]

        # Compile into a single regex: "contact|get\s+in\s+touch|locations?|about|..."
        a_links = links.filter(
            has_text=re.compile("|".join(TARGET_KEYWORDS), re.IGNORECASE)
        )

        link_hrefs = await a_links.evaluate_all(
            "(elements)=> elements.map((ele)=> ele.href)"
        )

        # maintain unique list
        link_list = set(link_hrefs)
        unique_link_hrefs = list(link_list)
        filter_unique_emails = set()

        for link in unique_link_hrefs:
            try:
                new_page = await context.new_page()
                res = await new_page.goto(link, wait_until="domcontentloaded")
                print("response status:", res.status if res else "no response")

                if res and res.status != 200:
                    continue
                await new_page.wait_for_timeout(2000)
                page_body = new_page.locator("body")
                await page_body.wait_for(state="attached", timeout=12000)
                body_text = await page_body.inner_text()
                new_emails = await self.getEmailsFromText(body_text)
                mailto_emails = await self.get_emails_from_mailto(new_page)
                filter_unique_emails.update(new_emails)
                filter_unique_emails.update(mailto_emails)
            except Exception as err:
                print("error during extract email from link:", str(err))
            finally:
                await new_page.close()

        return await email_filter_engine.email_filter(list(filter_unique_emails), limit=maxLimit)
        
    

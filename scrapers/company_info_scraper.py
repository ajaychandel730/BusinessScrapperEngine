from urllib.parse import urlsplit

from playwright.async_api import Page, BrowserContext
import re

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

    def filter_business_emails(self, emails: list[str]) -> list[str]:
        """Return unique emails that do not use blocked email domains."""
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
            if self.is_consumer_domain(domain):
                continue

            # Preserve order while removing duplicates
            valid_business_emails.add(clean_email)

        return list(valid_business_emails)

    async def get_emails_list(self, page: Page, context: BrowserContext):
        footer = page.locator("footer")
        await footer.first.wait_for(state="visible", timeout=12000)
        footer_text = await footer.first.inner_text()
        footer_emails = await self.getEmailsFromText(footer_text)
        #   email_regx = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        #   footer_raw_emails: list[str] = re.findall(email_regx, footer_text)
        #   footer_emails = list({email.strip().lower() for email in footer_raw_emails})

        if len(footer_emails) > 0:
            return footer_emails

        # check in nav links
        links = page.locator("nav a")
        if await links.count() > 0:
           await links.first.wait_for(state="attached", timeout=12000)
           
        # Human-readable keywords for visible/hidden link text
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
        print("uniqueLinks:", unique_link_hrefs)
        filter_unique = set()

        for link in unique_link_hrefs:
            try:
                new_page = await context.new_page()
                res = await new_page.goto(link, wait_until="domcontentloaded")
                print("response status:", res.status if res else "no response")

                if res and res.status != 200:
                    continue
                await new_page.wait_for_timeout(2000)
                page_body = new_page.locator("body")
                await page_body.wait_for(state="visible", timeout=12000)
                body_text = await page_body.inner_text()
                new_emails = await self.getEmailsFromText(body_text)
                mailto_emails = await self.get_emails_from_mailto(new_page)
                filter_unique.update(new_emails)
                filter_unique.update(mailto_emails)
            except Exception as err:
                print("error during extract email from link:", str(err))
            finally:
                await new_page.close()

        print("emails before filter:", list(filter_unique))
        return self.filter_business_emails(list(filter_unique))

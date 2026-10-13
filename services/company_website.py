from playwright.async_api import Browser, Page, async_playwright

from scrapers.google_map_scraper import GoogleMapScraper
from services.businessManager import BusinessManager
import re
from scrapers.company_info_scraper import CompanyInfoScraper
from models.businessModels import CompanyWebsiteInfo


class CompanyWebsite:
    async def get_company_info(self, url: str)-> CompanyWebsiteInfo:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            company_info_scraper = CompanyInfoScraper()
            try:
                page = await browser.new_page()
                context = await browser.new_context()

                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                emails: list[str] = await company_info_scraper.get_emails_list(
                    page, context
                )
                company_website_info = CompanyWebsiteInfo()
                company_website_info.emails = emails
                print("emails:", emails)
                return company_website_info
            except Exception as err:
                print("Error:", str(err))
                return CompanyWebsiteInfo()
            finally:
                await context.close()
                await browser.close()

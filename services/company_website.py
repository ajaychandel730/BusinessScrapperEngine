from playwright.async_api import Page, async_playwright

from config import DESKTOP_CONTEXT_OPTIONS, GOOGLE_MAPS_URL, HEADLESS, browser_args
from api.exception_handler.global_exception_handler import GlobalException
from scrapers.google_map_scraper import GoogleMapScraper
from services.businessManager import BusinessManager
import re
from scrapers.company_info_scraper import CompanyInfoScraper
from models.businessModels import CompanyWebsiteInfo


class CompanyWebsite:
    async def get_company_info(self, url: str) -> CompanyWebsiteInfo:
        async with async_playwright() as p:
            if not GOOGLE_MAPS_URL:
                raise GlobalException(
                    message="Google Maps URL configuration is missing in environment variables.",
                    status_code=500,
                )
            browser = await p.chromium.launch(headless=HEADLESS, args=browser_args)
            company_info_scraper = CompanyInfoScraper()
            try:
                context = await browser.new_context(**DESKTOP_CONTEXT_OPTIONS)
                page = await context.new_page()

                await page.goto(url, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
                emails: list[str] = await company_info_scraper.get_emails_list(
                    page, context
                )
                company_website_info = CompanyWebsiteInfo()
                company_website_info.emails = emails
                return company_website_info
            except Exception as err:
                print("service/company_website_Error:", str(err))
                return CompanyWebsiteInfo()
            finally:
                await context.close()
                await browser.close()

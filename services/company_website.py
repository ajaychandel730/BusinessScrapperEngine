from playwright.async_api import BrowserContext, Page, async_playwright

from config import DESKTOP_CONTEXT_OPTIONS, GOOGLE_MAPS_URL, HEADLESS, browser_args
from api.exception_handler.global_exception_handler import GlobalException
from scrapers.google_map_scraper import GoogleMapScraper
from services.businessManager import BusinessManager
import re
from scrapers.company_info_scraper import CompanyInfoScraper
from models.businessModels import CompanyWebsiteInfo


class CompanyWebsite:
    async def get_company_info(self, context:BrowserContext, url: str) -> CompanyWebsiteInfo:
       
            if not GOOGLE_MAPS_URL:
                raise GlobalException(
                    message="Google Maps URL configuration is missing in environment variables.",
                    status_code=500,
                )
            company_info_scraper = CompanyInfoScraper()
            try:
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
                await page.close()
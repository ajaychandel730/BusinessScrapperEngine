from playwright.async_api import Browser, Page, async_playwright

from scrapers.google_map_scraper import GoogleMapScraper
from services.businessManager import BusinessManager


class GoogleMapBusiness:
    async def get_company_list(self, search_for: str, find: int):
        async with async_playwright() as p:
            google_map_scraper = GoogleMapScraper()
            browser = await p.chromium.launch(headless=False)
            business_manager = BusinessManager()
            try:
                page = await browser.new_page()
                await page.goto("https://google.com/maps", timeout=60000)

                # search input operations
                search_input_box = page.get_by_role("combobox")
                await search_input_box.wait_for(state="visible", timeout=15000)
                await search_input_box.fill(search_for)
                await page.keyboard.press("Enter")

                # collect all article
                articles = page.get_by_role("article")
                await articles.first.wait_for(state="visible", timeout=12000)
                articlesList = await articles.all()

                for article in articlesList[:find]:
                    await article.click()
                    company_name = await article.get_by_role(
                        "link"
                    ).first.get_attribute("aria-label")

                    # main info section
                    main_section = await google_map_scraper.get_main_info_section(
                        page=page, company_name=company_name
                    )
                    address = await google_map_scraper.get_company_address(page=page)

                    # company website link
                    website = await google_map_scraper.get_company_website(page=page)

                    # company phone number
                    phone_number = await google_map_scraper.get_company_phone_number(
                        page=page
                    )
                    #   #create business and append
                    business_manager.add_company(
                        name=company_name,
                        address=address,
                        phone_number=phone_number,
                        website=website,
                    )
                 
                return business_manager
            except Exception as err:
                print("Error:", str(err))
                return None
            finally:
                await browser.close()
               

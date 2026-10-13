from playwright.async_api import async_playwright
from scrapers.google_map_scraper import GoogleMapScraper
from services.businessManager import BusinessManager
from services.company_website import CompanyWebsite
from models.businessModels import CompanyWebsiteInfo
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
                articles = page.get_by_role("article")
                await articles.last.wait_for(state="visible", timeout=12000)
                count = 0
                pre_aticle_count = 0
                while True:
                    await articles.last.hover()
                    await page.mouse.wheel(0, 500)
                    total_articles = await articles.count()
                
                    if pre_aticle_count == total_articles:
                        count += 1
                    else:
                        count = 0
                        
                    if count > 5:
                        break    
                    
                    pre_aticle_count = total_articles    
                    
                    print(f"every cycle:{count}:{pre_aticle_count}", total_articles)
                    if total_articles > find:
                        print("article_count:", total_articles)
                        break
                    await page.wait_for_timeout(1000)

                # collect all article
                articlesList = await articles.all()

                for article in articlesList[:find]:
                    await article.scroll_into_view_if_needed()
                    await page.wait_for_timeout(4000)
                    await article.wait_for(state="visible", timeout=12000)
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
                    if company_name and website:
                        company_website = CompanyWebsite() 
                        company_website_info:CompanyWebsiteInfo = await company_website.get_company_info(url=website)
                        business_manager.add_company(
                            name=company_name,
                            address=address,
                            phone_number=phone_number,
                            website=website,
                            emails=company_website_info.emails
                        )
                        
                return business_manager
            except Exception as err:
                print("Error goole map :", str(err))
                return None
            finally:
                await browser.close()

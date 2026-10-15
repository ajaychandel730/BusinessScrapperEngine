
from playwright.async_api import Page, Locator

class GoogleMapScraper:
    async def get_main_info_section(self, page: Page, company_name:str):
        main_section = page.locator(
                    f'[aria-label="{company_name}"][role="main"]'
                )
        await main_section.first.wait_for(state="visible", timeout=12000)
        return main_section
    
    async def get_company_address(self, page:Page):
        address = page.locator('button[data-item-id="address"]')
        await address.first.wait_for(state="visible", timeout=12000)
        address = await address.first.get_attribute("aria-label")
        return address
    
    async def get_company_website(self, page:Page):
        website = page.locator('a[data-item-id="authority"]')
        if (await website.count()) > 0:
            await website.first.wait_for(state="visible", timeout=12000)
            return await website.first.get_attribute("href")
    
        return None    
    
    async def get_company_phone_number(self, page:Page):
        phone_number = page.locator('a[aria-label="Call phone number"]')
        if (await phone_number.count()) > 0:
            await phone_number.first.wait_for(state="visible", timeout=12000)
            phone_number = (
                    await phone_number.first.get_attribute("href")
                    ).split(":")
            phone_number = phone_number[1] if len(phone_number) >= 2 else None
        else:
            phone_number = None
            
        return phone_number     
    async def get_company_rating(self, article:Locator)->str|None:
         rating = article.locator('[role="img"]').first
         if (await rating.count()) == 0:
             return None
         await rating.wait_for(state="attached", timeout=12000)
         return await rating.get_attribute("aria-label")    
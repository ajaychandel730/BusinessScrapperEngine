from playwright.async_api import async_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
from datetime import datetime
import asyncio
from models.business import Business
from services.businessManager import BusinessManager
from scrapers.google_map_scraper import GoogleMapScraper
from services.google_map_business import GoogleMapBusiness

async def main():
   google_map_business = GoogleMapBusiness()
   business_manager = await google_map_business.get_company_list(search_for=search_for, find=5)
   
   if business_manager == None:
       print("Something went wrong. Please try later.")
   else:
       business_manager.save_to_json("Google_map_company_info")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Business Scraper Engine")
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-l", "--location", type=str)
    args = parser.parse_args()

    if args.location and args.search:
        search_for = f"{args.search} {args.location}"
    else:
        search_for = "dentist new york"


async def startEngine():
    await main()


asyncio.run(startEngine())

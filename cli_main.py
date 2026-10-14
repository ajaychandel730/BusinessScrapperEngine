# from playwright.async_api import async_playwright
# from dataclasses import dataclass, asdict, field
# import pandas as pd
# import argparse
# from datetime import datetime
# import asyncio
# from services.google_map_business import GoogleMapBusiness


# async def main():
#     google_map_business = GoogleMapBusiness()
#     business_manager = await google_map_business.get_company_list(
#         search_for=search_for, find=find
#     )

#     if business_manager == None:
#         print("Something went wrong. Please try later.")
#     else:
#         business_manager.save_to_json("Google_map_company_info")


# if __name__ == "__main__":
#     print("hello")
#     parser = argparse.ArgumentParser(description="Business Scraper Engine")
#     parser.add_argument("-s", "--search", type=str)
#     parser.add_argument("-l", "--location", type=str)
#     parser.add_argument("-f", "--find", type=int)
#     args = parser.parse_args()

#     if args.location and args.search:
#         search_for = f"{args.search} {args.location}"
#     else:
#         search_for = "dentist new york"
#     # total result
#     find = 10
#     if args.find:
#         find = args.find

#     async def startEngine():
#         await main()

#     asyncio.run(startEngine())

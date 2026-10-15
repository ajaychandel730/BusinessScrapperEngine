from concurrent.futures import ThreadPoolExecutor
import asyncio
from fastapi import APIRouter, HTTPException, Response, Query, status
import nh3

from api.exceptions.custom_exception import (
    ScraperFailedException,
    SecurityInputValidationException,
)
from api.exceptions.global_exception import GlobalException
from services.google_map_business import GoogleMapBusiness

router = APIRouter(prefix="/leads", tags=["Leads"])
executor = ThreadPoolExecutor()

@router.get("/")
async def get_scraped_leads(
    response: Response,
    search: str = Query(..., description="Target businesss type, dentist near me"),
    location: str = Query(..., description="City or are like new york"),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Total means: like limit=10, search 10 business, filter out geniune business. it can be less then limit",
    ),
):
    try:
        search_for = f"{search},{location}"
        plain_text = nh3.clean(search_for, tags=set())
        # check spam input
        if nh3.is_html(search_for) or plain_text != search_for:
            raise SecurityInputValidationException(field_name="search and location")
        # start scraper engine
        loop = asyncio.get_running_loop()
        google_map_business = GoogleMapBusiness()
        
        business_manager = await loop.run_in_executor(
            executor,
            google_map_business.scrape_runner,
            plain_text,
            limit
            )
        if business_manager is None:
            raise ScraperFailedException(
                message="failed to retive data. Please try later."
            )

        response.status_code = status.HTTP_200_OK
        return {
            "status": "ok",
            "message": f"Found {len(business_manager.business_list)} businesses",
            "result": business_manager.business_list,
        }
    except GlobalException:
        raise

    except Exception as err:
        print("/leads/error:", str(err))
        raise GlobalException(message="internal server error. Please try later.")

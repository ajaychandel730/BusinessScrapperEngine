from fastapi import APIRouter
from api.routers.leads import router as leadsRouter

# Master router 
main_router = APIRouter(prefix="/api/v1")

#Mount sub-router
main_router.include_router(leadsRouter)

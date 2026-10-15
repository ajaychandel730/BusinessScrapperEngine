from fastapi import FastAPI, Response, status
from fastapi.exceptions import RequestValidationError
from api.exception_handler.global_exception_handler import global_exception_handler
from api.exception_handler.custom_exception_handler import validation_exception_handler
from api.exceptions.global_exception import GlobalException
from api.main_router import main_router
import uvicorn
import os

app = FastAPI()

app = FastAPI(title="My business scraper engine")

app.include_router(main_router)

@app.get("/health")
def health_check(response:Response):
    response.status_code = status.HTTP_200_OK
    return {"status":"ok"}

# Check before registering:
app.add_exception_handler(GlobalException, global_exception_handler)

# 2. Catch missing query params / wrong types / validation errors
app.add_exception_handler(
    RequestValidationError, validation_exception_handler
)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

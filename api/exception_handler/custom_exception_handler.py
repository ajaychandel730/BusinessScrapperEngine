# 2. Built-in FastAPI Validation Error Handler
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
  # Extract clean, human-readable messages from the errors list
  errors = []
  for err in exc.errors():
    field = err["loc"][-1]  # Gets the missing field name (e.g. 'search')
    message = err["msg"]  # Gets the reason (e.g. 'Field required')
    errors.append(f"'{field}': {message}")

  error_summary = ", ".join(errors)

  return JSONResponse(
      status_code=422,
      content={
          "status": "error",
          "message": f"Validation failed: {error_summary}"
      },
  )
  
  
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    print("Error:", str(exc))

    return JSONResponse(
        status_code=500,
        content={
            "success": "error",
            "message": "Unknown eror. Please try later",
        },
    )  
  
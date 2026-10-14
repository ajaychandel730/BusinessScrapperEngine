from fastapi import Request
from fastapi.responses import JSONResponse

from api.exceptions.global_exception import GlobalException


async def global_exception_handler(request: Request, exc: GlobalException):
  return JSONResponse(
      status_code=exc.status_code,
      content={
          "status": "error",
          "message": exc.message,
      },
  )
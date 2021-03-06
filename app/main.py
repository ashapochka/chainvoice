from typing import Union

import uvicorn
from fastapi.exceptions import RequestValidationError, ValidationError
from loguru import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.timing import add_timing_middleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from app.db import db_client
from app.api import api_router
from app.services import (UserService, PartyService)
from app.blockchain import blockchain_client

app = FastAPI(title="Chainvoice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_timing_middleware(app, record=logger.info)

app.include_router(api_router, prefix='/api')


async def http422_error_handler(
    req: Request, exc: Union[RequestValidationError, ValidationError]
) -> JSONResponse:
    logger.error(await req.json())
    return JSONResponse(
        {"errors": exc.errors()}, status_code=HTTP_422_UNPROCESSABLE_ENTITY
    )

app.add_exception_handler(ValidationError, http422_error_handler)
app.add_exception_handler(RequestValidationError, http422_error_handler)


@app.on_event("startup")
async def startup():
    db_client.create_schema()
    await db_client.connect()
    user_service = UserService(db_client.database)
    await user_service.create_default_superuser(None)
    party_service = PartyService(db=db_client.database)
    qadmin_party = await party_service.create_qadmin_party(None)
    await blockchain_client.init_contracts(db_client.database, qadmin_party)


@app.on_event("shutdown")
async def shutdown():
    await db_client.disconnect()


# for local debugging
if __name__ == "__main__":
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"][
        "fmt"] = "%(asctime)s | %(levelname)s     | %(message)s"
    log_config["formatters"]["default"][
        "fmt"] = "%(asctime)s | %(levelname)s     | %(message)s"
    uvicorn.run(app, host="127.0.0.1", port=8000, log_config=log_config)

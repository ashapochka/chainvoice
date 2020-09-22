import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import db_client
from app.api import api_router
from app.services import (user_service, party_service)
from app.blockchain import blockchain_client


app = FastAPI(title = "Chainvoice")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix='/api')


@app.on_event("startup")
async def startup():
    db_client.create_schema()
    await db_client.connect()
    await user_service.create_default_superuser(db_client.database, None)
    await party_service.create_qadmin_party(db_client.database, None)
    await blockchain_client.init_contracts(db_client.database)



@app.on_event("shutdown")
async def shutdown():
    await db_client.disconnect()


# for local debugging
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

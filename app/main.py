from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from . import db
from .api import api_router


db.create_schema()


app = FastAPI(title = "Chainvoice - Invoicing on Blockchain")

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
    await db.connect_databases()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect_databases()

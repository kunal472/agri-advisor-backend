# In app/main.py
from fastapi import FastAPI
from .db import models
from .db.database import engine
from .api import auth, farms, recommendations
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agri-Advisor API")

app.include_router(auth.router) # Include the router
app.include_router(farms.router) # Include the farms router
app.include_router(recommendations.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agri-Advisor Platform Backend!"}
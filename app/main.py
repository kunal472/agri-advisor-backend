# In app/main.py
from fastapi import FastAPI
from .db import models
from .db.database import engine
from .api import auth # Import the auth router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agri-Advisor API")

app.include_router(auth.router) # Include the router

@app.get("/")
def read_root():
    return {"message": "Welcome to the Agri-Advisor Platform Backend!"}
from fastapi import FastAPI, Request
from pydantic import BaseModel
from sqliteModule import *
import sqlite3

#Dev
app = FastAPI()


class UserRegister(BaseModel):
    EmailAddress : str
    Username: str
    DisplayName : str
    Password : str


@app.get("/")
def index(request: Request):
    return {f"Stuck? Try {request.url}docs"}

@app.post("/register")
def register(user: UserRegister):
    for field, value in user.model_dump().items():
        if not value or value.strip() == "":
            return {f"Missing Required Field: {field}"}
    return "Ok"

# TODO:
"""
Description: This will be an API for a todolist application.

Requirements:
Login & Registration
CRUD Operations on todolist items
Use SQLite for the database (Will expand to supporting others)
After implementing these, I will continue to work on the next steps

"""
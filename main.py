from fastapi import FastAPI, Request, Response, Cookie, Depends, HTTPException
from pydantic import BaseModel
from sqliteModule import Database
from uuid import uuid4


sqlite3Database = Database()
sqlite3Database.createDatabase()

app = FastAPI()

# TODO: CHANGE IN-MEM SESSIONS INTO DB
sessions = {}

# TEMP
def getCurrentUser(session_id: str = Cookie(default=None)):
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return sessions[session_id]

class UserRegister(BaseModel):
    EmailAddress : str
    Password: str
    Username: str
    DisplayName : str

class UserLogin(BaseModel):
    EmailAddress : str
    Password : str


@app.get("/")
def index(request: Request):
    return {f"Stuck? Try {request.url}docs"}

@app.post("/register")
def register(user: UserRegister):
    for field, value in user.model_dump().items():
        if not value or value.strip() == "":
            return {f"Missing Required Field: {field}"}

    databaseResponse = sqlite3Database.registerUser(user.EmailAddress, user.Password, user.Username, user.DisplayName)

    return databaseResponse

@app.post("/login")
def login(user: UserLogin, response: Response):
    for field, value in user.model_dump().items():
        if not value or value.strip() == "":
            return {f"Missing Required Field: {field}"}
    # If correct. Response should look like:  {"Successful": True, "Response": "Correct Credentials", "EmailAddress": "email", "Username": "username", "DisplayName": "displayname"}
    databaseResponse = sqlite3Database.userLogin(user.EmailAddress, user.Password)

    if databaseResponse["Successful"] == False:
        raise HTTPException(status_code=401, detail=databaseResponse["Response"])
    session_id = str(uuid4())
    sessionCreationResponse = sqlite3Database.createSession(databaseResponse["UserID"], session_id, databaseResponse["EmailAddress"], databaseResponse["Username"])
    if sessionCreationResponse["Successful"] == True:
        response.set_cookie(key="session_id", value=session_id, httponly=True, max_age=1800, samesite="lax", secure=False)
        return databaseResponse
    else:
        raise HTTPException(status_code=401, detail=sessionCreationResponse["Response"])

@app.get("/me")
def get_me(user=Depends(getCurrentUser)):
    return {
        "EmailAddress": user["EmailAddress"],
        "Username": user["Username"]
    }

# TODO:
"""
Description: This will be an API for a todolist application.

Requirements:
Login & Registration
CRUD Operations on todolist items
Use SQLite for the database (Will expand to supporting others)
After implementing these, I will continue to work on the next steps

"""
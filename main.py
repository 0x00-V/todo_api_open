from fastapi import FastAPI, Request, Response, Cookie, Depends, HTTPException
from pydantic import BaseModel
from sqliteModule import Database
from uuid import uuid4


sqlite3Database = Database()
sqlite3Database.createDatabase()
sqlite3Database.todo_toggleCompletion(1, 1)
app = FastAPI()


class UserRegister(BaseModel):
    EmailAddress : str
    Password: str
    Username: str
    DisplayName : str
class UserLogin(BaseModel):
    EmailAddress : str
    Password : str

class NewTodoItem(BaseModel):
    Title : str
    Description : str


def Authorized(session_id: str = Cookie(default=None)):
    databaseResponse = sqlite3Database.checkSession(session_id)
    if databaseResponse["Successful"] == False:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"UserID": databaseResponse["UserID"], "EmailAddress": databaseResponse["EmailAddress"], "Username": databaseResponse["Username"]}

def CheckSession(session_id):
    databaseResponse = sqlite3Database.checkSession(session_id)
    return databaseResponse["Successful"]
        

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
def login(user: UserLogin, response: Response, session_id: str = Cookie(default=None)):
    loginCheck = CheckSession(session_id)
    if loginCheck == True:
        raise HTTPException(status_code=401, detail="You're already logged in.")
    for field, value in user.model_dump().items():
        if not value or value.strip() == "":
            return {f"Missing Required Field: {field}"}
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
def get_me(user=Depends(Authorized)):
    return {
        "EmailAddress": user["EmailAddress"],
        "Username": user["Username"]
    }


@app.put("/create_item")
def create_item(newItem: NewTodoItem, user=Depends(Authorized)):
    newItemResponse = sqlite3Database.todo_createItem(user["UserID"], newItem.Title, newItem.Description)
    if newItemResponse["Successful"] == True:
       return newItemResponse 


# TODO:
"""
Description: This will be an API for a todolist application.

Requirements:
> Login & Registration [DONE]
> Implement Database-stored sessions where the user can only have 10 sessions. If they reach 10, delete oldest one. [DONE]
> TODOLIST CREATE []
> TODOLIST READ (LIST) []
> TODOLIST DELETE []
> TODOLIST UPDATE []
"""
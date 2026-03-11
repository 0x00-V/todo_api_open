from fastapi import FastAPI, Request, Response, Cookie, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqliteModule import Database
from uuid import uuid4
import re

sqlite3Database = Database()
sqlite3Database.createDatabase()
app = FastAPI()

origins = [
    "http://127.0.0.1:5500",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    EmailAddress : str
    Password: str
    Username: str
    DisplayName : str
class UserLogin(BaseModel):
    EmailAddress : str
    Password : str

class TodoItem(BaseModel):
    Title : str
    Description : str
class TodoItemWithID(BaseModel):
    TodoItemID : int
    Title : str
    Description : str

class TodoItemIDOnly(BaseModel):
    ItemID : int


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
    email = re.fullmatch("[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", user.EmailAddress)
    username = re.fullmatch("^[A-Za-z0-9_]{1,15}$", user.Username)
    if bool(email) == False:
        raise HTTPException(status_code=400, detail=[{"Response": "Invalid email format."}])
    if bool(username) == False:
        raise HTTPException(status_code=400, detail=[{"Response": "Invalid username format."}])
    databaseResponse = sqlite3Database.registerUser(user.EmailAddress, user.Password, f"@{user.Username}", user.DisplayName)
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


@app.put("/create-item")
def create_item(newItem: TodoItem, user=Depends(Authorized)):
    newItemResponse = sqlite3Database.todo_createItem(user["UserID"], newItem.Title, newItem.Description)
    if newItemResponse["Successful"] == False:
        raise HTTPException(status_code=400, detail=[newItemResponse["Response"]])
    return newItemResponse 


@app.get("/get-items")
def get_items(user=Depends(Authorized)):
    usersItems = sqlite3Database.todo_listItems(user["UserID"])
    if usersItems["Successful"] == False:
        raise HTTPException(status_code=400, detail=[usersItems["Response"]])
    return usersItems


@app.post("/edit-item")
def edit_item(todoItem: TodoItemWithID, user=Depends(Authorized)):
    editItemResponse = sqlite3Database.todo_editItem(todoItem.TodoItemID, user["UserID"], todoItem.Title, todoItem.Description)
    if editItemResponse["Successful"] == False:
        raise HTTPException(status_code=400, detail=[editItemResponse["Response"]])
    return editItemResponse


@app.post("/toggle-completion")
def toggle_item_completion(ItemID: int,user=Depends(Authorized)):
    toggleResponse = sqlite3Database.todo_toggleCompletion(ItemID, user["UserID"])
    if toggleResponse["Successful"] == False:
        raise HTTPException(status_code=400, detail=[toggleResponse["Response"]])
    return toggleResponse


@app.post("/delete-item")
def delete_item(ItemID: int, user=Depends(Authorized)):
    deleteResponse = sqlite3Database.todo_deleteItem(ItemID, user["UserID"])
    if deleteResponse["Successful"] == False:
        raise HTTPException(status_code=400, detail=[deleteResponse["Response"]])
    return deleteResponse


@app.get("/me")
def get_me(user=Depends(Authorized)):
    return {
        "EmailAddress": user["EmailAddress"],
        "Username": user["Username"]
    }
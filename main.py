from fastapi import FastAPI, Request, Response, Cookie, Depends, HTTPException
from pydantic import BaseModel
from sqliteModule import Database
from uuid import uuid4


sqlite3Database = Database()
sqlite3Database.createDatabase()
app = FastAPI()


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
def create_item(newItem: TodoItem, user=Depends(Authorized)):
    newItemResponse = sqlite3Database.todo_createItem(user["UserID"], newItem.Title, newItem.Description)
    if newItemResponse["Successful"] == True:
       return newItemResponse 

@app.post("/get-items")
def get_items(user=Depends(Authorized)):
    usersItems = sqlite3Database.todo_listItems(user["UserID"])
    return usersItems

@app.post("/edit-item")
def edit_item(todoItem: TodoItemWithID, user=Depends(Authorized)):
    editItemResponse = sqlite3Database.todo_editItem(todoItem.TodoItemID, user["UserID"], todoItem.Title, todoItem.Description)
    if editItemResponse["Successful"] == True:
        return editItemResponse

@app.post("/toggle-completion")
def toggle_item_comletion(ItemID: int,user=Depends(Authorized)):
    toggleResponse = sqlite3Database.todo_toggleCompletion(ItemID, user["UserID"])
    return toggleResponse
# TODO:
"""
Description: This will be an API for a todolist application.

Requirements:
> Login & Registration [DONE]
> Implement Database-stored sessions where the user can only have 10 sessions. If they reach 10, delete oldest one. [DONE]
> TODOLIST CREATE [DONE]
> TODOLIST READ (LIST) [DONE]
> TODOLIST DELETE [DONE]
> TODOLIST UPDATE [DONE]


> Maybe do some err handling.
I could improve todo logic and use userid as primary key and add a seperate id per user for items.

"""
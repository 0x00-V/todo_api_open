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


@app.put("/create-item")
def create_item(newItem: TodoItem, user=Depends(Authorized)):
    newItemResponse = sqlite3Database.todo_createItem(user["UserID"], newItem.Title, newItem.Description)
    return newItemResponse 


@app.post("/get-items")
def get_items(user=Depends(Authorized)):
    usersItems = sqlite3Database.todo_listItems(user["UserID"])
    return usersItems


@app.post("/edit-item")
def edit_item(todoItem: TodoItemWithID, user=Depends(Authorized)):
    editItemResponse = sqlite3Database.todo_editItem(todoItem.TodoItemID, user["UserID"], todoItem.Title, todoItem.Description)
    return editItemResponse


@app.post("/toggle-completion")
def toggle_item_completion(ItemID: int,user=Depends(Authorized)):
    toggleResponse = sqlite3Database.todo_toggleCompletion(ItemID, user["UserID"])
    return toggleResponse


@app.post("/delete-item")
def delete_item(ItemID: int, user=Depends(Authorized)):
    deleteResponse = sqlite3Database.todo_deleteItem(ItemID, user["UserID"])
    return deleteResponse


@app.get("/me")
def get_me(user=Depends(Authorized)):
    return {
        "EmailAddress": user["EmailAddress"],
        "Username": user["Username"]
    }
# TODO:
"""
Description: This will be an API for a todolist application.

Requirements:
BASIC AUTH - DONE
CRUD - DONE

NEXT:
Input validation
Password Resets
Proper error handling

"""
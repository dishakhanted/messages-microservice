#
# FastAPI is a framework and library for implementing REST web services in Python.
# https://fastapi.tiangolo.com/
#
from fastapi import FastAPI, Response, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from fastapi.staticfiles import StaticFiles
from typing import List, Union
from fastapi import Depends, FastAPI, HTTPException
import strawberry
from strawberry.asgi import GraphQL


# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn

from resources.messages.message_data_service import MessageDataService
from resources.messages.message_resource import MessageRspModel, MessageModel, MessageResource
from resources.users.users_data_service import UserDataService
from resources.users.users_resource import UserResource
from resources.users.users_models import UserRspModel, UserModel
from pydantic import BaseModel

LOCAL = False

import strawberry
from pydantic import BaseModel

@strawberry.type
class User:
    userID: int
    firstName: str
    lastName: str
    isAdmin: bool


@strawberry.type
class Message:
    userMessageID: int
    userID: int
    messageID: int
    messageContents: str
    creationDT: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, userID: int) -> User | None:
        result = user_resource.get_users(userID, firstName=None, lastName=None, isAdmin=None, offset=None, limit=None)
        if result is not []:
            return User(**result[0])
        else:
            return None
    @strawberry.field
    def messages(self, user_id: int | None = None, message_thread_id: int | None = None, message_id: int | None = None, message_contents: int | None = None, offset: int | None = None, limit: int | None = None) -> list[Message]:
        result = message_resource.get_messages(user_id, message_thread_id, message_id, message_contents, offset, limit)
        print(result)
        return [Message(**msg) for msg in result]
    
schema = strawberry.Schema(query=Query)
    
graphql_app = GraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_data_service():
    database = {}
    if LOCAL:
        database = {
            "db_name" : "message",
            "db_host" : "localhost",
            "db_user" : "message",
            "db_pass" : "message",
        }
    else:
        database = {
            "db_name" : "message",
            "db_host" : '/cloudsql/{}'.format("messages-microservice:us-east1:message-db"),
            "db_user" : "message",
            "db_pass" : "message",
        }

    ds = UserDataService(database)
    return ds


def get_user_resource():
    ds = get_data_service()
    config = {
        "data_service": ds
    }
    res = UserResource(config)
    return res


user_resource = get_user_resource()

def get_message_resource():
    database = {}
    if LOCAL:
        database = {
            "db_name" : "message",
            "db_host" : "localhost",
            "db_user" : "message",
            "db_pass" : "message",
        }
    else:
        database = {
            "db_name" : "message",
            "db_host" : '/cloudsql/{}'.format("messages-microservice:us-east1:message-db"),
            "db_user" : "message",
            "db_pass" : "message",
        }


    ds = MessageDataService(database)

    config = {
        "data_service": ds
    }
    res = MessageResource(config)
    return res


message_resource = get_message_resource()


#
# END TODO
# **************************************

"""
/api/messages/{userID}
/api/messages/{userID}/newMessage
/api/messages/{userID}/{messageThreadID}
"""

@app.get("/")
async def root():
    return RedirectResponse("/static/index.html")

@app.get("/api")
async def api():
    """
    Redirects to FastAPI Documentation.
    """
    return RedirectResponse("/docs")

@app.get("/profile/{userID}", response_class=HTMLResponse)
async def profile(request: Request, userID: int):
    result = user_resource.get_users(userID, firstName=None, lastName=None, isAdmin=None, offset=None, limit=None)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return templates.TemplateResponse("profile.html", {"request": request, "userID": userID, "result": result})

@app.get("/api/users", response_model=List[UserRspModel])
async def get_users(userID: int | None = None, firstName: str | None = None, lastName: str | None = None, isAdmin: bool | None = None, offset: int | None = None, limit: int | None = None):
    """
    Return all users.
    """
    result = user_resource.get_users(userID, firstName, lastName, isAdmin, offset, limit)
    return result

@app.get("/api/users/{userID}", response_model=Union[List[UserRspModel], UserRspModel, None])
async def get_student(userID: int):
    """
    Return a user based on userID.

    - **userID**: User's userID
    """
    result = user_resource.get_users(userID, firstName=None, lastName=None, isAdmin=None, offset=None, limit=None)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result


@app.post("/api/users/newUser")
def add_users(request: UserModel):
    
    result = user_resource.add_user(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.get("/api/messages", response_model=List[MessageRspModel])
async def get_messages(userID: int | None = None, messageThreadID: int | None = None, messageID: int | None = None, messageContents: int | None = None, offset: int | None = None, limit: int | None = None):
    """
    Returns all messages.
    """

    result = message_resource.get_messages(userID, messageThreadID, messageID, messageContents, offset, limit)
    return result

@app.get("/api/messages/{userID}", response_model=Union[List[MessageRspModel], MessageRspModel, None])
async def get_messages(userID: int):
    """
    Return messages based on userID.

    - **userID**: User's userID
    """
    
    result = message_resource.get_messages(userID, messageThreadID=None, messageID=None, messageContents=None, offset=None, limit=None)

    return result

@app.get("/api/messages/{userID}/{messageThreadID}", response_model=Union[List[MessageRspModel], MessageRspModel, None])
async def get_messages(userID: int, messageThreadID: int):
    """
    Return messages based on userID and message Thread ID.

    - **userID**: User's userID
    - **messageThreadID**: ThreadID
    """

    result = message_resource.get_messages(userID, messageThreadID, messageID=None, messageContents=None, offset=None, limit=None)

    return result

@app.post("/api/messages/newMessage")
def new_message(request: MessageModel):
    
    result = None
    result = message_resource.add_message(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.put("/api/messages/newMessage")
def new_message(request: MessageModel):
    
    result = None
    result = message_resource.put_message(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.delete("/api/messages/newMessage")
def new_message(request: MessageModel):
    
    result = None
    result = message_resource.delete_message(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8011, reload=True)

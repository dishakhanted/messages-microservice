#
# FastAPI is a framework and library for implementing REST web services in Python.
# https://fastapi.tiangolo.com/
#
from fastapi import FastAPI, Response, HTTPException
from fastapi.responses import RedirectResponse

from fastapi.staticfiles import StaticFiles
from typing import List, Union

# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn

from resources.database.database_data_service import DatabaseDataService
from resources.messages.message_data_service import MessageDataService
from resources.messages.message_resource import MessageResource
from resources.messages.message_resource import MessageRspModel, MessageModel
from resources.users.users_data_service import UserDataService
from resources.users.users_resource import UserResource
from resources.users.users_models import UserRspModel, UserModel
from pydantic import BaseModel


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# ******************************
#
# DFF TODO Show the class how to do this with a service factory instead of hard code.


def get_data_service():

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

@app.get("/api/users", response_model=List[UserRspModel])
async def get_users():
    """
    Return all users.
    """
    result = user_resource.get_users(userID=None)
    return result

@app.get("/api/users/{userID}", response_model=Union[List[UserRspModel], UserRspModel, None])
async def get_student(userID: int):
    """
    Return a user based on userID.

    - **userID**: User's userID
    """
    result = None
    result = user_resource.get_users(userID)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")

    return result


@app.post("/api/users/newUser")
def add_users(request: UserModel):
    
    result = None
    result = user_resource.add_user(request)
    if len(result) == 1:
        result = result[0]
    else:
        raise HTTPException(status_code=404, detail="Not found")
    
    return result

@app.get("/api/messages", response_model=List[MessageRspModel])
async def get_messages():
    """
    Returns all messages.
    """
    result = message_resource.get_messages(userID=None, messageID=None)
    return result

@app.get("/api/messages/{userID}", response_model=Union[List[MessageRspModel], MessageRspModel, None])
async def get_messages(userID: int):
    """
    Return messages based on userID.

    - **userID**: User's userID
    """
    result = message_resource.get_messages(userID, None)

    return result

@app.get("/api/messages/{userID}/{messageThreadID}", response_model=Union[List[MessageRspModel], MessageRspModel, None])
async def get_messages(userID: int, messageThreadID: int):
    """
    Return messages based on userID and message Thread ID.

    - **userID**: User's userID
    - **messageThreadID**: ThreadID
    """
    result = message_resource.get_messages(userID, messageThreadID)

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

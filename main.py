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

from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


# I like to launch directly and not use the standard FastAPI startup process.
# So, I include uvicorn
import uvicorn

from resources.messages.message_data_service import MessageDataService
from resources.messages.message_resource import MessageRspModel, MessageModel, MessageResource
from resources.users.users_data_service import UserDataService
from resources.users.users_resource import UserResource
from resources.users.users_models import UserRspModel, UserModel
from pydantic import BaseModel

SECRET_KEY = "4f6c5db6278a552eee164342cdf6880921c21676560313d2d8a67aeadd37768a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60000
LOCAL = False

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(userID):
    user = user_resource.get_users(userID, firstName=None, lastName=None, isAdmin=None, offset=None, limit=None)
    if len(user) == 1:
        user = user[0]
        return user
    else:
        return None


def authenticate_user(userID, password = None):
    user = get_user(userID)
    if user:
        return user
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userID: str = payload.get("sub")
        if userID is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(userID=userID)
    if user is None:
        raise credentials_exception
    return user

@app.get("/users/me/", response_model=Union[List[UserRspModel], UserRspModel, None])
async def read_users_me(
    current_user: Annotated[UserRspModel, Depends(get_current_user)]
):
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.userID), "fn": user.firstName, "ln": user.lastName}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    result = message_resource.get_messages(userID, messageThreadID, messageID, messageContents, offset, limit)
    return result

@app.get("/api/messages/{userID}", response_model=Union[List[MessageRspModel], MessageRspModel, None])
async def get_messages(userID: int, current_user: Annotated[UserRspModel, Depends(get_current_user)]):
    """
    Return messages based on userID.

    - **userID**: User's userID
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not current_user.isAdmin and current_user.userID != userID:
        raise credentials_exception
    
    result = message_resource.get_messages(userID, messageThreadID=None, messageID=None, messageContents=None, offset=None, limit=None)

    return result

@app.get("/api/messages/{userID}/{messageThreadID}", response_model=Union[List[MessageRspModel], MessageRspModel, None])
async def get_messages(userID: int, messageThreadID: int, current_user: Annotated[UserRspModel, Depends(get_current_user)]):
    """
    Return messages based on userID and message Thread ID.

    - **userID**: User's userID
    - **messageThreadID**: ThreadID
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not current_user.isAdmin and current_user.userID != userID:
        raise credentials_exception
    
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

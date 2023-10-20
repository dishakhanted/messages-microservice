from __future__ import annotations
from pydantic import BaseModel
from typing import List

from resources.rest_models import Link


class UserModel(BaseModel):
    userID: int
    firstName: str
    lastName: str
    isAdmin: bool

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "userID": 1,
                    "firstName": "Maxwell",
                    "lastName": "Gonsalves",
                    "isAdmin": True
                }
            ]
        }
    }


class UserRspModel(UserModel):
    links: List[Link] = None




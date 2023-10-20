from __future__ import annotations
from pydantic import BaseModel
from typing import List

from resources.rest_models import Link


class MessageModel(BaseModel):
    userMessageID: int
    userID: int
    messageID: int
    messageContents: str
    creationDT: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "userMessageID": 1,
                    "userID": 1,
                    "messageID": 1,
                    "messageContents": "Hi! (Potentially Encrypted).",
                    "creationDT": "10/3/23 16:25"
                }
            ]
        }
    }


class MessageRspModel(MessageModel):
    links: List[Link] = None




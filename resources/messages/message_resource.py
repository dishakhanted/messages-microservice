from resources.abstract_base_resource import BaseResource
from resources.messages.message_models import MessageRspModel, MessageModel
from resources.rest_models import Link
from typing import List


class MessageResource(BaseResource):
    #
    # This code is just to get us started.
    # It is also pretty sloppy code.
    #

    def __init__(self, config):
        super().__init__()

        self.data_service = config["data_service"]

    @staticmethod
    def _generate_links(s: dict) -> MessageRspModel:

        self_link = Link(**{
            "rel": "self",
            "href": "/users/" + str(s['userID'])
        })

        links = [
            self_link,
        ]
        rsp = MessageRspModel(**s, links=links)
        return rsp

    def get_messages(self, userID: int, messageThreadID: int, messageID: int, messageContents: int, offset: int, limit: int) -> List[MessageRspModel]:

        result = self.data_service.get_messages(userID, messageThreadID, messageID, messageContents, offset, limit)
        final_result = []

        for s in result:
            m = self._generate_links(s)
            final_result.append(m)

        return final_result

    def add_message(self, request: MessageModel) -> List[MessageRspModel]:

        result = self.data_service.add_message(request)

        return result
    
    def put_message(self, request: MessageModel) -> List[MessageRspModel]:

        result = self.data_service.put_message(request)

        return result

    def delete_message(self, request: MessageModel) -> List[MessageRspModel]:

        result = self.data_service.delete_message(request)

        return result



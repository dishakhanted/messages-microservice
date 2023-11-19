from resources.abstract_base_resource import BaseResource
from resources.users.users_models import UserRspModel, UserModel
from resources.rest_models import Link
from typing import List


class UserResource(BaseResource):
    #
    # This code is just to get us started.
    # It is also pretty sloppy code.
    #

    def __init__(self, config):
        super().__init__()

        self.data_service = config["data_service"]

    @staticmethod
    def _generate_links(s: dict) -> UserRspModel:

        self_link = Link(**{
            "rel": "self",
            "href": "/users/" + str(s['userID'])
        })

        links = [
            self_link
        ]
        rsp = UserRspModel(**s, links=links)
        return rsp

    def get_users(self, userID: int, firstName: str, lastName: str, isAdmin: bool, offset: int, limit: int) -> List[UserRspModel]:

        result = self.data_service.get_users(userID, firstName, lastName, isAdmin, offset, limit)
        final_result = []

        for s in result:
            m = self._generate_links(s)
            final_result.append(m)

        return final_result
    
    def add_user(self, request: UserModel) -> List[UserRspModel]:

        result = self.data_service.add_user(request)

        return result


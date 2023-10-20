from resources.abstract_base_data_service import BaseDataService
from resources.database.database_data_service import DatabaseDataService
import json


class UserDataService(BaseDataService):

    def __init__(self, config: dict):
        """

        :param config: A dictionary of configuration parameters.
        """
        super().__init__()

        #self.data_dir = config['data_directory']
        #self.data_file = config["data_file"]
        #self.students = []

        self.database = DatabaseDataService(config)
        self._load()

    def _load(self):

        users = """CREATE TABLE IF NOT EXISTS "messageUsers" (
        "userID" serial,
        "firstName" text,
        "lastName" text,
        "isAdmin" boolean,
        PRIMARY KEY ("userID")
        );"""
        
        self.database.execute_query(users)


    def _save(self):
        fn = self._get_data_file_name()
        with open(fn, "w") as out_file:
            json.dump(self.students, out_file)

    def get_database(self):
        return self.database

    def get_users(self, userID: int) -> list:
        """

        Returns users with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param userID: userID to match.
        :return: A list of matching JSON records.
        """
        result = []
        users = {}
        if userID == None:
            users = self.database.fetchallquery('SELECT * FROM "messageUsers";')
        else:
            users = self.database.fetchallquery('SELECT * FROM "messageUsers" WHERE "userID"='+str(userID)+';')
        
        for s in users:
            result.append(s)

        return result
    
    def add_user(self, request: dict) -> list:
        """

        Adds students with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param request: A dictionary of the UserModel
        :return: userID of the newly created user.
        """
        query = f"""INSERT INTO "messageUsers"("userID", "firstName", "lastName", "isAdmin") VALUES (DEFAULT, '{request.firstName}' , '{request.lastName}', {request.isAdmin}) RETURNING "userID";"""
        users = self.database.execute_query(query)
        result = users.fetchone()

        return result


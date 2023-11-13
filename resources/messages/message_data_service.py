from resources.abstract_base_data_service import BaseDataService
from resources.database.database_data_service import DatabaseDataService
import json


class MessageDataService(BaseDataService):

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

        messages = """CREATE TABLE IF NOT EXISTS "userMessages" (
        "userMessageID" serial,
        "userID" int,
        "messageID" int,
        "messageContents" text,
        "creationDT" timestamp,
        PRIMARY KEY ("userMessageID"),
        CONSTRAINT "FK_userMessages.messageID"
            FOREIGN KEY ("messageID")
            REFERENCES "messageThread"("messageID"),
        CONSTRAINT "FK_userMessages.userID"
            FOREIGN KEY ("userID")
            REFERENCES "messageUsers"("userID")
        );"""
        threads = """CREATE TABLE IF NOT EXISTS "messageThread" (
        "messageID" serial,
        "creationDT" timestamp,
        PRIMARY KEY ("messageID")
        );"""
        self.database.execute_query(threads)
        self.database.execute_query(messages)

    def get_database(self):
        return self.database

    def get_messages(self, userID: int, messageID: int) -> list:
        """

        Returns students with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param uni: UNI to match.
        :param last_name: last_name to match.
        :param school_code: first_name to match.
        :return: A list of matching JSON records.
        """
        result = []
        users = {}
        if userID == None:
            users = self.database.fetchallquery("""SELECT * FROM "userMessages";""")
        elif messageID == None:
            users = self.database.fetchallquery(f"""SELECT * FROM "userMessages" WHERE "userID"='{userID}';""")
        else: 
            users = self.database.fetchallquery(f"""SELECT * FROM "userMessages" WHERE "userID"='{userID}'AND "messageID"='{messageID}';""")

        for s in users:
            s['creationDT'] = s['creationDT'].strftime("%m/%d/%Y, %H:%M:%S")
            result.append(s)

        return result
    
    def add_message(self, request: dict) -> list:
        """

        Adds a message to a thread. Thread is created if the current ID doesnt exist.

        :param request: POST request with message data.
        """
        check_thread = f"""INSERT INTO "messageThread" ("messageID", "creationDT") VALUES ('{request.messageID}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"""
        self.database.execute_query(check_thread)
        query = f"""INSERT INTO "userMessages"("userMessageID", "userID", "messageID", "messageContents", "creationDT") VALUES (DEFAULT, '{request.userID}', '{request.messageID}' , '{request.messageContents}', CURRENT_TIMESTAMP) RETURNING "messageID";"""
        users = self.database.execute_query(query)
        result = users.fetchone()

        return result
    
    def put_message(self, request: dict) -> list:
        """

        Puts a message to a thread. Thread is created if the current ID doesnt exist.

        :param request: POST request with message data.
        """
        check_thread = f"""INSERT INTO "messageThread" ("messageID", "creationDT") VALUES ('{request.messageID}', CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING"""
        self.database.execute_query(check_thread)
        query = f"""INSERT INTO "userMessages"("userMessageID", "userID", "messageID", "messageContents", "creationDT") VALUES ('{request.userMessageID}', '{request.userID}', '{request.messageID}' , '{request.messageContents}', CURRENT_TIMESTAMP) ON CONFLICT ("userMessageID") DO UPDATE SET "messageContents"='{request.messageContents}', "creationDT"='CURRENT_TIMESTAMP' RETURNING "messageID";"""
        users = self.database.execute_query(query)
        result = users.fetchone()

        return result
    
    def delete_message(self, request: dict) -> list:
        """

        Deletes a message from a thread.

        :param request: DELETE request with message ID.
        """
        query = f"""DELETE FROM "userMessages" WHERE "userMessageID" = '{request.userMessageID}' RETURNING "messageID";"""
        users = self.database.execute_query(query)
        result = users.fetchone()

        return result


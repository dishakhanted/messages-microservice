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

    def get_messages(self, userID: int, messageThreadID: int, messageID: int, messageContents: int, offset: int, limit: int) -> list:
        """

        Returns students with properties matching the values. Only non-None parameters apply to
        the filtering.

        :param uni: UNI to match.
        :param last_name: last_name to match.
        :param school_code: first_name to match.
        :return: A list of matching JSON records.
        """
        result = []

        params = ["""\"userID\"""", """\"messageID\"""", """\"userMessageID\"""", """\"messageContents\"""", """\"offset\"""", """\"limit\""""]
        values = [userID, messageThreadID, messageID, messageContents, offset, limit]

        query = """SELECT * FROM \"userMessages\""""
        conditions = []
        for param, value in zip(params, values):
            if value is not None:
                if param == """\"messageContents\"""":
                    conditions.append(f"{param} LIKE %s")
                else:
                    conditions.append(f"{param} = %s")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += ";"
              
        messages = self.database.fetchallquery(query, tuple(value for value in values if value is not None))

        for s in messages:
            s['creationDT'] = s['creationDT'].strftime("%m/%d/%Y, %H:%M:%S")
            result.append(s)

        return result
    
    def add_message(self, request: dict) -> list:
        """

        Adds a message to a thread. Thread is created if the current ID doesnt exist.

        :param request: POST request with message data.
        """
        self.database.execute_query("INSERT INTO \"messageThread\" (\"messageID\", \"creationDT\") VALUES (%s, CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING", (request.messageID,))
        messages = self.database.execute_query("INSERT INTO \"userMessages\" (\"userMessageID\", \"userID\", \"messageID\", \"messageContents\", \"creationDT\") VALUES (DEFAULT, %s, %s, %s, CURRENT_TIMESTAMP) RETURNING \"messageID\"", (request.userID, request.messageID, request.messageContents))
        result = messages.fetchone()

        return result
    
    def put_message(self, request: dict) -> list:
        """

        Puts a message to a thread. Thread is created if the current ID doesnt exist.

        :param request: POST request with message data.
        """
        self.database.execute_query("INSERT INTO \"messageThread\" (\"messageID\", \"creationDT\") VALUES (%s, CURRENT_TIMESTAMP) ON CONFLICT DO NOTHING", (request.messageID,))
        messages = self.database.execute_query("INSERT INTO \"userMessages\" (\"userMessageID\", \"userID\", \"messageID\", \"messageContents\", \"creationDT\") VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP) ON CONFLICT (\"userMessageID\") DO UPDATE SET \"messageContents\"=%s, \"creationDT\"=CURRENT_TIMESTAMP RETURNING \"messageID\"", (request.userMessageID, request.userID, request.messageID, request.messageContents, request.messageContents))
        result = messages.fetchone()

        return result
    
    def delete_message(self, request: dict) -> list:
        """

        Deletes a message from a thread.

        :param request: DELETE request with message ID.
        """
        messages = self.database.execute_query("DELETE FROM \"userMessages\" WHERE \"userMessageID\" = %s RETURNING \"messageID\"", (request.userMessageID,))
        result = messages.fetchone()

        return result


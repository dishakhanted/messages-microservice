#from resources.abstract_base_data_service import BaseDataService
import json
import psycopg2



#class DatabaseDataService(BaseDataService):
class DatabaseDataService():
    def __init__(self, config: dict):
        """

        :param config: A dictionary of configuration parameters.
        """
        #super().__init__()

        self.conn = psycopg2.connect(database=config["db_name"],
                        host=config["db_host"],
                        user=config["db_user"],
                        password=config["db_pass"])
        self.conn.autocommit = True
        self.cursor = self.conn.cursor()

    def _get_cursor(self):
        return self.cursor

    def execute_query(self, query: str = None, params: () = None):
        if (query):
            self.cursor.execute(query, params)
        return self.cursor

    def fetchallquery(self, query: str = None, params: () = None):
        if (query):
            self.cursor.execute(query, params)
        else: 
            return []
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    
    def fetchonequery(self, query: str = None, params: () = None):
        if (query):
            self.cursor.execute(query, params)
        else: 
            return []
        return self.cursor.fetchone()

    def fetchmanyquery(self, query: str = None, size: int = 1, params: () = None):
        if (query):
            self.cursor.execute(query, params)
        else: 
            return []
        return self.cursor.fetchmany(size=size)
import os

import dotenv
import MySQLdb

dotenv.load_dotenv() # Load environment variables.


class Database:
    __DBMS = 'MySQL'
    __connection = None
    __cursor = None


    def __init__(self):
        try:
            print(f'Connecting to the {self.__DBMS} database...')
            self.__connection = MySQLdb.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT')),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
            )
            self.__cursor = self.__connection.cursor()
            print(f'Successfully connected to the {self.__DBMS} database.')
        except Exception as e:
            print(e)
            print(f"Couldn't connect to the {self.__DBMS} database.")


    def execute(self, query, arguments=None):
        self.__cursor.execute(query, arguments)
        crud = query.split(' ')[0]
        if crud != 'SELECT':
            self.__connection.commit()


    def fetch_one(self):
        return self.__cursor.fetchone()


    def fetch_all(self):
        return self.__cursor.fetchall()


    def close(self):
        if self.__cursor is not None:
            self.__cursor.close()
        if self.__connection is not None:
            self.__connection.close()
        print('The database connection was closed.')


if __name__ == '__main__':
    Database()

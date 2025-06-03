from mysql.connector import connection, Error
import json

class datadoer:

    def __init__(self):
    
        with open('Logins/databaselogin.txt', 'r') as file:
            lines = file.readlines()
            user = lines[1].split(':', 1)[1].strip()
            password = lines[2].split(':', 1)[1].strip()
            host = lines[3].split(':', 1)[1].strip()
            database = lines[4].split(':', 1)[1].strip()

            self.cnx = connection.MySQLConnection(user=user, password=password,
                                                    host=host,
                                                    database= database)
            self.cursor = self.cnx.cursor()
        

    def write(self, data):
        try:
            self.cursor.executemany("INSERT INTO prodvote VALUES (%s, %s, %s)", data)
            self.cnx.commit()

        except Error as err:
            print(f"Error: {err}")
            return err

    def read_column(self, table_name, column_name):
        try:
            query = f"SELECT `{column_name}` FROM `{table_name}`"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [row[0] for row in results]
        except Error as err:
            print(f"Error: {err}")
            return []


    def convertjson(self, jsonfilepath):
        with open(jsonfilepath, 'r') as file:
            data = json.load(file)
        return [tuple(item.values()) for item in data]


    def close(self):
        self.cursor.close()
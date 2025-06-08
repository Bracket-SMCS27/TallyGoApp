from mysql.connector import connection, Error
import json
import os
import re

class datadoer:

    def __init__(self):
    
        with open('Logins/databaselogin.txt', 'r') as file:
            lines = file.readlines()
            user = lines[1].split(':', 1)[1].strip()
            password = lines[2].split(':', 1)[1].strip()
            host = lines[3].split(':', 1)[1].strip()
            database = lines[4].split(':', 1)[1].strip()

            print(user + password + host + database)

            self.cnx = connection.MySQLConnection(user=user, password=password,
                                                    host=host,
                                                    database= database)
            self.cursor = self.cnx.cursor()
        

    def write(self, data, table):
        try:
            self.cursor.executemany(f"INSERT INTO {table} VALUES (%s, %s, %s)", data)
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

    def validatejson(self, jsonfilepath):
            with open(jsonfilepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

            validated_data = []

            for entry in data:
                problems = []

                # Validate reg_id: must be 5 digits
                if not (isinstance(entry.get("reg_id"), str) and re.fullmatch(r"\d{5}", entry["reg_id"])):
                    problems.append("INVALID_reg_id")

                # Validate id_letter: must be 1-2 alphabetic characters
                if not (isinstance(entry.get("id_letter"), str) and re.fullmatch(r"[A-Za-z]{1,2}", entry["id_letter"])):
                    problems.append("INVALID_id_letter")

                # Validate vote_id: must be 3 digits
                if not (isinstance(entry.get("vote_id"), str) and re.fullmatch(r"\d{3}", entry["vote_id"])):
                    problems.append("INVALID_vote_id")

                # Add invalid marker if any issues
                if problems:
                    entry["__INVALID__"] = ", ".join(problems)

                validated_data.append(entry)

            return validated_data

    def validate_folder(self, folder_path):
        for dirpath, _, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.endswith('.json'):
                    full_path = os.path.join(dirpath, filename)
                    try:
                        validated = self.validatejson(full_path)

                        # Overwrite the original file with validated data
                        with open(full_path, 'w', encoding='utf-8') as f:
                            json.dump(validated, f, indent=4)

                        print(f"Validated and updated: {full_path}")
                    except Exception as e:
                        print(f"Error processing {full_path}: {e}")
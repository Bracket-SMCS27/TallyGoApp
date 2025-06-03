from database import datadoer
import imageai

def start():
    print("Welcome to TallyGo! \n" 
            "Would you like to:\n" 
            "(1):Extract ballot information from images?\n" 
            "(2):Upload the extracted information to your database?")
    response = input(":")

    return response

def image_extract():

        return none

def close():
    print("Thank you for using TallyGo")
    quit()

db = datadoer()

print(db.convertjson("all_results.json"))

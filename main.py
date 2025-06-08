from database import datadoer
import imageai
import time
import asyncio
import os

votetable = ""

def dbWriteHelper():
    db = datadoer()

    # Set root folder path
    root_folder = 'output_folder'
    table = 'prodvote'
    
  
    for dirpath, dirnames, filenames in os.walk(root_folder):
        for filename in filenames:
            if filename.endswith('.json'):
                json_path = os.path.join(dirpath, filename)
                try:
                    records = db.convertjson(json_path)
                    if records:
                        db.write(records, table)
                        print(f"Inserted {len(records)} records from {json_path}")
                    else:
                        print(f"No records in {json_path}")
                except Exception as e:
                    print(f"Error processing {json_path}: {e}")
    db.close()


#-------------------------------------------------------------------------------------------------

def info():
    print("Welcome to TallyGo! \n" 
        "Before you continue please make sure you have read ALL of the instructions provided\n" 
        "This application is not very intuitive to setup")



def start():
    valid = False
    print(
                "Would you like to:\n" 
                "(1):Extract ballot information from images?\n" 
                "(2):Simple data validation. \n" 
                "(3):Upload the extracted information to your database? \n" 
                "(4):Close")

    while(not valid):
        response = input("Input: ")
        if(response != "1" and response != "2" and response != "3" and response != "4"):
            print("Please pick one of the options")
        else:
            valid = True
    if(response == "1"):
        image_extract()
    if(response == "2"):
        validation()
    if(response == "3"):
        enter_to_database()
    else:
        close()
#---------------------------------------------------
def image_extract():
    print("This may take a while")

    start_time= time.time()
    asyncio.run(imageai.main())
    print("time taken:" + str(time.time()-start_time))

    print("You should check the response for accuracy before entering it into your database!")
    start()

def enter_to_database():
    print("Are you sure you want to enter all information in the file 'all_results.json' into the database?\n" 
            "[y/n]")
    valid = False
    while(not valid):
        response = input("Input: ")
        if(response != "y" and response != "Y" and response != "n" and response != "N"):
            print("Please pick one of the options")
        else:
            valid = True

    if(response == "Y" or response == "y"):
        dbWriteHelper()
        start()
    else:
        start()

def validation():
    print("Currently non-functional")

    db = datadoer()
    db.validate_folder("output_folder")

    start()

def close():
    print("Thank you for using TallyGo :)")
    quit()

#-------------------------------------------------


start()
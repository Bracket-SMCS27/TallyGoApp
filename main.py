from database import datadoer
import imageai
import time
import asyncio


def start():
    valid = False
    print(
                "Would you like to:\n" 
                "(1):Extract ballot information from images?\n" 
                "(2):Upload the extracted information to your database? \n" 
                "(3):Close")

    while(not valid):
        response = input("Input: ")
        if(response != "1" and response != "2" and response != "3"):
            print("Please enter 1, 2, or 3")
        else:
            valid = True
    if(response == "1"):
        image_extract()
    if(response == "2"):
        enter_to_database()
    if(response == "3"):
        close()

def image_extract():

    start_time= time.time()
    asyncio.run(imageai.main())
    print("time taken:" + str(time.time()-start_time))

    print("You should check the response for accuracy before entering it into your database!")
    
    start()

def enter_to_database():
    start()

def close():
    print("Thank you for using TallyGo")
    quit()

print("Welcome to TallyGo!")
start()





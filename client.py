# //-----------------------------------------
# // NAME: Kamarabbas Saiyed
# // STUDENT NUMBER: 7885332
# // COURSE: COMP 4300
# // INSTRUCTOR: Sara Rouhani
# // Assignment 1
# // REMARKS: it is a chat room implementation
# //
# //-----------------------------------------
import socket
import sys
import threading
import json

hostname=sys.argv[1]        # pass the first argument as the hostname 
port=int(sys.argv[2])       # pass the second argument as the port number
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((hostname,port))    # the server first has to be run with a port then client connects to it
myName=input("Enter your name \n")   # it will first ask the name of the user
myRoom=-1                    # when a user is not in a room this will be set to -1 
numRooms=0                   # room number starts from Room 0
rooms=[]

# function to handle if user asks for room info
def handleRoomInfo():
    msg={
        "type":"ROOM-INFO",
        "name": myName,
    }
    client_socket.send(json.dumps(msg).encode())
# function to handle if user asks to create new room
def handleCreateRoom():
    if myRoom==-1:
        msg={
            "type":"CREATE-ROOM",
            "name": myName
        }
        client_socket.send(json.dumps(msg).encode())
    else:
        print("You are currently in a room, leave your room then create a new one.")
# function to handle if user asks to leave room
def handleLeaveRoom():
    myRoom=-1
    msg={
        "type":"LEAVE-ROOM",
        "room":myRoom,
        "name": myName
    }
    client_socket.send(json.dumps(msg).encode())
# function to handle if user wants to send a message
def handleMessage(val): 
    if myRoom!=-1:

        msg={
            "type":"MESSAGE",
            "room":myRoom,
            "message": val,
            "name": myName
        }
        client_socket.send(json.dumps(msg).encode())
    else:
        print("You are not in a room,join a room first")

# function to handle if user wants to join a room with a given room number
def handleJoinRoom(val): 
    msg={
        "type":"JOIN-ROOM",
        "room": int(val),
        "name": myName
    }
    client_socket.send(json.dumps(msg).encode())

# this function will be run in a different thread to take user input so that it doesnt inturrupt receiving messages    

def keyboardInput():
    
    while True:
        inp=input("Enter your command or type 'help' for a list of all commands \n")
        # This is a list of commands a user can type
        if inp == "help":
            print("To get room info - 'ROOM-INFO'")
            print("To join for example room 2 a specific room - 'JOIN-ROOM 2'")
            print("To create a new room - 'CREATE-ROOM'")
            print("To leave your current room - 'LEAVE-ROOM'")
            print("To send a message to current room - MESSAGE Type your message here")

        elif inp== "ROOM-INFO":
            handleRoomInfo()

        elif inp== "CREATE-ROOM":
            handleCreateRoom()

        elif inp== "LEAVE-ROOM":
            handleLeaveRoom()

        elif inp.split(" ")[0]== "MESSAGE":
            handleMessage(inp.split(" ")[1])
        
        elif inp.split(" ")[0]== "JOIN-ROOM":
            handleJoinRoom(inp.split(" ")[1])
        else:
            print("Invalid Input")



    
# this function is to print out the room info
def printRoomInfo(info):
    print("The number of Rooms are "+ str(numRooms))
    if myRoom!=-1:
     print("You are in Room "+ str(myRoom))
    elif numRooms>0:
        print(" The list of available rooms are: Room 0\n")
        for i in range(1,numRooms-1):
            print("Room "+ str(i)+"\n ")
        print("\nYou can join Room 0 to Room "+str(numRooms-1)+"\n")
    print(data["rooms"])
   


thread = threading.Thread(target=keyboardInput)
thread.start()
# this is a forevar loop to receive messages
while True: 
    try:

        data= client_socket.recv(1024)
        data=json.loads(data.decode('UTF-8'))
        # print(data)
        # we will look at differnt types of messages and then handle it accordingly
        if data !={} and data["type"] == "WELCOME":
            print("You are in the chat room. There are "+ str(data["rooms"])+" rooms in total")
            msg={
                "type": "WELCOME-REPLY",
                "name": myName
            }
            client_socket.send(json.dumps(msg).encode())
        elif data !={} and data["type"] == "ROOM-INFO-REPLY":
            numRooms=int(data["roomNum"])
            rooms=data["rooms"]
            printRoomInfo(data)

        
        elif data !={} and data["type"] == "JOIN-ROOM-REPLY":
            if data["status"]=="SUCCESS":
                print("You have successfully joined room "+ str(data["room"]))
                myRoom= int(data["room"])
            else:
                print("You have failed to joined room "+ str(data["room"]) +" either it does not exist or the room has reached max lit of 5 members")

            # data={
            #     "type":"JOIN-ROOM",
            #     "room":1,
            #     "name": "Kam"
            # }

        elif data !={} and data["type"] == "MESSAGE":

            print(data["name"]+": "+ data["message"])
            # data={
            #     "type":"MESSAGE",
            #     "room":1,
            #     "message:"Hi",
            #     "name": "Kam"
            # }

        elif data !={} and data["type"] == "CREATE-ROOM-REPLY":
            if data["status"]=="SUCCESS":
                print("You have successfully created and joined room "+ str(data["room"]))
                myRoom= int(data["room"])
            else:
                print("You have failed to create room "+ str(data["room"]))

            # data={
            #     "type":"JOIN-ROOM",
            #     "room":1,
            #     "name": "Kam"
            # }
            

    except Exception as e:
        print("SOMETHING IS BAD")
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(e, exc_tb.tb_lineno)
        client_socket.close()
        sys.exit()


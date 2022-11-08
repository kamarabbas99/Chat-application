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
import json
import threading
import os

#global variables
# use this if OS name is not know and then pass it to the client.py
# my_hostname=os.environ["HOST"]
my_hostname="localhost"
my_port=8487
users=[]
numChatRooms=0
rooms=[]    # this will store a 2D array with users in each room index, room 0 is the first room
   

server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
server_socket.bind((my_hostname, my_port))
server_socket.listen()
print('Starting server on port: '+str(my_port)) 

#a new thread every time a new user connects with the server

def newUser(conn,addr):
    global numChatRooms
    global rooms
    global users 
    user=""
    room=-1
    imsg={                              #welcome messege sent first when we join the server
        "type": "WELCOME",
        "rooms":numChatRooms,
        "host": my_hostname,
        "port": my_port,
    }
    conn.send(json.dumps(imsg).encode())        
    #forever loop to keep receiving messages
    while True:  

        try:
            data = conn.recv(1024)
            data=json.loads(data.decode('UTF-8'))                  #convert it to a python dict object
            # print(data) 

            # we look at diffrent reply type and then handle it appropriately
            if data !={} and data["type"] == "WELCOME-REPLY":
                users.append((data["name"],conn,addr))
                user=(data["name"],conn,addr)
                print(data["name"]+ str(addr)+" just joined the chat application.")
                # data={               data should look like this
                #     "type": "WELCOME-REPLY",
                #     "name": "KAM"
                # }
            elif data !={} and data["type"] == "ROOM-INFO":
                roomsInfo=''
                for i in range(0,len(rooms)):
                    roomsInfo+="There are "+str(len(rooms[i]))+" users in room "+ str(i) + " which are: \n"
                    for y in rooms[i]:
                        roomsInfo+=str(y[0])
                        roomsInfo+=str(y[2])
                        roomsInfo+="\n"
                msg={
                    "type":"ROOM-INFO-REPLY",
                    "roomNum": numChatRooms,
                    "rooms": roomsInfo,
                }
                conn.send(json.dumps(msg).encode())
                # data={
                #     "type":"ROOM-INFO",
                #     "name":"Kam",
                # }
            
            elif data !={} and data["type"] == "JOIN-ROOM":
                # condition to check if the there are 5 users in the room if there are, user cant join the room
                if data["room"]< len(rooms) and len(rooms[data["room"]])<5 and user in users:
                    rooms[data["room"]].append(user)
                    msg={
                        "type":"JOIN-ROOM-REPLY",
                        "status":"SUCCESS",
                        "room": data["room"]
                    }
                    room=data["room"]
                    conn.send(json.dumps(msg).encode())
                else:
                    msg={
                        "type":"JOIN-ROOM-REPLY",
                        "status":"FAIL",
                        "room": data["room"]
                    }
                    conn.send(json.dumps(msg).encode())
                # data={
                #     "type":"JOIN-ROOM",
                #     "room":1,
                #     "name": "Kam"
                # }
     

            elif data !={} and data["type"] == "LEAVE-ROOM":
                userRoom=data["room"]
                if user in rooms[userRoom]:
                    rooms[userRoom].remove(user)
                    room=-1
                else:
                    print("user not in the room")



                # data={
                #     "type":"LEAVE-ROOM",
                #     "room":1,
                #     "name": "Kam"
                # }
     
            elif data !={} and data["type"] == "MESSAGE":
                userRoom=data["room"]
                # send message to every other user in that room
                if user in rooms[userRoom]:
                    for x in rooms[userRoom]:
                        x[1].send(json.dumps(data).encode())

                else:
                    print("user is not in the room")

                # data={
                #     "type":"MESSAGE",
                #     "room":1,
                #     "message:"Hi",
                #     "name": "Kam"
                # }
             
            elif data !={} and data["type"] == "CREATE-ROOM":
                rooms.append([])    #append a new empty list at the end rooms 
                msg={
                    "type":"CREATE-ROOM-REPLY",
                    "status":"SUCCESS",
                    "room": numChatRooms
                }
                rooms[numChatRooms].append(user)
                print("Room "+ str(numChatRooms)+" was created by "+ data["name"])
                room=numChatRooms
                numChatRooms+=1

                conn.send(json.dumps(msg).encode())
 
                
                # data={
                #     "type":"CREATE-ROOM",
                #     "name": "Kam"
                # }

            


        except KeyboardInterrupt:
            print("Closing the socket")                
            server_socket.close()
            sys.exit()
            os._exit(0)


        except Exception as e: 
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e, exc_tb.tb_lineno)
           # if any client leaves or closes the program the we will remove that user from 
           # from the user list and the rooms, close the socket and exit the thread
            if user in users:
                users.remove(user)        
            if user in rooms[room]:
                rooms[room].remove(user)
            conn.close()
            sys.exit()
            
# this is a forevar loop which will keep accepting connection requests and then start a new thread which will then receive and send messages for that particular client
while True: 
    conn, addr = server_socket.accept()
    thread = threading.Thread(target=newUser,args=(conn,addr))
    thread.start()
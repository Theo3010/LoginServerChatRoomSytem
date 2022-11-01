import sys
import time
import json
sys.path.insert(0, '..')

from LoginSystem.LoginSystem import loginSystem, encryptDecrypt
from Network.Network import Network
import threading
import datetime

def convertListToStr(list):
    str = ""
    for i in list:
        str += i + " "
    return str[:-1]

class Server(object):
    def __init__(self, host, port) -> None:
        self.Network = Network(host, port)
        self.clock = datetime.datetime.now().strftime("%H:%M:%S")
        self.conns = []
        self.addrs = []
        self.usernames = [] # rewrite username to [{"username":<username>, "addr":<addr>, "conn":<conn>}]
        self.bannedUsers = json.load(open("BannedUsers.json", "r"))["bannedUsers"]
        self.commands = {"self.login":self.login, "self.signin":self.signin}
    
    def login(self, conn, addr):
        username = self.Network.recv(conn)
        password = self.Network.recv(conn)
        for banneduser in self.bannedUsers:
            if username == banneduser["name"]:
                print(f"<{username}> tried to login but is banned")
                self.Network.send(conn, "Banned")
                self.Network.send(conn, banneduser["reasons"])
                return False
        
        for user in self.usernames:
            if username == user["username"]:
                self.Network.send(conn, "allreadyLogggedIn")
                return False
        
        if loginSystem().login(username, password):
            
            self.Network.send(conn, "True")
            
            self.usernames.append({"username":username, "addr":addr, "conn":conn})
            
            print(f"[{username}] Logged in")
            
            return self.chat(conn, username)
        
        self.Network.send(conn, "False")
        return False
    
    def signin(self, conn, addr):
        username = self.Network.recv(conn)
        password = self.Network.recv(conn)
        
        if loginSystem().signin(username, password): 
            
            self.Network.send(conn, "True")
            self.usernames.append({"username":username, "addr":addr, "conn":conn})
            
            print(f"[{username}] signed in")
            
            return self.chat(conn, username)
        return False

    def chat(self, conn, username):
        ServerOrClient = "Client"
        while self.Network.serverRunning:
            self.clock = datetime.datetime.now().strftime("%H:%M:%S")
            msg = self.Network.recv(conn)
            
            if not msg:
                return False
            
            print(f"[{self.clock}, Client] <{username}> {msg}")
            self.brodcast(ServerOrClient, username, msg)
        
        return False
    
    def ServerConnect(self):
        while self.Network.serverRunning:
            try:
                conn, addr = self.Network.ServerConnect()
                self.conns.append(conn)
                self.addrs.append(addr)
                threading.Thread(target=self.ClientHandler, args=(conn, addr)).start()
            except Exception as e:
                #print(e)
                print("Server closing")
                break
    
    def ClientHandler(self, conn, addr):
        if conn:
            connected = True
        
        while connected:
            inputCommand = self.Network.recv(conn)
            if not inputCommand:
                connected = False
            
            for command in self.commands:
                if inputCommand == str(command):
                    if not self.commands[command](conn, addr):
                        connected = False
        
        conn.close()
        self.Network.connnections -= 1
        self.conns.remove(conn)
        self.addrs.remove(addr)
        try:
            for user in self.usernames:
                if user["addr"] == addr and user["conn"] == conn:
                    del user
        except Exception:
            pass

    def brodcast(self, ServerOrClient, username, msg):
        """
        Send a msg to all Clients
        
        Input: (ServerOrClient: server/client, username: str, msg: str) # messageFromclient: boolen
        """
        for conn in self.conns:
            self.Network.send(conn, ServerOrClient)
            self.Network.send(conn, username)
            self.Network.send(conn, msg)
    
    def ServerInput(self,): 
        """
        Commmands for the server.

        VaildCommands: quit, list, ban
        
        """
        if not self.Network.serverRunning: # wait for server to start running.
            time.sleep(5)
            self.ServerInput()
        
        while self.Network.serverRunning:
            rawcommand = input("") # get command input
            vaildUsername = False
            command, args = rawcommand.split(" ")[0], rawcommand.split(" ")[1:]
            
            # dict for vaild command with description
            commands = {"quit": " shutdown the server",
                        "list": " view a list of the users online",
                        "ban": " ban a user from logging in.",
                        "banlist": " show a list of the banned users",
                        "unban": " remove a ban form a user",
                        "say": " broadcast a msg to all users online",
                        "help": " shows this list",
                        "?": " --> help"}
            
            if command == "quit" or command == "/quit":
                # shutdown server
                self.Network.serverRunning = False
                self.Network.ServerDisconnect()
            
            elif command == "list" or command == "/list":
                print(f"[{self.clock}, SERVER] Total Connections: {self.Network.connnections}") # total connections
                for user in self.usernames:
                    print(f"--->Users: {user['username'], user['addr']}") # print all users
            
            elif command == "ban" or command == "/ban":
                # check for args
                if not args:
                    print(f"[{self.clock}, SERVER] Invaild arguments for ban command. ban <username> <reason (optional)> ")
                    continue
                user = args[0]
               
                # check if username is vaild
                usernames = json.load(open("Users.json", "r"))["Users"]      
                for users in usernames: 
                    if users == encryptDecrypt().encryptUsername(args[0]):
                        vaildUsername = True
                
                # check if user is allready banned
                for banneduser in self.bannedUsers:
                    if banneduser["name"] == args[0]:
                        print(f"[{self.clock}, SERVER] Users allready banned")
                        vaildUsername = False
                
                # print error to screen
                if not vaildUsername:
                    print(f"[{self.clock}, SERVER] Invaild users...")
                    continue
                
                
                reason = "Banned by Operator"
                
                if args[1:]:
                    reason = convertListToStr(args[1:])
                
                for listofuser in self.usernames:
                    if listofuser["username"] == user:
                        self.Network.send(listofuser["conn"], "Banned")
                        self.Network.send(listofuser["conn"], reason)

                # update bannedusers list
                self.bannedUsers.append({"name":user, "reasons":reason})
                
                # update bannedusers file
                with open("bannedUsers.json", "r+") as file:
                    data = json.load(file)
                    data["bannedUsers"].append({"name":user, "reasons":reason})
                    file.seek(0)
                    json.dump(data, file, indent=4)
                
                print(f"[{self.clock}, SERVER] <{user}> is now banned")

            elif command == "unban" or command == "/unban":
                # check for args
                if not args:
                    print(f"[{self.clock}, SERVER] invaild arguments for ban command. unban <username> ")
                    continue
                
                # if user allready banned
                for banneduser in self.bannedUsers:
                    if banneduser["name"] == args[0]:
                        self.bannedUsers.remove({"name":args[0], "reasons":banneduser["reasons"]})
                        json.dump({"bannedUsers": self.bannedUsers}, open("bannedUsers.json", "w"), indent=4)
            
                        print(f"[{self.clock}, SERVER] <{args[0]}> is now unbanned")
                    else:
                         print(f"[{self.clock}, SERVER] Users not banned")
            
            elif command == "banlist" or command == "/banlist":
                print(f"[{self.clock}, SERVER] {len(self.bannedUsers)} total bans:") # total bans
                for banneduser in self.bannedUsers:
                    print(f"[{self.clock}, Server] {banneduser['name']}: {banneduser['reasons']}") # print all banned users

            elif command == "say" or command == "/say":
                msg = convertListToStr(args) # msg to send to the client
                print(f"[{self.clock}, Server] <Server> {msg}") # print the msg
                self.brodcast("SERVER", "server", msg) # send the msg
            
            elif command == "help" or command == "/help" or command == "?":
                print(f"Commands:") 
                for key in commands:
                    print(f"-->{key}:{commands[key]}") # list of all the commands
            
            else:
                print(f"[{self.clock}, Server] Invaild command. /help or ? for list off command") # print if invaild command

    def __call__(self):
        threading.Thread(target=self.ServerInput, ).start() # command
        self.Network.StartServer() # start socket server
        self.ServerConnect() # connect server
         


if __name__ == "__main__":
    Server("localhost", 5050)()

import datetime
import sys
import threading
import time

sys.path.insert(0, '..')

from Network.Network import Network


class Client(object):
    def __init__(self, host, port) -> None:
        super().__init__()
        self.Network = Network(host, port)
        self.clock = datetime.datetime.now().strftime("%H:%M:%S")
        self.IsRunning = True
    
    def Connect(self):
        self.Client = self.Network.ClientConnect()
        if not self.Client:
            print("Server is not running")
            return False
        return True
    
    def disconnect(self):
        self.IsRunning = False
        self.Network.send(self.Client, "Disconnected")
        time.sleep(.1)
        self.Network.ClientDisconnect(self.Client)
        quit()
    
    def send(self):
        while self.IsRunning:
            msg = input("")
            if not msg or not self.IsRunning:
                continue
            if msg[0] == "/":
                self.command(msg.lower())
            else:
                self.Network.send(self.Client, msg)
            time.sleep(.5)
    
    def command(self, msg):
        if msg == "/quit": 
            self.disconnect()
        # elif msg == "/w":
            # whisper
    
    def recv(self):
        while self.IsRunning:
            self.clock = datetime.datetime.now().strftime("%H:%M:%S")
            
            ClientOrServer = self.Network.recv(self.Client)
            if not ClientOrServer:
                self.disconnect()
            if ClientOrServer == "Banned":
                reason = self.Network.recv(self.Client)
                print(f"You got banned\nReason: {reason}")
                self.disconnect()
            username = self.Network.recv(self.Client)
            msg = self.Network.recv(self.Client)
            
            print(f"[{self.clock}, {ClientOrServer}] <{username}> {msg}")

    def chat(self):
        threading.Thread(target=self.send, ).start()
        threading.Thread(target=self.recv, ).start()

    def LoginSignin(self):
        logsign = input("LogIn or signIn [l/s]: ").lower()
        if logsign == "l" or logsign == "login":
            
            self.Network.send(self.Client, "self.login")
            self.UserInfoToserver()
            loginInfo = self.Network.recv(self.Client)
            
            if loginInfo == "True":
                print("You are now Logged in")
                self.chat()
            
            elif loginInfo == "Banned":
                reasons = self.Network.recv(self.Client)
                print(f"You are banned\nReason: {reasons}")
                self.Network.ClientDisconnect(self.Client)
            
            elif loginInfo == "allreadyLogggedIn":
                print(f"The users is allready online")
                self.Network.ClientDisconnect(self.Client)
            
            else:
                print("Invaild username or password")
                self.IsRunning = False
                self.Network.ClientDisconnect(self.Client)
        
        elif logsign == "s" or logsign == "signin":
            
            self.Network.send(self.Client, "self.signin")
            self.UserInfoToserver()
            
            if self.Network.recv(self.Client) != "False":
                print("You are now signed in")
                self.chat()
            else:
                self.IsRunning = False
                self.Network.ClientDisconnect(self.Client)
                quit()
        
        else:
            print("Not a vaild input....")
            self.LoginSignin()

    def UserInfoToserver(self):
        self.username = input("Username: ")
        self.Network.send(self.Client, self.username)
        self.Password = input("Password: ")
        self.Network.send(self.Client, self.Password)

    def __call__(self):
        if not self.Connect():
            quit()
        self.LoginSignin()



if __name__ == "__main__":
    Client("10.43.189.6", 8002)()

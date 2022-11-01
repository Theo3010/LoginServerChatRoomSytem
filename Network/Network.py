import socket
import sys
import threading
import time
import os

class Network(object):
    def __init__(self, host, port) -> None:
        super().__init__()
        self.serverRunning = False
        self.connnections = 0
        self.FORMAT = "utf-8"
        self.host = host
        self.port = port
        self.DISCONNECT_MESSAGE = "DISCONNECT"

    def StartServer(self):
        self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ServerSocket.bind((self.host, self.port))
        self.ServerSocket.listen()
        self.serverRunning = True
    
    def ServerConnect(self):
        conn, addr = self.ServerSocket.accept()
        self.connnections += 1
        print(f"[SERVER] Connection: {addr}, {self.connnections} connected in total")
        return conn, addr
    
    def ClientConnect(self):
        try:
            self.connecting = True
            threading.Thread(target=self.connectingMsg, ).start()
            IP = (self.host, self.port)
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(IP)
            self.connecting = False
            return client
        except:
            self.connecting = False
            return False
    
    def connectingMsg(self):
        i = 1
        while self.connecting:
            text = "connecting" + "." * i
            sys.stderr.write(text + "\r")
            sys.stderr.flush()
            time.sleep(1)
            i += 1
            if i >= 4:
                i = 1
        
    def recv(self, conn):
        size = conn.recv(1024).decode(self.FORMAT)
        if not size:
            return False
        msg = conn.recv(int(size)).decode(self.FORMAT)
        
        if msg == self.DISCONNECT_MESSAGE:
            return False
        return msg
        #TODO: size not being integer ('11!DISCONNECT'), can't decode some symbols (¨)
    
    def send(self, conn, msg):
        try:
            # Check for invaild symbols
            CanBeEncoded = b""
            for charcaters in str(msg):
                try:
                    CanBeEncoded += charcaters.encode(self.FORMAT)
                except Exception as e:
                    # print(e) # DEBUG
                    pass

            # send the length of the actual message
            time.sleep(.1)
            conn.send(str(len(CanBeEncoded)).encode(self.FORMAT))
            
            # send the messsage
            time.sleep(.1)
            conn.send(CanBeEncoded)
       
        except Exception as e:
            print(e) # DEBUG
            return False
        
        return True
    
    def ClientDisconnect(self, conn):
        time.sleep(.5)
        self.send(conn, self.DISCONNECT_MESSAGE)
    
    def ServerDisconnect(self):
        self.ServerSocket.close()

def main():
    n = Network("10.43.189", "5353")
    print(n.ClientConnect())


if __name__ == "__main__":
    main()
   

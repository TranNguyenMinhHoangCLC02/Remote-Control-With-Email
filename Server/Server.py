import socket
import tkinter as tk
from PIL import Image, ImageTk

from mySocket import MySocket
import appController
import processController
import ftpController
import keyboardController
import macAddress
import powerController
import registryController
import streamingClient

PORT = 5000
PORT_STREAM = 5500
PORT_FTP = 5999

appbg = "#232631"
btnbg = "#141414"
btnfg = "white"

class Server(tk.Frame):
    def __init__(self, master = None):
        self.__host = ''
        self.__port = PORT
        self.__portStream = PORT_STREAM
        self.__portFTP = PORT_FTP
        self.__client = None
        
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.master.resizable(False,False)
        self.createWidgets()

    #DESIGN
    def createWidgets(self):

        self.frame0 = tk.Frame(self,background=appbg)
        self.frame0.place(x=0, y=0, height=140, width=220)

        img = Image.open("logo.png")
        img =img.resize((60,100))
        self.img=ImageTk.PhotoImage(img)
        self.theme=tk.Label(self.frame0,image=self.img,background=appbg)
        self.theme.place(x=20, y=20)
        img.close()

        #Button1
        self.butConnect = tk.Button(self.frame0,text = "Open server",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.butConnect["command"] = self.buttonClick
        self.butConnect.place(x=100, y=20, height=100, width=100)   
        
    def buttonClick(self):
        self.__serverSocket = MySocket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind((self.__host, self.__port))
        self.__serverSocket.listen(1)
        print("Waiting for connection...")
        self.__client, addr = self.__serverSocket.accept()

        self.appController = appController.AppController(self.__client)
        self.processController = processController.ProcessController(self.__client)
        self.ftpController = ftpController.FtpController(self.__client, addr[0], self.__portFTP)
        self.keyboardController = keyboardController.KeyboardController(self.__client)
        self.macAddress = macAddress.MacAddress(self.__client)
        self.powerController = powerController.PowerController(self.__client)
        self.registryController = registryController.RegistryController(self.__client)
        self.screenShareClient = streamingClient.ScreenShareClient(addr[0],self.__portStream, self.__client)

        while True:
            buffer = self.__client.recv(1024)
            
            if not buffer:
                break
            message = buffer.decode('utf-8')

            if message == "APP":
                self.appController.startListening()
            elif message == "PROCESS":
                self.processController.startListening()
            elif message == "FTP":
                self.ftpController.startListening()
            elif message == "KEYBOARD":
                self.keyboardController.startListening()
            elif message == "MACADDRESS":
                self.macAddress.startListening()
            elif message == "POWER":
                self.powerController.startListening()
            elif message == "REGISTRY":
                self.registryController.startListening()
            elif message == "STREAM":
                self.screenShareClient.startListening()
            elif message == 'EXIT':
                self.__serverSocket.close()
                self.screenShareClient.stop_stream()
                break
            else:
                break
        self.__serverSocket.close()
        

def CloseButton(root):
    root.destroy()

root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', lambda: CloseButton(root))
root.iconbitmap(default='serverIcon.ico')
app = Server(root)
app.master.title('SUPER CONTROLLER Server')
app.master.minsize(220, 140)
app.mainloop()

import socket
import tkinter as tk

from tkinter import Label, ttk
from tkinter import Image, messagebox, filedialog
from tkinter import END,INSERT
from tkinter.constants import E
from tkinter.font import BOLD

from PIL import Image
from PIL import ImageTk

import cv2

import pickle
import struct
import threading
import json

import os
from posixpath import relpath
import psutil
import shutil
import win32com.client

from mySocket import MySocket

PORT = 5000
PORT_STREAM = 5500
PORT_FTP = 5999

clientSocket = None
streamSocket = None

IS_STREAM_TAB_FLAG = False
FLAG_CLOSE = 0
CHUNKSIZE = 1024*1024
METADATA = ['Name', 'Size', 'Item type', 'Date modified', 'Date created']

appbg = "#232631"
appfg = "white"

outbtnbg = "#ff970c"
outbtnfg = "black"

btnbg = "#141414"
btnfg = "white"

entrybg = "black"
entryfg = "#0bcdf2"

txtbg = "black"
txtfg = "#0bcdf2"

def closeButton(root, FLAG_CLOSE):
    if FLAG_CLOSE == 0:
        closeClient(root)
    elif FLAG_CLOSE == 1:
        closeStream(root)

def closeClient(root):
    try:
        s = "EXIT"
        clientSocket.send(s.encode("utf-8"))
    except:
        None
    root.destroy()

def closeStream(root):
    global streamSocket 
    if IS_STREAM_TAB_FLAG:
        try:
            s = "stop"
            clientSocket.send(s.encode("utf-8"))
        except:
            pass
        
    try:
        streamSocket.stop_server()
    except Exception as E:
        pass
    streamSocket = None
    root.destroy()


class StreamingServer:  
    def __init__(self, host, port, window, screen):
        self.__host = host
        self.__port = port
        self.__running = False
        self.__block = threading.Lock()
        self.__server_socket = None
        self.__window = window
        self.__screen = screen
        self.__img = None
        self.__init_socket()

    def __init_socket(self):
        """
        Binds the server socket to the given host and port
        """
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind((self.__host, self.__port))

    def start_server(self):
        """
        Starts the server if it is not running already.
        """
        if self.__running:
            print("Server is already running")
        else:
            self.__running = True
            server_thread = threading.Thread(target=self.__server_listening)
            server_thread.daemon = True
            server_thread.start()

    def __server_listening(self):
        """
        Listens for new connections.
        """
        self.__server_socket.listen()
        while self.__running:
            self.__block.acquire()
            connection, address = self.__server_socket.accept()

            self.__block.release()
            thread = threading.Thread(target= self.__client_connection, args=(connection, address,))
            thread.start()

    def stop_server(self):
        """
        Stops the server and closes all connections
        """
    
        if self.__running:
            self.__running = False
            closing_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.__host == '':
                closing_connection.connect(("localhost", self.__port))
            else:   
                closing_connection.connect((self.__host, self.__port))
            closing_connection.close()
            self.__block.acquire()
            self.__server_socket.close()
            self.__block.release()
        else:
            print("Server not running!")

    def __client_connection(self, connection, address):
        """
        Handles the individual client connections and processes their stream data.
        """
        payload_size = struct.calcsize('>L')
        data = b""

        while self.__running:

            break_loop = False

            while len(data) < payload_size:
                try:
                    received = connection.recv(4096)
                except:
                    connection.close()
                    break_loop = True
                    closeStream(self.__window)
                    break
                data += received

            if break_loop:
                break

            packed_msg_size = data[:payload_size]
            data = data[payload_size:]

            msg_size = struct.unpack(">L", packed_msg_size)[0]

            while len(data) < msg_size:
                data += connection.recv(4096)

            frame_data = data[:msg_size]
            data = data[msg_size:]

            frame = pickle.loads(frame_data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

            try:
                self.__img = ImageTk.PhotoImage(Image.fromarray(frame))  
                self.__screen.configure(image=self.__img) 
                self.__screen.image = self.__img
            except:
                self.__running = False





class Client(tk.Frame):

    #--------------------GENERAL----------------------------------------
    def __init__(self, root):
            super(Client, self).__init__()
            self.root=root
            self.root.title("SUPER CONTROLLER")
            self.root.geometry("740x635")
            self.root.resizable(False,False)
            self.root.grab_set()
            self.createWidgets()
            self.firstChanged = True
            self.FTPStart = True

    def checkConnected(self):
        if clientSocket == None:
            messagebox.showinfo("Error", "Connection lost")
            return False
        else: return True

    def butConnectClick(self, event = None):
        test = True
        global clientSocket
        try:
            clientSocket = MySocket(socket.AF_INET, socket.SOCK_STREAM)
            self.host = self.ipConnect.get().strip()
            clientSocket.connect((self.host, PORT))
        except:
            print ("Fail to connect with the socket-server")
            clientSocket= None
            test = False
        if test:
            messagebox.showinfo("", "Success")
            for i in range(0,8):
                self.tabControl.tab(i,state="normal")
            self.tabControl.select(0)
            self.tabControl.bind('<<NotebookTabChanged>>', self.on_tab_change)
            self.butDisconnect.config(state="normal")
            self.butConnect.config(state="disabled")
        else:
            messagebox.showinfo("Error", "Not connected to the server")

    def butDisconnectClick(self, event = None):
        global clientSocket
        try:
            clientSocket.send("quit".encode('utf-8'))
            clientSocket.send("EXIT".encode('utf-8'))
            clientSocket.close()
            clientSocket = None
        except:
            pass
        clientSocket = None
        for i in range(0,8):
                self.tabControl.tab(i,state="disabled")
        self.firstChanged = True
        self.FTPStart = True
        self.butConnect.config(state="normal")
        self.butDisconnect.config(state="disabled")

    def on_tab_change(self,event=None):
        global IS_STREAM_TAB_FLAG
        if  clientSocket == None:
            return

        if self.firstChanged == False:
            try:
                clientSocket.send("quit".encode('utf-8'))
            except:
                messagebox.showwarning("Disconnect", "Lost connection with server")
                self.butDisconnectClick()
        else: self.firstChanged = False

        self.root.geometry("745x635")
        self.frame1.place(width=605)

        tabName = self.tabControl.tab(self.tabControl.select(),"text")
        IS_STREAM_TAB_FLAG = False
        s = ""
        if tabName == "APPS\nCONTROLLER":
            s = "APP"
        elif tabName == "PROCESSES\nCONTROLLER":
            s = "PROCESS"
        elif tabName == "FTP\nCONTROLLER":
            s = "FTP"
        elif tabName == "KEYBOARD\nCONTROLLER":
            s = "KEYBOARD"
        elif tabName == "MAC\n    ADDRESS    ":
            s = "MACADDRESS"
        elif tabName == "POWER\nCONTROLLER":
            s = "POWER"
        elif tabName == "STREAMING\nCONTROLLER":
            s = "STREAM"
            IS_STREAM_TAB_FLAG = True
        elif tabName == "REGISTRY\nCONTROLLER":
            s = "REGISTRY"
        clientSocket.send(s.encode('utf-8'))

        if s == "FTP":
            self.root.geometry("1045x635")
            self.frame1.place(width=905)
            self.gettingStarted()
        elif s == "STREAM":
            self.root.geometry("1045x635")
            self.frame1.place(width=905)
        elif s == "KEYBOARD":
            self.setKeyboardUI()
            


    #--------------------TAB1 2 APP PROCESS----------------------------------------
    def doTab12Popup(self,event):
        tabName = self.tabControl.tab(self.tabControl.select(),"text")
        if tabName == "APPS\nCONTROLLER":
            tab = self.tab1
        elif tabName == "PROCESSES\nCONTROLLER":
            tab = self.tab2
        try:
            tab.popup.selection = tab.tv1.set(tab.tv1.identify_row(event.y))
            tab.popup.post(event.x_root, event.y_root)
        finally:
            tab.popup.grab_release()
    
    def killRightClick(self):
        if not self.checkConnected():
            return
        s = "kill"
        clientSocket.send(s.encode('utf-8'))
        tabName = self.tabControl.tab(self.tabControl.select(),"text")
        if tabName == "APPS\nCONTROLLER":
            id = self.tab1.popup.selection
        elif tabName == "PROCESSES\nCONTROLLER":
            id = self.tab2.popup.selection
        if id == {}: return
        clientSocket.send(id["2"].encode('utf-8'))
        buffer = clientSocket.recv(4096)
        if not buffer:
            return
        message = buffer.decode('utf-8')
        messagebox.showinfo("", message,parent = self)
        self.butRefreshClick()

    def clearTreeView(self, tree):
        rows = tree.get_children()
        if rows != '()':
            for row in rows:
                tree.delete(row)
    
    def butRefreshClick(self):
        if not self.checkConnected():
           return
        s = "view"
        clientSocket.send(s.encode('utf-8'))
        size = int(clientSocket.recv(10).decode('utf-8'))
        clientSocket.send("OK".encode('utf-8'))
        tabName = self.tabControl.tab(self.tabControl.select(),"text")
        if tabName == "APPS\nCONTROLLER":
            tab = self.tab1
        elif tabName == "PROCESSES\nCONTROLLER":
            tab = self.tab2
        tab.data = []
        buffer = "".encode("utf-8")
        while size > 0:
               data = clientSocket.recv(4096)
               size -= len(data)
               buffer += data
        tab.data = json.loads(buffer.decode("utf-8"))
        self.clearTreeView(tab.tv1)
        rows = tab.data
        for row in rows:
            tab.tv1.insert("", "end", values=row)

    def butKillClick(self, event = None):
        if not self.checkConnected():
            return
        s = "kill"
        clientSocket.send(s.encode('utf-8'))
        tabName = self.tabControl.tab(self.tabControl.select(),"text")
        if tabName == "APPS\nCONTROLLER":
            tab = self.tab1
        elif tabName == "PROCESSES\nCONTROLLER":
            tab = self.tab2
        s = tab.killID.get().strip()
        clientSocket.send(s.encode('utf-8'))
        buffer = clientSocket.recv(4096)
        if not buffer:
            return
        message = buffer.decode('utf-8')
        self.butRefreshClick()
        messagebox.showinfo("", message,parent = self)


    def butStartClick(self, event = None):
        if not self.checkConnected():
            return
        s = "start"
        clientSocket.send(s.encode('utf-8'))
        tabName = self.tabControl.tab(self.tabControl.select(),"text")
        if tabName == "APPS\nCONTROLLER":
            tab = self.tab1
        elif tabName == "PROCESSES\nCONTROLLER":
            tab = self.tab2
        s = tab.startID.get().strip()
        clientSocket.send(s.encode('utf-8'))
        buffer = clientSocket.recv(4096)
        if not buffer:
            return
        message = buffer.decode('utf-8')
        self.butRefreshClick()
        messagebox.showinfo("", message, parent = self)




    #--------------------TAB3 FTP----------------------------------------
    def doTab3Popup1(self,event):
        try:
            self.tab3.popup1.selection = self.tab3.tv1.set(self.tab3.tv1.identify_row(event.y))
            self.tab3.popup1.post(event.x_root, event.y_root)
        finally:
            self.tab3.popup1.grab_release()

    def doTab3Popup2(self,event):
        try:
            self.tab3.popup2.selection = self.tab3.tv2.set(self.tab3.tv2.identify_row(event.y))
            self.tab3.popup2.post(event.x_root, event.y_root)
        finally:
            self.tab3.popup2.grab_release()

    def getFileMetadata(self, fullPath, metadata):
        path, filename = os.path.split(fullPath)
        sh = win32com.client.gencache.EnsureDispatch('Shell.Application', 0)
        ns = sh.NameSpace(path)
        file_metadata = dict()
        item = ns.ParseName(str(filename))
        for ind, attribute in enumerate(metadata):
            attr_value = ns.GetDetailsOf(item, ind)
            if attr_value:
                file_metadata[attribute] = attr_value
        return file_metadata

    def getFolderInfo(self, path):
        self.info = []
        for root, subfolder, files in os.walk(path):
            for i in files:
                dict = self.getFileMetadata(os.path.join(path,i),METADATA)
                self.info.append([dict['Name'], dict['Size'], dict['Item type']])
            for i in subfolder:
                self.info.append([i, '', 'File folder'])
            break
        return self.info

    def displayInfo(self, tree, infos):
        self.clearTreeView(tree)
        for info in infos:
            tree.insert("", "end", values=info)

    def displayDrive(self):
        drps = psutil.disk_partitions()
        self.tab3.clientPath = ""
        self.tab3.clientInfos = [[dp.device, '', 'File folder'] for dp in drps if dp.fstype == 'NTFS']
        self.displayInfo(self.tab3.tv1,self.tab3.clientInfos)
        self.tab3.clientPathtxt.configure(state="normal")
        self.tab3.clientPathtxt.delete('1.0', END)
        self.tab3.clientPathtxt.insert(END,self.tab3.clientPath)

    def gettingStarted(self):
        #if self.FTPStart == True:
            self.displayDrive()
            size = int(clientSocket.recv(10).decode('utf-8'))
            clientSocket.send("OK".encode('utf-8'))
            buffer = "".encode("utf-8")
            while size > 0:
                data = clientSocket.recv(4096)
                size -= len(data)
                buffer += data
            self.tab3.serverPath = ""
            self.tab3.serverInfos = json.loads(buffer.decode("utf-8"))
            self.displayInfo(self.tab3.tv2,self.tab3.serverInfos)
            self.tab3.serverPathtxt.configure(state="normal")
            self.tab3.serverPathtxt.delete('1.0', END)
            self.tab3.serverPathtxt.insert(END,self.tab3.serverPath)
            self.FTPStart = False

    def butClientPreviousPathClick(self, event = None):
        l = len(self.tab3.clientPath)
        if self.tab3.clientPath[l-2:-1] == ":":
            self.displayDrive()
            return
        elif self.tab3.clientPath =="": return
        self.tab3.clientPath, tail = os.path.split(self.tab3.clientPath)
        self.tab3.clientInfos = self.getFolderInfo(self.tab3.clientPath)
        self.displayInfo(self.tab3.tv1,self.tab3.clientInfos)
        self.tab3.clientPathtxt.configure(state="normal")
        self.tab3.clientPathtxt.delete('1.0', END)
        self.tab3.clientPathtxt.insert(END,self.tab3.clientPath)
        self.tab3.clientPathtxt.configure(state="disabled")

    def butServerPreviousPathClick(self, event = None):
        if not self.checkConnected():
            return
        s = "back"
        clientSocket.send(s.encode('utf-8'))
        size = int(clientSocket.recv(10).decode('utf-8'))
        clientSocket.send("OK".encode('utf-8'))
        buffer = "".encode("utf-8")
        while size > 0:
               data = clientSocket.recv(4096)
               size -= len(data)
               buffer += data
        l = len(self.tab3.serverPath)
        if self.tab3.serverPath[l-2:-1] == ":":
            self.tab3.serverPath = ""
        else:
            self.tab3.serverPath, tail = os.path.split(self.tab3.serverPath)
        self.tab3.serverInfos = json.loads(buffer.decode("utf-8"))
        self.displayInfo(self.tab3.tv2,self.tab3.serverInfos)
        self.tab3.serverPathtxt.configure(state="normal")
        self.tab3.serverPathtxt.delete('1.0', END)
        self.tab3.serverPathtxt.insert(END,self.tab3.serverPath)
        self.tab3.serverPathtxt.configure(state="disabled")

    def viewServerFolder(self,serverPath):
        if not self.checkConnected():
            return
        s = "view"
        clientSocket.send(s.encode('utf-8'))
        self.tab3.serverPath = serverPath
        clientSocket.send(self.tab3.serverPath.encode('utf-8'))
        size = int(clientSocket.recv(10).decode('utf-8'))
        clientSocket.send("OK".encode('utf-8'))
        buffer = "".encode("utf-8")
        while size > 0:
               data = clientSocket.recv(4096)
               size -= len(data)
               buffer += data
        self.tab3.serverInfos = json.loads(buffer.decode("utf-8"))
        self.displayInfo(self.tab3.tv2,self.tab3.serverInfos)
        self.tab3.serverPathtxt.configure(state="normal")
        self.tab3.serverPathtxt.delete('1.0', END)
        self.tab3.serverPathtxt.insert(END,self.tab3.serverPath)
        self.tab3.serverPathtxt.configure(state="disabled")

    def clientOnDoubleClick(self, event = None):
        if self.tab3.tv1.selection() == ():
            return
        item = self.tab3.tv1.selection()[0]
        folderName = self.tab3.tv1.item(item,"value")[0]
        self.tab3.clientPath = os.path.join(self.tab3.clientPath,folderName)
        self.tab3.clientInfos = self.getFolderInfo(self.tab3.clientPath)
        self.displayInfo(self.tab3.tv1,self.tab3.clientInfos)
        self.tab3.clientPathtxt.configure(state="normal")
        self.tab3.clientPathtxt.delete('1.0', END)
        self.tab3.clientPathtxt.insert(END,self.tab3.clientPath)
        self.tab3.clientPathtxt.configure(state="disabled")

    def serverOnDoubleClick(self, event = None):
        if not self.checkConnected():
            return
        if self.tab3.tv2.selection() == ():
            return
        item = self.tab3.tv2.selection()[0]
        folderName = self.tab3.tv2.item(item,"value")[0]
        self.tab3.serverPath = os.path.join(self.tab3.serverPath,folderName)
        self.viewServerFolder(self.tab3.serverPath)    

    def copyToClient(self):
        if not self.checkConnected():
            return
        s = "copy2client"
        clientSocket.send(s.encode('utf-8'))
        info = self.tab3.popup2.selection["1"]
        clientSocket.send(info.encode('utf-8'))
        self.recvData(self.tab3.clientPath)
        self.displayInfo(self.tab3.tv1,self.getFolderInfo(self.tab3.clientPath))

    def deleteClientFile(self):
        info = self.tab3.popup1.selection["1"]
        path = os.path.join(self.tab3.clientPath,info)
        if(os.path.isfile(path)):
            os.remove(path)
        elif(os.path.isdir(path)):
            try:
                shutil.rmtree(path)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        else:
            return
        self.displayInfo(self.tab3.tv1,self.getFolderInfo(self.tab3.clientPath))

    def copyToServer(self):
        if not self.checkConnected():
            return
        s = "copy2server"
        clientSocket.send(s.encode('utf-8'))
        info = self.tab3.popup1.selection["1"]
        pathSend = os.path.join(self.tab3.clientPath,info)
        self.sendData(pathSend)
        self.viewServerFolder(self.tab3.serverPath)

    def deleteServerFile(self):
        if not self.checkConnected():
            return
        s = "delete"
        clientSocket.send(s.encode('utf-8'))
        info = self.tab3.popup2.selection["1"]
        clientSocket.send(info.encode('utf-8'))
        self.viewServerFolder(self.tab3.serverPath)     

    def sendData(self, path):
        ftpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftpClient.connect((self.host, PORT_FTP))

        head, relpath = os.path.split(path)
        if(os.path.isfile(path)):
            clientSocket.send(''.encode())
            self.sendFile(ftpClient, path, relpath)
        elif(os.path.isdir(path)):
            clientSocket.send(relpath.encode())
            self.sendFolder(ftpClient, path)
        else:
            return
        clientSocket.send("DONE".encode())

        ftpClient.close()

    def recvData(self, path):
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSock.bind(('', PORT_FTP))
        serverSock.listen(1)
        clientSock, addr = serverSock.accept()

        folderName = clientSocket.recv(20).decode()
        if folderName == '':
            self.recvFolder(clientSock, path)
        else:
            tempPath = os.path.join(path,folderName)
            if os.path.exists(tempPath) == False:
                os.makedirs(tempPath)
            self.recvFolder(clientSock, tempPath)   

        serverSock.close()
        clientSock.close()

    def sendFile(self, serverSock, fullPath, relpath):
        filesize = os.path.getsize(fullPath)
        clientSocket.send(relpath.encode())
        clientSocket.send(str(filesize).encode())

        # Message when need overwrite, rename or not
        check = clientSocket.recv(10).decode()

        if check == "exists":
            request = None

            MsgBox = tk.messagebox.askyesnocancel('File ' + relpath + ' exist',"Yes to overwrite/ No to rename/ Cancel to cancel copy")
            if MsgBox:
                request = 'overwrite'
            elif MsgBox == False:
                request = 'rename'
            else:
                request = 'pause'

            clientSocket.send(request.encode())
            if request == 'pause':
                return
        else: 
            pass

        with open(fullPath,'rb') as f:
            while True:
                data = f.read(CHUNKSIZE)
                if not data: break
                serverSock.send(data)

    def sendFolder(self, serverSock, srcPath):
        for path,subfolder,files in os.walk(srcPath):
            for file in files:
                fullPath = os.path.join(path,file)
                relpath = os.path.relpath(fullPath,srcPath)
                
                print(f'Sending {relpath}')
                self.sendFile(serverSock, fullPath, relpath)


    def recvFolder(self, clientSock, desPath):
            while True:
                filename = clientSocket.recv(1024).decode()
                if filename== 'DONE':
                    break
                length = int(clientSocket.recv(1024).decode())


                print(f'Downloading {filename}...\n  Expecting {length:,} bytes...',end='',flush=True)

                path = os.path.join(desPath,filename)
                os.makedirs(os.path.dirname(path),exist_ok=True)

                # Check if exists
                request = 'continue'
                if os.path.exists(path):
                    MsgBox = tk.messagebox.askyesnocancel('File ' + filename + ' exist',"Yes to overwrite/ No to rename/ Cancel to cancel copy")
                    if MsgBox:
                        request = 'continue' #overwrite
                    elif MsgBox == False:
                        request = 'continue' #rename
                        i = 1
                        while os.path.exists(path) == True:
                            dir, fileName = os.path.split(path)
                            fileName = f"Copy {i} of " + fileName 
                            path = os.path.join(dir, fileName)
                            i += 1
                    else:
                        request = 'pause'

                    clientSocket.send(request.encode())
                else:
                    clientSocket.send("continue".encode())   

                if request == 'pause':
                    continue
                # Read the data in chunks so it can handle large files.
                with open(path,'wb') as f:
                    while length:
                        chunk = min(length,CHUNKSIZE)
                        data = clientSock.recv(chunk)
                        if not data: break
                        f.write(data)
                        length -= len(data)
                    else: # only runs if while doesn't break and length==0
                        print('Complete')
                        continue

                # socket was closed early.
                print('Incomplete')
                break 




    #--------------------TAB4 KEY----------------------------------------
    def setKeyboardUI(self):
        self.tab4.butLock.config(text = "Lock")
        self.tab4.butUnhook.config(state = "normal")
        self.tab4.butHook.config(state = "normal")

    def butLockClick(self):
        if not self.checkConnected():
           return
        request = self.tab4.butLock["text"].lower()
        clientSocket.send(request.encode())
        if request == "lock":
            self.tab4.butLock.config(text = "Unlock")
        else:
            self.tab4.butLock.config(text = "Lock")

    def butHookClick(self):
        if not self.checkConnected():
           return
        s = "hook"
        clientSocket.send(s.encode('utf-8'))

        self.tab4.butUnhook.config(state = "normal")
        self.tab4.butHook.config(state = "disabled")
        
    def butUnhookClick(self):
        if not self.checkConnected():
           return
        s = "unhook"
        clientSocket.send(s.encode('utf-8'))

        self.tab4.butHook.config(state = "normal")
        self.tab4.butUnhook.config(state = "disabled")
    
    def butPrintClick(self):
        if not self.checkConnected():
           return
        s = "print"
        clientSocket.send(s.encode('utf-8'))
        buffer = clientSocket.recv(4096).decode('utf-8')
        if not buffer or buffer=="No":
            self.tab4.butHook.config(state = "normal")
            self.tab4.butUnhook.config(state = "disabled")
            return
        clientSocket.send("Ok".encode("utf-8"))
        self.tab4.KeyLog = clientSocket.recv(4096).decode("utf-8")

        self.tab4.KeyView.config(state="normal")
        self.tab4.KeyView.insert('end', self.tab4.KeyLog)
        self.tab4.KeyView.pack()
        self.tab4.KeyView.config(state="disabled")
        self.tab4.KeyLog = "" 

        self.tab4.butHook.config(state = "normal")
        self.tab4.butUnhook.config(state = "disabled")

    def butDelClick4(self):
        self.tab4.keyLog = ""
        self.tab4.KeyView.config(state="normal")
        self.tab4.KeyView.delete('1.0','end')
        self.tab4.KeyView.pack()
        self.tab4.KeyView.config(state="disabled")




    #--------------------TAB5 MAC----------------------------------------
    def butGetMACClick(self):
        self.tab5.MACView.configure(state='normal')
        if not self.checkConnected():
           return
        s = "macaddress"
        clientSocket.send(s.encode('utf-8'))
        size = int(clientSocket.recv(10).decode('utf-8'))
        clientSocket.send("OK".encode('utf-8'))
        self.tab5.MACs = []
        buffer = "".encode("utf-8")
        while size > 0:
               data = clientSocket.recv(4096)
               size -= len(data)
               buffer += data
        self.tab5.MACs = json.loads(buffer.decode("utf-8"))
        self.tab5.MACView.delete('1.0', END)
        for MAC in self.tab5.MACs:
            self.tab5.MACView.insert(INSERT, MAC[0] + "\n\n")
            self.tab5.MACView.insert(INSERT, "\tPhysical Address:\t\t" + MAC[1] + "\n")
            self.tab5.MACView.insert(INSERT, "\tIPv4 Address:\t\t" + MAC[2] + "\n")
            self.tab5.MACView.insert(INSERT, "\tSubnet Mask:\t\t" + MAC[3] + "\n")
            self.tab5.MACView.insert(INSERT, "\n\n\n")
        self.tab5.MACView.configure(state='disabled')
        



    #--------------------TAB6 POWER----------------------------------------
    def butLogOutClick(self,event=None):
        if not self.checkConnected():
           return
        s = "logout"
        clientSocket.send(s.encode('utf-8'))
        messagebox.showinfo("", "The server logged out successfully.")

    def butShutDownClick(self,event=None):
        if not self.checkConnected():
           return
        s = "shutdown"
        clientSocket.send(s.encode('utf-8'))
        messagebox.showinfo("", "Server shut down after 60s.")




    #--------------------TAB7 STREAM----------------------------------------
    def butStartRecording(self):
        global streamSocket
        if not self.checkConnected():
           return
        window = tk.Toplevel()  
        screen = Label(window)
        window.protocol('WM_DELETE_WINDOW', lambda: closeButton(window,1))
        screen.grid()
        assert streamSocket is None
        streamSocket = StreamingServer('', PORT_STREAM, window=window , screen=screen)
        streamSocket.start_server()  
 
        clientSocket.send("stream".encode())      



    
    #--------------------TAB8 REGISTRY----------------------------------------
    def butBrowseClick(self, event = None):
        s = "browse"
        sfile = filedialog.askopenfilename(initialdir=os.getcwd(), title=s, filetypes=[("reg file",".reg"), ("all file",".*")], parent = self.tab8)
        self.tab8.Path1.config(state="normal")
        self.tab8.Path1.delete("1.0", END)
        self.tab8.Path1.insert("1.0", sfile)
        self.tab8.Path1.place(x=0, y=0, height=22, width=335)
        self.tab8.Path1.config(state="disabled")
        if sfile == "":
            return
        try:
            f = open(sfile, "r")
        except:
            messagebox.showinfo("Error", "Error",parent = self.tab8)
        content = f.read()
        if content == None:
            return
        self.tab8.Content.delete("1.0", END)
        self.tab8.Content.insert("1.0", content)
        f.close()
        
    def butSend1Click(self, event = None):
        s = "reg"
        clientSocket.send(s.encode('utf-8'))
        content = self.tab8.Content.get('1.0', END)
        clientSocket.send(content.encode('utf-8'))
        message = clientSocket.recv(100).decode('utf-8')
        messagebox.showinfo("", message,parent = self.tab8)

    def butSend2Click(self, event = None):
        s = "edit"
        clientSocket.send(s.encode('utf-8'))

        option = self.tab8.box1.get().strip()
        clientSocket.send(option.encode('utf-8'))

        link = self.tab8.Path2.get("1.0", END).strip()
        clientSocket.send(link.encode('utf-8'))

        valueName = self.tab8.Name.get("1.0", END).strip()
        clientSocket.send(valueName.encode('utf-8'))

        value = self.tab8.Value.get("1.0", END).strip()
        clientSocket.send(value.encode('utf-8'))

        typeValue = self.tab8.box2.get().strip()
        clientSocket.send(typeValue.encode('utf-8'))

        message = clientSocket.recv(1024).decode('utf-8')
        self.tab8.resView.config(state = "normal")
        self.tab8.resView.insert(END, f"{option}: {message}" + "\n")
        self.tab8.resView.config(state = "disable")

    def butDelClick(self, event = None):
        self.tab8.resView.config(state = "normal")
        self.tab8.resView.delete("1.0", END)
        self.tab8.resView.config(state = "disable")

    def chooseFunc(self, event = None):
        func = self.tab8.box1.get().strip()
        if func == "Get value":
            self.tab8.Name.config(state = "normal")
            self.tab8.Value.config(state = "disabled")
            self.tab8.box2.config(state = "disabled")
        elif func == "Set value":
            self.tab8.Name.config(state = "normal")
            self.tab8.Value.config(state = "normal")
            self.tab8.box2.config(state = "normal")
        elif func == "Delete value":
            self.tab8.Name.config(state = "normal")
            self.tab8.Value.config(state = "disabled")
            self.tab8.box2.config(state = "disabled")
        elif func == "Create key":
            self.tab8.Name.config(state = "disabled")
            self.tab8.Value.config(state = "disabled")
            self.tab8.box2.config(state = "disabled")
        elif func == "Delete key":
            self.tab8.Name.config(state = "disabled")
            self.tab8.Value.config(state = "disabled")
            self.tab8.box2.config(state = "disabled")
        else:
            return





    def createWidgets(self):
        
    #--------------------GENERAL----------------------------------------
        self.frame0 = tk.LabelFrame(self.root,bd=1,background=appbg)
        self.frame0.place(x=0, y=0, height=635, width=140)

        self.frame1 = tk.LabelFrame(self.root,bd=1,background=appbg)
        self.frame1.place(x=140, y=0, height=635, width=900)

        img = Image.open("logo.png")
        img =img.resize((87,138))
        self.img=ImageTk.PhotoImage(img)
        self.theme=tk.Label(self.frame0,image=self.img,background=appbg)
        self.theme.place(x=25, y=50)
        img.close()

        self.ipConnect = tk.StringVar()
        self.ipConnect.set("Enter IP address")
        self.txtIP = tk.Entry(self.frame0, textvariable = self.ipConnect)
        self.txtIP.place(x=20, y=250, height=30, width=100)
        self.txtIP.configure(bg=entrybg,fg=entryfg,insertbackground=entryfg,bd=3,font=("Lato",8))
        self.txtIP.bind("<Key-Return>", self.butConnectClick)
        
        #flat, groove, raised, ridge, solid, or sunken
        self.butConnect = tk.Button(self.frame0,text = "Connect",font=("Lato",10),relief="groove",bg=outbtnbg,fg=outbtnfg,justify="center",cursor="circle")
        self.butConnect["command"] = self.butConnectClick
        self.butConnect.place(x=20, y=300, height=30, width=100)

        self.butDisconnect = tk.Button(self.frame0,text = "Disconnect",font=("Lato",10),relief="groove",bg=outbtnbg,fg=outbtnfg,justify="center",cursor="circle")
        self.butDisconnect["command"] = self.butDisconnectClick
        self.butDisconnect.place(x=20, y=580, height=30, width=100)
        self.butDisconnect.config(state="disabled")
        
        noteBookStyle = ttk.Style(self.frame1)
        noteBookStyle.theme_use('default')
        noteBookStyle.configure("TNotebook", background=appbg, tabposition='wn',cursor="circle")
        noteBookStyle.configure("TNotebook.Tab", font=('Lato', 8, BOLD), justify="center", background=txtbg, foreground="white", ANCHOR="c",cursor="circle")
        noteBookStyle.map("TNotebook.Tab", background= [("selected", entryfg)],foreground=[("selected",appbg)])

        tabFrameStyle = ttk.Style(self.frame1)
        tabFrameStyle.configure("TFrame", background=appbg)

        treeViewStyle = ttk.Style(self.frame1)
        treeViewStyle.configure("Treeview", background="black", foreground="white", fieldbackground=appbg)
        treeViewStyle.configure("Treeview.Heading", font=('Lato', 11), background=txtbg, foreground=txtfg)
        
        self.tabControl = ttk.Notebook(self.frame1,style="TNotebook")
        self.tabControl.pack(expand=1,fill="both")
        

        

    #--------------------TAB1----------------------------------------APP
        self.tab1 = ttk.Frame(self.tabControl,style="TFrame")
        tab1Img = Image.open("tab1.png")
        tab1Img = tab1Img.resize((40,40))
        self.tab1.img = ImageTk.PhotoImage(tab1Img)
        self.tabControl.add(self.tab1,text="APPS\nCONTROLLER",image=self.tab1.img,compound=tk.TOP)
        tab1Img.close()

        self.tab1.frame0 = tk.Frame(self.tab1,background=appbg)
        self.tab1.frame0.place(x=20, y=20, height=495, width=480)
        self.tab1.tv1 = ttk.Treeview(self.tab1.frame0)
        self.tab1.tv1.place(relheight=1, relwidth=1)
        self.tab1.treescrolly = tk.Scrollbar(self.tab1.frame0, orient="vertical", command=self.tab1.tv1.yview)
        self.tab1.tv1.config(yscrollcommand=self.tab1.treescrolly.set)
        self.tab1.treescrolly.pack(side="right", fill="y")
        self.tab1.tv1["columns"] = ("1", "2", "3")
        self.tab1.tv1["show"] = "headings"
        self.tab1.tv1.heading(1, text = "Application 's Name")
        self.tab1.tv1.heading(2, text = "Application 's ID")
        self.tab1.tv1.heading(3, text = "Thread")
        self.tab1.tv1.column(1, width = 100)
        self.tab1.tv1.column(2, width = 75)
        self.tab1.tv1.column(3, width = 75)
        self.tab1.data = []
        self.tab1.popup = tk.Menu(self.tab1, tearoff=0,bg=txtbg,fg=txtfg,font=("Lato",10,BOLD))
        self.tab1.popup.add_command(label="Kill", command=self.killRightClick)
        self.tab1.popup.add_separator()
        self.tab1.tv1.bind("<Button-3>", self.doTab12Popup)

        self.tab1.butRefresh = tk.Button(self.tab1,text = "Refresh",font=("Lato",15),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab1.butRefresh["command"] = self.butRefreshClick
        self.tab1.butRefresh.place(x=20, y=535, height=80, width=120)

        self.tab1.killID = tk.StringVar()
        self.tab1.killID.set("Enter ID")
        self.tab1.KillIDEntry = tk.Entry(self.tab1, textvariable = self.tab1.killID)
        self.tab1.KillIDEntry.place(x=160, y=585, height=30, width=210)
        self.tab1.KillIDEntry.configure(font=("Lato",10),relief="groove",bg=entrybg,fg=entryfg,insertbackground=entryfg)
        self.tab1.KillIDEntry.bind("<Key-Return>", self.butKillClick)

        self.tab1.butKill = tk.Button(self.tab1,text = "Kill",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab1.butKill["command"] = self.butKillClick
        self.tab1.butKill.place(x=400, y=585, height=30, width=100)

        self.tab1.startID = tk.StringVar()
        self.tab1.startID.set("Enter Name")
        self.tab1.StartIDEntry = tk.Entry(self.tab1, textvariable = self.tab1.startID)
        self.tab1.StartIDEntry.place(x=160, y=535, height=30, width=210)
        self.tab1.StartIDEntry.configure(font=("Lato",10),relief="groove",bg=entrybg,fg=entryfg,insertbackground=entryfg)
        self.tab1.StartIDEntry.bind("<Key-Return>", self.butStartClick)

        self.tab1.butStart = tk.Button(self.tab1,text = "Start",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab1.butStart["command"] = self.butStartClick
        self.tab1.butStart.place(x=400, y=535, height=30, width=100)





    #--------------------TAB2----------------------------------------PROCESS
        self.tab2 = ttk.Frame(self.tabControl)
        tab2Img = Image.open("tab2.png")
        tab2Img = tab2Img.resize((40,40))
        self.tab2.img = ImageTk.PhotoImage(tab2Img)
        self.tabControl.add(self.tab2,text="PROCESSES\nCONTROLLER",image=self.tab2.img,compound=tk.TOP) 
        tab2Img.close()

        self.tab2.frame0 = tk.Frame(self.tab2,background=appbg)
        self.tab2.frame0.place(x=20, y=20, height=495, width=480)
        self.tab2.tv1 = ttk.Treeview(self.tab2.frame0)
        self.tab2.tv1.place(relheight=1, relwidth=1)
        self.tab2.treescrolly = tk.Scrollbar(self.tab2.frame0, orient="vertical", command=self.tab2.tv1.yview)
        self.tab2.tv1.config(yscrollcommand=self.tab2.treescrolly.set)
        self.tab2.treescrolly.pack(side="right", fill="y")
        self.tab2.tv1["columns"] = ("1", "2", "3")
        self.tab2.tv1["show"] = "headings"
        self.tab2.tv1.heading(1, text = "Process 's Name")
        self.tab2.tv1.heading(2, text = "Process 's ID")
        self.tab2.tv1.heading(3, text = "Thread")
        self.tab2.tv1.column(1, width = 100)
        self.tab2.tv1.column(2, width = 75)
        self.tab2.tv1.column(3, width = 75)
        self.tab2.data = []
        self.tab2.popup = tk.Menu(self.tab2, tearoff=0,bg=txtbg,fg=txtfg,font=("Lato",10,BOLD))
        self.tab2.popup.add_command(label="Kill", command=self.killRightClick)
        self.tab2.popup.add_separator()
        self.tab2.tv1.bind("<Button-3>", self.doTab12Popup)
        
        self.tab2.butRefresh = tk.Button(self.tab2,text = "Refresh",font=("Lato",15),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab2.butRefresh["command"] = self.butRefreshClick
        self.tab2.butRefresh.place(x=20, y=535, height=80, width=120)

        self.tab2.killID = tk.StringVar()
        self.tab2.killID.set("Enter ID")
        self.tab2.KillIDEntry = tk.Entry(self.tab2, textvariable = self.tab2.killID)
        self.tab2.KillIDEntry.place(x=160, y=585, height=30, width=210)
        self.tab2.KillIDEntry.configure(font=("Lato",10),relief="groove",bg=entrybg,fg=entryfg,insertbackground="white")
        self.tab2.KillIDEntry.bind("<Key-Return>", self.butKillClick)

        self.tab2.butKill = tk.Button(self.tab2,text = "Kill",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab2.butKill["command"] = self.butKillClick
        self.tab2.butKill.place(x=400, y=585, height=30, width=100)

        self.tab2.startID = tk.StringVar()
        self.tab2.startID.set("Enter Name")
        self.tab2.StartIDEntry = tk.Entry(self.tab2, textvariable = self.tab2.startID)
        self.tab2.StartIDEntry.place(x=160, y=535, height=30, width=210)
        self.tab2.StartIDEntry.configure(font=("Lato",10),relief="groove",bg=entrybg,fg=entryfg,insertbackground="white")
        self.tab2.StartIDEntry.bind("<Key-Return>", self.butStartClick)

        self.tab2.butStart = tk.Button(self.tab2,text = "Start",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab2.butStart["command"] = self.butStartClick
        self.tab2.butStart.place(x=400, y=535, height=30, width=100)





    #--------------------TAB3----------------------------------------FTP
        self.tab3 = ttk.Frame(self.tabControl)
        tab3Img = Image.open("tab3.png")
        tab3Img = tab3Img.resize((40,40))
        self.tab3.img = ImageTk.PhotoImage(tab3Img)
        self.tabControl.add(self.tab3,text="FTP\nCONTROLLER",image=self.tab3.img,compound=tk.TOP)
        tab3Img.close()

        self.tab3.label1 = Label(self.tab3,text="LOCAL",font=("Lato",10,BOLD),relief="groove",bg=txtbg,fg=txtfg)
        self.tab3.label1.place(x=20,y=20,height=30,width=380)

        self.tab3.label2 = Label(self.tab3,text="REMOTE",font=("Lato",10,BOLD),relief="groove",bg=txtbg,fg=txtfg)
        self.tab3.label2.place(x=420,y=20,height=30,width=380)

        self.tab3.clientPath = "\\"
        self.tab3.clientPathtxt = tk.Text(self.tab3)
        self.tab3.clientPathtxt.insert(INSERT,self.tab3.clientPath)
        self.tab3.clientPathtxt.configure(font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",state="disabled")
        self.tab3.clientPathtxt.place(x=20,y=50,height=60,width=380)

        self.tab3.serverPath = "\\"
        self.tab3.serverPathtxt = tk.Text(self.tab3)
        self.tab3.serverPathtxt.insert(INSERT,self.tab3.serverPath)
        self.tab3.serverPathtxt.configure(font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",state="disabled")
        self.tab3.serverPathtxt.place(x=420,y=50,height=60,width=380)

        self.tab3.butClientPreviousPath=tk.Button(self.tab3,text = "Previous",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")        
        self.tab3.butClientPreviousPath["command"] = self.butClientPreviousPathClick
        self.tab3.butClientPreviousPath.place(x=20, y=110, height=30, width=100)

        self.tab3.butServerPreviousPath=tk.Button(self.tab3,text = "Previous",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")        
        self.tab3.butServerPreviousPath["command"] = self.butServerPreviousPathClick
        self.tab3.butServerPreviousPath.place(x=420, y=110, height=30, width=100)

        self.tab3.frame0 = tk.Frame(self.tab3,background=appbg)
        self.tab3.frame0.place(x=20, y=140, height=480, width=380)
        self.tab3.tv1 = ttk.Treeview(self.tab3.frame0)
        self.tab3.tv1.place(relheight=1, relwidth=1)
        self.tab3.treescrolly = tk.Scrollbar(self.tab3.frame0, orient="vertical", command=self.tab3.tv1.yview)
        self.tab3.tv1.config(yscrollcommand=self.tab3.treescrolly.set)
        self.tab3.treescrolly.pack(side="right", fill="y")
        self.tab3.tv1["columns"] = ("1", "2", "3")
        self.tab3.tv1["show"] = "headings"
        self.tab3.tv1.heading(1, text = "Name")
        self.tab3.tv1.heading(2, text = "Size")
        self.tab3.tv1.heading(3, text = "Item type")
        self.tab3.tv1.column(1, width = 70)
        self.tab3.tv1.column(2, width = 40)
        self.tab3.tv1.column(3, width = 40)
        self.tab3.clientInfos = []
        self.tab3.tv1.bind("<Double-1>", self.clientOnDoubleClick)

        self.tab3.popup1 = tk.Menu(self.tab3, tearoff=0,bg=txtbg,fg=txtfg,font=("Lato",10,BOLD))
        self.tab3.popup1.add_command(label="Send", command=self.copyToServer)
        self.tab3.popup1.add_command(label="Delete", command=self.deleteClientFile)
        self.tab3.popup1.add_separator()
        self.tab3.tv1.bind("<Button-3>", self.doTab3Popup1)

        self.tab3.frame1 = tk.Frame(self.tab3,background=appbg)
        self.tab3.frame1.place(x=420, y=140, height=480, width=380)
        self.tab3.tv2 = ttk.Treeview(self.tab3.frame1)
        self.tab3.tv2.place(relheight=1, relwidth=1)
        self.tab3.treescrolly = tk.Scrollbar(self.tab3.frame1, orient="vertical", command=self.tab3.tv2.yview)
        self.tab3.tv2.config(yscrollcommand=self.tab3.treescrolly.set)
        self.tab3.treescrolly.pack(side="right", fill="y")
        self.tab3.tv2["columns"] = ("1", "2", "3")
        self.tab3.tv2["show"] = "headings"
        self.tab3.tv2.heading(1, text = "Name")
        self.tab3.tv2.heading(2, text = "Size")
        self.tab3.tv2.heading(3, text = "Item type")
        self.tab3.tv2.column(1, width = 70)
        self.tab3.tv2.column(2, width = 40)
        self.tab3.tv2.column(3, width = 40)
        self.tab3.serverInfos = []
        self.tab3.tv2.bind("<Double-1>", self.serverOnDoubleClick)
        for i in range(100):
            row=["Coc Coc",i,"1234567"]
            self.tab3.tv2.insert("", "end", values=row, tags="a")
            self.tab3.tv2.tag_configure("a", background=txtbg, foreground=txtfg)

        self.tab3.popup2 = tk.Menu(self.tab3, tearoff=0,bg=txtbg,fg=txtfg,font=("Lato",10,BOLD))
        self.tab3.popup2.add_command(label="Get", command=self.copyToClient)
        self.tab3.popup2.add_command(label="Delete", command=self.deleteServerFile)
        self.tab3.popup2.add_separator()
        self.tab3.tv2.bind("<Button-3>", self.doTab3Popup2)





    #--------------------TAB4----------------------------------------KEYBOARD
        self.tab4 = ttk.Frame(self.tabControl)
        tab4Img = Image.open("tab4.png")
        tab4Img = tab4Img.resize((40,40))
        self.tab4.img = ImageTk.PhotoImage(tab4Img)
        self.tabControl.add(self.tab4,text="KEYBOARD\nCONTROLLER",image=self.tab4.img,compound=tk.TOP)
        tab4Img.close()

        self.tab4.butLock = tk.Button(self.tab4, text = "Lock",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab4.butLock["command"] = self.butLockClick
        self.tab4.butLock.place(x=20, y=20, height=50, width=80)

        self.tab4.butHook = tk.Button(self.tab4, text = "Hook",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab4.butHook["command"] = self.butHookClick
        self.tab4.butHook.place(x=120, y=20, height=50, width=80)

        self.tab4.butUnhook = tk.Button(self.tab4, text = "Unhook",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab4.butUnhook["command"] = self.butUnhookClick
        self.tab4.butUnhook.place(x=220, y=20, height=50, width=80)

        self.tab4.butPrint = tk.Button(self.tab4, text = "Print",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab4.butPrint["command"] = self.butPrintClick
        self.tab4.butPrint.place(x=320, y=20, height=50, width=80)
   
        self.tab4.butDel = tk.Button(self.tab4, text = "Delete",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab4.butDel["command"] = self.butDelClick4
        self.tab4.butDel.place(x=420, y=20, height=50, width=80)

        self.tab4.frame1 = tk.LabelFrame(self.tab4, text="")
        self.tab4.frame1.place(x=20, y=90, height=525, width=480)
        self.tab4.KeyView = tk.Text(self.tab4.frame1,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle")
        self.tab4.KeyLog = ""
        self.tab4.KeyView.insert(INSERT, self.tab4.KeyLog)
        self.tab4.KeyView.config(state="disabled")
        self.tab4.KeyView.place(x=0,y=0,height=522,width=477)
        self.tab4.treescrolly = tk.Scrollbar(self.tab4.frame1, orient="vertical", command=self.tab4.KeyView.yview)
        self.tab4.KeyView.config(yscrollcommand=self.tab4.treescrolly.set)
        self.tab4.treescrolly.pack(side="right", fill="y")
        




    #--------------------TAB5----------------------------------------MAC
        self.tab5 = ttk.Frame(self.tabControl)
        tab5Img = Image.open("tab5.png")
        tab5Img = tab5Img.resize((40,40))
        self.tab5.img = ImageTk.PhotoImage(tab5Img)
        self.tabControl.add(self.tab5,text="MAC\n    ADDRESS    ",image=self.tab5.img,compound=tk.TOP)
        tab5Img.close()

        self.tab5.frame1 = tk.LabelFrame(self.tab5, text="MAC Address",font=("Lato",10),relief="groove",bg=appbg,fg=appfg,cursor="circle")
        self.tab5.frame1.place(x=20, y=20, height=525, width=480)
        self.tab5.MACView = tk.Text(self.tab5.frame1,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab5.MACs = []
        self.tab5.MACView.place(x=0,y=0,height=505,width=475)
        self.tab5.treescrolly = tk.Scrollbar(self.tab5.frame1, orient="vertical", command=self.tab5.MACView.yview)
        self.tab5.MACView.config(yscrollcommand=self.tab5.treescrolly.set)
        self.tab5.treescrolly.pack(side="right", fill="y")

        self.tab5.butGetMAC = tk.Button(self.tab5,text="Get MAC Address",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab5.butGetMAC["command"] = self.butGetMACClick
        self.tab5.butGetMAC.place(x=190, y=565, height=50, width=140)





    #--------------------TAB6----------------------------------------POWER
        self.tab6 = ttk.Frame(self.tabControl)
        tab6Img = Image.open("tab6.png")
        tab6Img = tab6Img.resize((40,40))
        self.tab6.img = ImageTk.PhotoImage(tab6Img)
        self.tabControl.add(self.tab6,text="POWER\nCONTROLLER",image=self.tab6.img,compound=tk.TOP)
        tab6Img.close()

        self.tab6.butLogOut = tk.Button(self.tab6,text = "Log out",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab6.butLogOut["command"] = self.butLogOutClick
        self.tab6.butLogOut.place(x=20, y=20, height=30, width=100)

        self.tab6.butShutDown = tk.Button(self.tab6,text = "Shutdown",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab6.butShutDown["command"] = self.butShutDownClick
        self.tab6.butShutDown.place(x=20, y=70, height=30, width=100)




    #--------------------TAB7----------------------------------------STREAMING
        self.tab7 = ttk.Frame(self.tabControl)
        tab7Img = Image.open("tab7.png")
        tab7Img = tab7Img.resize((40,40))
        self.tab7.img = ImageTk.PhotoImage(tab7Img)
        self.tabControl.add(self.tab7,text="STREAMING\nCONTROLLER",image=self.tab7.img,compound=tk.TOP)
        tab7Img.close()

        self.tab7.butStartRecording = tk.Button(self.tab7,text = "Start Streaming",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab7.butStartRecording["command"] = self.butStartRecording
        self.tab7.butStartRecording.place(x=310, y=565, height=50, width=200)





    #--------------------TAB8----------------------------------------REGIS
        self.tab8 = ttk.Frame(self.tabControl)
        tab8Img = Image.open("tab8.png")
        tab8Img = tab8Img.resize((40,40))
        self.tab8.img = ImageTk.PhotoImage(tab8Img)
        self.tabControl.add(self.tab8,text="REGISTRY\nCONTROLLER",image=self.tab8.img,compound=tk.TOP)
        tab8Img.close()

        self.tab8.frame = tk.LabelFrame(self.tab8,text="File Path",font=("Lato",10),relief="groove",bg=appbg,fg=appfg,cursor="circle")
        self.tab8.frame.place(x=20, y=20, height=60, width=350)
        self.tab8.Path1 = tk.Text(self.tab8.frame,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab8.Path1.insert(INSERT, "")
        self.tab8.Path1.place(x=0, y=0, height=40, width=345)
        self.tab8.Path1.config(state="disabled")
        
        self.tab8.butBrowse = tk.Button(self.tab8, text = "Browse",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab8.butBrowse["command"] = self.butBrowseClick
        self.tab8.butBrowse.place(x=400, y=25, height=55, width=100)

        self.tab8.frame0 = tk.LabelFrame(self.tab8,text="File content",font=("Lato",10),relief="groove",bg=appbg,fg=appfg,cursor="circle")
        self.tab8.frame0.place(x=20, y=100, height=200, width=350)
        self.tab8.Content = tk.Text(self.tab8.frame0,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab8.Content.insert(INSERT, "")
        self.tab8.Content.place(x=0, y=0, height=180, width=345)
        self.tab8.treescrolly1 = tk.Scrollbar(self.tab8.frame0, orient="vertical", command=self.tab8.Content.yview)
        self.tab8.Content.config(yscrollcommand=self.tab8.treescrolly1.set)
        self.tab8.treescrolly1.pack(side="right", fill="y")
        
        self.tab8.butSend1 = tk.Button(self.tab8, text = "Send content",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab8.butSend1["command"] = self.butSend1Click
        self.tab8.butSend1.place(x=400, y=105, height=195, width=100)

        self.tab8.frame1 = tk.LabelFrame(self.tab8, text="Edit value directly",font=("Lato",10),relief="groove",bg=appbg,fg=appfg,cursor="circle")
        self.tab8.frame1.place(x=20, y=315, height=300, width=480)

        comboboxStyle = ttk.Style()
        comboboxStyle.configure("TCombobox", font=('Lato', 8), background="white", foreground=txtfg,fieldbackground= "black",insertbackground="white",cursor="circle")
        comboboxStyle.configure("TCombobox.Menu", font=('Lato', 8), background=txtbg, foreground="white",fieldbackground= "black", ANCHOR="c",cursor="circle")

        func = ('Get value', 'Set value', 'Delete value', 'Create key', 'Delete key')
        self.tab8.func = tk.StringVar()
        self.tab8.func.set("Choose function")
        self.tab8.box1 = ttk.Combobox(self.tab8.frame1, textvariable=self.tab8.func, state='readonly')
        self.tab8.box1['values'] = func
        self.tab8.box1.place(x=20, y=10, height = 30, width=435)
        self.tab8.box1.bind('<<ComboboxSelected>>', self.chooseFunc)

        self.tab8.Path2 = tk.Text(self.tab8.frame1,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab8.Path2.insert(INSERT, "Input file path")
        self.tab8.Path2.place(x=20, y=50, height=30, width=435)  

        self.tab8.Name = tk.Text(self.tab8.frame1,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab8.Name.insert(INSERT, "Name value")
        self.tab8.Name.place(x=20, y=100, height=30, width=133)

        self.tab8.Value = tk.Text(self.tab8.frame1,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab8.Value.insert(INSERT, "Value")
        self.tab8.Value.place(x=173, y=100, height=30, width=133)
        
        dataType = ('String', 'Binary', 'DWORD', 'QWORD', 'Multi-String', 'Expandable String')
        self.tab8.dataType = tk.StringVar()
        self.tab8.dataType.set("Data 's type")
        self.tab8.box2 = ttk.Combobox(self.tab8.frame1, textvariable=self.tab8.dataType, state='readonly')
        self.tab8.box2['values'] = dataType
        self.tab8.box2.place(x=326, y=100, height = 30, width=129)

        self.tab8.frame2 = tk.LabelFrame(self.tab8.frame1,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle")
        self.tab8.frame2.place(x=20, y=150, height=60, width=435)
        self.tab8.resView = tk.Text(self.tab8.frame2,font=("Lato",10),relief="groove",bg=txtbg,fg=txtfg,cursor="circle",insertbackground="white")
        self.tab8.resView.insert(INSERT, "")
        self.tab8.resView.place(x=0, y=0, height=55, width=425)
        self.tab8.treescrolly2 = tk.Scrollbar(self.tab8.frame2, orient="vertical", command=self.tab8.resView.yview)
        self.tab8.resView.config(yscrollcommand=self.tab8.treescrolly2.set)
        self.tab8.treescrolly2.pack(side="right", fill="y")
        self.tab8.resView.config(state = "disable")

        self.tab8.butSend2 = tk.Button(self.tab8.frame1, text = "Send",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab8.butSend2["command"] = self.butSend2Click
        self.tab8.butSend2.place(x=130, y=230, height=30, width=100)

        self.tab8.butDel = tk.Button(self.tab8.frame1, text = "Delete",font=("Lato",10),relief="groove",bg=btnbg,fg=btnfg,justify="center",cursor="circle")
        self.tab8.butDel["command"] = self.butDelClick
        self.tab8.butDel.place(x=250, y=230, height=30, width=100)

    #------------------------------------------------------------
        for i in range(0,8):
            self.tabControl.tab(i,state="disabled")


root=tk.Tk()
root.protocol('WM_DELETE_WINDOW', lambda: closeButton(root,0))
root.iconbitmap(default='clientIcon.ico')
controller=Client(root)
root.mainloop()
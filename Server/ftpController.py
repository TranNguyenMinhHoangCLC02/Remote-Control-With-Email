import os
import socket
import psutil
import shutil
import json
from mySocket import MySocket

CHUNKSIZE = 1024*1024
import win32com.client 

METADATA = ['Name', 'Size', 'Item type', 'Date modified', 'Date created']


class FtpController():
    def __init__(self, clientSocket, host, port):
        self.__host = host
        self.__port = port
        print(port)
        self.__client = clientSocket
        self.currentPath = "\\"
        self.info = []

    def startListening(self):
        self.senDrive()
        request = ""
        while True:
            request = self.__client.recv(1024).decode("utf-8")
            if not request:
                break
            if request == "view":
                # fullpath view
                info = self.__client.recv(1024).decode("utf-8")
                if os.path.exists(info):
                    self.currentPath = info
                    self.sendFolderInfo(self.currentPath)
            elif request == "back":
                l = len(self.currentPath)
                if self.currentPath[l-2:-1] == ":":
                    self.senDrive()
                    self.currentPath == "\\"
                elif self.currentPath =="": return
                else:
                    self.currentPath, tail = os.path.split(self.currentPath)
                    self.sendFolderInfo(self.currentPath)
            elif request == "copy2server":
                self.recvData(self.currentPath)
            elif request == "copy2client":
                info = self.__client.recv(1024).decode("utf-8")
                fullPath = os.path.join(self.currentPath, info)
                self.sendData(fullPath)
            elif request == "delete":
                info = self.__client.recv(1024).decode("utf-8")
                fullPath = os.path.join(self.currentPath, info)
                self.deleteData(fullPath)
            elif request == "quit":
                return
            else: #Quit
                continue

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

    def getDrive(self):
        drps = psutil.disk_partitions()
        self.drives = [[dp.device, '', 'File folder'] for dp in drps if dp.fstype == 'NTFS']

    def senDrive(self):
        self.getDrive()

        dataToSend = json.dumps(self.drives).encode('utf-8') 
        size = len(dataToSend)
        self.__client.send(str(size).encode('utf-8'))
        check = self.__client.recv(10)
        self.__client.send(dataToSend)

    def getFolderInfo(self, path):
        self.info = []
        for root, subfolder, files in os.walk(path):
            for i in files:
                dict = self.getFileMetadata(os.path.join(path,i),METADATA)
                self.info.append([dict['Name'], dict['Size'], dict['Item type']])
            for i in subfolder:
                self.info.append([i, '', 'File folder'])
            break


    def sendFolderInfo(self,path):
        self.getFolderInfo(path)

        dataToSend = json.dumps(self.info).encode('utf-8') 
        size = len(dataToSend)
        self.__client.send(str(size).encode('utf-8'))
        check = self.__client.recv(10)
        self.__client.send(dataToSend)
        
        
    def deleteData(self,path):
        if(os.path.isfile(path)):
            os.remove(path)
        elif(os.path.isdir(path)):
            try:
                shutil.rmtree(path)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
        else:
            return

    def sendData(self, path):
        ftpClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ftpClient.connect((self.__host, self.__port))

        head, relpath = os.path.split(path)
        if(os.path.isfile(path)):
            self.__client.send(''.encode())
            self.sendFile(ftpClient, path, relpath)
        elif(os.path.isdir(path)):
            self.__client.send(relpath.encode())
            self.sendFolder(ftpClient, path)
        else:
            return
        self.__client.send("DONE".encode())
        
        ftpClient.close()

    def recvData(self, path):
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverSock.bind(("", self.__port))
        serverSock.listen(1)
        clientSock, addr = serverSock.accept()

        folderName = self.__client.recv(20).decode()
        if folderName == '':
            self.recvFolder(clientSock, path)
        else:
            tempPath = os.path.join(path,folderName)
            if os.path.exists(tempPath) == False:
                os.makedirs(tempPath)
            self.recvFolder(clientSock, tempPath)
        serverSock.close()
        clientSock.close()


    def sendFile(self, ftpClient, fullPath, relpath):
        filesize = os.path.getsize(fullPath)
        self.__client.send(relpath.encode())
        self.__client.send(str(filesize).encode())

        # Message when need overwrite, rename or not
        check = self.__client.recv(10).decode()
        print("check: ", check)
        if check == "continue":
            with open(fullPath,'rb') as f:
            # Send the file in chunks so large files can be handled.
                while True:
                    data = f.read(CHUNKSIZE)
                    if not data: break
                    ftpClient.send(data)
        # When duplicate and pause copy
        else:  #pause
            return

    def sendFolder(self, ftpClient, srcPath):
        for path,subfolder,files in os.walk(srcPath):
            for file in files:
                fullPath = os.path.join(path,file)
                relpath = os.path.relpath(fullPath,srcPath)
                
                print(f'Sending {relpath}')
                self.sendFile(ftpClient, fullPath, relpath)

    def recvFolder(self, clientSock, desPath):
        #with self.__client, self.__client.makefile('rb') as clientfile:
            while True:
                #raw = clientfile.readline()
                #if not raw: break # no more files, server closed connection.

                filename = self.__client.recv(1024).decode()
                print(filename)
                if filename == 'DONE':
                    break
                length = int(self.__client.recv(1024).decode())

                print(f'Downloading {filename}...\n  Expecting {length:,} bytes...',end='',flush=True)

                path = os.path.join(desPath, filename)
                os.makedirs(os.path.dirname(path),exist_ok=True)

                # Check if exists
                if os.path.exists(path):
                    self.__client.send("exists".encode())
                    request = self.__client.recv(20).decode()
                    if request == "pause":
                        continue
                    elif request == "rename":
                        i = 1
                        dir, fileName = os.path.split(path)
                        while True:
                            temp = f"Copy {i} of " + fileName 
                            temp = os.path.join(dir, temp)
                            if(os.path.exists(temp) == False):
                                path = temp
                                break
                            i += 1
                    else:
                        pass
                else:
                    self.__client.send("not exists".encode())   

                # Read the data in chunks so it can handle large files.
                with open(path,'wb') as f:
                    while length:
                        print("len: ",length)
                        chunk = min(length,CHUNKSIZE)
                        data = clientSock.recv(chunk)
                        if not data: 
                            break
                        f.write(data)
                        length -= len(data)
                    else: # only runs if while doesn't break and length==0
                        print('Complete')
                        continue

                # socket was closed early.
                print('Incomplete')
                break 




import os, signal
import subprocess
import json

class AppController():
    def __init__(self, clientSocket):
        self.appList = []
        self.__client = clientSocket

    def startListening(self):
        request = ""
        while True:
            request = self.__client.recv(1024).decode("utf-8")
            if not request:
                break
            if request == "view":
                self.viewList()
            elif request == "kill":   
                self.killApp()
            elif request == "start":   
                self.startApp()
            else: #Quit
                return

    def process2List(self,processes):
        a = processes.decode().strip()
        b = a.split("\r\n")
        b = [" ".join(x.split()) for x in b]
        c = [x.split() for x in b][2:]
        return c

    def viewList(self):
        app = subprocess.check_output(
            "powershell gps | where {$_.MainWindowTitle} | \
            select Name,Id,@{Name='ThreadCount';Expression={$_.Threads.Count}}",
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        self.appList = self.process2List(app)

        dataToSend = json.dumps(self.appList).encode('utf-8') 
        size = len(dataToSend)
        self.__client.send(str(size).encode('utf-8'))
        check = self.__client.recv(10)
        self.__client.send(dataToSend)

    def killApp(self):
        IDtoKill = self.__client.recv(10).decode('utf-8')
        test = False
        for app in self.appList:
            if IDtoKill==app[1]:
                try:
                    os.kill(int(IDtoKill), signal.SIGTERM) 
                    s = "Success"
                    self.__client.send(s.encode('utf-8'))
                except:
                    s = "Error"
                    self.__client.send(s.encode('utf-8'))
                test = True
        if test==False:
            s = "No App Found"
            self.__client.send(s.encode('utf-8'))

    def startApp(self):
        ProcessToStart = self.__client.recv(1024).decode('utf-8') + ".exe"
        try:
            PathProcess = os.path.relpath(ProcessToStart)
            os.startfile(PathProcess)
            s = "Success"
            self.__client.send(s.encode('utf-8'))
        except:
            s = "Error"
            self.__client.send(s.encode('utf-8'))


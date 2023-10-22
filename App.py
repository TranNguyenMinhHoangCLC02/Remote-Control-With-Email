import os, signal
import subprocess
import json

class AppController():
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
        print(dataToSend)

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


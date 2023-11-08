import os, signal
import psutil
import subprocess
import json
import ast
from tabulate import tabulate

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

            # Format the appList as a table
            table_headers = ["Process", "PID", "Thread Count"]
            formatted_table = tabulate(self.appList, headers=table_headers, tablefmt="pretty")

            return formatted_table
    
    def startApp(self, application_name):
        try:
            PathProcess = os.path.relpath(application_name + ".exe")
            os.startfile(PathProcess)
            return f"Started application: {application_name}"
        except Exception as e:
            return f"Error starting application: {e}"

    def endApp(self, application_name):
        check = False
        for process in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_info = process.info
                if process_info['name'] == application_name + ".exe":
                    pid = process_info['pid']
                    process = psutil.Process(pid)
                    process.terminate()  # Tắt tiến trình
                    check = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if(check == True):
            return f"End Application {application_name} Successfully!"
        else:
            return f"No App {application_name} Found."
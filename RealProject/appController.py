import os, signal
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

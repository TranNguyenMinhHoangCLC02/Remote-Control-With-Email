import subprocess
from tabulate import tabulate
import psutil

class ProcessController():
    def process2List(self, processes):
        a = processes.decode().strip()
        b = a.split("\r\n")
        b = [" ".join(x.split()) for x in b]
        c = [x.split() for x in b][2:]

        # Wrap the first column to a maximum width of 100 characters
        max_width = 200
        for item in c:
            item[0] = '\n'.join([item[0][i:i+max_width] for i in range(0, len(item[0]), max_width)])

        return c


    def viewList(self):
        app = subprocess.check_output(
            "powershell Get-Process | Where-Object { $_.MainWindowTitle.Length -eq 0 } | Select-Object Name,Id,@{Name='ThreadCount';Expression={$_.Threads.Count}}",
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        self.appList = self.process2List(app)

        # Format the appList as a table
        table_headers = ["Process", "PID", "Thread Count"]
        formatted_table = tabulate(self.appList, headers=table_headers, colalign=("left", "center", "center"), tablefmt="pretty",)

        return formatted_table
    
    
    def startBackgroundProcess(self, process_name):
        try:
            subprocess.Popen(process_name, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Started process: {process_name}"
        except Exception as e:
            return f"Error starting process: {e}"
        
        
    def endProcess(self, process_name):
        check = False
        for process in psutil.process_iter(attrs=['pid', 'name']):
            try:
                process_info = process.info
                if process_info['name'] == process_name:
                    pid = process_info['pid']
                    process = psutil.Process(pid)
                    process.terminate()
                    check = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        if(check == True):
            return (f"End Process {process_name} Successfully!")
        else:
            return (f"No Process {process_name} Found.")
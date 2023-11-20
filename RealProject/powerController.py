import os
from ctypes import windll

class powerController():
    def shutdown(self):
        os.system("shutdown /s /t 60")
    
    def logout(self):
        windll.user32.ExitWindowsEx(0, 1)

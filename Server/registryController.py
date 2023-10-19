import winreg
import os

class RegistryController():
    def __init__(self, clientSocket):
        self.__client = clientSocket

    def startListening(self):
        request = ""
        while True:
            request = self.__client.recv(1024).decode("utf-8")
            if not request:
                break
            if request == "reg":
                self.addRegFile()
            elif request == "edit":   
                self.editReg()
            else: #Quit
                return

    def addRegFile(self):
        data = self.__client.recv(4096).decode("utf-8")
        f = open("fileReg.reg","w")
        f.write(data)
        f.close()
        test = True
        s = None
        try:
            os.system("reg import fileReg.reg")
            #k = subprocess.check_output(["reg", "import", "fileReg.reg"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as E:
            print(E)
            test = False    
        if test: s = "Successful edit"
        else: s = "Edit failure"
        self.__client.send(s.encode("utf-8"))

    def editReg(self):
        option = self.__client.recv(1024).decode("utf-8")
        print("option:", option)

        link = self.__client.recv(1024).decode("utf-8")
        print("link:", link)

        valueName = self.__client.recv(1024).decode("utf-8")
        print("value:", valueName)

        value = self.__client.recv(1024).decode("utf-8")
        print("value:", value)

        typeValue = self.__client.recv(1024).decode("utf-8")
        print("typevalue:", typeValue)

        s = None
        aKey = self.baseRegistryKey(link)
        subKey = self.subKey(link)

        if option == "Create key":
            try:
                winreg.CreateKey(aKey,subKey)
                s = "Success"
            except:
                s = "Error"
        elif option == "Delete key":
            try:
                winreg.DeleteKey(aKey,subKey)
                s = "Success"
            except:
                s = "Error"
        elif option == "Get value": 
            s = self.getValue(aKey,subKey,valueName)
        elif option == "Set value":
            s = self.setValue(aKey,subKey,valueName,value,typeValue)
        elif option == "Delete value":
            s = self.deleteValue(aKey,subKey,valueName)
        else:
            s = "Error"
        
        self.__client.send(s.encode("utf-8"))


    def baseRegistryKey(self,link):
        a = None
        if link.find("\\")>=0 :
            key = link[:link.find("\\")]
            if key == "HKEY_CLASSIES_ROOT": a = winreg.HKEY_CLASSES_ROOT
            elif key == "HKEY_CURRENT_USER": a = winreg.HKEY_CURRENT_USER
            elif key == "HKEY_LOCAL_MACHINE": a = winreg.HKEY_LOCAL_MACHINE
            elif key == "HKEY_USERS": a = winreg.HKEY_USERS
            elif key == "HKEY_CURRENT_CONFIG": a = winreg.HKEY_CURRENT_CONFIG
            else: a = None
        return a   
        
    def subKey(self,link):
        a = None
        if link.find("\\")>=0 :
            a = link[link.find("\\")+1:]
        return a

    def value2String(self,value,typeValue):
        if typeValue == winreg.REG_SZ: 
            return value
        elif typeValue == winreg.REG_MULTI_SZ:
            return " ".join(value)
        elif typeValue ==  winreg.REG_EXPAND_SZ:
            return value
        elif typeValue == winreg.REG_BINARY:
            temp = bytearray(value)
            temp = [str(i) for i in temp]
            return " ".join(temp)
        elif typeValue == winreg.REG_DWORD:
            return str(value)
        elif typeValue == winreg.REG_QWORD:
            return str(value)
        else:
            return str(value)
            
    def string2Value(self,stringValue,typeValue):
        try:
            if typeValue == winreg.REG_SZ: 
                return stringValue
            elif typeValue == winreg.REG_MULTI_SZ:
                return stringValue.split("\n")
            elif typeValue ==  winreg.REG_EXPAND_SZ:
                return stringValue
            elif typeValue == winreg.REG_BINARY:
                temp = bytes()
                for  i in stringValue.split():
                    try:
                        temp += bytes([int(i)])
                    except:
                        temp += bytes([int(i,16)])
                return temp
            elif typeValue == winreg.REG_DWORD:
                return int(stringValue)
            elif typeValue == winreg.REG_QWORD:
                return int(stringValue)
            else:
                return stringValue
        except:
            return None

    def getValue(self,aKey,subKey,valueName):
        try:
            key = winreg.OpenKey(aKey,subKey,0, winreg.KEY_ALL_ACCESS)
            if not key:
                return "Error"
        except:
            return "Error"

        try: 
            value = winreg.QueryValueEx(key, valueName)
            stringValue = self.value2String(value[0], value[1])
            return stringValue
        except:
            return "Error"
    
    def setValue(self,aKey,subKey,valueName, value, typeValue):
        try:
            key = winreg.OpenKey(aKey,subKey,0, winreg.KEY_ALL_ACCESS)
            if not key:return "Error"
        except:
            return "Error"
        
        kind = None
        if typeValue == "Binary": kind = winreg.REG_BINARY 
        elif typeValue == "DWORD": kind = winreg.REG_DWORD
        elif typeValue == "QWORD": kind = winreg.REG_QWORD
        elif typeValue == "String": kind = winreg.REG_SZ
        elif typeValue == "Multi-String": kind = winreg.REG_MULTI_SZ
        elif typeValue == "Expandable String": kind = winreg.REG_EXPAND_SZ
        else: return "Error"

        try:
            tempValue = self.string2Value(value,kind)
            winreg.SetValueEx(key,valueName,0,kind,tempValue)
        except:
            return "Error"
        return "Success"

    def deleteValue(self,aKey,subKey,valueName):
        try:
            key = winreg.OpenKey(aKey,subKey,0, winreg.KEY_ALL_ACCESS)
            if not key:return "Error"
        except:
            return "Error"
        try:
            winreg.DeleteValue(key,valueName)
        except:
            return "Error"
        return "Success"
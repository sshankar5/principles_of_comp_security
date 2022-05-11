import os
from socket import *
from cryptography.fernet import Fernet
import time
import hashlib

curr_dir=os.getcwd()
c_key = b'Z4-L_1FMlhMiHJgNtI5hCyry2nV6-brcEW2lOsFZ7K8='
c_Pkey = Fernet(c_key)
server_ip = "localhost"
server_port = 8001
ds_ip = 'localhost'
ds_port = 9001
s_sock = socket(AF_INET, SOCK_STREAM)
s_sock.bind((server_ip, server_port))
s_sock.listen(5)
print("Server is ready")

fv_map = {}
dv_map = {}
edv_map = {}


def socket_connection():
    c_sock = socket(AF_INET, SOCK_STREAM)
    return c_sock


def thread_1():
    while (1):
        server_status_check()
        time.sleep(9)


def getListOfFiles(dirName):
    listOfFile = os.listdir(dirName)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(dirName, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            if ".txt" in entry:
                allFiles.append(entry)

    return allFiles

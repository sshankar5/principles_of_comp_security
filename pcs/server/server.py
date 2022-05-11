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

def server_status_check():
    print("server health is being checked")
    cs1 = socket_connection()
    b = getListOfFiles(curr_dir)
    c = []
    for x in b:
        if x.endswith(".txt"):
            size = len(x)
            x1 = x[:size - 4]
            try:
                x2 = c_Pkey.decrypt(x1.encode()).decode('utf-8')
                c.append(x2)
            except:
                c.append(x1)
    send_query = ' '.join([str(item) for item in c])
    # print(send_query)
    send_query = "server_status_check" + " " + send_query
    print("the details of send query:")
    print(send_query)
    send_query = c_Pkey.encrypt(send_query.encode('utf-8'))
    cs1.connect((ds_ip, ds_port))
    cs1.send(send_query)
    cs1.close()

def replica_file(filename):
    data = []
    print(filename)
    if "<DIRRENAME>" in filename:
        h = filename.split('|')[4]
        dat = eval(h)
        data=dat['replicas']
        msg=filename
    elif "<DIRCREATE>" in filename:
        h = filename.split('|')[3]
        dat = eval(h)
        data=dat['replicas']
        msg=filename
    elif "RENAME" in filename:
        msg = filename
        h = filename.split('|')[3]
        data = eval(h)
    # data = p['replicas']
    elif "DELETE" in filename:
        msg = filename
        h = filename.split('|')[2]
        data = eval(h)
        # data = p['replicas']
    else:
        print(fv_map)
        fname = filename.split('|')[0]
        path=filename.split('|')[1]
        print("fname in replica ", fname)
        f = open(fname, 'r')
        #fn = c_Pkey.decrypt(fn.encode('utf-8')).decode('utf-8')
        #fn+=".txt"
        text = f.read()
        f.close()
        file1 = filename.split('|')[3]
        print("fv_map is ",fv_map[fname])
        msg = "REPLICATE|" + file1 + "|" + text + "|" + str(fv_map[fname]) + "|" + path
        print("msg is ",msg)
        h = filename.split('|')[2]
        data = eval(h)

    for i in data:
        server_ip = i['server_name']
        port = i['portno']
        try:
            replicate_socket = socket(AF_INET, SOCK_STREAM)
            replicate_socket.connect((server_ip, port))
            msg1 = c_Pkey.encrypt(msg.encode('utf-8'))
            replicate_socket.send(msg1)
            print("replication done succesfully")
            replicate_socket.close()
        except error as msg:
            print(msg)
            print("exception occured")



import time
from socket import *
import sys
import os.path
from cryptography.fernet import Fernet

c_key = b'Z4-L_1FMlhMiHJgNtI5hCyry2nV6-brcEW2lOsFZ7K8='
c_Pkey = Fernet(c_key)
ds_ip = "localhost"
ds_port = 9001
lock_ip = 'localhost'
lock_port = 8051
curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))


def socket_connection():
    c_sock = socket(AF_INET, SOCK_STREAM)
    return c_sock

def create_user(username, pwd):
    c_sock = socket_connection()
    c_sock.connect((ds_ip, ds_port))
    msg = " " + "|" + " " + "|" + "USER_CREATE" + "|" + username + "|" + pwd
    msg=c_Pkey.encrypt(msg.encode('utf-8'))
    c_sock.send(msg)
    resp = c_sock.recv(1024)
    c_sock.close()
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    return resp


def verification_user(username, pwd):
    c_sock = socket_connection()
    c_sock.connect((ds_ip, ds_port))
    msg = " " + "|" + " " + "|" + "USER_VERIFY" + "|" + username + "|" + pwd
    msg=c_Pkey.encrypt(msg.encode('utf-8'))
    c_sock.send(msg)
    resp = c_sock.recv(1024)
    c_sock.close()
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    return resp
  

def menu():
    print("\n----------------MENU---------------")
    print("<create> [filename] [permission]- Create the file")
    print("\t\t\tchoose the permission from below: 1 -> read_only, 2 -> read_write, 3 -> restricted")
    print("<write> [Filename] - Write text to a file")
    print("<read> [Filename] - Read from a file")
    print("<rename> [oldfilename] [newfilename] - Rename the file")
    print("<delete> [filename] - Delete the file")
    print("<CDIR> [Dirname]- create the directory")
    print("<CHDIR> [Dirname]- change to the other directory")
    print("<RDIR> [OldDirname] [NewDirname]- Rename the directory")
    print("<quit> - Quit from the application")
    print("-------------------------------------")

    
def send_rename(c_sock, file, filename_DS, IP_DS, PORT_DS, c_id, replicate_servers,path):
    file += ".txt"
    send_msg = file + "|" + filename_DS + "|" + "RENAME" + "|" + replicate_servers + "|" + path + "|" + c_id
    send_msg = c_Pkey.encrypt(send_msg.encode('utf-8'))
    check_cache(filename_DS, file, c_id, 0)
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5", PORT_DS)
    c_sock.connect((IP_DS, PORT_DS))
    c_sock.send(send_msg)
    resp = c_sock.recv(1024)
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    if resp == "Not permitted":
        print("You are not permitted")
    elif resp is not None:
        print("rename was success")

  
def send_delete(c_sock, file, filename_DS, IP_DS, PORT_DS, c_id, replicate_servers, path):
    msg = filename_DS + "|" + "DELETE" + "|" + replicate_servers + "|" + path + "|" + c_id
    check_cache(filename_DS, file, c_id, 1)
    msg = c_Pkey.encrypt(msg.encode('utf-8'))
    c_sock.connect((IP_DS, PORT_DS))
    c_sock.send(msg)
    resp = c_sock.recv(1024)
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    if resp == "success":
        print("delete was success")
    else:
        print("delete operation didn't execute properly")
        
def write(c_sock, fs_IP, fs_PORT, filename, rw, fvmap, msg, replicate_servers, path, c_id):
    if filename not in fvmap:
        fvmap[filename] = 0
    elif rw != "r":
        fvmap[filename] += 1
    send_query = filename + "|" + rw + "|" + msg + "|" + replicate_servers + "|" + path + "|" + c_id
    # send the sting requesting a write to the file server
    c_sock.connect((fs_IP, fs_PORT))
    send_query = c_Pkey.encrypt(send_query.encode('utf-8'))
    print("the data transmitting over the network was: ", send_query)
    c_sock.send(send_query)


def read(c_sock, fs_IP, fs_PORT, filename, rw, fvmap, msg, filename_DS, path, c_id):

    if filename not in fvmap:
        print("Requested file is not in cache")
        send_query = filename + "|" + rw + "|" + msg + "|" + path + "|" + c_id
        print("Send query: ",send_query)
        print("fs ip and port ", fs_IP, fs_PORT)
        send_query = c_Pkey.encrypt(send_query.encode('utf-8'))
        try:
            c_sock.connect((fs_IP, fs_PORT))
            c_sock.send(send_query)
            fvmap[filename] = 0
            return False
        except error as msg:
            return 2
    cache_filepath = curr_path + "\\client_cache" + c_id + "\\" + filename_DS
    if os.path.exists(cache_filepath) == True:
        send_query = "CHECK_VERSION|" + filename +"|" +c_id
        send_query = c_Pkey.encrypt(send_query.encode('utf-8'))
        print("Send query is ",send_query)
        cs1 = socket_connection()
        try:
            cs1.connect((fs_IP, fs_PORT))
            cs1.send(send_query)
            fsversion = cs1.recv(1024)  # receive file server version number
            fsversion = c_Pkey.decrypt(fsversion).decode('utf-8')
            print("fsversion is ",fsversion)
        except error as e:
            print("Not getting connected")
            return 2
        cs1.close()

    if fsversion != str(fvmap[filename]):
        print("Versions are different and so requesting file from server")
        fvmap[filename] = int(fsversion)
        send_query = filename + "|" + rw + "|" + msg
        send_query = c_Pkey.encrypt(send_query.encode('utf-8'))

        # send the string requesting a read from the file server
        c_sock.connect((fs_IP, fs_PORT))
        c_sock.send(send_query)
        return False  # didn't go to cache - new version
    else:
        # read from cache
        print("Reading from cache as the file is updated")
        cache(filename_DS, "READ", "r", c_id)

    return True  # went to cache

def directory(c_sock, c_id, filename, rw, flag, check_list, path="EMPTY", atype=" ", user_list=" "):
    c_sock.connect((ds_ip, ds_port))
    if check_list:
        msg = " " + '|' + " " + '|' + "LIST" + '|' + c_id
        c_sock.send(msg.encode())
        resp = c_sock.recv(1024).decode()
        c_sock.close()
        print("List of existing files:\n")
        print(resp)
    else:
        if flag == 0:
            msg = filename + '|' + rw + '|' + "CREATE" + '|' + c_id + '|' + path + '|' + atype + '|' + user_list
            print(msg)
        elif len(filename.split()) == 2:
            msg = filename + '|' + rw + '|' + "RENAME" + '|' + c_id + '|' + path
        # elif flag==1:
        #    msg = filename + '|' + rw + '|' + "Write" + '|' + c_id
        elif flag == 2:
            msg = filename + '|' + rw + '|' + "DELETE" + '|' + c_id + '|' + path
        else:
            msg = filename + '|' + rw + '|' + "Read" + '|' + c_id + '|' + path
        # send the string requesting file info to directory send_directory_service
        msg = c_Pkey.encrypt(msg.encode('utf-8'))
        c_sock.send(msg)
        resp = c_sock.recv(1024)
    return resp


def validity(input, rename=0):
    if len(input.split()) < 2:
        print("Format is incorrect")
        menu()
        return False
    elif len(input.split()) < 3 and rename == 1:
        print("Format is incorrect")
        menu()
        return False
    else:
        return True  

    
def lock_unlock_file(c_sock, c_id, filename, flag):
    c_sock.connect((lock_ip, lock_port))
    msg = ""
    if flag == "lock":
        # msg = filename + "|" + "_1_:" + "| |" + c_id
        msg = c_id + "|_1_:|" + filename  # 1 = lock the file
    elif flag == "unlock":
        # msg = filename + "|" + "_2_:" + "| |" + c_id
        msg = c_id + "|_2_:|" + filename  # 2 = unlock the file

    # send the string requesting file info to directory service
    c_sock.send(msg.encode())
    resp = c_sock.recv(1024).decode()
    return resp

def handle_create(filename, atype, c_id, flag, fv_map, dv_map, user_list):
    # file creation started
    c_sock = socket_connection()  # create socket to directory service
    if c_id not in dv_map:
        dv_map[c_id] = "EMPTY"
    reply = directory(c_sock, c_id, filename, 'w', flag, False, dv_map[c_id], atype, user_list)  # request the file info from directory service
    c_sock.close()  # close the connection
    reply = c_Pkey.decrypt(reply).decode('utf-8')
    if reply == "FILE_Already_EXIST":
        print(filename + " already exist on a fileserver")
        return False
    else:
        print(reply)
        filename_DS, IP_DS, PORT_DS, replicate_servers, path = reply.split('|')
        execute_write(filename_DS, IP_DS, PORT_DS, filename, c_id, fv_map, replicate_servers, path)
    return True


def execute_write(filename_DS, IP_DS, PORT_DS, filename, c_id, fv_map, replicate_servers, path):
    # ------ LOCKING ------
    c_sock = socket_connection()
    grant_lock = lock_unlock_file(c_sock, c_id, filename_DS, "lock")
    c_sock.close()
    while grant_lock != "file_granted":
        print("File not granted, polling again...")
        c_sock = socket_connection()
        grant_lock = lock_unlock_file(c_sock, c_id, filename_DS, "lock")
        c_sock.close()

        if grant_lock == "TIMEOUT":  # if timeout message received from locking service, break
            return False
        time.sleep(0.1)  # wait 0.1 sec if lock not available and request it again

    print("You are granted the file...")
    # ------ ClIENT WRITING TEXT ------
    print("Write some text...")
    print("<end> to finish writing")
    print("-----------------------------------")
    text = ""
    while True:
        input = sys.stdin.readline()
        if "<end>" in input:  # check if user wants to finish writing
            break
        else:
            text += input
    print("-----------------------------------")
    # ------ WRITING TO FS ------
    c_sock = socket_connection()
    write(c_sock, IP_DS, int(PORT_DS), filename_DS, "a+", fv_map, text, replicate_servers,path, c_id)  # send text and filename to the fileserver
    # print ("SENT FOR WRITE")
    resp = c_sock.recv(1024)
    c_sock.close()
    resp = c_Pkey.decrypt(resp).decode('utf-8')

    print(resp.split("...")[0])  # split version num from success message and print message
    version_num = int(resp.split("...")[1])
    if version_num != fv_map[filename_DS]:
        print("Server version no changed - updating client version no.")
        fv_map[filename_DS] = version_num
    # ------ CACHING ------
    cache(filename_DS, text, "a+", c_id)

    # ------ UNLOCKING ------
    c_sock = socket_connection()
    reply_unlock = lock_unlock_file(c_sock, c_id, filename_DS, "unlock")
    c_sock.close()
    print(reply_unlock)
    return True


def handle_write(filename, c_id, flag, fv_map, dv_map):
    # ------ INFO FROM DS ------
    c_sock = socket_connection()  # create socket to directory service
    if c_id not in dv_map:
        dv_map[c_id] = "EMPTY"
    resp = directory(c_sock, c_id, filename, 'w', flag, False,dv_map[c_id])  # request the file info from directory service
    c_sock.close()  # close the connection
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    if resp == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        filename_DS, IP_DS, PORT_DS, replicate_servers, path = resp.split('|')
        execute_write(filename_DS, IP_DS, PORT_DS, filename, c_id, fv_map, replicate_servers, path)
        return True


def handle_read(filename, fv_map, c_id, dv_map):
    c_sock = socket_connection()  # create socket to directory service
    if c_id not in dv_map:
        dv_map[c_id] = "EMPTY"
    print("the value of read id", dv_map[c_id])
    resp = directory(c_sock, c_id, filename, 'r', 1, False, dv_map[c_id])  # send file name to directory service
    c_sock.close()  # close directory service connection
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    if resp == "FILE_DOES_NOT_EXIST":
        print(filename + " does not exist on a fileserver")
    else:
        # parse info received from the directory service
        filename_DS = resp.split('|')[0]
        data = resp.split('|')[1]
        p = eval(data)
        h = p['replicas']
        path = resp.split('|')[2]
        for i in h:
            IP_DS = i['server_name']
            PORT_DS = i['portno']
            c_sock = socket_connection()  # create socket to file server

            read_cache = read(c_sock, IP_DS, int(PORT_DS), filename_DS, "r", fv_map, "READ", filename_DS, path, c_id)  # send filepath and read to file server
            if read_cache != 2:
                break

        if not read_cache:
            reply = c_sock.recv(1024).decode()  # receive reply from file server, this will be the text from the file
            c_sock.close()

            print("the received msg was: ", reply)
            try:
                reply = c_Pkey.decrypt(reply.encode()).decode('utf-8')
            except:
                print()
            print("reply is ",reply)
            if reply != "EMPTY_FILE":
                print("-------------------------------------------")
                print(reply)
                print("-------------------------------------------")
                cache(filename_DS, reply, "w", c_id, path)  # update the cached file with the new version from the file server
                print(filename_DS + " successfully cached...")
            else:
                print(filename_DS + " is empty...")
                del fv_map[filename_DS]


  
def handle_rename(oldfilename, newfilename, c_id, dv_map):
    c_sock = socket_connection()  # create socket to directory service
    if c_id not in dv_map:
        dv_map[c_id] = "EMPTY"
    filename = oldfilename + " " + newfilename
    resp = directory(c_sock, c_id, filename, 'r', 1, False, dv_map[c_id])  # send file name to directory service
    c_sock.close()  # close directory service connection
    resp = c_Pkey.decrypt(resp).decode('utf-8')

    if resp == "FILE_DOES_NOT_EXIST":
        print("you don't have access to rename this file or this file is not present in your system")
        return False
    elif resp == "Not permitted":
        print("You are not permitted")
        return False
    else:
        c_sock = socket_connection()
        filename_DS, IP_DS, PORT_DS, replicate_servers, path = resp.split('|')
        send_rename(c_sock, oldfilename, filename_DS, IP_DS, int(PORT_DS), c_id, replicate_servers, path)
        return True

    
  
def handle_delete(file, c_id, dv_map):
    c_sock = socket_connection()  # create socket to directory service
    if c_id not in dv_map:
        dv_map[c_id] = "EMPTY"
    resp = directory(c_sock, c_id, file, 'r', 2, False, dv_map[c_id])  # send file name to directory service
    c_sock.close()  # close directory service connection
    resp = c_Pkey.decrypt(resp).decode('utf-8')
    if resp == "FILE_DOES_NOT_EXIST":
        print("you don't have access to delete this file or this file is not present in your system")
        return False
    elif resp == "Not permitted":
        print("You are not permitted")
        return False
    else:
        c_sock = socket_connection()
        p = eval(resp)
        filename_DS = p[file]['filename']
        path=p[file]['path']
        IP_DS = (p[file]['primary']['server_name'])
        # IP_DS = 'localhost'
        PORT_DS = p[file]['primary']['portno']
        replicate_servers = str(p[file]['replicas'])

        # -----------------------LOCKING------------------------
        grant_lock = lock_unlock_file(c_sock, c_id, filename_DS, "lock")
        c_sock.close()
        while grant_lock != "file_granted":
            print("File not granted, polling again...")
            c_sock = socket_connection()
            grant_lock = lock_unlock_file(c_sock, c_id, filename_DS, "lock")
            c_sock.close()

            if grant_lock == "TIMEOUT":  # if timeout message received from locking service, break
                return False
            time.sleep(0.1)  # wait 0.1 sec if lock not available and request it again

        print("You are granted the file...")

        c_sock = socket_connection()
        send_delete(c_sock, file, filename_DS, IP_DS, int(PORT_DS), c_id, replicate_servers, path)
        c_sock.close()

        # ------ UNLOCKING ------
        c_sock = socket_connection()
        reply_unlock = lock_unlock_file(c_sock, c_id, filename_DS, "unlock")
        c_sock.close()
        print(reply_unlock)
        cache_filepath = curr_path + "\\client_cache" + c_id + "\\" + filename_DS
        if os.path.exists(cache_filepath):
            os.remove(cache_filepath)
        return True

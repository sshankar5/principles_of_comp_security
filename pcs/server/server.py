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
            
            
def read_write_request(filename, rw, write_data, fv_map, k, c_id):
    cs1 = socket_connection()
    filename1 = filename.split("\\")[-1]
    size = len(filename1)
    filename1 = filename1[:size - 4]
    fn = c_Pkey.decrypt(filename1.encode('utf-8')).decode('utf-8')
    print("filename sent is ",fn)
    send_query = fn + "|" + c_id + "|" +"GET_KEY"
    send_query = c_Pkey.encrypt(send_query.encode('utf-8'))
    cs1.connect((ds_ip, ds_port))
    cs1.send(send_query)
    reply = cs1.recv(1024)
    reply = c_Pkey.decrypt(reply).decode('utf-8')
    if reply == "Not permitted":
        return "You are not permitted"
    else:
        u_key = reply
        u_Pkey = Fernet(u_key)
    if rw == "a+":  # if write request
        if filename not in fv_map:
            fv_map[filename] = 0  # if empty (ie. if its a new file), set the version no. to 0
        else:
            fv_map[filename] += 1  # increment version no.
        print("filename for server ",filename)
        if k == 1:
            file = open(filename, "r")
            filedata = file.read()  # read the file's text into a string
            filedata = u_Pkey.decrypt(filedata.encode()).decode('utf-8')
            write_data = filedata + write_data
            file.close()
        file = open(filename, "w")
        print("file opened")
        write_data = u_Pkey.encrypt(write_data.encode('utf-8'))
        write_data = write_data.decode()
        print("write data is: ", write_data)
        file.write(write_data)
        print("New version of " + filename + " is " + str(fv_map[filename]))
        return "write request is successful", fv_map[filename]
    elif rw == "r":  # if read request
        try:
            file = open(filename, rw)
            filedata = file.read()  # read the file's text into a string
            filedata = u_Pkey.decrypt(filedata).decode('utf-8')
            if filename not in fv_map:
                fv_map[filename] = 0
            return (filedata, fv_map[filename])
        except IOError:  # IOError occurs when open(filepath,RW) cannot find the file requested
            print(filename + " does not exist\n")
            return "File does not exist", -1


def client_response(resp, rw, client_socket):
    if resp[0] == "write request is successful":
        reply = "File successfully written to..." + str(resp[1])
    elif resp[0] == "You are not permitted":
        reply = "File does not exist"
    elif resp[1] != -1 and rw == "r":
        reply = resp[0]
    elif resp[1] == -1:
        reply = resp[0]
    reply = c_Pkey.encrypt(reply.encode('utf-8'))
    client_socket.send(reply)

 

def main():
    T = Thread(target = thread_1)
    T.setDaemon(True)                  
    T.start()    
    while 1:
        client_socket, address = s_sock.accept()
        msg = client_socket.recv(1024)
        msg = c_Pkey.decrypt(msg).decode('utf-8')
        # msg= msg.decode()
        print("the request msg is", msg)
        if "<GETPATH>" in msg:
            id = msg.split("|")[1]
            if id not in edv_map:
                res="EMPTY"
            else:   
                res = edv_map[id]
            print("the value of res", res)
            res = c_Pkey.encrypt(res.encode('utf-8'))
            client_socket.send(res)
        elif "<DIRRENAME>" in msg:
            res=""
            file1=msg.split("|")[0]
            file4=msg.split("|")[1]
            file2=msg.split("|")[2]
            file3=msg.split("|")[3]
            serv=msg.split("|")[5]
            if file3=="EMPTY":
                dv_map[file2]=""
                edv_map[file2]=""
                cpath=curr_dir
            else:
                cpath=curr_dir+"\\"+edv_map[file2]
            p=os.listdir(cpath)
            print("the cureent path is",cpath)
            print(" the directories in cpath is",p)
            c=0
            k=""
            q=""
            st=hashlib.sha256(file1.encode('utf-8')).hexdigest()
            print("the value of st is",st)
            sp=hashlib.sha256(file4.encode('utf-8')).hexdigest()
            for i in p:
                if ".txt" not in i:
                    print("the value of i is",i)
                    sp=hashlib.sha256(file4.encode('utf-8')).hexdigest()
                    if st==i:
                        k=cpath+"\\"+i
                        print(k)
                        q=i
                        c=1
                    if sp==i:
                        c=2
                        break
            if c==2:
                res="Already exsits a dir with this name"
            elif c==1:
                file5=hashlib.sha256(file4.encode('utf-8')).hexdigest()
                k1=cpath+"\\"+file5
                print("value of new dir ",k1)
                os.rename(k,k1)
                if dv_map[file2]!="": 
                    res="SUCCESS"+'|'+dv_map[file2]
                    p1=edv_map[file2]
                else:
                    res="SUCCESS"
                    p1="EMPTY"
                msg="<DIRRENAME>"+"|"+p1+"|"+q+"|"+file5+"|"+serv
                replica_file(msg)
            res= c_Pkey.encrypt(res.encode('utf-8'))
            client_socket.send(res)
        elif "<DIRCREATE>" in msg:
            res=""
            file1=msg.split("|")[0]
            file2=msg.split("|")[1]
            file3=msg.split("|")[2]
            serv=msg.split("|")[4]
            cpath=curr_dir
            if file3=="EMPTY":
                dv_map[file2]=""
                edv_map[file2]=""
            else:
                cpath=curr_dir+"\\"+edv_map[file2]
            p=os.listdir(cpath)
            c=0
            for i in p:
                if ".txt" not in i:
                    st=hashlib.sha256(file1.encode('utf-8')).hexdigest()
                    if st==i:
                        c=1
                        res="Already exsits a dir with this name"
                        break
            if c==0:
                file1=hashlib.sha256(file1.encode('utf-8')).hexdigest()
                sk=cpath+"\\"+file1
                print("the value of dir",sk)
                os.mkdir(sk)
                if dv_map[file2]!="": 
                    res="SUCCESS"+'|'+dv_map[file2]
                    g=edv_map[file2]
                else:
                    res="SUCCESS"
                    g="EMPTY" 
                msg="<DIRCREATE>"+"|"+g+"|"+file1+"|"+serv
                replica_file(msg)   
            res= c_Pkey.encrypt(res.encode('utf-8'))
            client_socket.send(res)
        elif "<DIRCHANGE>" in msg:
            res=""
            file1=msg.split("|")[0]
            file2=msg.split("|")[1]
            file3=msg.split("|")[2]
            if file3=="EMPTY":
                dv_map[file2]=""
                edv_map[file2]=""
                cpath=curr_dir
            else:
                cpath=curr_dir+"\\"+edv_map[file2]
            if file1=="..":
                if cpath==curr_dir or dv_map[file2]=="":
                    res="you are present at the root directory idiot"
                else:
                    d=dv_map[file2].split("\\")
                    e=edv_map[file2].split("\\")
                    v=len(d)
                    if v==1:
                        dv_map[file2]=""
                        edv_map[file2]=""
                        res="SUCCESS"
                    else:
                        for i in range(v-1):
                            if i==0:
                                dv_map[file2]=d[i]
                                edv_map[file2]=e[i]
                            else:
                                dv_map[file2]=dv_map[file2]+"\\"+d[i]
                                edv_map[file2]=edv_map[file2]+"\\"+e[i]
                        res="SUCCESS"+"|"+dv_map[file2]
            else:
                p=os.listdir(cpath)
                c=0
                for i in p:
                    if ".txt" not in i:
                        st=hashlib.sha256(file1.encode('utf-8')).hexdigest()
                        if i==st:
                            c=1
                            cpath=cpath+"\\"+i
                            # res="Already exsits a dir with this name"
                            if dv_map[file2]=="":
                                dv_map[file2]=file1
                                print("you have entered this stupid block")
                                edv_map[file2]=i
                                res="SUCCESS"+"|"+dv_map[file2]
                                c=1
                                break
                            else:
                                dv_map[file2]=dv_map[file2]+"\\"+file1
                                edv_map[file2]=edv_map[file2]+"\\"+i
                                res="SUCCESS"+"|"+dv_map[file2]
                                c=1
                                break
                if c==0:
                    res="No such directory exsists"
            res= c_Pkey.encrypt(res.encode('utf-8'))
            client_socket.send(res)
        elif "RENAME" in msg:
            hi = "failure"
            oldfilename = msg.split("|")[0]
            newfilename = msg.split("|")[1]
            id = msg.split("|")[5]
            c_path = msg.split("|")[4]
            repser = msg.split("|")[3]
            v = c_path.split("\\")
            if len(v) == 1:
                if ".txt" not in c_path:
                    curr_path = curr_dir + "\\" + edv_map[id]
                    hs = edv_map[id]
                else:
                    curr_path = curr_dir
                    hs = "EMPTY"
            else:
                curr_path = curr_dir + "\\" + edv_map[id]
                hs = edv_map[id]
            for x in os.listdir(curr_path):
                if x.endswith(".txt"):
                    size = len(x)
                    x1 = x[:size - 4]
                    x1 = c_Pkey.decrypt(x1.encode()).decode('utf-8')
                    x1 += ".txt"
                    if x1 == oldfilename:
                        size1 = len(newfilename)
                        newfilename = newfilename[:size1 - 4]
                        newfilename = c_Pkey.encrypt(newfilename.encode('utf-8'))
                        newfilename = newfilename.decode() + ".txt"
                        p = x
                        q = newfilename
                        x = curr_path + "\\" + x
                        newfilename = curr_path + "\\" + newfilename
                        os.rename(x, newfilename)
                        hi = "success"
                        msg = p + "|" + q + "|" + "RENAME" + "|" + repser + "|" + hs
                        replica_file(msg)
                        break
            hi = c_Pkey.encrypt(hi.encode('utf-8'))
            client_socket.send(hi)
        elif "DELETE" in msg:
            hi = "failure"
            file = msg.split("|")[0]
            id = msg.split("|")[4]
            repserv = msg.split("|")[2]
            c_path = msg.split("|")[3]
            v=c_path.split("\\")
            if len(v)==1:
                if ".txt" not in c_path:
                    curr_path=curr_dir+"\\"+edv_map[id]
                    hs=edv_map[id]
                else:
                    curr_path=curr_dir
                    hs="EMPTY"
            else:
                curr_path=curr_dir+"\\"+edv_map[id]
                hs=edv_map[id]
            for x in os.listdir(curr_path):
                if x.endswith(".txt"):
                    size = len(x)
                    x1 = x[:size - 4]
                    x1 = c_Pkey.decrypt(x1.encode()).decode('utf-8')
                    x1 += ".txt"
                    if x1 == file:
                        k = x
                        print("the name of file is", k)
                        x = curr_path + "\\" + x
                        os.remove(x)
                        hi = "success"
                        msg1 = k + "|" + "DELETE" + "|" + repserv + "|" + hs
                        replica_file(msg1)
                        break
            hi = c_Pkey.encrypt(hi.encode('utf-8'))
            client_socket.send(hi)
        elif msg != "" and "CHECK_VERSION" not in msg:
            filename, rw, text, temp, path, id = msg.split("|")  # file path to perform read/write on
            print("starting is ",filename)
            msgs = []
            res = ""
            k = 0
            v = path.split("\\")
            print(v)
            if len(v) == 1:
                if ".txt" not in path:
                    print("entered root block")
                    curr_path = curr_dir + "\\" + edv_map[id]
                    hs = edv_map[id]
                else:
                    curr_path = curr_dir
                    hs = "EMPTY"
            else:
                curr_path = curr_dir + "\\" + edv_map[id]
                hs = edv_map[id]
            q = ""
            for x in os.listdir(curr_path):
                if x.endswith(".txt"):
                    size = len(x)
                    print("the value of x1 is:", x)
                    q = x
                    x1 = x[:size - 4]
                    print("the value of x1 is:", x1)
                    x1 = c_Pkey.decrypt(x1.encode('utf-8')).decode('utf-8')
                    x1 += ".txt"
                    if x1 == filename:
                        print("entered the exisisting file block")
                        res = curr_path + "\\" + x
                        k = 1
                        break
            if (len(res) == 0):
                siz = len(filename)
                filename = filename[:siz - 4]
                print(filename)
                re = c_Pkey.encrypt(filename.encode('utf-8'))
                res = re.decode() + ".txt"
                q = res
                res = curr_path + "\\" + res
            print("the file name is: ", res)
            response = read_write_request(res, rw, text, fv_map, k,id)  # perform the read/write and check if successful
            client_response(response, rw,
                            client_socket)  # send back write successful message or send back text for client to read
            if rw !="r" and response == "File does not exist":
                continue
            else:
                msg1 = res + "|" + hs + "|" + temp + "|" + q
                print("msg1 is ", msg1)
                replica_file(msg1)
        elif "CHECK_VERSION" in msg:
            c_file = msg.split("|")[1]  # parse the version number to check
            for x in os.listdir():
                if x.endswith(".txt"):
                    size = len(x)
                    x1 = x[:size - 4]
                    x1 = c_Pkey.decrypt(x1).decode('utf-8')
                    x1 += ".txt"
                    if x1 == c_file:
                        print("Checking version of " + c_file)
                        hi = c_Pkey.encrypt(str(fv_map[x]).encode('utf-8'))
                        client_socket.send(hi)
                        client_socket.close()

if __name__ == "__main__":
    main()

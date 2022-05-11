def socket_connection():
    c_sock = socket(AF_INET, SOCK_STREAM)
    return c_sock

def get_permission(i):
    m = int(i)
    if m == 1:
        return "read_only"
    elif m == 2:
        return "read_write"
    elif m == 3:
        return "Restricted"

def servers():
    k=str({"replicas": [
            {
                "server_name": "localhost",
                "portno": 8002
            },
            {
                "server_name": "localhost",
                "portno": 8003
            }
        ]})
    return s1_ip+"|"+str(s1_port)+"|"+k

def change_mappings(client_msg):
    print("change mapping: ",client_msg)
    filename = client_msg.split('|')[0]
    file1 = filename.split()[0]
    file2 = filename.split()[1]
    author = client_msg.split('|')[3]
    path = client_msg.split('|')[4]
    data = {}
    c = 0
    if path=="EMPTY":
        path=file1+".txt"
    with open("filemappings.txt", 'rb') as file:
        cred_decrypt = file.read()
        dat = c_Pkey.decrypt(cred_decrypt).decode('utf-8')
        j = eval(dat)
        # file2=c_Pkey.encrypt(file2.encode('utf-8'))
        for key, i in j.items():
            if key == file1:
                if j[key]['permission'] == 'read_write' and j[key]['path'] == path:
                    data[file2] = j[key]
                    data[file2]['filename'] = file2 + ".txt"
                    if ".txt" in data[file2]['path']:
                        data[file2]['path'] = file2 + ".txt"
                    c = 1
                elif j[key]['permission'] == 'Restricted' and (j['key']['author'] == author and j[key]['path'] == path):
                    data[file2] = j[key]
                    data[file2]['filename'] = file2 + ".txt"
                    if ".txt" in data[file2]['path']:
                        data[file2]['path'] = file2 + ".txt"
                    c = 1
                else:
                    return None

            if c == 1:
                del j[key]
                break
        j.update(data)
        with open("filemappings.txt", 'wb') as file:
            print(j)
            dat = str(j)
            d1 = c_Pkey.encrypt(dat.encode('utf-8'))
            file.write(d1)
            # print(json.dump(j, file, indent=4))
    if c == 1:
        actual_filename = data[file2]['filename']  # get actual filename (eg. file123.txt)
        server_addr = str(data[file2]['primary']['server_name'])  # get the file's file server IP address
        server_port = str(data[file2]['primary']['portno'])  # get the file's file server PORT number
        replicas = data[file2]['replicas']
        path = data[file2]['path']
        print("actual_filename: " + actual_filename)
        print("server_addr: " + server_addr)
        print("server_port: " + server_port)
        return actual_filename + "|" + server_addr + "|" + server_port + "|" + str(replicas) + "|" +path

    

def delete_mappings(client_msg):
    print("delete mapping: ",client_msg)
    key = client_msg.split('|')[0]
    path = client_msg.split('|')[4]
    if path=="EMPTY":
        path=key+".txt"
    data = {}
    with open("filemappings.txt", 'rb') as file:
        # j = json.load(file)
        cred_decrypt = file.read()
        dat = c_Pkey.decrypt(cred_decrypt).decode('utf-8')
        j = eval(dat)
        print(type(j))
        author = client_msg.split('|')[3]
        if key in j:
            data[key] = j[key]
        else:
            return None
        if j[key]['permission'] == "read_write" and j[key]['path'] == path:
            del j[key]
        elif j[key]['permission'] == "Restricted" and (author == j[key]['author'] and j[key]['path'] == path):
            del j[key]
        else:
            return None
        with open("filemappings.txt", 'wb') as file:
            # jdata.update(data)
            print(j)
            dat = str(j)
            d1 = c_Pkey.encrypt(dat.encode('utf-8'))
            file.write(d1)
            # print(json.dump(j, file, indent=4))
    return data
  
  
  def create_userid(client_msg):
    username, pwd = client_msg.split('|')[3:]
    print(username, pwd)
    details = []
    key = Fernet.generate_key()
    details.append(username)
    details.append(pwd)
    details.append(key.decode('utf-8'))
    with open("logins.csv", 'a+', newline='') as login:
        writer = csv.writer(login)
        writer.writerow(details)
        login.close()
    return "1"


def user_verification(client_msg):
    username, pwd = client_msg.split('|')[3:]
    j = 0
    with open("logins.csv", 'rt') as file:
        d_reader = csv.DictReader(file, delimiter=',')  # read file as a csv file, taking values after commas
        header = d_reader.fieldnames  # skip header of csv file
        for row in d_reader:
            if row['user_id'] == username and pwd == row['password']:
                j = 1
                break
    if j == 1:
        return username
    else:
        return ""


    
def main():
    while 1:
        c_sock, addr = s_sock.accept()
        recv_msg = c_sock.recv(1024)
        print("host is ", addr)
        print("++++++++++++++", recv_msg)
        try:
            recv_msg = c_Pkey.decrypt(recv_msg).decode('utf-8')
        except:
            recv_msg = c_Pkey.decrypt(recv_msg).decode('utf-8')
        response = ""
        print("++++++++++++++", recv_msg)
        if "server_status_check" in recv_msg:
            status_check(recv_msg)
        elif "GET_KEY" in recv_msg:
            fn, c_id, temp = recv_msg.split("|")
            print("filename fn is ",fn)
            filesize = os.path.getsize("filemappings.txt")
            ans = ""
            with open("filemappings.txt", 'rb') as file:
                if filesize == 0:
                    ans = "Not permitted"
                else:
                    cred_decrypt = file.read()
                    print("cred_decrypt is ",cred_decrypt)
                    dat = c_Pkey.decrypt(cred_decrypt).decode('utf-8')
                    j = eval(dat)
                    # file2=c_Pkey.encrypt(file2.encode('utf-8'))
                    for key, i in j.items():
                        print("key is ",key)
                        print("fn is ",fn)
                        if key == fn:
                            print("permitted list ",j[key]['permitted_users'])
                            if (j[key]['permitted_users'].find(c_id) == -1 and j[key]['author']!=c_id):
                                ans = "Not permitted"
                                print("sent not permitted")
                            else:
                                author = j[key]['author']
                                with open("logins.csv", 'rt') as file:
                                    d_reader = csv.DictReader(file,
                                                          delimiter=',')  # read file as a csv file, taking values after commas
                                    header = d_reader.fieldnames  # skip header of csv file
                                    for row in d_reader:
                                        if row['user_id'] == author:
                                            print("found the key for user")
                                            ans = row['key']
                                print("sent the key : ",ans)
                            break
                print("ans issssssss ", ans)
                ans = c_Pkey.encrypt(ans.encode('utf=8'))
                c_sock.send(ans)
                c_sock.close()
                continue
        elif "<CREATEDIR>" in recv_msg or "<CHANGEDIR>" in recv_msg:
            response = servers()
        elif "<RNAMEDIR>" in recv_msg:
            response = servers()
        elif "<RENAMEDIR>" in recv_msg:
            response = change_path(recv_msg)
        elif "USER_CREATE" in recv_msg:
            response = create_userid(recv_msg)
            response = c_Pkey.encrypt(response.encode())
            c_sock.send(response)  # send the file information or non-existance message to the client
            c_sock.close()
            continue
        elif "USER_VERIFY" in recv_msg:
            response = user_verification(recv_msg)
            response = c_Pkey.encrypt(response.encode('utf-8'))
            c_sock.send(response)  # send the file information or non-existance message to the client
            c_sock.close()
            continue
        elif "CREATE" in recv_msg:
            print("started the mapping scenario")
            response1 = create_mappings(recv_msg)
            if response1 is not None:
                response = check_mappings(recv_msg, False, 1)
            else:
                response = "FILE_Already_EXIST"
                print("RESPONSE: \n" + response)
                print("\n")
        elif "LIST" in recv_msg:
            print("entered the dummy block")
            response = check_mappings(recv_msg, True)  # check the mappings for the file
        elif "RENAME" in recv_msg:
            filename = recv_msg.split('|')[0]
            fn = filename.split()[0]
            author = recv_msg.split('|')[3]
            filesize = os.path.getsize("filemappings.txt")
            ans = ""
            with open("filemappings.txt", 'rb') as file:
                if filesize == 0:
                    ans = "Not permitted"
                else:
                    cred_decrypt = file.read()
                    print("cred_decrypt is ",cred_decrypt)
                    dat = c_Pkey.decrypt(cred_decrypt).decode('utf-8')
                    j = eval(dat)
                    # file2=c_Pkey.encrypt(file2.encode('utf-8'))
                    for key, i in j.items():
                        print("key is ",key)
                        print("fn is ",fn)
                        if key == fn:
                            if (j[key]['author']==author):
                                response = change_mappings(recv_msg)
                            elif (j[key]['permitted_users'].find(author) == -1):
                                response = "Not permitted"
                                print("sent not permitted")
                            else:
                                response = change_mappings(recv_msg)
        elif "DELETE" in recv_msg:
            fn = recv_msg.split('|')[0]
            author = recv_msg.split('|')[3]
            filesize = os.path.getsize("filemappings.txt")
            ans = ""
            with open("filemappings.txt", 'rb') as file:
                if filesize == 0:
                    ans = "Not permitted"
                else:
                    cred_decrypt = file.read()
                    print("cred_decrypt is ",cred_decrypt)
                    dat = c_Pkey.decrypt(cred_decrypt).decode('utf-8')
                    j = eval(dat)
                    # file2=c_Pkey.encrypt(file2.encode('utf-8'))
                    for key, i in j.items():
                        print("key is ",key)
                        print("fn is ",fn)
                        if key == fn:
                            if (j[key]['author']==author):
                                response = delete_mappings(recv_msg)
                            elif (j[key]['permitted_users'].find(author) == -1):
                                response = "Not permitted"
                                print("sent not permitted")
                            else:
                                response = delete_mappings(recv_msg)                                                 
        else:
            response = check_mappings(recv_msg, False)
        if response is not None:  # for existance of file
            response = str(response)
            print("RESPONSE: \n" + response)
            print("\n")
        else:
            response = "FILE_DOES_NOT_EXIST"
            print("RESPONSE: \n" + response)
            print("\n")
        response = c_Pkey.encrypt(response.encode('utf-8'))
        print("response over the network: ", response)
        c_sock.send(response)  # send the file information or non-existance message to the client
        c_sock.close()

if __name__ == "__main__":
    main()

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

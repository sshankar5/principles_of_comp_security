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

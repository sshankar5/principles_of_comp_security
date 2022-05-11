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

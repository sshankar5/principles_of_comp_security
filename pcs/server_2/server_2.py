


















def main():
    while 1:
        client_socket, address = s_sock.accept()
        msg = client_socket.recv(1024)
        msg = c_Pkey.decrypt(msg).decode('utf-8')
        # msg= msg.decode()
        print("the requested msg is", msg)
        if "<DIRRENAME>" in msg:
            file1 = msg.split("|")[2]
            file4 = msg.split("|")[3]
            p = msg.split("|")[1]
            if p == "EMPTY":
                c_path = curr_dir + "\\" + file1
                r_path = curr_dir + "\\" + file4
            else:
                c_path = curr_dir + "\\" + p + "\\" + file1
                r_path = curr_dir + "\\" + p + "\\" + file4
            os.rename(c_path, r_path)
        elif "<DIRCREATE>" in msg:
            p = msg.split("|")[1]
            file1 = msg.split("|")[2]
            if p == "EMPTY":
                c_path = curr_dir + "\\" + file1
            else:
                c_path = curr_dir + "\\" + p + "\\" + file1
            os.makedirs(c_path)
        elif "RENAME" in msg:
            oldfilename = msg.split("|")[0]
            newfilename = msg.split("|")[1]
            p = msg.split("|")[4]
            if p == "EMPTY":
                oldfilename = curr_dir + "\\" + oldfilename
                newfilename = curr_dir + "\\" + newfilename
            else:
                oldfilename = curr_dir + "\\" + p + "\\" + oldfilename
                newfilename = curr_dir + "\\" + p + "\\" + newfilename
            response = os.rename(oldfilename, newfilename)
        elif "DELETE" in msg:
            hi = "failure"
            file = msg.split("|")[0]
            p = msg.split("|")[3]
            if p == "EMPTY":
                file = curr_dir + "\\" + file
            else:
                file = curr_dir + "\\" + p + "\\" + file
            if os.path.exists(file):
                os.remove(file)
                hi = "success"
                hi = c_Pkey.encrypt(hi.encode('utf-8'))
            client_socket.send(hi)
        elif msg != "" and "CHECK_VERSION" not in msg and "REPLICATE" not in msg:
            filename, rw, text, p, id = msg.split("|")  # file path to perform read/write on
            if ".txt" in p:
                file = curr_dir
            else:
                c_socket = socket_connection()
                msg = "<GETPATH>" + "|" + id
                c_socket.connect((p_ip, p_port))
                msg = c_Pkey.encrypt(msg.encode())
                c_socket.send(msg)
                real_path = c_socket.recv(1024)
                real_path = c_Pkey.decrypt(real_path).decode('utf-8')
                file = curr_dir + "\\" + real_path
            print("the path is ", file)
            print(os.listdir(file))
            for x in os.listdir(file):
                print("the value of x is", x)
                if x.endswith(".txt"):
                    size = len(x)
                    x1 = x[:size - 4]
                    x1 = c_Pkey.decrypt(x1.encode()).decode('utf-8')
                    print("value of x1 is", x1)
                    x1 += ".txt"
                    if x1 == filename:
                        file = file + "\\" + x
                        response = read_write_request(file, rw, text,
                                                      fv_map, id)  # perform the read/write and check if successful
                        client_response(response, rw,
                                        client_socket)  # send back write successful message or send back text for client to read
                        break
        elif "CHECK_VERSION" in msg:
            c_file = msg.split("|")[1] 
            id=msg.split("|")[2] # parse the version number to check
            print("Checking version of " + c_file + "\n")
            c_socket = socket_connection()
            msg="<GETPATH>"+"|"+id
            c_socket.connect((p_ip,p_port))
            msg=c_Pkey.encrypt(msg.encode())
            c_socket.send(msg)
            real_path=c_socket.recv(1024)
            real_path=c_Pkey.decrypt(real_path).decode('utf-8')
            print(" the value of real path is",real_path)
            if real_path=="EMPTY":
                file=curr_dir
            else:
                file=curr_dir+"\\"+real_path
            print("filepath ",file)
            for x in os.listdir(file):
                print(x)
                if x.endswith(".txt"):
                    size=len(x)
                    x1=x[:size-4]
                    x1=c_Pkey.decrypt(x1.encode()).decode('utf-8')
                    x1+=".txt"
                    if x1==c_file:
                        if x not in fv_map:
                            fv_map[x] = 0
                        print("version is ",fv_map[x])
                        hi=c_Pkey.encrypt(str(fv_map[x]).encode('utf-8'))
                        client_socket.send(hi)
                        break
        elif "REPLICATE|" in msg:
            temp, rep_filename, rep_text, rep_version,p = msg.split("|")
            fv_map[rep_filename] = int(rep_version)
            if p=="EMPTY":
                file=curr_dir+"\\"+rep_filename
            else:
                file=curr_dir+"\\"+p+"\\"+rep_filename
            f = open(file, 'w')
            # write_data = Pkey.encrypt(rep_text.encode('utf-8'))
            f.write(rep_text)
            f.close()
            print(rep_filename + " successfully replicated...\n")
    client_socket.close()


if __name__ == "__main__":
    main()

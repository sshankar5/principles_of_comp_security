import sys
import getpass
import time
from builtins import input

import client_functions


def user_creation():
    print("enter the username:")
    username = input()
    while 1:
        pwd = getpass.getpass("enter the password:")
        pwd1 = getpass.getpass("please re-enter the password again:")
        if pwd == pwd1:
            break
        else:
            print("password didn't match so please retype your password")
    return client_functions.create_user(username, pwd)


def user_verify():
    while 1:
        print("please enter the user name:")
        username = input()
        pwd = getpass.getpass("enter the password:")
        u = client_functions.verification_user(username, pwd)
        if u != "":
            break
        else:
            print("user credentials didn't match")
    return u, username
  
  def uinstruct():
    print("Please select one option:")
    print("1. New User Creation")
    print("2. Login")


def main():
    while 1:
        uinstruct()
        k = int(input())
        if k == 1:
            d = user_creation()
            if d:
                print("user have been created successfully")
                print("please login to access the files:")
                k1, temp = user_verify()
                if k1 is not None:
                    c_id = k1
                    break
        elif k == 2:
            k1, temp = user_verify()
            if k1 is not None:
                c_id = k1
                break
        else:
            print("invalid input")
    client_functions.menu()
    fv_map = {}
    dv_map = {}
    while 1:
        c_input = sys.stdin.readline()
        if "<create>" in c_input:
            while not client_functions.validity(c_input):  # error check the input
                c_input = sys.stdin.readline()
            flag = 0
            temp, filename, aType = c_input.split()
            print("Type the users you want to give permission\n")
            print("<end> to finish writing")
            print("-----------------------------------")
            text = ""
            j = 0
            while True:
                u = sys.stdin.readline()
                u = u.strip('\n')
                if "<end>" in u:  # check if user wants to finish writing
                    break
                else:
                    if j == 0:
                        text += u
                    else:
                        text += "," + u
                j += 1
            print("-----------------------------------")
            print("permitted user's list is ", text)
            resp = client_functions.handle_create(filename, aType, c_id, flag, fv_map, dv_map, text)
            if resp:
                print("file has been created successfully")
        elif "<write>" in c_input:
            while not client_functions.validity(c_input):
                c_input = sys.stdin.readline()
            filename = c_input.split()[1]
            flag = 1
            resp = client_functions.handle_write(filename, c_id, flag, fv_map, dv_map)
            if not resp:
                print("File unlock polling timeout")
            print("<write> mode exitted")
        elif "<read>" in c_input:
            while not client_functions.validity(c_input):
                c_input = sys.stdin.readline()
            filename = c_input.split()[1]
            client_functions.handle_read(filename, fv_map, c_id, dv_map)
            print("<read> mode exitted")

import sys
import getpass
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

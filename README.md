README ----

We have created the following modules:
(1) 3 Servers
(2) Directory Service
(3) Locking Service

Our DFS system can attend 10000 parallel requests at a time. Every file will have total 3 copies of them. 
We have added permissions like read only, read write and restricted and based on the permissions on the 
file, clients can create, read, write, delete, and rename the file. We have used a cache service to be used
for easy access and maintained file version to check whether the present copies are recently updated one or not.

We have implemented the locking service using which we can manage the file versions when multiple clients are 
accessing the same file. As an example, if 2 clients are requesting to write in same file then the first request 
will be considered, and system will lock that file until first request is completed. After completion of first 
client's request, our system will unlock the file and second client can access it.

In order to run the file system, the first thing to be done is to start the three servers named server.py, server_2.py and server_3.py. 

The next file to run would be the directory service file named database_checking.py, and then the locking service file named lock_unlock.py. 

These files can be run by using the python line command "python <filename>.py", after 'cd'ing into the directory of the file. 

After this, the client file (client.py) needs to be run by different users on different machines. 

The user(s) will be presented with a menu which will display the services offered by the file system and he/she can proceed with a choice of their own.

The outline of this menu has been shown below:

 - <create> [filename] [permission]- Create the file
 - <write> [Filename] - Write text to a file
 - <read> [Filename] - Read from a file
 - <rename> [oldfilename] [newfilename] - Rename the file
 - <delete> [filename] - Delete the file
 - <CDIR> [Dirname] – create a directory
 - <CHDIR> [Dirname] – change to another directory 
 - <RDIR> [oldDirname] [newDirname] – rename a directory
 - <quit> - Quit from the application

Functions available to the user in the menu:

 1> Create file:
    This function is used for creating a file to be stored in the database.
    While creating the file, the user needs to specify the file name and the permissions associated with the file.
    Syntax - <create> [filename] [permission]

2> Write file:
    The user can write content to an existing file using this function, and this can be done only if that file is given the read-write permission.
    Syntax - <write> [Filename]

3> Read file: 
    This function is for reading the content present in an existing file in the database.
    Syntax - <read> [Filename]

4> Rename file:
    This function can be used for renaming an existing file. 
    This function can only be performed by users who have access to a particular file. 
    For example, a user without having the appropriate permissions to access a file will not be allowed to rename it as well.
    Syntax - <rename> [oldfilename] [newfilename]

5> Delete file:
    This function is for deleting a file stored in the database or a directory by authorized users.
    Syntax - <delete> [filename]

6> Create directory:
    This function is for allowing the user to create a directory in which they can create and store files.
    Syntax - <cdir> [Dirname]

7> Change Directory:
    This function is used for changing the working directory from one existing directory to another.
    Syntax - <chdir> [Dirname]

8> Rename Directory:
    This function is for allowing the user to change the name of an existing directory.
    Syntax - <rdir> [oldDirname] [newDirname]


PERMISSIONS AVAILABLE TO USERS IN THE FILE SYSTEM:

1> Read_only:
    This permission denotes that the file can be inserted with data only at the time of creation, and once
    the file has been created and saved with data, when it is accessed later on, it can only be read from. The content of
    the file cannot be changed anytime in the future. If a user without this permission tries to read a file, 
    a “file does not exist” message will be displayed.    

2> Read_write:
    This means that a file with this permission can be read and edited even after the creation of the file. 
    The file contents can be edited anytime in the future as well. The users granted this permission can
    read, write, rename and delete a particular file. If a user without this permission tries to make changes to a file,
    a “file does not exist” message will be displayed.

3> Restricted:
    When a file is created with this permission, it means that only the person who can access or edit the file is the user 
    who created the file itself, and none of the other users can read or write to that particular file.

In this file system, the group permission grant feature has also been implemented. 
This means that an owner can grant file permissions to multiple people at the same time. 
For example, if the owner wants to provide a read_only permission to a group of 3 or 4 users, 
that can be performed at the same time, rather than granting the permission to each user individually and at separate times.

The malicious server detection is being performed by running a daemon thread for every 45 seconds.
What this means is that files present in the "filemappings.txt" file and the files present in the server 
do not match and this essentialy shows that a malicious server is present. 
If any mismatches are existing, they will be reported to the master, which is the databse_checking file.
A malicious server message will be displayed.
 
In our system we are using one key to transmit the data, one key for encrypting the filenames and directory names. Along with this we are genrating one key per user. It will be created when user credentials are created. While sharing the file with other users, we are not sharing the key with other users. if the user is permitted by the owner of the file then system will allow him to make changes based on the permissions. We are encrypting and decrypting the data of files using the key of the owner.

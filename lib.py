"""
Version 0-5-8
github.com/Ogg3/CheckArroyo
"""

import datetime
import sqlite3
import tkinter as tk
import re
from tkinter import *
from tkinter import messagebox
from zipfile import ZipFile
import traceback

from parse3 import *


class GUI_args(object):
    input_path = None
    output_path = None
    speed = None
    mode = None
    time_start = None
    time_stop = None
    # contentmanager = None
    msg_id = None
    display_window = None

    def __init__(self, input_path, output_path, speed, mode, time_start, time_stop, msg_id,
                 display_window):
        self.input_path = input_path
        self.output_path = output_path
        self.speed = speed
        self.mode = mode
        self.time_start = time_start
        self.time_stop = time_stop
        # self.contentmanager = contentmanager
        self.msg_id = msg_id
        self.display_window = display_window


# Return known types of content types
def check_ctype(int_ctype):

    # 1 is text message
    if int_ctype == 1:
        return "Text message"
    # 0 is snap
    elif int_ctype == 0:
        return "Snap"
    # 2 is media
    elif int_ctype == 2:
        return "Media"
    # 4 is audio messages
    elif int_ctype == 4:
        return "Audio message"
    else:
        return "Content type " + str(int_ctype)


# GUI Section
# Insert a value in an entry box and del the existing text
def ent_insert(ent, var):
    ent.delete(0, 'end')
    ent.insert(0, var)


# Retrun the value from an entry widget and check if widget is empty
def return_entry_check(en):

    content = en.get()
    if content == "":
        messagebox.showinfo("ERROR", "ENTRY BOX " + str(en) + "IS EMPTY")
    else:
        return content


# Retrun the value from an entry widget without checking if widget is empty
def return_entry(en):
    return en.get()


# Write a list to a text widget
def write_to_tex(lista, tex):
    try:
        tex.config(state=tk.NORMAL)

        def write_to(strin, tex):
            s = strin + "\n"
            tex.insert(tk.END, s)
            tex.see(tk.END)

        for i in range(len(lista)):
            write_to(str(lista[i]), tex)
            tex.insert(tk.END, "\n")

        tex.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)


# Write a string to a text widget
def write_string_tex(strin, tex):
    tex.config(state=tk.NORMAL)

    s = str(strin) + "\n"
    tex.insert(tk.END, s)
    tex.see(tk.END)

    tex.config(state=tk.DISABLED)


# Write a strin to a rapport window
def write_rapport_tex(lista, tex):
    try:
        def write_to(strin, tex):
            s = strin + "\n"
            tex.insert(tk.END, s)
            tex.see(tk.END)

        for i in range(len(lista)):
            write_to(str(lista[i]), tex)
        tex.insert(tk.END, "]" + "\n")
        tex.see(tk.END)
    except Exception as e:
        messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)


def write_rapport_image_tex(im, tex):
    try:
        tex.insert(tk.END, "[" + "\n")
        tex.see(tk.END)

        s = str(im)
        tex.insert(tk.END, s)
        tex.see(tk.END)

        tex.insert(tk.END, "\n")
        tex.see(tk.END)
    except Exception as e:
        messagebox.showinfo("ERROR", traceback.format_exc() + "\n" + e.__doc__)


# Retrive the content of a text widget
def retrieve_input(tex):
    lista = []
    strin = ""
    for i in tex.get("1.0", 'end-1c'):
        if i != "\n":
            strin = strin + i
        else:
            lista.append(strin)
            strin = ""
    return lista


# Check if list contains only empty strings
def check_list_for_empty(lst):

    for i in lst:
        if i != "":
            return False

    return True


# Check zip file for contetntmanagers and return the path of the largest one
def check_contentmanagers(input_path, output_path):

    # Get the largest content manager
    def largets(content_managers):
        large = ""

        check = True

        for i in content_managers:

            # Add the first one to var
            if check:
                large = i
                check = False

            # Check if content managers size is larger
            if i[1] > large[1]:
                large = i

        return large

    managers = []

    with ZipFile(input_path, "r") as f:
        y = 0
        for i in f.infolist():

            if 'contentmanagerV3' in i.filename:
                a = i.filename.split('/')

                if a[len(a) - 1] == 'contentManagerDb.db':
                    y = y + 1
                    managers.append((i.filename, i.file_size / (1024 * 1024)))

        # Check the size of content managers
        manager = largets(managers)
        f.extract(manager[0], output_path)
        f.close()

        # return the manager that is gonna be used and the amount of content managers found
        return manager, y


# Decode string
def decode_string(proto_string, bin_string):
    strings = []

    # Check if any string messages where found
    if proto_string is not None:

        # Check if multiple strings where found
        if type(proto_string) is list:

            for i in proto_string:
                # Encode because reasons
                tmp = i.encode('utf-8', 'ignore')

                strings.append("".join(re.findall("[a-zA-Z0-9äöåÄÖÅ -:()=?&$%#\/]+", tmp.decode('utf-8', 'ignore'))))
    else:
        strings.append("".join(re.findall("[a-zA-Z0-9äöåÄÖÅ ]+", bin_string.decode('utf-8', 'ignore'))))

    # Check if list is only empty strings
    if check_list_for_empty(strings):
        return ["ERROR - No strings in protobuffer or script is unable to parse message"]

    return strings


# return a dict of a nested dict
def find_string_in_dict(data):
    for k, v in data.items():
        if isinstance(v, dict):
            yield k, v
            yield from find_string_in_dict(v)
        else:
            yield k, v


# Turn a raw protobuf file to find a msg string
def proto_to_msg(bin_file):
    messages_found = []
    messages = ParseProto(bin_file)

    res = find_string_in_dict(messages)
    for k, v in res:
        if "string" in k:
            messages_found.append(v)

    return messages_found


# Turn raw protobuf file and find key
def proto_to_key(bin_file):
    messages = ParseProto(bin_file)

    res = find_string_in_dict(messages)
    for k, v in res:
        if "string" in k:
            return v


"""
If both values are None then no time has been set so all times are valid
"""
def check_time(msg, args, gui_check):
    # Check if GUI is being used or not
    if gui_check:
        if args.time_start != "" and args.time_stop != "":
            # Check if message was created within a range of dates
            return inRange(args.time_start, args.time_stop, msg)
        else:
            return True
    else:
        if args.time_start is not None and args.time_stop is not None:
            # Check if message was created within a range of dates
            return inRange(args.time_start, args.time_stop, msg)
        else:
            return True


"""
Check blobs for usernames in primary.docobjects
"""


def check_id_username(userid, pdpath):
    check = checkPD(userid, pdpath)
    if check != "":
        return check
    else:
        pass


"""
Used for CLI mode
Displays contentmanagers and returns a content manager based on user input
"""


def displayIOScontentmanagers(input_path, ouput_path):
    managers = []

    # Display contentmanagers
    print("Available content managers:")

    with ZipFile(input_path, "r") as f:
        y = 0
        for i in f.infolist():

            if 'contentmanagerV3' in i.filename:
                a = i.filename.split('/')

                if a[len(a) - 1] == 'contentManagerDb.db':
                    # print(a)
                    y = y + 1
                    managers.append(i.filename)
                    print(str(y) + " Name: " + i.filename)
                    print("Size: " + str(i.file_size / (1024 * 1024)) + " MB")
                    print()

        ret = input("Use content manager (1 - " + str(len(managers)) + "): ")

        if (int(ret) - 1) >= len(managers) or (int(ret) - 1) < 0:
            print("Error: Invalid choice")
            print()
            displayIOScontentmanagers(input_path)

        f.extract(managers[int(ret) - 1], ouput_path)
        f.close()

        return managers[int(ret) - 1]


"""
Used for GUI mode
Displays contentmanagers and returns a content manager based on user input
"""


def displayIOScontentmanagers_GUI(input_path):
    managers = []

    with ZipFile(input_path, "r") as f:
        y = 0
        for i in f.infolist():

            if 'contentmanagerV3' in i.filename:
                a = i.filename.split('/')

                if a[len(a) - 1] == 'contentManagerDb.db':
                    # print(a)
                    y = y + 1
                    managers.append((i.filename, str(i.file_size / (1024 * 1024))))

        return managers


# Searches for a file with name and extracts them
def checkandextract(args, string, mode):
    check = checkinzip(args, string, mode)
    if check is None:
        return None
    else:
        effromzip(check[0], args)
        return os.path.abspath(args.output_path + '/' + check[0])


# Checks primary.docobjects for a hits on a id and returns the username
def checkPD(pd, path):
    path = os.path.abspath(path)

    conn = sqlite3.connect(path)

    qr = "SELECT p FROM 'snapchatter' WHERE userId LIKE '%s'" % pd

    curs = conn.execute(qr)

    # Check for usernames in blob
    def checkUsernam(blob, conn):

        # Get all the usernames
        qr = "SELECT username FROM 'index_snapchatterusername'"

        curs = conn.execute(qr)

        for i in curs:
            index = blob[0].find(i[0].encode())
            if index != -1:
                return i[0]

        return False

    check = ""
    for i in curs:

        check = checkUsernam(i, conn)

        # If we found a matching username
        if check is not False:
            return check

        # For some reason this is the only way to return a False query, plz help
        if i is not None:
            pass
        else:
            return None

    return check


# Check if time is in range
def inRange(start, stop, time_check):
    if stop is not None and start is not None:
        start = conv2Time(start)
        stop = conv2Time(stop)
        time_check = convTime(time_check)
        time_check = datetime.date(time_check.year, time_check.month, time_check.day)

        return start <= time_check <= stop
    else:
        return True


# Checks zipfile from files with the name string and returns a list with paths to those files
def checkforfile21(path):
    path = os.path.abspath(path)

    data = []

    with ZipFile(path, "r") as f:
        for i in f.namelist():

            a = i.split('/')

            if len(a[len(a) - 1]) >= 21 and i[len(i) - 1] != "/":
                data.append(i)
        f.close()

    if data == []:
        return None
    else:
        return data


# Extract contentmanager
def checkinzip(args, string, mode):
    path = os.path.abspath(args.input_path)

    data = []

    with ZipFile(path, "r") as f:
        for i in f.namelist():
            if mode == "path":
                if string in i and i[len(i) - 1] != "/":
                    data.append(i)
            elif mode == "file":
                new = i.split("/")
                if string == new[len(new) - 1] and i[len(i) - 1] != "/":
                    data.append(i)
            elif mode == "contentmanager":
                new = i.split("/")
                if string in i and i[len(i) - 1] != "/":
                    if new[len(new) - 1] == "contentManagerDb.db":
                        data.append(i)
        f.close()

    if data == []:
        return None
    else:
        return data


# Reads content managers to report back where a key is used
def readContentManager(key, path):
    try:
        path = os.path.abspath(path)
        # Opens contentManagerDb.db
        # Searches blob (CONTENT_DEFINITION) for a string
        # TODO report if no attachment was found
        conn = sqlite3.connect(path)

        qr = "SELECT * FROM CONTENT_OBJECT_TABLE WHERE KEY LIKE '%" + key + "%'"

        curs = conn.execute(qr)

        return curs
    except:
        print("Could not connect to: ", str(path))


# Convert string to time object
def conv2Time(time):
    datea = datetime.datetime.strptime(time, "%Y-%m-%d")
    return datetime.date(datea.year, datea.month, datea.day)


# Convert Time
def convTime(tim):
    # UTC +0
    tim = str(tim)
    return datetime.datetime.utcfromtimestamp(int(tim[:10]))


# Gets a list of conversations ids
def getConv(conn, msg_id):
    # if msg_id is empty get all convos
    if msg_id == "":
        curs = conn.execute("SELECT client_conversation_id FROM 'conversation_message'")
    elif msg_id is None:
        curs = conn.execute("SELECT client_conversation_id FROM 'conversation_message'")
    else:
        qr = "SELECT client_conversation_id FROM 'conversation_message' WHERE client_conversation_id == '%s'" % msg_id

        curs = conn.execute(qr)

    conv = []

    # Make list on conv ids
    for i in curs:
        check = False
        for j in conv:

            # Check if msg id is had
            if j == i[0]:
                check = True

        # If passed check
        if check is False:
            conv.append(i[0])

    return conv


# Open zipfile
def readzip(zip):
    with ZipFile(zip, "r") as f:
        f.printdir()

    f.close()


# Extract file from zip to path
def effromzip(file, args):
    path = os.path.abspath(args.output_path)
    with ZipFile(args.input_path, 'r') as f:
        f.extract(file, path)

    f.close()


# Read from file in zip
def readfromzip(zip, file):
    with ZipFile(zip, 'r') as f:
        return f.read(file)


# Check keys with proto strings
def check_keys_proto(args, files, con, proto_string):
    match = []

    try:
        conn = sqlite3.connect(args.output_path + "/" + con)
    except Exception as e:
        print("Could not connect to: " + str(args.output_path + "/" + str(con)))
        print(e)
        return

    # Can be more then one key
    for i in proto_string:

        # Check length of key
        if len(i) > 15:
            qr = "SELECT CONTENT_DEFINITION, KEY FROM CONTENT_OBJECT_TABLE WHERE KEY LIKE '%" + i + "%'"
            curs = conn.execute(qr)

            # Loop through query
            for ii in curs:
                # Check if query is empty
                if i == ():
                    return False
                # print('INFO - Found key in contentmanager: '+i)
                # For all files
                for iii in files:

                    # Get only the file name
                    filename = iii.split('/')[len(iii.split('/')) - 1]

                    # Decode the blob
                    dblob = "".join(re.findall("[a-zA-Z0-9äöåÄÖÅ -]+", ii[0].decode('utf-8', 'ignore')))

                    # If a filename can be found in the blob add it in a tuple to matching list
                    if filename in dblob:
                        # print('INFO - Found link with key and file')
                        match.append((i, iii))

                    # Check if file is a key
                    if i in filename:
                        print("RARE - Found a key that is a file: " + str(i))
    return match


# Checks content managers for keys and stores them for later use
"""
3 - pics and videos
4 - voice messages
"""


def check_keys(args, files, con):
    match = []

    try:
        conn = sqlite3.connect(args.output_path + "/" + con)
    except Exception as e:
        print("Could not connect to: " + str(args.output_path + "/" + con))
        print(e)
        return

    # Diffrent querys gives different speed
    if args.speed == "F":
        curs = conn.execute(
            "SELECT CONTENT_DEFINITION, KEY FROM CONTENT_OBJECT_TABLE WHERE KEY LIKE '3-%' OR KEY LIKE '4-%'")
    elif args.speed == "M":
        curs = conn.execute(
            "SELECT CONTENT_DEFINITION, KEY FROM CONTENT_OBJECT_TABLE WHERE KEY LIKE '3-%' OR KEY LIKE '4-%' OR KEY LIKE '10-%' OR KEY LIKE '16-%'")
    elif args.speed == "S":
        curs = conn.execute("SELECT CONTENT_DEFINITION, KEY FROM CONTENT_OBJECT_TABLE")

    files_checked = 0
    print("Querys checked against files..")
    for res in curs:
        files_checked = files_checked + 1
        print('\r' + str(files_checked), end='', flush=True)
        # Make it usable
        condef = "".join(re.findall("[a-zA-Z0-9äöåÄÖÅ ]+", res[0].decode('utf-8', 'ignore')))

        # Go through every image that can be found
        for image in files:

            # Check if the name of the file match what is stored in CONTENT_DEFENITION
            if image.split('/')[len(image.split('/')) - 1] in condef:
                if '3-content~' in res[1]:
                    match.append((res[1].split('3-content~')[1][:21], checkinzip(args, image, "path"), res[1]))
                elif '3-thumbnail~' in res[1]:
                    match.append((res[1].split('3-thumbnail~')[1][:21], checkinzip(args, image, "path"), res[1]))
                elif '10-deeplink_icon~' in res[1]:
                    match.append((res[1].split('10-deeplink_icon~')[1], checkinzip(args, image, "path"), res[1]))
                elif '10-topvideo_firstframe~' in res[1]:
                    match.append((res[1].split('10-topvideo_firstframe~')[1], checkinzip(args, image, "path"), res[1]))
                elif '10-lfv_firstframe~' in res[1]:
                    match.append((res[1].split('10-lfv_firstframe~')[1], checkinzip(args, image, "path"), res[1]))
                elif '10-topimage~' in res[1]:
                    match.append((res[1].split('10-topimage~')[1], checkinzip(args, image, "path"), res[1]))
                elif '10-topvideo~' in res[1]:
                    match.append((res[1].split('10-topvideo~')[1], checkinzip(args, image, "path"), res[1]))
                elif '13-' in res[1]:
                    match.append((res[1].split('13-')[1], checkinzip(args, image, "path"), res[1]))
                elif '16-' in res[1]:
                    match.append((res[1].split('16-')[1], checkinzip(args, image, "path"), res[1]))
                elif '16-overlay~' in res[1]:
                    match.append((res[1].split('16-')[1], checkinzip(args, image, "path"), res[1]))
                elif '16-video~' in res[1]:
                    match.append((res[1].split('16-video~')[1], checkinzip(args, image, "path"), res[1]))
                elif '3-' in res[1]:
                    match.append((res[1].split('3-')[1][:21], checkinzip(args, image, "path"), res[1]))
                elif '4-' in res[1]:
                    match.append((res[1].split('4-')[1], checkinzip(args, image, "path"), res[1]))
                elif '4-overlay~' in res[1]:
                    match.append((res[1].split('4-overlay~')[1], checkinzip(args, image, "path"), res[1]))
                elif '4-video~' in res[1]:
                    match.append((res[1].split('4-video~')[1], checkinzip(args, image, "path"), res[1]))
                elif image.split('/')[len(image.split('/')) - 1] in condef and image.split('/')[
                    len(image.split('/')) - 1] in res[1]:
                    match.append((res[1], checkinzip(args, image, "path"), res[1]))

    return match


"""

"""


def check_participants(convID, conn, PDpath):
    part = []

    # query who is participating in conv
    qr = "SELECT * FROM user_conversation WHERE client_conversation_id == '%s'" % convID

    curs1 = conn.execute(qr)

    for j in curs1:

        # Check if username can be found
        checkU = checkPD(j[0], PDpath)

        if checkU != False:
            id = checkU, j[0]
        else:
            id = j[0]

        part.append(id)

    return part

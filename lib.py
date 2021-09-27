"""
github.com/Ogg3/CheckArroyo
"""

import datetime
import sqlite3
import time
import re
from tkinter import *
from zipfile import ZipFile
from parse3 import *
from datetime import datetime

"""
Make a class to match the args.parser being used for CLI
"""
class GUI_args(object):
    input_path = None
    output_path = None
    speed = None
    mode = None
    time_start = None
    time_stop = None
    # contentmanager = None
    msg_id = None
    #display_window = None

    def __init__(self, input_path, output_path, speed, mode, time_start, time_stop, msg_id):
        self.input_path = input_path
        self.output_path = output_path
        self.speed = speed
        self.mode = mode
        self.time_start = time_start
        self.time_stop = time_stop
        # self.contentmanager = contentmanager
        self.msg_id = msg_id
        #self.display_window = display_window


"""
Check what type of content is being sent
Return string if known
Return number if unknown
"""
def check_ctype(int_ctype):
    if type(int_ctype) is int:
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
    else:
        print("ERROR - lib.check_ctype excpects a int, not " + str(type(int_ctype)))


"""
Check if list contains only empty strings
"""
def check_list_for_empty(lst):
    for i in lst:
        if i != "":
            return False

    return True


"""
Check zip file for contetntmanagers and return the path of the largest one
"""
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
        return manager[0], y


"""
Decode a list of strings
Emojis are not supported
"""
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


"""
return a dict of a nested dict
"""
def find_string_in_dict(data):
    for k, v in data.items():
        if isinstance(v, dict):
            yield k, v
            yield from find_string_in_dict(v)
        else:
            yield k, v


"""
Turn a raw protobuf file to find a msg string
"""
def proto_to_msg(bin_file):
    messages_found = []
    messages = ParseProto(bin_file)

    res = find_string_in_dict(messages)
    for k, v in res:
        if "string" in k:
            messages_found.append(v)

    return messages_found


"""
Turn raw protobuf file and find key
"""
def proto_to_key(bin_file):
    messages = ParseProto(bin_file)

    res = find_string_in_dict(messages)
    for k, v in res:
        if "string" in k:
            return v


"""
If both values are None then no time has been set so all times are valid
"""
def check_time(msg, args):
    # Check if both vars are in use
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


"""
Searches for a file with name and extracts them
"""
def checkandextract(args, string, mode):
    check = checkinzip(args, string, mode)
    if check is None:
        return None
    else:
        effromzip(check[0], args)
        return os.path.abspath(args.output_path + '/' + check[0])


"""
Checks primary.docobjects for a hits on a id and returns the username
"""
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


"""
Check if time is in range
"""
def inRange(start, stop, time_check):
    if stop is not None and start is not None:
        start = conv2Time(start)
        stop = conv2Time(stop)
        time_check = convTime(time_check)
        time_check = datetime.date(time_check.year, time_check.month, time_check.day)

        return start <= time_check <= stop
    else:
        return True


"""
Checks zipfile from files with the name string and if the name is larger than 21 in length
returns a list with paths to those files
"""
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


"""
Extract contentmanager
"""
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


"""
Convert string to time object
"""
def conv2Time(time):
    datea = datetime.datetime.strptime(time, "%Y-%m-%d")
    return datetime.date(datea.year, datea.month, datea.day)


"""
Convert Time
"""
def convTime(tim):
    # UTC +0
    tim = str(tim)
    return datetime.datetime.utcfromtimestamp(int(tim[:10]))


"""
Gets a list of conversations ids
"""
def getConv(conn, msg_id):
    try:
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
    except Exception as e:
        print(e)
        return


"""
Open zipfile
"""
def readzip(zip):
    try:
        with ZipFile(zip, "r") as f:
            f.printdir()

        f.close()
    except Exception as e:
        print(e)
        return


"""
Extract file from zip to path
"""
def effromzip(file, args):
    try:
        path = os.path.abspath(args.output_path)
        with ZipFile(args.input_path, 'r') as f:
            f.extract(file, path)

        f.close()
    except Exception as e:
        print(e)
        #write_to_log(args, timea, e)
        return


"""
Read from file in zip
"""
def readfromzip(zip, file):
    try:
        with ZipFile(zip, 'r') as f:
            return f.read(file)
    except Exception as e:
        print(e)
        #write_to_log(args, timea, e)
        return


"""
Check keys with proto strings
Contentmanager is the queryed for the string and checked if there is a hit
Returns a list of tupels where the tupels are (key, path_to_image)
"""
def check_keys_proto(args, files, con, proto_string):

    match = []

    # Connect to database
    path = os.path.abspath(args.output_path + "/" + con)
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        print("ERROR - Could not connect to: " + str(args.output_path + "/" + str(con)))
        print(e)
        return

    # Get the key row from CONTENT_OBJECT_TABLE
    key = check_contentmangaredb(args, con)

    # Check output
    if key == None:
        errorstring = "ERROR - Could not find key row in contentmanager. Check the database for changes."
        write_to_log(errorstring)
        print(errorstring)
        return

    # Can be more then one key
    for string in proto_string:

        # Check length of key
        if len(string) > 15:
            # Old version used KEY now its CONTENT_KEY
            try:
                # Check if KEY table can be used
                qr = "SELECT CONTENT_DEFINITION, " + key + " FROM CONTENT_OBJECT_TABLE WHERE " + key + " LIKE '%" + string + "%'"
                curs = conn.execute(qr)

                # Loop through query
                for ii in curs:

                    # Check if query is empty
                    if string == ():
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
                            match.append((string, iii))

                        # Check if file is a key
                        if string in filename:
                            print("RARE - Found a key that is a file: " + str(string))

            except Exception as e:
                errorstring = "ERROR - Could not check key " + str(string) + " using " + qr + " " + str(e)
                write_to_log(errorstring)
                print(errorstring)
                return

    return match


"""
Returns unparsed structure of a database
"""
def get_database_struct(args, database):

    ret = []

    # Connect to database
    path = os.path.abspath(args.output_path + "/" + database)
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        print("ERROR - Could not connect to: ")
        print(e)
        return

    qr = "SELECT sql FROM sqlite_master"

    curs = conn.execute(qr)

    for i in curs:
        ret.append(i)

    return ret


"""
Checks the contentmanager.db structure and returns what kind of key is being used
"""
def check_contentmangaredb(args, database):

    sqlmaster = get_database_struct(args, database)

    # Go through sql structure
    for i in sqlmaster:
        if i[0] is not None:
            if "CONTENT_OBJECT_TABLE" in i[0]:
                data = i[0].split()
                check = data[4]
                if "KEY" == check or "CONTENT_KEY" == check:
                    return check

    # If no key row was found return None
    return None


"""

"""
def check_participants(convID, conn, PDpath):
    try:
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
    except Exception as e:
        errorstring = "ERROR - Could not check participants for " + str(convID) + " using " + PDpath + " " + str(e)
        write_to_log(errorstring)
        print(errorstring)


"""
Set up database to store data while its being parsed
"""
def create_store_data(database):
    # [id] INTEGER PRIMARY KEY,
    conn = sqlite3.connect(database)

    conn.execute('''
              CREATE TABLE IF NOT EXISTS Participants
              ( [Conversation] TEXT, [username] TEXT, [snapchat_id] TEXT)
              ''')

    conn.execute('''
              CREATE TABLE IF NOT EXISTS messages
              ([Conversation_id] text, [sent_by_username] text, [sent_by_snapchat_id] text, [Content_type] INTEGER, [Message_decoded] TEXT, [Message_og_id] TEXT, [Attachments_id] INTEGER, [Timestamp_sent] TEXT, [Timestamp_recived] TEXT)
              ''')

    conn.execute('''
              CREATE TABLE IF NOT EXISTS messages_attachments
              ( [Attachments_id] INTEGER, [filename] TEXT, [contentmangare_key] TEXT)
              ''')

    conn.commit()


"""
Insert the participants of a chat to data_store.db
"""
def insert_participants(database, Conversation, username, snapchat_id):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        qr = 'INSERT INTO Participants VALUES("' + str(Conversation) + '", "' + str(username) + '", "' + str(
            snapchat_id) + '")'
        c.execute(qr)
        conn.commit()
    except Exception as e:
        errorstring = "ERROR - Could not insert " + str(qr) + " to store_data.db." + str(e)
        write_to_log(errorstring)
        print(errorstring)


"""
Insert the message of a chat to data_store.db
"""
def insert_message(database, Conversation_id, sent_by_username, sent_by_snapchat_id, Content_type, Message_decoded,
                   Message_encoded, Attachments_id, Timestamp_sent, Timestamp_recived):
    try:
        conn = sqlite3.connect(database)
        qr = 'INSERT INTO messages VALUES("' + str(Conversation_id) + '", "' + str(sent_by_username) + '", "' + str(
            sent_by_snapchat_id) + '", "' + str(Content_type) + '", "' + str(Message_decoded) + '", "' + str(
            Message_encoded) + '", "' + str(Attachments_id) + '", "' + str(Timestamp_sent) + '", "' + str(
            Timestamp_recived) + '")'
        conn.execute(qr)
        conn.commit()
    except Exception as e:
        errorstring = "ERROR - Could not insert " + str(qr) + " to store_data.db." + str(e)
        write_to_log(errorstring)
        print(errorstring)


"""
Insert the attachment filename of a chat to data_store.db
"""
def insert_attachment(database, Attachments_id, filename, contentmangare_key):
    try:
        conn = sqlite3.connect(database)
        qr = 'INSERT INTO messages_attachments VALUES("' + str(Attachments_id) + '", "' + str(filename) + '", "' + str(
            contentmangare_key) + '")'
        conn.execute(qr)
        conn.commit()
    except Exception as e:
        errorstring = "ERROR - Could not insert "+str(qr)+" to store_data.db." + str(e)
        write_to_log(errorstring)
        print(errorstring)


"""
Check if file is a database
"""
def check_database(filename):
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    result = c.execute("SELECT sql FROM sqlite_master")

    # Check if results are returned
    for i in result:
        if i is not None:
            return True


"""
Retrieves the username and snapchat id for a every participant of a conversation
"""
def get_participants(database, conversation_id):
    ret = []

    conn = sqlite3.connect(database)
    qr = 'SELECT username, snapchat_id FROM Participants WHERE Conversation =="%s"' % conversation_id
    curs = conn.execute(qr)

    for res in curs:
        ret.append(res)

    return ret


"""
Retrieves the filename for a specific id
"""
def get_attachments(database, attachments_id):
    ret = []

    conn = sqlite3.connect(database)
    qr = 'SELECT filename FROM messages_attachments WHERE Attachments_id =="%s"' % attachments_id
    curs = conn.execute(qr)

    for res in curs:
        ret.append(res)

    return ret


"""
Get the timestamp for a specifik message and convert it to localtime of the computers settings
"""
def get_timestamp(database, Message_og_id, timestamp_sent):
    ret = []

    conn = sqlite3.connect(database)
    qr = """SELECT strftime('%Y-%m-%d %H:%M:%S.', "Timestamp_sent"/1000, 'unixepoch', 'localtime') || 
                ("Timestamp_sent"%1000), strftime('%Y-%m-%d %H:%M:%S.', "Timestamp_recived"/1000, 'unixepoch', 'localtime') || 
                ("Timestamp_recived"%1000) FROM messages WHERE Message_og_id == {0} AND Timestamp_sent == {1} """.format(
        Message_og_id, timestamp_sent)
    curs = conn.execute(qr)

    for res in curs:
        ret.append(res)

    return ret[0]


"""
Statistically the owner should be the user that shows the most
Get the user that has most occurrence in all conversations
"""

def get_owner(database):
    ret = []
    users = {}

    conn = sqlite3.connect(database)
    qr = "SELECT username FROM Participants"

    curs = conn.execute(qr)

    # Get usernames
    for res in curs:
        ret.append(res[0])

    # Get the occurrence of every participant
    for username in ret:

        # Check if user is in dict
        if username in users:
            users[username] = users[username] + 1
        else:
            users[username] = 1

    return max(users, key=users.get)


"""
Get all users and GUIDs
"""
def export_users(args, timea, database):
    ret = []
    users = []

    conn = sqlite3.connect(database)
    qr = "SELECT username, snapchat_id FROM Participants"

    curs = conn.execute(qr)

    # Get usernames
    for res in curs:
        ret.append(res)

    # Get the occurrence of every participant
    for username, snapchat_id in ret:

        # Check if user is in dict
        if (username, snapchat_id) not in users:
            users.append((username, snapchat_id))

    # Write contacts to file file
    with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "contacts.txt", "w") as a:
        for username, snapchat_id in users:
            a.write(username + ", " + snapchat_id + "\n")


"""
Write to log file
"""
def write_to_log(args, timea, msg):
    with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "log.txt", "a") as a:
        a.write(str(datetime.now()) + " " + msg + "\n")
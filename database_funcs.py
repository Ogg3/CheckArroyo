import sqlite3
from lib import *

def get_timestamp(database, Message_og_id, timestamp_sent):
    """
    Get the timestamp for a specifik message and convert it to localtime of the computers settings
    :param database:
    :param Message_og_id:
    :param timestamp_sent:
    :return:
    """
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

def getConv(conn, msg_id, args, timea):
    """
    Gets a list of conversations ids
    """
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
        write_to_log(e)
        return


def get_attachments(database, attachments_id):
    """
    Retrieves the filename for a specific id
    :param database:
    :param attachments_id:
    :return:
    """
    ret = []

    conn = sqlite3.connect(database)
    qr = 'SELECT filename, file_type FROM messages_attachments WHERE Attachments_id =="%s"' % attachments_id
    curs = conn.execute(qr)

    for res in curs:
        ret.append(res)

    return ret

def get_participants(database, conversation_id):
    """
    Retrieves the username and snapchat id for a every participant of a conversation
    :param database:
    :param conversation_id:
    :return:
    """
    ret = []

    conn = sqlite3.connect(database)
    qr = 'SELECT username, snapchat_id FROM Participants WHERE Conversation =="%s"' % conversation_id
    curs = conn.execute(qr)

    for res in curs:
        ret.append(res)

    return ret


def get_owner(database):
    """
    Statistically the owner should be the user that shows the most
    Get the user that has most occurrence in all conversations
    :param database:
    :return:
    """
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


def qurey_database(database, qr):
    """
    Runs database query
    returns a array with the result
    returns None if connection fails
    """

    ret = []

    try:
        conn = sqlite3.connect(database)
    except:
        errorstring = "ERROR - Could not connect to: " + database
        write_to_log(errorstring)
        return

    curs = conn.execute(qr)

    for i in curs:
        ret.append(i)

    return ret



def table_exists(database, name):
    """
    Checks if table exists in database
    returns 1 if exists
    returns 0 if not exists
    """

    try:
        conn = sqlite3.connect(database)
    except:
        errorstring = "ERROR - Could not connect to: " + database
        write_to_log(errorstring)
        return

    qr = '''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='%s' ''' % name

    curs = conn.execute(qr)

    for i in curs:
        return i[0]


def row_exists_count(database, table, name):
    """
    Checks a given database for a name in a table
    returns the number of rows if name and table was found
    Else returns 0
    :param database:
    :param table:
    :param name:
    :return: 0 if none or the amount of rows
    """

    try:
        conn = sqlite3.connect(database)
    except:
        errorstring = "ERROR - Could not connect to: " + database
        write_to_log(errorstring)
        return 0

    qr = '''SELECT count(%s) FROM %s ''' % (name, table)

    try:
        curs = conn.execute(qr)

        for i in curs:
            return i[0]

    except Exception as e:
        write_to_log(e)
        return 0


def export_users(database):
    """
    Get all users and GUIDs
    """
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
    with open(IO_paths.report_folder + "contacts.txt", "w") as a:
        for username, snapchat_id in users:
            a.write(username + ", " + snapchat_id + "\n")

def check_database(filename):
    """
    Check if file is a database
    :param filename:
    :return:
    """
    conn = sqlite3.connect(filename)
    c = conn.cursor()
    result = c.execute("SELECT sql FROM sqlite_master")

    # Check if results are returned
    for i in result:
        if i is not None:
            return True

def insert_attachment(database, Attachments_id, filename, contentmangare_key, file_type, args, timea):
    """
    Insert the attachment filename of a chat to data_store.db
    :param database:
    :param Attachments_id:
    :param filename:
    :param contentmangare_key:
    :param file_type:
    :param args:
    :param timea:
    :return:
    """
    try:
        conn = sqlite3.connect(database)
        qr = 'INSERT INTO messages_attachments VALUES("' + str(Attachments_id) + '", "' + str(filename) + '", "' + str(
            contentmangare_key) + '", "' + str(file_type) + '")'
        conn.execute(qr)
        conn.commit()
    except Exception as e:
        errorstring = "ERROR - Could not insert "+str(qr)+" to store_data.db." + str(e)
        write_to_log(errorstring)


def insert_message(database, Conversation_id, sent_by_username, sent_by_snapchat_id, Content_type, Message_decoded,
                   Message_encoded, Attachments_id, Timestamp_sent, Timestamp_recived, args, timea):
    """
    Insert the message of a chat to data_store.db
    :param database:
    :param Conversation_id:
    :param sent_by_username:
    :param sent_by_snapchat_id:
    :param Content_type:
    :param Message_decoded:
    :param Message_encoded:
    :param Attachments_id:
    :param Timestamp_sent:
    :param Timestamp_recived:
    :param args:
    :param timea:
    :return:
    """
    try:
        conn = sqlite3.connect(database)
        qr = 'INSERT INTO messages VALUES("' + str(Conversation_id) + '", "' + str(sent_by_username) + '", "' + str(
            sent_by_snapchat_id) + '", "' + str(Content_type) + '", "' + str(Message_decoded) + '", "' + str(
            Message_encoded) + '", "' + str(Attachments_id) + '", "' + str(Timestamp_sent) + '", "' + str(
            Timestamp_recived) + '")'
        conn.execute('INSERT INTO messages VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(Conversation_id), str(sent_by_username), str(
            sent_by_snapchat_id), str(Content_type), str(Message_decoded), str(
            Message_encoded), str(Attachments_id), str(Timestamp_sent), str(
            Timestamp_recived)))
        conn.commit()
    except Exception as e:
        errorstring = "ERROR - Could not insert " + str(qr) + " to store_data.db." + str(e)
        write_to_log(errorstring)


def insert_participants(database, Conversation, username, snapchat_id, args, timea):
    """
    Insert the participants of a chat to data_store.db
    :param database:
    :param Conversation:
    :param username:
    :param snapchat_id:
    :param args:
    :param timea:
    :return:
    """
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        qr = 'INSERT INTO Participants VALUES("' + str(Conversation) + '", "' + str(username) + '", "' + str(
            snapchat_id) + '")'
        c.execute("INSERT INTO Participants VALUES(?, ?, ?)", (str(Conversation), str(username), str(
            snapchat_id)))
        conn.commit()
    except Exception as e:
        errorstring = "ERROR - Could not insert " + str(qr) + " to store_data.db." + str(e)
        write_to_log(errorstring)


def create_store_data(database):
    """
    Set up database to store data while its being parsed
    :param database:
    :return:
    """
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
              ( [Attachments_id] INTEGER, [filename] TEXT, [contentmangare_key] TEXT, [file_type] TEXT)
              ''')

    conn.commit()


"""
Returns unparsed structure of a database
returns a array with the result of a query
"""
def get_database_struct(database):

    ret = []

    try:
        conn = sqlite3.connect(database)
    except:
        errorstring = "ERROR - Could not connect to: " + database
        write_to_log(errorstring)
        return

    qr = "SELECT sql FROM sqlite_master"

    curs = conn.execute(qr)

    for i in curs:
        ret.append(i)

    return ret
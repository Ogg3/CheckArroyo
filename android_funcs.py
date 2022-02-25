import sys

from lib import *
from database_funcs import *

def android_mode(args, IO_paths, GUI_check, store_data, start_time):
    """

    :param args:
    :param IO_paths:
    :param GUI_check:
    :return:
    """
    info = "INFO - Using Android mode"
    write_to_log(info)

    # Extract arroyo and perform checks
    arroyo = checkandextract(args, 'arroyo.db', "file")

    # Check if file exists
    if arroyo is None:
        info = "ERROR - Could not find arroyo."
        write_to_log(info)
        return

    # Check if core.db exists
    CorePath = checkandextract(args, 'core.db', "file")
    if CorePath is None:
        info = "ERROR - Could not find core.db"
        write_to_log(info)

    # Check if main.db exists
    MainPath = checkandextract(args, 'main.db', "file")
    if MainPath is None:
        info = "ERROR - Could not find main.db"
        write_to_log(info)

    files = ""

    # Check if script should look for attachments or not
    if args.check_attachmets == "Y":

        # Make a list of files in com.snap.file_manager_ with mode path
        files = checkinzip(args, 'files', "path")

        info = "INFO - Checking for attachments"
        write_to_log(info)
    else:
        info = "INFO - NOT checking for attachments"
        write_to_log(info)

    # Check integrity of important files
    try:

        conn_arroyo = sqlite3.connect(arroyo)

        info = "INFO - Checking arroyo"
        write_to_log(info)

        # Write arroyo path
        write_to_log("INFO - Path: "+str(arroyo))

        # Check if arroyo is usable
        messages_count, Carroyo = check_arroyo(arroyo)

        if Carroyo:
            info = """
                        ===================================
                        SUCCESS - Arroyo passed all checks!
                        ===================================
                        """
            write_to_log(info)
        else:
            info = """
                        ===================================
                        WARNING - Arroyo passed all checks!
                        ===================================
                        """
            write_to_log(info)

            info = "INFO - Exiting"
            write_to_log(info)

            return

        info = "INFO - Checking main.db"
        write_to_log(info)

        info = "INFO - Path: " + str(MainPath)
        write_to_log(info)

        # Check if main.db is usable
        count_usernames_raw, Cmain = check_main_db(MainPath)

        if Cmain:
            info = """
                        ===================================
                        SUCCESS - main.db passed all checks!
                        ===================================
                        """
            partCheck = True
            write_to_log(info)
        else:
            info = """
                        ===================================
                        SUCCESS - main.db passed all checks!
                        ===================================
                        """
            partCheck = False
            write_to_log(info)

        info = "INFO - Checking core.db"
        write_to_log(info)
        info = "INFO - Path: " + str(CorePath)
        write_to_log(info)

        # Check if core.db is usable
        count, Ccore, = check_core(os.path.abspath(CorePath))

        if Ccore:
            info = """
                        ===================================
                        SUCCESS - core.db passed all checks!
                        ===================================
                        """
            content_check = True
            write_to_log(info)
        else:
            info = "WARNING - core.db did not pass checks"
            content_check = False
            write_to_log(info)


    except Exception as e:
        error = "ERROR - Checks Failed, one or more database is unusable" + str(
            traceback.format_exc() + "\n" + e.__doc__)
        write_to_log(error)
        return "ERROR"

    # Get all conversations
    convons = getConv(conn_arroyo, args.msg_id, args, IO_paths.report_time)

    # Check amount of conversations
    if convons != []:

        if args.msg_id is not None:
            info = "INFO - Filtering for " + args.msg_id
            write_to_log(info)

        info = "INFO - Found conversations " + str(convons)
        write_to_log(info)

    else:
        write_to_log("ERROR - No conversations found.")
        sys.exit(1)

    # Set var
    attachment_id = 0
    nr = 0

    info = "INFO - Parsing messages"
    write_to_log(info)

    # For every conversation
    for conv_id in convons:

        # Get a conversation
        qr = "SELECT * FROM 'conversation_message' WHERE client_conversation_id LIKE '%s' ORDER BY creation_timestamp ASC" % conv_id
        curs = conn_arroyo.execute(qr)

        # Write participants only once
        participants_bool = True

        # Go through database query
        for i in curs:
            nr = nr + 1
            print("\rParsed " + str(nr) + " out of " + str(messages_count) + " messages", flush=True, end='')

            # Write participants only once
            if participants_bool:
                participants = ""

                # Check if primary.docobjects was usable
                if partCheck:

                    # Get participants of a conversation
                    participants = link_user_convo(conv_id, conn_arroyo, MainPath)

                    if participants != None:

                        # For every paricipant
                        for username, snapchat_id in participants:

                            # Add to database for storage
                            insert_participants(store_data, conv_id, username, snapchat_id, args,
                                                IO_paths.report_time)

                # Write participants only once
                participants_bool = False

            # Get raw timestamp from arroyo
            raw_timestamp = i[7]

            # Check if time filter is applied
            res = check_time(raw_timestamp, args)

            # Content type
            ctype = i[13]
            ctype_string = check_content_type(i[13])

            # Rename list
            # Rename list
            client_conversation_id = i[0]
            client_message_id = i[1]
            server_message_id = i[2]
            client_resolution_id = i[3]
            local_message_content_id = i[4]
            message_content = i[5]
            message_state_type = i[6]
            creation_timestamp = i[7]
            read_timestamp = i[8]
            sent_by_snapchat_id = i[16]


            # Check for content type and decode
            #raw_protobuf(i[5], i[1], i[2])
            #proto_to_bytes(i[5])
            Message_encoded = ParseProto(i[5])
            proto_string = proto_to_msg(i[5])
            string_list = decode_string(proto_string, i[5])

            # Check time flag
            if res:

                attachment_check = False

                if partCheck:
                    # Link usersnames to snapchat ids
                    checkU = link_snapchatid_username(i[16], MainPath)

                    # Check if username was linked
                    if checkU != []:
                        sent_by_username = checkU
                        sent_by_snapchat_id = i[16]
                    else:
                        sent_by_username = ""
                        sent_by_snapchat_id = i[16]
                else:
                    sent_by_username = sent_by_snapchat_id

                # if a text message was found
                if ctype == 1:

                    # Get only the text message
                    string_list = string_list[0]

                else:

                    # If no attachment was found with cache check old method
                    if not attachment_check:

                        # If content manager passed checks
                        if content_check:
                            attachments = check_keys_proto_Android(args, files, CorePath, proto_string,
                                                       IO_paths.report_time)

                            # Check flags
                            if args.check_attachmets == "Y":
                                # print(attachments)
                                # Check if attachments link was found
                                if attachments:

                                    attachment_check = True

                                    # Increase id
                                    attachment_id = attachment_id + 1

                                    # Write attachments and key to html report and link to the extracted file
                                    for key, image in attachments:
                                        effromzip(image)
                                        file_type = compare_magic_bytes(
                                            os.path.abspath(IO_paths.report_folder + "/" + image))
                                        insert_attachment(store_data,
                                                          attachment_id,
                                                          image,
                                                          key,
                                                          file_type,
                                                          args,
                                                          IO_paths.report_time)
                                else:
                                    attachment_check = False

                # If an attachment was found
                if attachment_check:

                    insert_message(store_data,
                                   conv_id,
                                   sent_by_username,
                                   sent_by_snapchat_id,
                                   ctype_string,
                                   message_content,
                                   Message_encoded,
                                   string_list,
                                   client_message_id,
                                   server_message_id,
                                   attachment_id,
                                   creation_timestamp,
                                   read_timestamp)
                # If no attachment was found
                else:
                    insert_message(store_data,
                                   conv_id,
                                   sent_by_username,
                                   sent_by_snapchat_id,
                                   ctype_string,
                                   message_content,
                                   Message_encoded,
                                   string_list,
                                   client_message_id,
                                   server_message_id,
                                   -1,
                                   creation_timestamp,
                                   read_timestamp)

    # Get the snapchat owner
    if partCheck:
        if participants != None:
            owner = get_owner(store_data)
        else:
            owner = None
    else:
        owner = None

    print()
    info = "INFO - Parsing complete"
    write_to_log(info)

    info = "INFO - Found "+str(attachment_id)+" attachments."
    write_to_log(info)

    execute_time = (time.time() - start_time)
    info = str(execute_time) + " (s)"
    write_to_log(info)

    return [convons, execute_time, store_data, owner, partCheck]

def check_main_db(database):
    """
    Checks the given main.db file structure (Android)
    returns True if its usable or False if not
    """
    try:
        if table_exists(database, 'Friend') != 1:
            write_to_log("WARNING - Could not find table: friend")
            return 0, False

        #write_to_log("INFO - Found friend")

        count_usernames = row_exists_count(database, 'Friend', 'username')

        write_to_log("INFO - Found " + str(count_usernames) + " users")

        count_userIds = row_exists_count(database, 'Friend', 'userId')

        write_to_log("INFO - Found " + str(count_userIds) + " users IDs")

        if count_usernames > 0:
            return count_usernames, True
        else:
            return 0, False
    except Exception as e:
        write_to_log("ERROR - " + str(e))
        return 0, False


def check_arroyo(database):
    """
    Checks the given arroyo.db file structure
    returns True if its usable or False if not
    """
    try:
        if table_exists(database, 'conversation_message') != 1:
            write_to_log("WARNING - No such table as conversation_message")
            return 0, False
        if table_exists(database, 'conversation') != 1:
            write_to_log("WARNING - No such table as conversation")
            return 0, False

        count = row_exists_count(database, 'conversation_message', 'client_conversation_id')
        row_exists_count(database, 'conversation', 'client_conversation_id')
        return count, True
    except Exception as e:
        write_to_log("ERROR - " + str(e))
        return 0, False


def check_core(database):
    """
    Checks the given core.db file structure
    returns True if its usable or False if not
    :param database:
    :return:
    """
    try:
        if table_exists(database, 'DataConsumption') != 1:
            write_to_log("Warning - Could not find table: DataConsumption")
            return 0, False

        #write_to_log("INFO - Found DataConsumption")
        rows = row_exists_count(database, 'DataConsumption', 'contentObjectId')
        if rows == 0:
            write_to_log("Warning - Could not find row: contentObjectId")
            return 0, False

        #write_to_log("INFO - Found contentObjectId")

        if row_exists_count(database, 'DataConsumption', 'cacheKey') == 0:
            write_to_log("Warning - Could not find row: cacheKey")
            return 0, False

        #write_to_log("INFO - Found cacheKey")

        return rows, True


    except Exception as e:
        write_to_log("ERROR - " + str(e))
        return 0, False


def link_snapchatid_username(snapchatID, MainPath):
    """
    Links together a snapchatID with a username
    :param snapchatID:String
    :param MainPath:path to main.db
    :return:
    """
    try:
        conn = sqlite3.connect(MainPath)

        part = []

        # query who is participating in conv
        qr = "SELECT username FROM Friend WHERE userId == '%s'" % snapchatID

        curs1 = conn.execute(qr)

        for j in curs1:
            part.append(j[0])

        return part

    except Exception as e:
        errorstring = "ERROR - Could not find user " + str(snapchatID) + " using " + MainPath + " " + str(e)
        write_to_log(errorstring)


def link_user_convo(convID, conn, MainPath):
    """
    Links together usernames and snapchat IDs to a specific conversation
    :param convID:conversation ID
    :param conn:Connection to arroyo.db
    :param MainPath:path to main.db
    :return: List of tuples (username, snapchat ID)
    """
    try:

        part = []

        # query who is participating in conv
        qr = "SELECT * FROM user_conversation WHERE client_conversation_id == '%s'" % convID

        curs1 = conn.execute(qr)

        for j in curs1:

            # Check if username can be found
            checkU = link_snapchatid_username(j[0], MainPath)

            if checkU != False:
                id = checkU, j[0]
            else:
                id = j[0]

            part.append(id)

        return part
    except Exception as e:
        errorstring = "ERROR - Could not check participants for " + str(convID) + " using " + MainPath + " " + str(e)
        write_to_log(errorstring)

def local_ref_media(files, ):
    """
    Snapchat on android seems to store info about localy referenced media in arroyo.db->conversation_message->local_message_content_id
    content://com.snapchat.android.provider/media-session/
    ?sendSource=CAMERA&forceUpload=true&isTimeline=false&isFromMemories=false.

    """

    return

def check_keys_proto_Android(args, files, con, proto_string, timea):
    """
    Check keys with proto strings
    Contentmanager is the queryed for the string and checked if there is a hit
    Returns a list of tupels where the tupels are (key, path_to_image)
    """
    match = []

    # Connect to database
    path = os.path.abspath(con)
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        write_to_log("ERROR - Could not connect to: " + str(con))
        write_to_log(e)
        return

    # Can be more then one key
    for string in proto_string:

        # Check length of key
        if len(string) > 15:
            # Old version used KEY now its CONTENT_KEY
            try:
                # Check if KEY table can be used
                qr = "SELECT contentObjectId, cacheKey FROM DataConsumption WHERE contentObjectId LIKE '%" + string + "%'"
                curs = conn.execute(qr)

                # Loop through query
                for res in curs:
                    key = res[0]
                    cacheName = res[1]

                    # Check if query is empty
                    if string == ():
                        return False
                    # print('INFO - Found key in core: '+str(res))
                    # For all files
                    for name in files:

                        # Get only the file name
                        filename = name.split('/')[len(name.split('/')) - 1]

                        # If a filename can be found in the blob add it in a tuple to matching list
                        if cacheName in filename:
                            #print('INFO - Found link with key and file'+str(res))
                            match.append((string, name))

                        # Check if file is a key
                        if string in filename:
                            info = "RARE - Found a key that is a file: " + str(string)
                            write_to_log(info)

            except Exception as e:
                errorstring = "ERROR - Could not check key " + str(string) + " using " + qr + " " + str(e)
                write_to_log(errorstring)

    return match


def get_convo(conn, msg_id, args, timea):
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
        write_to_log("ERROR - " + str(e))
        return
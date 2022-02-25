from lib import *
from database_funcs import *
import re

def iPhone_mode(args, IO_paths, GUI_check, store_data, start_time):
    """

    :param args:
    :param IO_paths:
    :param GUI_check:
    :return:
    """
    info = "INFO - Using iPhone mode"
    write_to_log(info)

    info = """
    ===================================
    USER INPUT - For auto press enter, this will however not take WAL files into account.
    To add custom paths type (Yes).
    ===================================
    """
    write_to_log(info)
    path_mode = input()

    if path_mode == "Yes":
        info = """
        Add path for arroyo:
        """
        write_to_log(info)
        arroyo = input()
    else:
        # Extract arroyo and perform checks
        arroyo = checkandextract(args, 'arroyo.db', "file")

    # Check if file exist
    if arroyo is None:
        info = "ERROR - Could not find arroyo."
        write_to_log(info)
        return

    if path_mode == "Yes":
        info = """
        Add path for contentmanager.db:
        """
        write_to_log(info)
        contextmanager = input()
    else:
        if not GUI_check:
            contextmanager = display_contentmanagers_CLI(args.input_path, args.output_path)
            info = "INFO - Using choose contentmanager mode"
            write_to_log(info)
        else:
            info = "INFO - Using auto contentmanager mode"
            write_to_log(info)
            contextmanager, nrofcontextmanagers = get_contentmanagers_largest(args.input_path, IO_paths.report_folder)

            info = "INFO - Found " + str(nrofcontextmanagers) + " contentmanagers."
            write_to_log(info)

    if contextmanager is None:
        info = "ERROR - Could not find contentmanager."
        write_to_log(info)
        return

    info = "INFO - Using " + str(contextmanager) + "."
    write_to_log(info)

    if path_mode == "Yes":
        info = """
        Add path for primary.docobjects:
        """
        write_to_log(info)
        PDpath = input()
    else:
        PDpath = checkandextract(args, 'primary.docobjects', "file")
        if PDpath is None:
            info = "ERROR - Could not find PDpath."
            write_to_log(info)

    if path_mode == "Yes":
        info = """
        Add path for cache_controller.db:
        """
        write_to_log(info)
        cachecontrollerPath = input()
    else:
        cachecontrollerPath = checkandextract(args, 'cache_controller.db', "file")
        if cachecontrollerPath is None:
            info = "ERROR - Could not find cachecontrller."
            write_to_log(info)

    files = ""

    if args.check_attachmets == "Y":
        # Make a list of files in com.snap.file_manager_
        files = checkinzip(args, '', "path")
        info = "INFO - Checking for attachments"
        write_to_log(info)
    else:
        info = "INFO - NOT checking for attachments"
        write_to_log(info)


    # Check important files
    try:
        conn_arroyo = sqlite3.connect(arroyo)

        # Check if arroyo is usable
        info = "INFO - Checking " + str(arroyo)
        write_to_log(info)
        messages_count, Carroyo = check_arroyo(arroyo)

        if Carroyo:

            info = """
            ===================================
            SUCCESS - arroyo passed all checks!
            ===================================
            """
            write_to_log(info)
        else:
            info = """
            ===================================
            WARNING - arroyo did not pass checks
            ===================================
            """
            write_to_log(info)

            info = "INFO - Exiting"
            write_to_log(info)

            return

        # Check if primary.docobjects is usable
        info = "INFO - Checking Primary.docobjects\n"
        write_to_log(info)

        PDpath = os.path.abspath(PDpath)

        info = "INFO - Path: " + str(PDpath)
        write_to_log(info)
        count_usersnames, count_usernames_raw, Cprimary = check_primarydocobjects(PDpath)

        if Cprimary:
            info = """
            ===================================
            SUCCESS - primarydocobjects passed all checks!
            ===================================
            """
            partCheck = True
            write_to_log(info)
        else:
            info = """
            ===================================
            WARNING - primarydocobjects did not pass checks
            ===================================
            """
            partCheck = False
            write_to_log(info)

        # Check if cachecontroller is usable
        info = "INFO - Checking cache_controller.db\n"
        write_to_log(info)

        info = "INFO - Path: " + str(cachecontrollerPath)
        write_to_log(info)
        Ccache = check_cachecontroller(cachecontrollerPath)

        if Ccache:
            info = """
            ===================================
            SUCCESS - cache_controller.db passed all checks!
            ===================================
            """
            write_to_log(info)
        else:
            info = """
            ===================================
            WARNING - cache_controller.db did not pass checks
            ===================================
            """
            write_to_log(info)

        # Check if contentmanager is usable
        info = "INFO - Checking " + str(contextmanager)
        write_to_log(info)
        count, Ccontentmanager, = check_contentmanager(
            os.path.abspath(IO_paths.report_folder + "/" + contextmanager))

        if Ccontentmanager:
            info = """
            ===================================
            SUCCESS - contentmanager passed all checks!
            ===================================
            """
            content_check = True
            write_to_log(info)
        else:
            info = """
            ===================================
            WARNING - contentmanager did not pass checks
            ===================================
            """
            write_to_log(info)
            content_check = False

    except Exception as e:
        error = "ERROR - Checks Failed, one or more database is unusable" + str(
            traceback.format_exc() + "\n" + e.__doc__)
        write_to_log(error)
        return "ERROR"


    convons = getConv(conn_arroyo, args.msg_id, args, IO_paths.report_time)

    if args.msg_id is not None:
        info = "INFO - Filtering for " + args.msg_id
        write_to_log(info)

    info = "INFO - Found conversations " + str(convons)
    write_to_log(info)

    if len(convons) > 0:
        cache_matches = parse_cache_controller(store_data, cachecontrollerPath, files, convons)

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
        check = True

        # Go through database query
        for i in curs:
            nr = nr + 1
            print("\rParsed " + str(nr) + " out of " + str(messages_count) + " messages", flush=True, end='')

            # info = "INFO - Parsing"+str(i)
            # write_to_log(info)

            # Write participants only once
            if check:
                part = ""
                # Get participants of a conversation
                if Cprimary:
                    part = get_participants(conv_id, conn_arroyo, PDpath)
                    if part != None:
                        for username, snapchat_id in part:
                            # Add to database for storage
                            insert_participants(store_data, conv_id, username, snapchat_id, args,
                                                IO_paths.report_time)

                check = False

            raw_timestamp = i[7]

            # Check if time filter is applied
            res = check_time(raw_timestamp, args)

            # Content type
            ctype = i[13]
            ctype_string = check_content_type(i[13])

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
            Message_encoded = ParseProto(i[5])
            proto_string = proto_to_msg(i[5])
            string_list = decode_string(proto_string, i[5])

            # Check time flag
            if res:

                attachment_check = False

                # Check if primary.docobjects can be used
                if partCheck:
                    # Check if username can be found
                    checkU = get_primarydocobjects(i[16], PDpath)

                    # If no username can be linked
                    if checkU != False:
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
                    # Check if cachecontroller passed checks
                    if Ccache:

                        # Check flags
                        if args.check_attachmets == "Y":
                            for filepath, conversation_id_cached, conversation_serverid_cached in cache_matches:
                                # print(conv_id, conversation_id_cached, server_message_id, conversation_serverid_cached)
                                # Check if conversation id matches
                                if conv_id == conversation_id_cached and str(server_message_id) == str(
                                        conversation_serverid_cached):
                                    attachment_id = attachment_id + 1
                                    effromzip(filepath)
                                    file_type = compare_magic_bytes(
                                        os.path.abspath(IO_paths.report_folder + "/" + filepath))
                                    insert_attachment(store_data,
                                                      attachment_id,
                                                      filepath,
                                                      conversation_serverid_cached,
                                                      file_type,
                                                      args,
                                                      IO_paths.report_time)

                                    attachment_check = True

                            # If no attachment was found with cache check old method
                            if not attachment_check:

                                # If content manager passed checks
                                if content_check:
                                    attachments = get_attachment(args,
                                                                 files,
                                                                 contextmanager,
                                                                 proto_string,
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
    if partCheck:
        if part != None:
            owner = get_owner(store_data)
        else:
            owner = None
    else:
        owner = None

    print()
    info = "INFO - Parsing complete, found %s attachments" % attachment_id
    write_to_log(info)

    execute_time = (time.time() - start_time)
    info = str(execute_time) + " (s)"
    write_to_log(info)

    return [convons, execute_time, store_data, owner, partCheck]


def parse_cache_controller(storedata, database, files, conversation_ids):
    """
    Check keys with proto strings
    Contentmanager is the queryed for the string and checked if there is a hit
    Returns a list of tupels where the tupels are (key, path_to_image)
    """

    info = "INFO - Parsing cachecontroller"
    write_to_log(info)

    match = []

    for filepath in files:
        filepath_list = filepath.split("/")
        only_filename = filepath_list[len(filepath_list) - 1]

        conn = sqlite3.connect(database)

        qr = "SELECT EXTERNAL_KEY FROM CACHE_FILE_CLAIM WHERE CACHE_KEY == '%s'" % only_filename

        curs = conn.execute(qr)

        for i in curs:
            for ids in conversation_ids:
                if ids in i[0]:
                    res = i[0].split(":")
                    conversation_id_cached = res[1]
                    conversation_serverid_cached = res[2]

                    match.append((filepath, conversation_id_cached, conversation_serverid_cached))
                    insert_cached_files(storedata, filepath, conversation_id_cached, conversation_serverid_cached)

    return match


def check_cachecontroller(database):
    """
    Checks the given cachecontroller file structure
    returns True if its usable or False if not
    """
    try:
        # write_to_log("INFO - Found snapchatter")
        if table_exists(database, 'CACHE_FILE_CLAIM') != 1:
            write_to_log("WARNING - No such table as CACHE_FILE_CLAIM")
            return False

        # write_to_log("INFO - Found index_snapchatterusername")

        if row_exists_count(database, 'CACHE_FILE_CLAIM', 'EXTERNAL_KEY') == 0:
            write_to_log("INFO - No such row as EXTERNAL_KEY or no data")
            return False

        if row_exists_count(database, 'CACHE_FILE_CLAIM', 'CACHE_KEY') == 0:
            write_to_log("INFO - No such row as CACHE_KEY or no data")

        return True
    except Exception as e:
        write_to_log("ERROR - " + str(e))
        return False


def check_primarydocobjects(database):
    """
    Checks the given check_primary.docobjects file structure
    returns True if its usable or False if not
    """
    try:
        if table_exists(database, 'snapchatter') != 1:
            write_to_log("WARNING - No such table as snapchatter")
            return 0, 0, False

        #write_to_log("INFO - Found snapchatter")
        if table_exists(database, 'index_snapchatterusername') != 1:
            write_to_log("WARNING - No such table as index_snapchatterusername")
            return 0, 0, False

        #write_to_log("INFO - Found index_snapchatterusername")

        count_usersnames = row_exists_count(database, 'snapchatter', 'userId')
        write_to_log("INFO - Found " + str(count_usersnames) + " users")

        count_usernames_raw = row_exists_count(database, 'index_snapchatterusername', 'username')

        write_to_log("INFO - Found " + str(count_usernames_raw) + " raw users")
        return count_usersnames, count_usernames_raw, True
    except Exception as e:
        write_to_log("ERROR - "+str(e))
        return 0, 0, False


def check_arroyo(database):
    """
    Checks the given arroyo.db file structure
    returns True if its usable or False if not
    """
    try:
        if table_exists(database, 'conversation_message') != 1:
            write_to_log("WARNING - no such table as conversation_message in arroyo")
            return 0, False
        if table_exists(database, 'conversation') != 1:
            write_to_log("WARNING - no such table as conversation in arroyo")
            return 0, False

        count = row_exists_count(database, 'conversation_message', 'client_conversation_id')
        row_exists_count(database, 'conversation', 'client_conversation_id')
        return count, True
    except Exception as e:
        write_to_log("ERROR - Exception occured "+str(e))
        return 0, False


def check_contentmanager(database):
    """
    Checks the given contentmanagers structure
    returns True if its usable or False if not
    """

    try:
        table_exists(database, 'CONTENT_OBJECT_TABLE')
        key = get_contentmangaredb_key(database)
        count = row_exists_count(database, 'CONTENT_OBJECT_TABLE', key)
        return count, True
    except Exception as e:
        write_to_log("ERROR - " + str(e))
        return 0, False


def get_participants(convID, conn, PDpath):
    """
    test
    :param convID:Conversation id
    :param conn:sqlite3 connection to the primary.docobjects
    :param PDpath:Full path to where the primary.docobjects is stored
    :return:List of tuples (username, snapchat ID)
    """
    try:
        part = []

        # query who is participating in conv
        qr = "SELECT * FROM user_conversation WHERE client_conversation_id == '%s'" % convID

        curs1 = conn.execute(qr)

        for j in curs1:

            # Check if username can be found
            checkU = get_primarydocobjects(j[0], PDpath)

            if checkU != False:
                id = checkU, j[0]
            else:
                id = j[0]

            part.append(id)

        return part
    except Exception as e:
        errorstring = "ERROR - Could not check participants for " + str(
            convID) + " using " + PDpath + " " + str(e)
        write_to_log(errorstring)


def get_attachment(args, files, con, proto_string, timea):
    """
    Check keys with proto strings
    Contentmanager is the queryed for the string and checked if there is a hit
    Returns a list of tupels where the tupels are (key, path_to_image)
    """

    match = []

    # Connect to database
    path = os.path.abspath(IO_paths.report_folder + "/" + con)
    try:
        conn = sqlite3.connect(path)
    except Exception as e:
        write_to_log("ERROR - Could not connect to: " + str(IO_paths.report_folder + "/" + str(con)))
        write_to_log(e)
        return

    # Get the key row from CONTENT_OBJECT_TABLE
    key = get_contentmangaredb_key(path)

    # Check output
    if key == None:
        errorstring = "ERROR - Could not find key row in contentmanager. Check the database for changes."
        write_to_log(errorstring)
        return

    # Can be more then one key
    for string in proto_string:

        # Check length of key
        if len(string) > 15 and len(string) < 22:
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
                            print('SUCCESS - Found link with key and file\n')
                            match.append((string, iii))

                        # Check if file is a key
                        if string in filename:
                            info = "RARE - Found a key that is a file: " + str(string)
                            write_to_log(info)

            except Exception as e:
                errorstring = "ERROR - Could not check key " + str(string) + " using " + qr + " " + str(e)
                write_to_log(errorstring)

    return match


def get_primarydocobjects(pd, path):
    """
    Checks primary.docobjects for a hits on a id and returns the username
    :param pd:
    :param path:
    :return:
    """
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


def get_username_blob(userid, pdpath):
    """
    TODO
    Check blobs for usernames in primary.docobjects
    :param userid:
    :param pdpath:
    :return:
    """
    check = get_primarydocobjects(userid, pdpath)
    if check != "":
        return check
    else:
        pass


def get_contentmangaredb_key(database):
    """
    Checks the contentmanager.db structure
    returns what kind of key is being used
    return None if no key was found
    """

    sqlmaster = get_database_struct(database)

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


def get_convos(conn, msg_id, args, timea):
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
        error = """
        =========================
        ERROR - iPhone_funcs.py -> get_convos
        %s
        =========================
        """ % e
        write_to_log(error)
        return


def display_contentmanagers_GUI(input_path):
    """
    Used for GUI mode
    Displays contentmanagers and returns a content manager based on user input
    """
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


def display_contentmanagers_CLI(input_path, ouput_path):
    """
    Used for CLI mode
    Displays contentmanagers and returns a content manager based on user input
    """
    managers = []

    # Display contentmanagers
    print("Available content managers:")

    with ZipFile(input_path, "r") as f:
        y = 0
        for i in f.infolist():

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
            display_contentmanagers_CLI(input_path, ouput_path)

        f.extract(managers[int(ret) - 1], IO_paths.report_folder)
        f.close()

        return managers[int(ret) - 1]


def get_contentmanagers_largest(input_path, output_path):
    """
    Check zip file for contetntmanagers and return the path of the largest one
    returns None if no manager was found
    """

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

            a = i.filename.split('/')

            if a[len(a) - 1] == 'contentManagerDb.db':
                y = y + 1
                managers.append((i.filename, i.file_size / (1024 * 1024)))

        # Check the size of content managers
        manager = largets(managers)

        if manager != "":
            f.extract(manager[0], output_path)
            f.close()

            # return the manager that is gonna be used and the amount of content managers found
            return manager[0], y

        return None

def get_userinfo(preferences, scdb27):
    """
    Connects to preferences.sqlite, scdb-27.sqlite3 and extracts user info
    :return:
    """
    def get_pref(preferences):
        """
        Documents\global_scoped\global-scoped-preferences\preferences.sqlite
        :return:
        """
        table = "docprefitem"
        row = "key"
        key_mobilnumber = "SCLastLoginUserSCPhoneNumberKey"
        key_username = "SCLastLoginUsernameKey"

        qr = "SELECT p FROM " + table + " WHERE key LIKE SCLastLoginUser"




    def get_scdb27(scdb27):
        """
        Documents\gallery_data_object\1\2319908e320f8dbb48997331ce1718444e95af57d707691058bfe6491435bd77\scdb-27.sqlite3
        :return:
        """
        table = "ZGALLERYPROFILE"
        row = "ZUSERID"
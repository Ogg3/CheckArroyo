"""
github.com/Ogg3/CheckArroyo
"""
import argparse
import webbrowser
from iPhone_funcs import *
from android_funcs import *
import sqlite3

__version__ = "0-6-9"

def main():
    parser = argparse.ArgumentParser(description='CheckArroyo: Snapchat chat parser.')

    # Point to where snapchat dmp is
    parser.add_argument('-i', '--input_path', required=False, action="store", help='Path to snapchat dump zipfile.')
    parser.add_argument('-o', '--output_path', required=False, action="store", help='Output folder path.')
    parser.add_argument('-m', '--mode', required=False, action="store",
                        help='Select mode, IOS - iPhone, AND - Android, ARY - only arroyo')
    parser.add_argument('-c', '--check_attachmets', required=False, action="store",
                        help='Select if attachments should be checked; Y (Yes) or N (No)')
    #parser.add_argument('-e', '--expert_mode', required=False, action="store_true",
                        #help='The HTML report will now contain more unfiltered data')
    parser.add_argument('-t1', '--time_start', required=False, action="store", help='Time range start. Ex: 2021-01-01')
    parser.add_argument('-t2', '--time_stop', required=False, action="store", help='Time range stop. Ex: 2021-01-01')
    parser.add_argument('-msg', '--msg_id', required=False, action="store",
                        help='Make report for only one conversation id')

    args = parser.parse_args()

    input_path = args.input_path
    #global verbose
    #verbose = args.verbose

    # iPhone mode
    if args.mode == "IOS":
        # Check so paths exists
        if args.output_path is None:
            parser.error('No OUTPUT folder path provided')
            return
        else:
            output_path = os.path.abspath(args.output_path)

            if output_path[1] == ':': output_path = '\\\\?\\' + output_path.replace('/', '\\')

        if output_path is None:
            parser.error('No OUTPUT folder selected. Run the program again.')
            return
        if input_path is None:
            parser.error('No INPUT file. Run the program again.')
            return
        else:
            input_path = os.path.abspath(args.input_path)

            if input_path[1] == ':': input_path = '\\\\?\\' + input_path.replace('/', '\\')

        if not os.path.exists(input_path):
            parser.error('INPUT file does not exist! Run the program again.')
            return
        if not os.path.exists(output_path):
            parser.error('OUTPUT folder does not exist! Run the program again.')
            return

        # Write html report while finding content
        try:
            writeHtmlReport(args)
        except Exception as e:
            error = "ERROR - " + str(
                traceback.format_exc() + "\n" + e.__doc__)
            write_to_log(error)

    # Android mode
    elif args.mode == "AND":
        # Check so paths exists
        if args.output_path is None:
            parser.error('No OUTPUT folder path provided')
            return
        else:
            output_path = os.path.abspath(args.output_path)

            if output_path[1] == ':': output_path = '\\\\?\\' + output_path.replace('/', '\\')

        if output_path is None:
            parser.error('No OUTPUT folder selected. Run the program again.')
            return
        if input_path is None:
            parser.error('No INPUT file. Run the program again.')
            return
        else:
            input_path = os.path.abspath(args.input_path)

            if input_path[1] == ':': input_path = '\\\\?\\' + input_path.replace('/', '\\')

        if not os.path.exists(input_path):
            parser.error('INPUT file does not exist! Run the program again.')
            return
        if not os.path.exists(output_path):
            parser.error('OUTPUT folder does not exist! Run the program again.')
            return

        # Write html report while finding content
        try:
            writeHtmlReport(args)
        except Exception as e:
            error = "ERROR - " + str(
                traceback.format_exc() + "\n" + e.__doc__)
            write_to_log(error)

    # If only arroyo database if available
    elif args.mode == "ARY":

        # Check so file exists
        if args.output_path is None:
            parser.error('No OUTPUT folder path provided')
            return
        else:
            output_path = os.path.abspath(args.output_path)
        if output_path is None:
            parser.error('No OUTPUT folder selected. Run the program again.')
            return
        if input_path is None:
            parser.error('No INPUT file. Run the program again.')
            return
        else:
            input_path = os.path.abspath(args.input_path)
        if not os.path.exists(input_path):
            parser.error('INPUT file does not exist! Run the program again.')
            return
        if not os.path.exists(output_path):
            parser.error('OUTPUT folder does not exist! Run the program again.')
            return

        # Write html report while finding content
        try:
            writeHtmlReport(args)
        except Exception as e:
            error = "ERROR - " + str(
                traceback.format_exc() + "\n" + e.__doc__)
            write_to_log(error)

    # If no mode selected
    else:
        parser.error('No mode selected.')



def pars_data(args, IO_paths, GUI_check):
    """
    0-speed,
    1-mode,
    2-debug,
    3-time_start,
    4-time_stop,
    5-contentmanager,
    6-msg_id
    """

    # Connect to database
    store_data = args.output_path + "\\" + "CheckArroyo-report-" + IO_paths.report_time + "\\" + "store_data.db"

    # Create database to store data
    create_store_data(store_data)

    # Start execute timer
    start_time = time.time()


    def arroyo_mode(args, IO_paths, GUI_check, store_data):
        """

        :param args:
        :param IO_paths:
        :param GUI_check:
        :return:
        """
        info = "INFO - Using arroyo.db mode"
        write_to_log(info)
        arroyo = args.input_path

        # Check important files
        try:
            conn_arroyo = sqlite3.connect(arroyo)

            # Check if arroyo is usable
            #if verbose:
            info = "INFO - Checking " + str(arroyo)
            write_to_log(info)
            messages_count, Carroyo = check_arroyo(arroyo)

            if Carroyo:
                info = "INFO - Check complete\n"
                write_to_log(info)
            else:
                info = "WARNING - arroyo did not pass checks\n"
                write_to_log(info)

                info = "INFO - Exiting"
                write_to_log(info)

                return
        except Exception as e:
            error = "ERROR - Checks Failed, one or more database is unusable" + str(
                traceback.format_exc() + "\n" + e.__doc__)
            write_to_log(error)
            return "ERROR"

        convons = getConv(conn_arroyo, args.msg_id, args, IO_paths.report_time)

        if args.msg_id is not None:
            info = "INFO - Filtering for " + args.msg_id
            write_to_log(info)

        info = "INFO - "+ str(convons) +"Found conversations"
        write_to_log(info)

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
                print("\rParsed " + str(nr) + " out of " + str(messages_count) + " messages\n", flush=True, end='')

                raw_timestamp = i[7]

                # Check if time filter is applied
                res = check_time(raw_timestamp, args)

                # Content type
                ctype = i[13]
                ctype_string = check_content_type(i[13])

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
                Message_encoded = ParseProto(i[5])

                # Check for content type and decode
                proto_string = proto_to_msg(i[5])
                string_list = decode_string(proto_string, i[5])

                # Check time flag
                if res:

                    sent_by_snapchat_id = i[16]
                    # if a text message was found
                    insert_message(store_data,
                                   conv_id,
                                   sent_by_snapchat_id,
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

        print()
        info = "INFO - Parsing complete"
        write_to_log(info)

        execute_time = (time.time() - start_time)
        info = str(execute_time) + " (s)"
        write_to_log(info)

        return [convons, execute_time, store_data, get_owner(arroyo), None]

    # Iphone mode
    if args.mode == "IOS":
        return iPhone_mode(args, IO_paths, GUI_check, store_data, start_time)

    # Android mode
    elif args.mode == "AND":
        return android_mode(args, IO_paths, GUI_check, store_data, start_time)

    # Only arroyo mode
    elif args.mode == "ARY":
        return arroyo_mode(args, IO_paths, GUI_check, store_data)


# Write report on findings
def writeHtmlReport(args):

    # Check if user is using gui
    GUI_check = False
    user_mode = ""
    # Check if CLI or GUI
    try:
        a = args[0]
        GUI_check = True
        args = GUI_args(args[0], args[1], args[2], args[3], args[4], args[5], args[6])
        info = "INFO - Using GUI"
    except:
        info = "INFO - Using CLI"

    output = IO_paths(args)

    write_to_log("INFO - Version " + str(__version__))

    write_to_log(info)

    # Pars data and store in database
    data = pars_data(args, output, GUI_check)
    if data != "ERROR":
        parsde_data = data[0]
        execute_time = data[1]
        database = data[2]
        owner = data[3]
        part = data[4]
    else:
        return None

    # Export contacts
    export_users(database)

    # Connect to stored data
    conn = sqlite3.connect(database)

    info = "INFO - Writing html reports"
    write_to_log(info)

    convos = 0

    # For every conversation
    for x in parsde_data:
        convos += 1

        print("\rINFO - writing conversation: " + str(convos) + " out of " + str(len(parsde_data)), flush=True, end='')

        msg = 0
        Attatchments = 0

        #info = 'INFO - writing conversation: ' + x
        #write_to_log(info)

        # Write html report
        with open(IO_paths.report_convos + x + "-HTML-Report.html", "w") as f:


            # Select all messages from a certain conversation
            qr = "SELECT * FROM 'messages' WHERE Conversation_id LIKE '%s' ORDER BY Timestamp_sent ASC" % x
            curs = conn.execute(qr)

            f.write(html_start())
            check = True
            for i in curs:

                # Set database vars
                conversation_id = i[0]

                # Check if username is owner
                if part:
                    if i[1] == owner:
                        sent_by_username = i[1]
                    else:
                        sent_by_username = i[1]
                else:
                    sent_by_username = i[1]
                sent_by_snapchat_id = i[2]
                content_type = i[3]
                message_decoded = i[4]
                message_og_id = i[5]
                Server_og_id = i[6]
                attachments_ids = i[7]
                timestamp_sent_raw = i[8]
                timestamp_recived_raw = i[9]


                if check:
                    parties = get_participants(database, conversation_id)
                    for username, snapchat_id in parties:
                        f.write(html_participants(username, snapchat_id))
                    check = False

                timestamp_sent, timestamp_recived = get_timestamp(database, message_og_id, timestamp_sent_raw)

                if i[1] == owner:
                    f.write(html_right_start([sent_by_snapchat_id, message_og_id, Server_og_id, message_decoded]))
                    timestamp_recived_modified = ""
                else:

                    if timestamp_recived == "1970-01-01 01:00:00.0":
                        timestamp_recived_modified = "NOT READ"
                    else:
                        timestamp_recived_modified = "Read: "+timestamp_recived+" localtime"

                    f.write(html_left_start([sent_by_snapchat_id, message_og_id, Server_og_id, message_decoded]))

                msg = msg + 1


                # Check if messages has an attachment
                if content_type != "Text message" and attachments_ids != -1:
                    attachments = get_attachments(database, attachments_ids)

                    # Check flags
                    if args.check_attachmets == "Y" and (args.mode == "AND" or args.mode == "IOS"):

                        # Check if attachments link was found
                        if attachments:
                            Attatchments = Attatchments + 1

                            # Write attachments and key to html report and link to the extracted file
                            for image, file_type in attachments:

                                if file_type == "PIC":
                                    f.write(html_pic(image))

                                elif file_type == "MOV":
                                    f.write(html_video(image))

                                elif file_type == "CONTROL FILE":
                                    pass
                                    # TODO

                                elif file_type == "COMPRESSED":
                                    pass
                                    # TODO

                                else:
                                    f.write(html_unknown())
                                    f.write(html_video(image))
                                    f.write(html_pic(image))

                # Is a text message
                elif content_type == "Text message":
                    f.write(html_text(message_decoded))

                if i[1] == owner:
                    f.write(html_right_end(sent_by_username, content_type, timestamp_sent))
                else:
                    f.write(html_left_end(sent_by_username, content_type, timestamp_sent, timestamp_recived_modified))

            f.write(html_end())

        with open(IO_paths.report_file, "a") as a:

            link = "./conversation-reports" + "\\" + x + "-HTML-Report.html"
            name = x + "-HTML-Report.html"
            home = """
            <div style="border: 1px solid black;">
                <div id="stats"> 
                    <table class="column-stats" >
                        <tr>
                            <th> <a href="%s"> %s </a></th>
                        </tr>
                    </table>
    
                </div>
                    """ % (link, name)
            a.write(home)

            Table_Header1 = """
                <div id="stats"> 
                    <table class="column-stats" >
                        <tr>
                            <th class="color1"><b>Participants</b></th>
                        </tr>
                """
            a.write(Table_Header1)

            if part:

                # Get participants of a chat from database
                for username, snapchat_id in parties:
                    if username == owner:
                        username = username+" (OWNER)"
                    data = """
                            <tr>
                                <td>%s, %s</th>
                            </tr>
                    """ % (username, snapchat_id)

                    a.write(data)

            # ENd of Participants
            Table_ender1 = """
                    
                    </table>
                </div>
            """
            a.write(Table_ender1)

            Stats = """
                    <div id="stats"> 
                        <table class="column-stats" >
                            <tr>
                                <th><b> Stats </b> </th>
                            </tr>
                            <tr>
                                <td>Messages decoded: %s</td>
                            </tr>
                            <tr>
                                <td>Attachments found: %s</td>
                            </tr>
                            <tr>
                                <td> Latest activity: %s </td>
                            </tr>
                        </table>
    
                    </div>
            </div>
                            """ % (msg, Attatchments, timestamp_sent)
            a.write(Stats)

    info = "INFO - Done"
    write_to_log(info)
    webbrowser.open(IO_paths.report_file)

    return IO_paths.report_file

# So weird
if __name__ == '__main__':
    main()

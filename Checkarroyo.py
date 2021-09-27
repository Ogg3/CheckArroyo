"""
github.com/Ogg3/CheckArroyo
"""
import argparse
import time

from lib import *


# Main
def main():
    parser = argparse.ArgumentParser(description='CheckArroyo: Snapchat chat parser.')

    # Point to where snapchat dmp is
    parser.add_argument('-i', '--input_path', required=False, action="store", help='Path to snapchat dump zipfile.')
    parser.add_argument('-o', '--output_path', required=False, action="store", help='Output folder path.')
    parser.add_argument('-m', '--mode', required=False, action="store",
                        help='Select mode, IOS - iPhone, AND - Android, ARY - only arroyo')
    parser.add_argument('-s', '--speed', required=False, action="store",
                        help='Select speed, F - fast, M - medium, S - slow')
    parser.add_argument('-t1', '--time_start', required=False, action="store", help='Time range start. Ex: 2021-01-01')
    parser.add_argument('-t2', '--time_stop', required=False, action="store", help='Time range stop. Ex: 2021-01-01')
    parser.add_argument('-msg', '--msg_id', required=False, action="store",
                        help='Make report for only one conversation id')
    parser.add_argument('-d', '--debug_mode', required=False, action="store_true", help='For my sanity')

    args = parser.parse_args()

    input_path = args.input_path

    # iPhone mode
    if args.mode == "IOS":
        # Check so paths exists
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
        writeHtmlReport(args)

    # Android mode
    elif args.mode == "AND":
        pass

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
        writeHtmlReport(args)

    # If no mode selected
    else:
        parser.error('No mode selected.')


"""
0-speed, 
1-mode, 
2-debug, 
3-time_start, 
4-time_stop, 
5-contentmanager, 
6-msg_id
"""

# Store data in database
def pars_data(args, timea, GUI_check):

    # Connect to database
    database = args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "store_data.db"

    # Create database to store data
    create_store_data(database)

    # Start execute timer
    start_time = time.time()

    # Iphone mode
    if args.mode == "IOS":
        info = "INFO - Using IOS mode"
        print(info)
        write_to_log(args, timea, info)

        # Extract arroyo and perform checks
        arroyo = checkandextract(args, 'arroyo.db', "file")

        # Check if file exist
        if arroyo is None:
            info = "ERROR - Could not find arroyo."
            print(info)
            write_to_log(args, timea, info)
            return

        if not GUI_check:
            contextmanager = displayIOScontentmanagers(args.input_path, args.output_path)
            info = "INFO - Using choose contentmanager mode"
            print(info)
            write_to_log(args, timea, info)
        else:
            info = "INFO - Using auto contentmanager mode"
            print(info)
            write_to_log(args, timea, info)
            contextmanager, nrofcontextmanagers = check_contentmanagers(args.input_path, args.output_path)

            info = "INFO - Found " + str(nrofcontextmanagers) + " contentmanagers."
            print(info)
            write_to_log(args, timea, info)

        if contextmanager is None:
            info = "ERROR - Could not find contentmanager."
            print(info)
            write_to_log(args, timea, info)
            return

        info = "INFO - Using " + str(contextmanager) + "."
        print(info)
        write_to_log(args, timea, info)

        PDpath = checkandextract(args, 'primary.docobjects', "file")
        if PDpath is None:
            info = "ERROR - Could not find PDpath."
            print(info)
            write_to_log(args, timea, info)
            return

        info = "INFO - Using " + PDpath + " as primary.docobjects"
        print(info)
        write_to_log(args, timea, info)

        files = ""

        if args.speed == "S":
            # Make a list of files in com.snap.file_manager_
            files = checkinzip(args, 'com.snap.file_manager_', "path")
            info = "INFO - Checking for attachments"
            print(info)
            write_to_log(args, timea, info)
        else:
            info = "INFO - NOT checking for attachments"
            print(info)
            write_to_log(args, timea, info)

    # Android mode
    elif args.mode == "AND":
        pass

    # Only arroyo mode
    elif args.mode == "ARY":
        info = "INFO - User is using arroyo.db mode"
        print(info)
        write_to_log(args, timea, info)
        arroyo = args.input_path

    info = "INFO - Connecting to " + arroyo
    print(info)
    write_to_log(args, timea, info)

    conn_arroyo = sqlite3.connect(arroyo)

    convons = getConv(conn_arroyo, args.msg_id)

    if args.msg_id is not None:
        info = "INFO - Filtering for " + args.msg_id
        print(info)
        write_to_log(args, timea, info)

    info = "INFO - Found conversations " + str(convons)
    print(info)
    write_to_log(args, timea, info)

    # Set var
    attachment_id = 0
    nr=0

    info = "INFO - Parsing messages"
    print(info)
    write_to_log(args, timea, info)

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
            print("\rParsed "+str(nr)+" messages...", flush=True, end='')

            # Write participants only once
            if check and args.mode != "ARY":
                # Get participants of a conversation
                for username, snapchat_id in check_participants(conv_id, conn_arroyo, PDpath):
                    # Add to database for storage
                    insert_participants(database, conv_id, username, snapchat_id)
                check = False

            raw_timestamp = i[7]

            # Check if time filter is applied
            res = check_time(raw_timestamp, args)

            # Content type
            ctype = i[13]
            ctype_string = check_ctype(i[13])

            # Check for content type and decode
            proto_string = proto_to_msg(i[5])
            string_list = decode_string(proto_string, i[5])

            # Check time flag
            if res:

                # Check mode
                if args.mode == "ARY":
                    sent_by_snapchat_id = i[16]
                    # if a text message was found
                    if ctype == 1:
                        insert_message(database, conv_id, sent_by_snapchat_id, sent_by_snapchat_id, ctype_string,
                                       string_list[0], i[1], -1, i[7], i[8])
                    else:
                        insert_message(database, conv_id, sent_by_snapchat_id, sent_by_snapchat_id, ctype_string,
                                       string_list, i[1], -1, i[7], i[8])
                else:
                    # Check if username can be found
                    checkU = checkPD(i[16], PDpath)
                    check_id_username(i[16], PDpath)

                    # If no username can be linked
                    if checkU != False:
                        sent_by_username = checkU
                        sent_by_snapchat_id = i[16]
                    else:
                        sent_by_username = ""
                        sent_by_snapchat_id = i[16]

                    # if a text message was found
                    if ctype == 1:
                        insert_message(database, conv_id, sent_by_username, sent_by_snapchat_id, ctype_string, string_list[0], i[1], -1, i[7], i[8])
                    else:
                        attachments = check_keys_proto(args, files, contextmanager, proto_string)

                        # Check flags
                        if args.speed == "S" and (args.mode == "AND" or args.mode == "IOS"):

                            # Check if attachments link was found
                            if attachments:

                                # Increase id
                                attachment_id = attachment_id + 1

                                # Add to database
                                insert_message(database, conv_id, sent_by_username, sent_by_snapchat_id, ctype_string, string_list, i[1], attachment_id,
                                               i[7], i[8])

                                # Write attachments and key to html report and link to the extracted file
                                # TODO check magic bytes for file type
                                for key, image in attachments:
                                    effromzip(image, args)
                                    insert_attachment(database, attachment_id, image, key)
                            else:

                                # Add to database
                                insert_message(database, conv_id, sent_by_username, sent_by_snapchat_id, ctype_string, string_list, i[1], -1,
                                               i[7], i[8])

    owner = get_owner(database)

    print()
    info = "INFO - Parsing complete"
    print(info)
    write_to_log(args, timea, info)

    execute_time = (time.time() - start_time)
    info = str(execute_time)+" (s)"
    print(info)
    write_to_log(args, timea, info)

    return convons, execute_time, database, owner


# Write report on findings
def writeHtmlReport(args):

    # Check if user is using gui
    GUI_check = False
    # Check if CLI or GUI
    try:
        a = args[0]
        GUI_check = True
        args = GUI_args(args[0], args[1], args[2], args[3], args[4], args[5], args[6])
        print("INFO - Using GUI")
    except Exception as e:
        print("INFO - Using CLI")
        pass

    # Create timestamp for when report was created
    timea = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    # Make base directory
    os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + timea)

    # Make conversation directory
    os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "conversation-reports")

    # Create report file
    with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "Report.html", "w") as a:
        a.write("<script></script>")

    # Create log file
    with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "log.txt", "w") as a:
        a.write("")

    # Create log file
    with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "log.txt", "w") as a:
        a.write("")

    # Pars data and store in database
    parsde_data, execute_time, database, owner = pars_data(args, timea, GUI_check)

    # Export contacts
    export_users(args, timea, database)

    # Connect to stored data
    conn = sqlite3.connect(database)

    info = "INFO - Writing html reports"
    print(info)
    write_to_log(args, timea, info)

    # For every conversation
    for x in parsde_data:
        msg = 0
        Attatchments = 0

        info = 'INFO - writing conversation: ' + x
        print(info)
        write_to_log(args, timea, info)

        # Write html report
        with open(
                args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "conversation-reports" + "\\" + x + "-HTML-Report.html",
                "w") as f:

            JavascriptFunc = """
            <script>
            function hide(div){
                var x = document.getElementById(div);
                if(x.style.display === "none"){
                    x.style.display = "block";
                }
                else{
                    x.style.display = "none";
                }
            }
            </script>

            <style>

                .column {
                    float: left;
                    width: 75%;
                }
                table, tbody, tr,th, td{
                    border: 1px solid black;
                    word-wrap: break-word;
                    overflow-warp: break-word;
                    max-width: 1080px;

                }
                table{
                    float: center;

                }

                .color1{
                    background: #e0e0e0;
                }

                .color2{
                    background: #d4d4d4;    
                }

                .column-stats {
                    float: left;
                    width: 50%; 
                }


                /*sticky navbar */
                #navbar {
                  overflow: hidden;
                  background-color: #333;
                }

                #navbar a {
                  float: left;
                  display: block;
                  color: #000000;
                  text-align: center;
                  text-decoration: none;
                  font-size: 17px;
                }

                .sticky {
                  position: fixed;
                  top: 0;
                  width: 100%;
                }

                .sticky + .content {
                  padding-top: 40px;
                }



                /*sökruta */ 

                .topnav a.active {
                  background-color: #2196F3;
                  color: white;
                }

                .topnav .search-container {
                  float: left;
                }

                .topnav input[type=text] {
                  padding: 6px;
                  margin-top: 8px;
                  font-size: 17px;
                  border: none;
                }




               /* Knapparna */

                .accordion {
                    background-color: #636363;
                    color: #ffffff;
                    cursor: pointer;
                    padding: 18px;
                    width: 100%;
                    border: none;
                    text-align: left;
                    outline: none;
                    font-size: 15px;
                    transition: 0.4s;
                }
                */ hover som inte används just nu
                .accordion:hover {
                  background-color: #e0e0e0;
                  color: black;
                }
                /*
               mark {
                    background: orange;
                    color: black;
                }
            </style>
            <!--   en navegering som inte används just nu
            <div id="navbar">
                <div class="topnav">
                    <div class="search-container">
                        <form action="/action_page.php">
                            <input type="text" value="test">
                        </form>
                    </div> 
                </div>
            </div>
            <script type="text/javascript">  
                $(function () {
                    $("input").on("input.highlight", function () {
                        // Determine specified search term
                        var searchTerm = $(this).val();
                        // Highlight search term inside a specific context
                            $("#context").unmark().mark(searchTerm,
                            {
                                "acrossElements": true,
                                "separateWordSearch": false,
                            }
                        );
                    }).trigger("input.highlight").focus();
                });
            </script>
            -->
        """
            f.write(JavascriptFunc)

            # Select all messages from a certain conversation
            qr = "SELECT * FROM 'messages' WHERE Conversation_id LIKE '%s' ORDER BY Timestamp_sent ASC" % x
            curs = conn.execute(qr)

            # Only write button once
            check = False
            for i in curs:

                # Set database vars
                conversation_id = i[0]

                # Check if username is owner
                if i[1] == owner:
                    sent_by_username = i[1]+" (OWNER)"
                else:
                    sent_by_username = i[1]
                sent_by_snapchat_id = i[2]
                content_type = i[3]
                message_decoded = i[4]
                message_og_id = i[5]
                attachments_id = i[6]
                timestamp_sent_raw = i[7]
                timestamp_recived_raw = i[8]

                if check == False:
                    Start = """
    <nav>
        <nav class="content"> 
    
                    <button class="accordion"('%s')">%s</button>
                    <div id="%s" style="display:in-line;">
                        <table>
    
    """ % (conversation_id, conversation_id, conversation_id)
                    # Only write button once
                    f.write(Start)

#----------------------------------------Participants------------------------------------------------------------------
                    if args.mode != "ARY":
                        Table_Header1 = """
                            <tbody>
                                <tr>
                                    <tr>
                                        <th class="color1"><b>Participants</b></th>
                                    </tr>
                            """
                        f.write(Table_Header1)

                        parties = get_participants(database, conversation_id)

                        # Get participants of a chat from database
                        for username, snapchat_id in parties:
                            data = """
                                    <tr>
                                        <th>%s, %s</th>
                                    </tr>
                            """ % (username, snapchat_id)

                            f.write(data)

                        # ENd of Participants
                        Table_ender1 = """
                                </tr>
                            </tbody>
                        """
                        f.write(Table_ender1)
#--------------------------------------------------------------------------------------------------------------------
                check = True

#--------------------------------------Message metadata----------------------------------------------------------------
                timestamp_sent, timestamp_recived = get_timestamp(database, message_og_id, timestamp_sent_raw)

                Table_Header = """
                        <tbody>
                            <tr>
                                <tr>
                                    <th class="color1"><b> %s </b> Created: %s localtime Read: %s localtime</th>
                                </tr>
                                <tr>
                                    <th class="color2"> %s </th>
                                </tr>
                            </tr> 
    
    """ % (sent_by_username, timestamp_sent, timestamp_recived, content_type)

                # Header for msg
                f.write(Table_Header)
    #--------------------------------------------------------------------------------------------------------------------

                msg = msg + 1

                # Write strings that where found
                Table_Data = """
                                        <tr>    
                                            <td> %s </td>
            """ % (message_decoded)
                f.write(Table_Data)
                Table_end = """
                                            </tr>
                                    </tbody>
                                        <tbody class="">
                            """
                f.write(Table_end)

                # Check if messages has an attachment
                if content_type != "Text message" and attachments_id != -1:
                    attachments = get_attachments(database, attachments_id)

                    # Check flags
                    if args.speed == "S" and (args.mode == "AND" or args.mode == "IOS"):

                        # Check if attachments link was found
                        if attachments:
                            Attatchments = Attatchments + 1

                            # Write attachments and key to html report and link to the extracted file
                            # TODO check magic bytes for file type
                            for image in attachments:

                                Atta = """
                                            <tr>
                                                <th class="color1">Attatchment</th>
                                            </tr>
    
                                    """
                                f.write(Atta)

                                Atta_Data = """
    
                                            <tr>
                                                <td> <img src="../../%s" style="max-height:400; max-width:600; align:left;" alt=""></img></td>
                                            </tr>
                                            <tr>
                                                <td> <video src="../../%s" style="max-height:400; max-width:600; align:left;" alt controls></video> </td>
                                            </tr>
                                            <tr>
                                                <td> %s </td>
                                            </tr>
        """ % (image[0], image[0], image[0])
                                f.write(Atta_Data)

            End = """
                        </tbody>        
                    </table>
                </div>
    
    </nav>
    </nav>
    
    
    <script>
    window.onscroll = function() {myFunction()};
    var navbar = document.getElementById("navbar");
    var sticky = navbar.offsetTop;
    
    function myFunction() {
        if (window.pageYOffset >= sticky) {
            navbar.classList.add("sticky")
        } 
        else {
            navbar.classList.remove("sticky");
        }
    }
    </script>
    
    """
            f.write(End)

        with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "Report.html", "a") as a:

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
    print(info)
    write_to_log(args, timea, info)

# So weird
if __name__ == '__main__':
    main()

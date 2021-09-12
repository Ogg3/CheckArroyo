"""
Version 0-6-0
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
        writeHtmlReport(input_path, output_path, args)

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
def store_data(args):

    # Create database to store data
    create_store_data()

    # Start execute timer
    start_time = time.time()

    # Check if user is using gui
    GUI_check = False
    # Check if CLI or GUI
    try:
        a = args[0]
        GUI_check = True
        args = GUI_args(args[0], args[1], args[2], args[3], args[4], args[5], args[6], args[7])
        print("INFO - Using GUI")
        write_to_tex(["INFO - Using GUI"], args.display_window)
    except:
        print("INFO - Using CLI")
        pass

    # Iphone mode
    if args.mode == "IOS":
        write_to_tex(["INFO - Using IOS mode"], args.display_window)
        print("INFO - Using IOS mode")

        # Extract arroyo and perform checks
        arroyo = checkandextract(args, 'arroyo.db', "file")

        # Check if file exist
        if arroyo is None:
            write_to_tex(["ERROR - Could not find arroyo."], args.display_window)
            print("ERROR - Could not find arroyo.")
            return

        if not GUI_check:
            contextmanager = displayIOScontentmanagers(args.input_path, args.output_path)
            print("INFO - Using auto contentmanager mode")
        else:
            write_to_tex(["INFO - Using auto contentmanager mode"], args.display_window)
            contextmanager, nrofcontextmanagers = check_contentmanagers(args.input_path, args.output_path)

        if contextmanager is None:
            print("ERROR - Could not find contentmanager.")
            return
        print("INFO - Found " + str(nrofcontextmanagers) + " contentmanagers.")
        print("INFO - Using " + str(contextmanager) + ".")
        write_to_tex(["INFO - Found " + str(nrofcontextmanagers) + " contentmanagers."], args.display_window)
        write_to_tex(["INFO - Using " + str(contextmanager) + "."], args.display_window)

        PDpath = checkandextract(args, 'primary.docobjects', "file")
        if PDpath is None:
            print("ERROR - Could not find PDpath.")
            return

        print("INFO - Using " + PDpath + " as primary.docobjects")
        write_to_tex(["INFO - Using " + PDpath + " as primary.docobjects"], args.display_window)

        files = ""

        if args.speed == "S":
            # Make a list of files in com.snap.file_manager_
            files = checkinzip(args, 'com.snap.file_manager_', "path")
            print("INFO - Checking for attachments")
            write_to_tex(["INFO - Checking for attachments"], args.display_window)
        else:
            print("INFO - NOT checking for attachments")
            write_to_tex(["INFO - NOT checking for attachments"], args.display_window)

    # Android mode
    elif args.mode == "AND":
        pass

    # Only arroyo mode
    elif args.mode == "ARY":
        print("INFO - User is using arroyo.db mode")
        write_to_tex(["INFO - User is using arroyo.db mode"], args.display_window)
        arroyo = args.input_path

    # Create timestamp for when report was created
    timea = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))

    print("INFO - Connecting to " + arroyo)
    write_to_tex(["INFO - Connecting to " + arroyo], args.display_window)

    conn = sqlite3.connect(arroyo)


# Write report on findings
def writeHtmlReport(args):


    # Make base directory
    os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + timea)

    # Make conversation directory
    os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "conversation-reports")

    msg = 0
    Attatchments = 0
    
    convons = getConv(conn, args.msg_id)

    if GUI_check and args.msg_id != "":
        print("INFO - Filtering for " + args.msg_id)
        write_to_tex(["INFO - Filtering for " + args.msg_id], args.display_window)
    elif not GUI_check and args.msg_id is not None:
        print("INFO - Filtering for " + args.msg_id)
        write_to_tex(["INFO - Filtering for " + args.msg_id], args.display_window)

    print("INFO - Found conversations " + str(convons))
    write_to_tex(["INFO - Found conversations " + str(convons)], args.display_window)


    print("INFO - Writing html reports")
    write_to_tex(["INFO - Writing html reports"], args.display_window)

    # For every conversation
    for x in convons:
        print('INFO - writing conversation: ' + x)
        write_to_tex(['\rINFO - writing conversation: ' + x], args.display_window)
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

            qr = "SELECT * FROM 'conversation_message' WHERE client_conversation_id LIKE '%s' ORDER BY creation_timestamp ASC" % x
            curs = conn.execute(qr)

            # Only write button once
            check = False
            for i in curs:
                if check == False:
                    Start = """
<nav>
    <nav class="content"> 

                <button class="accordion"('%s')">%s</button>
                <div id="%s" style="display:in-line;">
                    <table>

""" % (i[0], i[0], i[0])
                    # Only write button once
                    f.write(Start)
                    Table_Header1 = """
                        <tbody>
                            <tr>
                                <tr>
                                    <th class="color1"><b>Participants</b></th>
                                </tr>
                        """
                    f.write(Table_Header1)
                    for j in check_participants(x, conn, PDpath):
                        data = """
                                <tr>
                                    <th>%s, %s</th>
                                </tr>
                        """ % (j[0], j[1])

                        f.write(data)

                    # ENd of Participants
                    Table_ender1 = """
                            </tr>
                        </tbody>
                    """
                    f.write(Table_ender1)
                    check = True

                res = check_time(i[7], args, GUI_check)

                # Check time flag
                if res:
                    if args.mode == "ARY":
                        id = i[16]
                    else:
                        # Check if username can be found
                        checkU = checkPD(i[16], PDpath)
                        check_id_username(i[16], PDpath)

                        if checkU != False:
                            id = checkU, i[16]
                        else:
                            id = i[16]

                    # Content type
                    ctype = i[13]
                    ctype_string = check_ctype(i[13])

                    Table_Header = """
                            <tbody>
                                <tr>
                                    <tr>
                                        <th class="color1"><b> %s </b> Created: %s UTC +0 Read: %s UTC +0</th>
                                    </tr>
                                    <tr>
                                        <th class="color2"> %s </th>
                                    </tr>
                                </tr> 
    
    """ % (id[0], convTime(i[7]), convTime(i[8]), ctype_string)

                    # Header for msg
                    f.write(Table_Header)

                    # Check for content type and decode
                    proto_string = proto_to_msg(i[5])
                    string_list = decode_string(proto_string, i[5])

                    # if a text message was found
                    if ctype == 1:
                        msg = msg + 1
                    else:
                        attachments = check_keys_proto(args, files, contextmanager[0], proto_string)

                    for string in string_list:
                        Table_Data = """
                                    <tr>    
                                        <td> %s </td>
        """ % (string)
                        f.write(Table_Data)
                    Table_end = """
                                    </tr>
                            </tbody>
                                <tbody class="">
                    """
                    f.write(Table_end)

                    # Check flags
                    if args.speed == "S" and (args.mode == "AND" or args.mode == "IOS"):

                        # Check content type
                        if ctype != 1:

                            # Check if attachments link was found
                            if attachments:
                                Attatchments = Attatchments + 1

                                # Write attachments and key to html report and link to the extracted file
                                # TODO check magic bytes for file type
                                for key, image in attachments:
                                    effromzip(image, args)

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
                                                <tr>
                                                    <td> %s </td>
                                                </tr>
            """ % (image, image, image, key)
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

    with open(args.output_path + "\\" + "CheckArroyo-report-" + timea + "\\" + "Report.html", "w") as a:

        for x in convons:
            link = "./conversation-reports" + "\\" + x + "-HTML-Report.html"
            name = x + "-HTML-Report.html"
            home = """
                <div id="stats"> 
                    <table class="column-stats" >
                        <tr>
                            <th> <a href="%s"> %s </a></th>
                        </tr>
                    </table>
    
                </div>
                    """ % (link, name)
            a.write(home)

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
                            <td>Run time (s): %s</td> 
                        </tr>
                    </table>

                </div>
                        """ % (msg, Attatchments, (time.time() - start_time))
        a.write(Stats)

    print()
    print("Done...")
    write_to_tex(["Done."], args.display_window)
    print((time.time() - start_time))
    write_to_tex(["Execute time "+str((time.time() - start_time))+"(s)."], args.display_window)


# So weird
if __name__ == '__main__':
    main()

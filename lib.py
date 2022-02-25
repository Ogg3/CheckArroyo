"""
github.com/Ogg3/CheckArroyo
"""

import datetime
import sqlite3
from tkinter import *
from zipfile import ZipFile
import time
import re
from parse3 import *


class GUI_args(object):
    """
    Make a class to match the args.parser being used for CLI
    """

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
        self.check_attachmets = speed
        self.mode = mode
        self.time_start = time_start
        self.time_stop = time_stop
        # self.contentmanager = contentmanager
        self.msg_id = msg_id
        #self.display_window = display_window

class IO_paths:
    """
    Output class
    """

    nl = '\n'
    log_file = ""
    report_folder = ""
    report_file = ""
    report_convos = ""
    input_path = None
    output_path = None
    report_time = ""
    research_txt = ""

    def __init__(self, args):

        # Create timestamp for when report was created
        report_time = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        IO_paths.report_time = report_time
        self.report_time = report_time
        IO_paths.input_path = args.input_path

        # Make base directory
        os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + report_time)
        IO_paths.report_folder = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\"

        # Make conversation directory
        os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "conversation-reports")

        # Create report file
        with open(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html", "w") as a:
            a.write("")

        # Create log file
        with open(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "log.txt", "w") as a:
            a.write("")

        with open(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "raw_protobufs.txt", "w") as a:
            a.write("")

        self.log_file = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "log.html"
        self.report_folder = args.output_path + "\\" + "CheckArroyo-report-" + report_time
        self.report_file = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html"
        self.report_convos = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "conversation-reports" + "\\"
        self.input_path = args.input_path
        self.output_path = args.output_path
        self.research_txt = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "raw_protobufs.txt"
        IO_paths.research_txt = os.path.abspath(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "raw_protobufs.txt")
        IO_paths.log_file = os.path.abspath(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "log.txt")
        IO_paths.report_file = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html"
        IO_paths.report_convos = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "conversation-reports" + "\\"



def check_content_type(int_ctype):
    """
    Check what type of content is being sent
    Return string if known
    Return number if unknown
    """
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
        elif int_ctype == 5:
            return "Emoji"
        elif int_ctype == 6:
            return "Shared Location (Not Tested)"
        elif int_ctype == 10:
            return "Took screenshot"
        elif int_ctype == 13:
            return "Unsuccessful voice call"
        else:
            return "Content type " + str(int_ctype)
    else:
        return "ERROR - scripts.check_ctype excpects a int, not " + str(type(int_ctype))


def check_list_for_empty(lst):
    """
    Check if list contains only empty strings
    """
    for i in lst:
        if i != "":
            return False

    return True


def decode_string(proto_string, bin_string):
    """
    Decode a list of strings
    Emojis are not supported
    """
    strings = []

    try:
        # Check if any string messages where found
        if proto_string is not None:

            # Check if multiple strings where found
            if type(proto_string) is list:

                for i in proto_string:
                    # Encode because reasons
                    tmp = i.encode('cp1252', 'xmlcharrefreplace')
                    tmp = tmp.decode('cp1252')

                    strings.append(tmp)
        else:
            strings.append("".join(re.findall("[a-zA-Z0-9äöåÄÖÅ ]+", bin_string.decode('utf-8', 'ignore'))))

        # Check if list is only empty strings
        if check_list_for_empty(strings):
            fallback = "".join(re.findall("[a-zA-Z0-9äöåÄÖÅ ]+", bin_string.decode('utf-8', 'ignore')))
            return ["WARNING - No string found, displaying raw data: "+str(fallback)]

        return strings
    except Exception as e:
        print(str(e))
        print("ERROR - Failed to encode string, proto_string: "+str(proto_string)+", bin_string: "+str(bin_string))


def find_string_in_dict(data):
    """
    return a dict of a nested dict
    """
    for k, v in data.items():
        if isinstance(v, dict):
            yield k, v
            yield from find_string_in_dict(v)
        else:
            yield k, v


def raw_protobuf(proto_bin, client_id, server_id):
    """
    Decodes the protobuf to raw format and stores in a text file for research
    """
    with open(IO_paths.research_txt, "a") as f:
        decoded_proto = ParseProto(proto_bin)
        f.write(str((decoded_proto, "Client id: "+str(client_id) + "Server id: "+str(server_id))))
        f.write("\n")
        f.write("\n")


def proto_to_msg(bin_file):
    """
    Turn a raw protobuf file to find a msg string
    """
    messages_found = []
    messages = ParseProto(bin_file)

    res = find_string_in_dict(messages)
    for k, v in res:
        if "string" in k:
            messages_found.append(v)

    return messages_found


def proto_to_bytes(bin_file):
    """
    Turn raw protobuf file and find key
    """
    messages = ParseProto(bin_file)

    def conv_protohex_to_hex(data):
        print("Hex data incoming...")
        """
        Converts hex format found after decoding a protocolbuffer to various decode modes
        """

        # Make array
        data = data.split(':')

        def decode_bytes(bytes_string, mode):
            """

            """

            string = ""

            for i in bytes_string:
                try:
                    string = string + str(bytes.fromhex(i[2:]).decode(mode))
                except:
                    pass

            print(string)

        decode_bytes(data, "cp1252")
        decode_bytes(data, "utf-8")
        print()
        print()

    res = find_string_in_dict(messages)
    for k, v in res:
        if "bytes" in k:
            conv_protohex_to_hex(v)


def check_time(msg, args):
    """
    If both values are None then no time has been set so all times are valid
    """
    # Check if both vars are in use
    if args.time_start is not None and args.time_stop is not None:
        # Check if message was created within a range of dates
        return inRange(args.time_start, args.time_stop, msg)
    else:
        return True


def checkandextract(args, string, mode):
    """
    Searches for a file with name and extracts them
    """
    check = checkinzip(args, string, mode)
    if check is None:
        return None
    else:
        effromzip(check[0])
        return os.path.abspath(IO_paths.report_folder + '/' + check[0])


def inRange(start, stop, time_check):
    """
    Check if time is in range
    :param start:
    :param stop:
    :param time_check:
    :return:
    """
    if stop is not None and start is not None:
        start = conv2Time(start)
        stop = conv2Time(stop)
        time_check = datetime.date(time_check.year, time_check.month, time_check.day)

        return start <= time_check <= stop
    else:
        return True


def checkforfile21(path):
    """
    Checks zipfile from files with the name string and if the name is larger than 21 in length
    returns a list with paths to those files
    """
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


def checkinzip(args, string, mode):
    """
    Extract contentmanager
    """
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



def conv2Time(time):
    """
    Convert string to time object
    """
    datea = datetime.datetime.strptime(time, "%Y-%m-%d")
    return datetime.date(datea.year, datea.month, datea.day)





def readzip(zip):
    """
    Open zipfile
    """
    try:
        with ZipFile(zip, "r") as f:
            f.printdir()

        f.close()
    except Exception as e:
        write_to_log(e)
        return


def effromzip(file):
    """
    Extract file from zip to path
    """
    try:
        with ZipFile(IO_paths.input_path, 'r') as f:
            f.extract(file, IO_paths.report_folder)

        f.close()
    except Exception as e:
        write_to_log(e)
        return


def readfromzip(zip, file):
    """
    Read from file in zip
    """
    try:
        with ZipFile(zip, 'r') as f:
            return f.read(file)
    except Exception as e:
        write_to_log(e)
        return


def write_to_log(message):
    """
    Write to log file
    """
    with open(IO_paths.log_file, 'a') as f:
        try:
            print(message)
            f.write(str(message)+IO_paths.nl)
        except Exception as e:
            print("ERROR - Logfile broke, how even.")
            print(e)


def compare_magic_bytes(file):
    """
    Reads in a file and gets the file header
    returns string with type of file
    :param file:input file
    :return:string
    """

    with open(file, "rb") as f:
        header = f.read(10)

        # JPG
        if header[6:] == b"JFIF":
            return "PIC"
        # PNG
        elif header[1:4] == b"PNG":
            return "PIC"
        # ?MP4?
        elif header[4:] == b"ftypmp":
            return "MOV"
        elif header[:4] == b"RIFF":
            return "PIC"
        elif header[:1] == b"\n" and header[2:8] == b"media~":
            return "CONTROL FILE"
        elif header[:5] == b'\xff\xd8\xff\xfe\x00':
            return "PIC"
        elif header == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" or header == b'':
            return "EMPTY"
        else:
            #print(header[:5])
            errorstring = "ERROR - Unable to determine file typ for: "+str(file)
            write_to_log(errorstring)
            write_to_log(str(header))
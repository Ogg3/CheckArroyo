"""
MIT License

Copyright (c) 2021 Ogg3

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import datetime
import traceback
from zipfile import ZipFile
import tarfile
from parse3 import *
import re
import sqlite3
import pathlib


def get_input_type(file):
    return pathlib.Path(file).suffix


class IO_paths():
    """
    Class to keep track of paths for files and folders
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
    research_folder = ""
    store_data = ""

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

        # Make research_folder directory
        os.mkdir(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "research_folder")

        # Create report file
        with open(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html", "w") as a:
            a.write("")

        # Create log file
        with open(args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "log.txt", "w") as a:
            a.write("")


        self.report_folder = args.output_path + "\\" + "CheckArroyo-report-" + report_time
        self.report_file = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html"
        self.report_convos = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "conversation-reports" + "\\"
        self.input_path = args.input_path
        self.output_path = args.output_path
        IO_paths.log_file = os.path.abspath(
            args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "log.txt")
        IO_paths.report_file = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html"
        IO_paths.report_convos = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "conversation-reports" + "\\"
        self.store_data = args.output_path + "\\" + "CheckArroyo-report-" + IO_paths.report_time + "\\" + "store_data.db"
        self.report_folder = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "research_folder" + "\\"



class proto():

    def __init__(self, protomessage):
        self.protomessage = protomessage

    def parse_proto(self):
        return ParseProto(self.protomessage)

    def proto_to_msg(self):
        """
        Turn a raw protobuf file to find a msg string
        """
        messages_found = []
        messages = self.parse_proto()

        res = self.find_string_in_dict(messages)
        for k, v in res:
            if "string" in k:
                messages_found.append(v)

        return messages_found

    def find_string_in_dict(self, data):
        """
        return a dict of a nested dict
        """
        for k, v in data.items():
            if isinstance(v, dict):
                yield k, v
                yield from self.find_string_in_dict(v)
            else:
                yield k, v

    def check_list_for_empty(self, lst):
        """
        Check if list contains only empty strings
        """
        for i in lst:
            if i != "":
                return False

        return True

    def decode_string(self, proto_string, bin_string):
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
            if self.check_list_for_empty(strings):
                fallback = "".join(re.findall("[a-zA-Z0-9äöåÄÖÅ ]+", bin_string.decode('utf-8', 'ignore')))
                return ["WARNING - No string found, displaying raw data: " + str(fallback)]

            return strings
        except Exception as e:
            print(str(e))
            print("ERROR - Failed to encode string, proto_string: " + str(proto_string) + ", bin_string: " + str(
                bin_string))


class zipper(object):

    def __init__(self, zipfile):
        self.zipfile = zipfile

    def find_file_all(self, filename):
        """
        Find files in zipfile
        returns all matches for this file
        """

        data = []

        with ZipFile(self.zipfile, "r") as f:
            for i in f.namelist():
                new = i.split("/")
                if filename in new[len(new) - 1] and i[len(i) - 1] != "/":
                    data.append(i)
            f.close()

        if data == []:
            return None
        else:
            return data

    def find_folder_all(self, foldername):
        """
        Find folder in zipfile
        returns all matches for this foldername
        """

        data = []

        with ZipFile(self.zipfile, "r") as f:
            for i in f.namelist():
                if foldername in i and i[len(i) - 1] == "/":
                    data.append(i)
            f.close()

        if data == []:
            return None
        else:
            return data

    def find_file_exact(self, filename):
        """
        Find files in zipfile
        returns all matches for this file
        """

        data = []

        with ZipFile(self.zipfile, "r") as f:
            for i in f.namelist():
                new = i.split("/")
                if filename == new[len(new) - 1] and i[len(i) - 1] != "/":
                    data.append(i)
            f.close()

        if data == []:
            return None
        else:
            return data

    def find_folder_exact(self, foldername):
        """
        Find folder in zipfile
        returns all matches for this foldername
        """

        data = []

        with ZipFile(self.zipfile, "r") as f:
            for i in f.namelist():
                if foldername in i and i[len(i) - 1] == "/":
                    split = i.split("/")
                    for name in split:
                        if name == foldername:
                            data.append(i)
            f.close()

        if data == []:
            return None
        else:
            return data


    def extract_files(self, file_list):
        """
        Extract file from zip to outputpath
        returns a list of path(s)
        """
        try:
            paths=[]
            with ZipFile(self.zipfile, 'r') as f:
                for filename in file_list:
                    f.extract(filename, IO_paths.report_folder)
                    paths.append(os.path.abspath(IO_paths.report_folder + '/' + filename))
            f.close()

            return paths
        except Exception as e:
            error(e, True)
            return

    def get_size_of_file(self, file):
        with ZipFile(self.zipfile, "r") as f:
            data = f.getinfo(file)
            print(data)
            f.close()


class tarrer():
    pass


"""
Logging
"""
def outputcolors(string, color):
    """
    string: string to change
    Color: Green, Red, or Yellow
    bold: True = yes False = no
    """
    attr = []
    if color == "Green":
        attr.append("32")
    elif color == "Red":
        attr.append("31")
    elif color == "Yellow":
        attr.append("33")

    # Add bold
    attr.append("1")
    return "\x1b[%sm%s\x1b[0m" % (';'.join(attr), string)

def info(message):
    """
    Write a information message to the logfile and stdout
    """
    with open(IO_paths.log_file, 'a') as f:
        print("INFO - "+message)
        f.write(str(message) + IO_paths.nl)


def error(exception, fatal):
    """
    Write a error message to the logfile and stdout
    """

    if exception == None:
        message = "ERROR - exception was None"
        print(outputcolors(message, "Red"))
        return

    with open(IO_paths.log_file, 'a') as f:
        if fatal:
            error = "ERROR - " + str(
                traceback.format_exc() + "\n" + exception.__doc__)
        else:
            error = "ERROR - "+str(exception)
        print(outputcolors(error, "Red"))
        f.write(str(error) + IO_paths.nl)


def warning(message):
    """
    Write a warning message to the logfile and stdout
    """
    with open(IO_paths.log_file, 'a') as f:
        error = "WARNING - " + str(message)
        print(outputcolors(error, "Yellow"))
        f.write(str(error) + IO_paths.nl)


def success(message):
    """
    Write a success message to the logfile and stdout
    """
    with open(IO_paths.log_file, 'a') as f:
        error = "SUCCESS - " + str(message)
        print(outputcolors(error, "Green"))
        f.write(str(error) + IO_paths.nl)


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
        elif b"ftypmp" in header:
            return "MOV"
        elif header[:4] == b"RIFF":
            return "PIC"
        elif header[:1] == b"\n" and header[2:8] == b"media~":
            return "CONTROL FILE"
        elif b'overlay~' in header:
            return "CONTROL FILE"
        elif b'thumbnai' in header:
            return "CONTROL FILE"
        elif header[:5] == b'\xff\xd8\xff\xfe\x00':
            return "PIC"
        elif header == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" or header == b'':
            return "EMPTY"
        elif header == b'\x00\x00\x00 ftypis':
            return "MOV"
        elif header == b'PK\x03\x04\n\x00\x00\x08\x00\x00':
            return "COMPRESSED"
        else:
            #print(header[:5])
            warning("Unable to determine file type for: "+str(file))


def check_content_type(int_ctype):
    """
    Check what type of content is being sent
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
        elif int_ctype == 3:
            return "Video (Not Tested)"
        # 4 is audio messages
        elif int_ctype == 4:
            return "Audio message"
        elif int_ctype == 5:
            return "Emoji"
        elif int_ctype == 6:
            return "Shared Location (Android Not Tested)"
        elif int_ctype == 8:
            return "Shared Location (Iphone Not Tested)"
        elif int_ctype == 10:
            return "Took screenshot"
        elif int_ctype == 12:
            return "Unsuccessful video call"
        elif int_ctype == 13:
            return "Unsuccessful voice call"
        else:
            return "Content type " + str(int_ctype)
    else:
        return "ERROR - scripts.check_ctype excpects a int, not " + str(type(int_ctype))
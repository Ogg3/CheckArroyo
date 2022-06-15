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
        IO_paths.research_txt = os.path.abspath(
            args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "raw_protobufs.txt")
        IO_paths.log_file = os.path.abspath(
            args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "log.txt")
        IO_paths.report_file = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "Report.html"
        IO_paths.report_convos = args.output_path + "\\" + "CheckArroyo-report-" + report_time + "\\" + "conversation-reports" + "\\"


class zipper(object):

    def __init__(self):
        pass

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

    def checkforfile21(self):
        """
        Checks zipfile from files with the name string and if the name is larger than 21 in length
        returns a list with paths to those files
        """
        path = os.path.abspath(IO_paths.input_path)

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


    def find_file(self, filename):
        """
        Find files in zipfile
        """
        path = os.path.abspath(IO_paths.input_path)

        data = []

        with ZipFile(path, "r") as f:
            for i in f.namelist():
                new = i.split("/")
                if filename == new[len(new) - 1] and i[len(i) - 1] != "/":
                    data.append(i)
            f.close()

        if data == []:
            return None
        else:
            return data

    def find_folder(self, foldername):
        """
        Find folder in zipfile
        """
        path = os.path.abspath(IO_paths.input_path)

        data = []

        with ZipFile(path, "r") as f:
            for i in f.namelist():
                if foldername in i:  # and i[len(i) - 1] != "/":
                    data.append(i)
            f.close()

        if data == []:
            return None
        else:
            return data

    def extract_file(self, file):
        """
        Extract file from zip to outputpath
        """
        try:
            with ZipFile(IO_paths.input_path, 'r') as f:
                f.extract(file, IO_paths.report_folder)
            f.close()
            return os.path.abspath(IO_paths.report_folder + '/' + file)
        except Exception as e:
            error(e)
            return


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
        print(message)
        f.write(str(message) + IO_paths.nl)


def error(exception: Exception) -> None:
    """
    Write a error message to the logfile and stdout
    """

    if exception == None:
        message = "ERROR - exception was None"
        print(outputcolors(message, "Red"))
        return

    exception = str(exception)

    with open(IO_paths.log_file, 'a') as f:
        error = "ERROR - " + str(
            traceback.format_exc() + "\n" + exception.__doc__)
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
        error = "WARNING - " + str(message)
        print(outputcolors(error, "Green"))
        f.write(str(error) + IO_paths.nl)

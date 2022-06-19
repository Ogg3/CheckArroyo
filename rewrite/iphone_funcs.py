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

import os.path
import sys

from lib import *
from database_funcs import *
import re


IOS_supported_versions = ['11120']

def iPhone_mode(args, seeker):


    # Create files and folder structure for report
    io = IO_paths(args)

    info("Using iPhone mode")

    if "." in args.snapchat_version:
        args.snapchat_version = args.snapchat_version.replace(".", "")

    if args.snapchat_version not in IOS_supported_versions:
        warning("Snapchat version is not supporter! To help with the progression of this script please upload the files in research_folder to ")

    if args.snapchat_version != "":
        args.snapchat_version = int(args.snapchat_version)

    # Create database to store information
    store = store_data(io.store_data)

    arroyo_qr = arroyo_queries(snapchat_version=args.snapchat_version, systemtype=args.mode, timefilter=args.time_filter)
    primarydocobjects_qr = primarydocobjects_queries(snapchat_version=args.snapchat_version, systemtype=args.mode, timefilter=args.time_filter)
    contentmanagers_qr = contentmanagers_queries(snapchat_version=args.snapchat_version, systemtype=args.mode, timefilter=args.time_filter)
    cachecontroller_qr = cachecontroller_queries(snapchat_version=args.snapchat_version, systemtype=args.mode, timefilter=args.time_filter)

    if args.custom_paths:
        paths = custom_paths()
        arroyo_path = paths[0]
        primarydocobjects_path = paths[1]
        content_managers_paths = paths[2]
        cachecontroller_path = paths[3]
    else:
        arroyo_path = seeker.extract_files(seeker.find_file_exact("arroyo.db"))
        primarydocobjects_path = seeker.extract_files(seeker.find_file_exact("primary.docobjects"))
        content_managers_paths = seeker.extract_files(seeker.find_file_all("contentManagerDb.db"))
        cachecontroller_path = seeker.extract_files(seeker.find_file_exact("cache_controller.db"))

    # Check arroyo (Ay!)
    if len(arroyo_path) != 1:
        warning("Mutiple arroyo.db found")

    arroyo_path = arroyo_path[0]

    if args.verbose:
        info("Arroyo path: "+str(arroyo_path))

    if not check_arroyo(arroyo_path, arroyo_qr, io):
        warning("Arroyo did not pass checks, exiting!")
        sys.exit(0)
    else:
        success("Arroyo passed checks!")

    # Check primarydocobjects
    if len(primarydocobjects_path) != 1:
        warning("Mutiple primary.docobjects found")

    primarydocobjects_path = primarydocobjects_path[0]

    if args.verbose:
        info("primary.docobjects path: "+str(primarydocobjects_path))

    primarydocobjects = check_primarydocobjects(primarydocobjects_path, primarydocobjects_qr, io)
    if not primarydocobjects:
        warning("Primarydocobjects did not pass checks!")
    else:
        success("Primarydocobjects passed checks!")

    # Check contentmanagers
    if len(content_managers_paths) != 1:
        warning("Mutiple contentmanagers found")

    if args.verbose:
        info("Contentmanagers path: "+str(content_managers_paths))

    contentmanagerDB, contentmanagers_paths = check_content_managers(content_managers_paths, contentmanagers_qr, io)


    # Check cachecontroller
    if len(cachecontroller_path) != 1:
        warning("Mutiple arroyo.db found")

    if args.verbose:
        info("Cachecontrller path: "+str(cachecontroller_path[0]))

    cachecontroller = check_cachecontroller(cachecontroller_path, cachecontroller_qr, io)
    if not cachecontroller:
        warning("cache_controller.db did not pass checks!")
    else:
        success("cache_controller.db passed checks!")


def check_snapchat_database(path, tablename, rownames):
    """
    Check if a database from input-source is usable
    """
    data = database(path)
    if data.connect_readonly() != False:

        if data.check_table(tablename) != False:

            for rowname in rownames:
                if data.check_row(rowname=rowname, tablename=tablename) != False:
                    pass
                else:
                    warning(str(rowname)+" was not found in "+str(path))
                    return False
            return True
        else:
            warning(str(tablename)+" was not found in "+str(path))
            return False


def check_arroyo(arroyo_path, arroyo_qr, IO_paths):
    data = database(arroyo_path)

    message_check = False
    id_check = False

    if data.connect_readonly() != False:
        # Write structure of database to researchfile
        with open(IO_paths.report_folder+"arroyo_structure", "w") as f:
            f.write(data.get_structure())

    # Check if arroyo has the ciritcal tables
    conversation_message = arroyo_qr.conversation_message_rownames(True)

    if check_snapchat_database(arroyo_path, "conversation_message", conversation_message):
        message_check = True

    # Check if arroyo has the ciritcal tables
    conversation_id = arroyo_qr.conversation_id()

    # For every entry make a check
    for dicti in conversation_id:
        if check_snapchat_database(arroyo_path, conversation_id):
            id_check = True

    if id_check and message_check:
        return True
    else:
        return False


def check_primarydocobjects(primarydocobjects_path, primarydocobjects_qr, IO_paths):

    data = database(primarydocobjects_path)

    if data.connect_readonly() != False:
        # Write structure of database to researchfile
        with open(IO_paths.report_folder + "primarydocobjects_structure", "w") as f:
            f.write(data.get_structure())


def check_content_managers(content_managers_paths, content_managers_qr, IO_paths):
    """
    Because there is a large chance more then one contentmanagers exists the output is true if one database is usable.
    There will be a warning for every database that is not usable
    """

    for managers in content_managers_paths:

        data = database(managers)

        if data.connect_readonly() != False:
            # Write structure of database to researchfile
            with open(IO_paths.report_folder + "contentManager_structure", "w") as f:
                f.write(str(managers)+IO_paths.nl)
                f.write(data.get_structure())


def check_cachecontroller(cachecontroller_path, cachecontroller_qr, IO_paths):
    data = database(cachecontroller_path)

    if data.connect_readonly() != False:
        # Write structure of database to researchfile
        with open(IO_paths.report_folder + "cachecontroller_structure", "w") as f:
            f.write(data.get_structure())


def custom_paths():
    """
    Get the custom paths for the following files
    arroyo.db
    primary.docobjects
    unlimited amount of contentmangares
    cachecontroller
    """
    paths = []

    arroyo_path = input("Input the path for arroyo.db: ")

    if not os.path.isfile(arroyo_path):
        warning("Specefied path for {} is not a file, restarting input method.".format(arroyo_path))
        custom_paths()

    paths.append(arroyo_path)

    primarydocobjects_path = input("Input the path for primary.docobjects: ")

    if not os.path.isfile(primarydocobjects_path):
        warning("Specefied path for {} is not a file, restarting input method.".format(primarydocobjects_path))
        custom_paths()

    paths.append(primarydocobjects_path)

    content_managers = []

    for i in input("Input the path(s) for contentmanagers, when finished press enter."):
        content_managers.append(i)

    for i in content_managers:
        if not os.path.isfile(i):
            warning("Specefied path for {} is not a file, restarting input method.".format(i))
            custom_paths()

    paths.append((content_managers))

    cachecontroller_path = input("Input the path for cache_controller.db: ")

    if not os.path.isfile(cachecontroller_path):
        warning("Specefied path for {} is not a file, restarting input method.".format(cachecontroller_path))
        custom_paths()

    paths.append(cachecontroller_path)

    return paths

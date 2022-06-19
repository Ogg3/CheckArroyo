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


def iPhone_mode(args, seeker):


    # Create files and folder structure for report
    io = IO_paths(args)

    info("Using iPhone mode")

    # Create database to store information
    store = store_data(io.store_data)

    arroyo_qr = arroyo_queries(snapchat_version="", systemtype="", timefilter=args.time_filter)
    primarydocobjects_qr = primarydocobjects_queries(snapchat_version="", systemtype="", timefilter=args.time_filter)
    contentmanagers_qr = contentmanagers_queries(snapchat_version="", systemtype="", timefilter=args.time_filter)
    cachecontroller_qr = cachecontroller_queries(snapchat_version="", systemtype="", timefilter=args.time_filter)

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

    if args.verbose:
        info("Arroyo path: "+str(arroyo_path[0]))

    if not check_arroyo(arroyo_path, arroyo_qr):
        warning("Arroyo did not pass checks, exiting!")
        sys.exit(0)
    else:
        success("Arroyo passed checks!")

    # Check primarydocobjects
    if len(primarydocobjects_path) != 1:
        warning("Mutiple primary.docobjects found")

    if args.verbose:
        info("primary.docobjects path: "+str(primarydocobjects_path[0]))

    if not check_primarydocobjects(primarydocobjects_path, primarydocobjects_qr):
        warning("Primarydocobjects did not pass checks!")
    else:
        success("Primarydocobjects passed checks!")

    # Check contentmanagers
    if len(content_managers_paths) != 1:
        warning("Mutiple contentmanagers found")

    if args.verbose:
        info("Contentmanagers path: "+str(content_managers_paths))

    contentmanagers = check_content_managers(content_managers_paths, contentmanagers_qr)


    # Check cachecontroller
    if len(cachecontroller_path) != 1:
        warning("Mutiple arroyo.db found")

    if args.verbose:
        info("Cachecontrller path: "+str(cachecontroller_path[0]))

    check_cachecontroller(cachecontroller_path, cachecontroller_qr)


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


def check_arroyo(arroyo_path, arroyo_qr):

    # Check if arroyo has the ciritcal tables
    conversation_message = arroyo_qr.conversation_message(True)

    if check_snapchat_database(arroyo_path[0], "conversation_message", conversation_message):
        return True
    else:
        return False


def check_primarydocobjects(primarydocobjects_path, primarydocobjects_qr):
    pass

def check_content_managers(content_managers_paths, content_managers_qr):
    """
    Because there is a large chance more then one contentmanagers exists the output is true if one database is usable.
    There will be a warning for every database that is not usable tho
    """
    pass

def check_cachecontroller(cachecontroller_path, cachecontroller_qr):
    pass


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

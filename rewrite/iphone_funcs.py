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

    # Write the structure of the database to file for research
    write_strucutres(arroyo_path, io)
    write_strucutres(primarydocobjects_path, io)
    write_strucutres(content_managers_paths, io)
    write_strucutres(cachecontroller_path, io)

    paths = {
        "arroyo.db":arroyo_path,
        "primary.docobjects":primarydocobjects_path,
        "contentManagerDb.db":content_managers_paths,
        "cache_controller.db":cachecontroller_path
    }


def write_strucutres(paths, IO_paths):

    for path in paths:

        data = database(path)

        # Get only the filename in the path
        filename = path.split("/")
        filename = filename[len(filename)-1]

        if data.connect_readonly() != False:
            # Write structure of database to researchfile
            with open(IO_paths.report_folder+filename+"_structure", "w") as f:
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

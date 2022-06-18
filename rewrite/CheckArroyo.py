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

import argparse
import webbrowser
from iPhone_funcs import *
from android_funcs import *
import sqlite3
from lib import *

__version__ = "0-7-0"

IOS_supported_versions = ['11.12.0', ]
Android_supported_versions = ['11.51.0.37', ]

def check_paths(parser, input_path, output_path):
    # Check so paths exists
    if output_path is None:
        parser.error('No OUTPUT folder path provided')
        return
    else:
        output_path = os.path.abspath(output_path)

    if output_path is None:
        parser.error('No OUTPUT folder selected. Run the program again.')
        return

    if input_path is None:
        parser.error('No INPUT file. Run the program again.')
        return
    else:
        input_path = os.path.abspath(input_path)

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
        error(e)


def main():

    parser = argparse.ArgumentParser(description='CheckArroyo '+__version__+': Snapchat chat parser.')

    parser.add_argument('-i', '--input_path', required=True, action="store", help='Path to snapchat dump.')
    parser.add_argument('-o', '--output_path', required=True, action="store", help='Output folder path.')
    parser.add_argument('-m', '--mode', required=True, action="store",
                        help='Select mode, IOS - iPhone, AND - Android, ARY - only arroyo')
    parser.add_argument('-s', '--snapchat_version', required=True, action="store",
                        help='Select mode, IOS - iPhone, AND - Android, ARY - only arroyo')
    parser.add_argument('-n', '--no_attachmets', required=False, action="store_true",
                        help='Use if attachments should NOT be checked')
    parser.add_argument('-c', '--custom_paths', required=False, action="store_true",
                        help='Use to input custom paths to databases.')
    parser.add_argument('-e', '--expert_mode', required=False, action="store_true",
                        help='The HTML report will now contain more unfiltered data')
    parser.add_argument('-v', '--verbose', required=False, action="store_true",
                        help='The HTML report will now contain more unfiltered data')
    parser.add_argument('-t', '--time_filter', required=False, action="store", help='Time range start. Ex: 2021-01-01 10:00:00 2022-02-02 20:00:00')
    parser.add_argument('-msg', '--msg_id', required=False, action="store",
                        help='Make report for only one conversation id')

    args = parser.parse_args()

    # Get flags
    input_path = args.input_path
    output_path = args.output_path
    mode = args.mode
    no_attachments = args.no_attachments
    expert_mode = args.expert_mode
    verbose = args.verbose
    timefilterStart = args.time_start
    custom_paths = args.custom_paths

def parse_data(args):
    pass


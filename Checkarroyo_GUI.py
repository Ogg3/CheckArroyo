"""
Version dev
github.com/Ogg3/CheckArroyo
"""

import PySimpleGUI as sg
from Checkarroyo import writeHtmlReport
from lib import *

"""
Req:
Input folder
Output folder

Optional:
Manual arroyo path
Manual contentmanager path
start and stop time
conversation id
check or dont check attachments
mode
write html reports

"""


window = sg.Window(title="Demo", layout=[[]], margins=(100,50)).read()
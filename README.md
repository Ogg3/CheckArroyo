# CheckArroyo
Snapchat parser for iPhone, Android and arroyo.db.

The script creates a html report for every conversation ID that was found. The conversation is parsed to check for attachments such as snaps, media and audio messages, it also displays the participants of the chat.

I recommend disabling the windows path limit. This might cause connection errors to databases

CheckArroyo.py - run this in CLI\
CheckArroyo_GUI.py - run this for GUI\
parser3.py - decode protbuffers (from ALEAP)\
lib.py - help functions

# Usage

Requirments: Python 3.9

## If you have a Full File System

Extract the folder for snapchat as a zip file and then run either the GUI or CLI version\

IOS - private/var/mobile/Containers/Data/Applications/ID\
Android - \

## If you only have certain databases

Extract the database (for now only arroyo.db is supported) and choose the database as input.\
\
Arroyo\
  IOS - private/var/mobile/Containers/Data/Applications/ID/Documents/user_scoped/ID/arroyo/arroyo.db\
  Android - 
  
## Flags
-i input file\
-o outputfolder\
-m mode. IOS = Iphone, AND = Android or ARY = arroyo.\
-c check attachments, Y(es) or N(o)

Optional filters\
-t1 time start -t2 time stop. Only display conversations within timespan\
-msg filter for a specific conversation ID

## Examples
Example: CheckArroyo.py -i C:\zipfile.zip -o C:\output -m IOS -c Y\
Example: CheckArroyo.py -i arroyo.db -o OUTPUTFOLDER -m ARY\
Example: CheckArroyo.py -i C:\zipfile.zip -o C:\output -m AND -c Y -t1 2021-01-01 -t2 2021-02-02 -msg ID_HERE

# Tips
Check out the wiki for more info on how it works

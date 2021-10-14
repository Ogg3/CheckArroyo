# CheckArroyo
Snapchat parser for IOS, Android (soon) and arroyo.db.

The script creates a html report for every conversation ID that was found. The conversation is parsed to check for attachments such as snaps, media and audio messages, it also displays the participants of the chat.

CheckArroyo.py - run this in CLI\
CheckArroyo_GUI.py - run this for GUI\
parser3.py - decode protbuffers (from ALEAP)\
lib.py - help functions

First project on github :D

# Usage

Requirments: Python 3.9

## If you have a Full File System

Extract the folder for snapchat as a zip file and then run either the GUI or CLI version\

IOS - private/var/mobile/Containers/Data/Applications/ID\
Android - Soon\

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

## Exapmles
Example: CheckArroyo.py -i ZIPFILE -o OUTPUTFOLDER -m IOS -c Y\
Example: CheckArroyo.py -i arroyo.db -o OUTPUTFOLDER -m IOS\
Example: CheckArroyo.py -i ZIPFILE -o OUTPUTFOLDER -m IOS -c Y -t1 2021-01-01 -t2 2021-02-02 -msg ID_HERE

# Tips

I recomend using something like AXIOM to parse the conversation if you just want text messages, its much easier to read than in my HTML reports.\

Check out the wiki for more info :)

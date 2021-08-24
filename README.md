# CheckArroyo
Snapchat parser for IOS, Android (soon) and arroyo.db.

The script creates a html report for every conversation ID that was found. The conversation is parsed to check for attachments such as snaps, media and audio messages, it also displays the participants of the chat.

CheckArroyo.py - run this in CLI\
CheckArroyo_GUI.py - run this for GUI\
parser3.py - decode protbuffers (from ALEAP)\
lib.py - help functions

First project on github :D

# Usage

Extract the folder for snapchat as a zip file and then run either the GUI or CLI version\

IOS - private/var/mobile/Containers/Data/Applications/ID\
Android - Soon\
\
Arroyo\
  IOS - private/var/mobile/Containers/Data/Applications/ID/Documents/user_scoped/ID/arroyo/arroyo.db\
  Android - 
  
-i input file\
-o outputfolder\
-m mode. IOS = Iphone, AND = Android or ARY = arroyo.\
-s speed, S = check attachments, F = only check for text

Optional filters\
-t1 time start -t2 time stop. Only display conversations within timespan\
-msg filter for a specific conversation ID

# Tips

I recomend using something like AXIOM to parse the conversation if you just want text messages, its much easier to read than in my HTML reports.\

Check out the wiki for more info :)

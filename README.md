# CheckArroyo
Snapchat parser for IOS, Android (soon) and arroyo.db.

The script creates a html report for every conversation ID that was found. The conversation is parsed to check for attachments such as snaps, media and audio messages, it also displays the participants of the chat.

CheckArroyo.py - run this in CLI\
CheckArroyo_GUI.py - run this for GUI\
lib.py - help functions

First project on github :D

# Usage

Extract the folder for snapchat as a zip file and then run either the GUI or CLI version

# Tips

I recomend using something like AXIOM to parse the conversation if you just want text messages, its much easier to read than in my HTML reports.

# How it works

## Arroyo.db
Arroyo is where conversations are stored. For every message there is a message_type where 1 is a regular text message. If it is not a text message there is a chance a key is stored in the message_content blob. The blob can be decoded as a raw protocol buffer, as of now I haven't found a good way to decode it with python. The key is 21 in length.

## Contentmanagerdb.db

This is where files are linked to a message. Sometimes there is just one key for one file, however with snaps there are multiple sub keys which is linked to for exapmle the layer file, the media content, a thumbnail file.

## primary.docobjects

Here usernames can be linked to snapchat IDs, it can also show the participants of a conversation.

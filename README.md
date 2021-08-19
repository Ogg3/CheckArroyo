# CheckArroyo
Snapchat parser for IOS, Android (soon) and arroyo.db

CheckArroyo.py - run this in CLI\
CheckArroyo_GUI.py - run this for GUI\
lib.py - help functions

First project on github :D

# How it works

## Arroyo.db
Arroyo is where conversations are stored. For every message there is a message_type where 1 is a regular text message. If it is not a text message there is a chance a key is stored in the message_content blob. The blob can be decoded as a raw protocol buffer, as of now I haven't found a good way to decode it with python. The key is 21 in length.

## Contentmanagerdb.db

This is where files are linked to a message. Sometimes there is just one key for one file, however with snaps there are multiple sub keys which is linked to for exapmle the layer file, the media content, a thumbnail file.

## primary.docobjects

Here usernames can be linked to snapchat IDs, it can also show the participants of a conversation.

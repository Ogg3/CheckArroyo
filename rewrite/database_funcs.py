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
import sqlite3
import struct
from lib import *



class database():
    """
    For a given database, do things
    """

    def __init__(self, database):
        self.database = database

    def connect_readonly(self):
        """
        Connect to a database using the uri mode
        """
        try:
            conn = sqlite3.connect('file:'+self.database+'?mode=ro', uri=True)
            return conn
        except Exception as e:
            error("Could not connect to "+str(self.database), False)
            #error(e, False)
            return False

    def execute_querie(self, querie):
        """
        Execute a querie on a database
        If querie results is only one
        """
        result = []

        conn = self.connect_readonly()

        if conn != False:

            curs = conn.cursor()

            curs.execute(querie)

            for i in curs.fetchall():
                if len(i) == 1:
                    result.append(i[0])
                else:
                    result.append(i)

            conn.close()

            return result
        else:
            return False


    def get_freelistpages(self):
        """
        Get the amount of freelistpages in database
        """
        f = open(self.database, 'rb')
        content = f.read()
        freepages = struct.unpack('>L', content[36:40])[0]
        f.close()
        return freepages

    def get_tablenames(self):
        """
        Get all tablenames in database
        """
        tables = self.execute_querie("SELECT name FROM sqlite_master WHERE type='table'")

        if tables != [] and tables != False:
            return tables
        else:
            warning(self.database+" has no tables!")

    def get_rownames(self, table):
        """
        Get all rownames in a table
        """
        rownames = self.execute_querie("PRAGMA table_info({})".format(table))

        if rownames != [] and rownames != False:

            names = []

            for name in rownames:
                names.append(name[1])

            return names
        else:
            warning("{0} table {1} has no rownames".format(self.database, table))

    def get_amount_tables(self):
        """
        Get amount of tables in database
        """
        tables = self.execute_querie("SELECT count(name) FROM sqlite_master WHERE type='table'")

        if tables != [] and tables != False:
            return tables[0]
        else:
            warning(self.database + " has no tables!")

    def get_amount_rows(self, table):
        """
        Get the amount of rows in given table
        """
        rownames = self.execute_querie("PRAGMA table_info({})".format(table))

        if rownames != [] and rownames != False:
            return len(rownames)
        else:
            warning("{0} table {1} has no rows".format(self.database, table))

    def get_row_position(self, table, rowname):
        """
        Get the CID of a giver rowname in a table
        """
        rownames = self.execute_querie("PRAGMA table_info({})".format(table))

        if rownames != [] and rownames != False:

            for name in rownames:
                if name[1] == rowname:
                    return name[0]
        else:
            warning("{0} table {1} has no row names {2}".format(self.database, table, rowname))

    def check_row(self, rowname, tablename):
        """
        Check if database has a rowname in tablename
        """
        if self.get_row_position(tablename, rowname) != "":
            return True
        else:
            return False

    def check_table(self, tablename):
        """
        Check if database has more than 0 rows in tablename
        """
        if self.get_amount_rows(tablename) != 0:
            return True
        else:
            return False

    def get_structure(self):
        """
        Get the structure of a database including comments in the sql statments
        """
        string=""""""
        data = self.execute_querie("SELECT sql FROM sqlite_master WHERE type='table'")
        if data != False:
            for table in self.get_tablenames():
                string += table+'\n'
                string += '\t'+str(self.get_rownames(table))+'\n'
                for i in data:
                    if "--" in i and table == i.split(" ")[2]:
                        string += '\t'+i
                string += '\n'

            return string
        else:
            return None


class store_data():

    def __init__(self, path):
        self.path = path

        # [id] INTEGER PRIMARY KEY,
        conn = sqlite3.connect(self.path)

        conn.execute('''
                      CREATE TABLE IF NOT EXISTS metadata
                      ( [executiontime] TEXT, 
                      [conversations] TEXT, 
                      [messages] TEXT,
                      [textmessages] TEXT,
                      [attachments] TEXT,
                      [failedtextmessages] TEXT,
                      [owner] TEXT)
                      
                      ''')

        conn.execute('''
                          CREATE TABLE IF NOT EXISTS Participants
                          ( [Conversation] TEXT, [username] TEXT, [snapchat_id] TEXT)
                          ''')

        conn.execute('''
                          CREATE TABLE IF NOT EXISTS messages
                          ([client_conversation_id] text, 
                          [sent_by_username] text, 
                          [sent_by_snapchat_id] text, 
                          [content_type] INTEGER,
                          [message] TEXT, 
                          [client_message_id] TEXT,
                          [server_message_id] TEXT, 
                          [attachments_id] INTEGER, 
                          [creation_timestamp] TEXT, 
                          [read_timestamp] TEXT,
                          [message_raw] TEXT, 
                          [message_dict] TEXT)
                          ''')

        conn.execute('''
                          CREATE TABLE IF NOT EXISTS messages_attachments
                          ( [attachments_id] INTEGER, 
                          [filename] TEXT, 
                          [contentmangare_key] TEXT, 
                          [file_type] TEXT)
                          ''')

        conn.execute('''
                          CREATE TABLE IF NOT EXISTS cached_files
                          ( [path_to_file] TEXT, 
                          [conversation_id] TEXT, 
                          [server_message_id] TEXT)
                          ''')

        conn.commit()

    def insert_cached_files(self, path_to_file, conversation_id, server_id):
        """
        Insert the cached files of a chat to data_store.db
        :return:
        """
        try:
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            c.execute("INSERT INTO cached_files VALUES(?, ?, ?)", (str(path_to_file), str(conversation_id), str(
                server_id)))
            conn.commit()
        except Exception as e:
            error(e, True)

    def insert_participants(self, Conversation, username, snapchat_id):
        """
        Insert the participants of a chat to data_store.db
        """
        try:
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            c.execute("INSERT INTO Participants VALUES(?, ?, ?)",
                      (str(Conversation),
                       str(username),
                       str(snapchat_id)))
            conn.commit()
        except Exception as e:
            error(e, True)

    def insert_message(self,
                       Conversation_id,
                       sent_by_username,
                       sent_by_snapchat_id,
                       Content_type,
                       Message_raw,
                       Message_encoded,
                       Message_decoded,
                       Message_id,
                       Server_og_id,
                       Attachments_id,
                       Timestamp_sent,
                       Timestamp_recived,
                       ):
        try:
            conn = sqlite3.connect(self.path)

            conn.execute('INSERT INTO messages VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (str(Conversation_id),
                                                                                             str(sent_by_username),
                                                                                             str(sent_by_snapchat_id),
                                                                                             str(Content_type),
                                                                                             str(Message_decoded),
                                                                                             str(Message_id),
                                                                                             str(Server_og_id),
                                                                                             str(Attachments_id),
                                                                                             str(Timestamp_sent),
                                                                                             str(Timestamp_recived),
                                                                                             str(Message_raw),
                                                                                             str(Message_encoded)))

            conn.commit()
        except Exception as e:
            error(e, True)

    def export_users(self, IO_paths):
        """
        Get all usernames and snapchat ids
        """
        ret = []
        users = []

        conn = sqlite3.connect(self.path)
        qr = "SELECT username, snapchat_id FROM Participants"

        curs = conn.execute(qr)

        # Get usernames
        for res in curs:
            ret.append(res)

        # Get the occurrence of every participant
        for username, snapchat_id in ret:

            # Check if user is in dict
            if (username, snapchat_id) not in users:
                users.append((username, snapchat_id))

        # Write contacts to file file
        with open(IO_paths.report_folder + "contacts.txt", "w") as a:
            for username, snapchat_id in users:
                a.write(username + ", " + snapchat_id + "\n")


class chat():

    def __init__(self, snapchat_version,
                 timefilter,
                 systemtype,
                 paths):
        self.snapchat_version = snapchat_version
        self.timefilter = timefilter
        self.systemtype = systemtype
        self.paths = paths


    def conversation_id(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename":"arroyo.db",
                         "tablename":"conversation",
                         "rowname":"client_conversation_id"
                         }]
            # Hail mary
            else:
                return [{"databasename":"arroyo.db",
                         "tablename":"conversation",
                         "rowname":"client_conversation_id"
                         }]


    def conversation_id_message(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename":"arroyo.db",
                         "tablename":"conversation_message",
                         "rowname":"client_conversation_id"
                         }]
            # Hail mary
            else:
                return [{"databasename":"arroyo.db",
                         "tablename":"conversation_message",
                         "rowname":"client_conversation_id"
                         }]

    def client_message_id(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
              "tablename": "conversation_message",
              "rowname": "client_message_id"
              }]

            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
              "tablename": "conversation_message",
              "rowname": "client_message_id"
              }]

    def server_message_id(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
              "tablename": "conversation_message",
              "rowname": "server_message_id"
              }]
            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
              "tablename": "conversation_message",
              "rowname": "server_message_id"
              }]

    def message_content(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "message_content"
                         }]
            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "message_content"
                         }]

    def creation_timestamp(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "creation_timestamp"
                         }]
            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "creation_timestamp"
                         }]

    def read_timestamp(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """

        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "read_timestamp"
                         }]
            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "read_timestamp"
                         }]

    def content_type(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "content_type"
                         }]
            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "content_type"
                         }]

    def sender_id(self):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "sender_id"
                         }]
            # Hail mary
            else:
                return [{"databasename": "arroyo.db",
                         "tablename": "conversation_message",
                         "rowname": "sender_id"
                         }]

    def attachments_method1(self, key):
        """
        {"Database": "name",
        "tablename": "name",
        "Rowname": "name",
        }
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                return [{"databasename": "contentManagerDb.db",
                         "tablename": "CONTENT_OBJECT_TABLE",
                         "rowname_key": "KEY",
                         "rowname_data": "CONTENT_DEFINITION"
                         }
                        ]
            # Hail mary
            else:
                return [{"databasename": "contentManagerDb.db",
                         "tablename": "CONTENT_OBJECT_TABLE",
                         "rowname": "KEY",
                         "rowname_data": "CONTENT_DEFINITION"
                         },
                        {"databasename": "contentManagerDb.db",
                         "tablename": "CONTENT_OBJECT_TABLE",
                         "rowname_key": "CONTENT_KEY",
                         "rowname_data": "CONTENT_DEFINITION"
                         }
                        ]

    def attachments_method2(self, key):
        """
        return
        True, data if success
        False, None if failed
        }

        T0DO What if table doesnt exist
        T0DO WHat if row doesnt exist
        T0DO What if row has no data
        """
        if self.systemtype == "IOS":
            if self.snapchat_version == 11120:
                qr = """
                    SELECT
                    EXTERNAL_KEY
                    FROM
                    CACHE_FILE_CLAIM
                    WHERE
                    CACHE_KEY == '{}'
                    """.format(key)
                data = self.execute_querie(self.paths["cache_controller.db"], qr)
                if data is not None:
                    return data

            # Hail mary
            else:
                return [{"databasename": "cache_controller.db",
                         "tablename": "CACHE_FILE_CLAIM",
                         "rowname_key": "CACHE_KEY",
                         "rowname_data": "EXTERNAL_KEY"
                         }
                        ]

    def execute_querie(self, path, qr):

        # Cant call my database class here
        try:
            conn = sqlite3.connect(path)
        except Exception as e:
            error("Could not connect to " + str(self.paths["cache_controller.db"]), False)
            return None

        curser = conn.cursor()

        curser.execute(qr)

        result = []

        for data in curser.fetchall():
            if len(data) == 1:
                result.append(data[0])
            else:
                result.append(data)

        conn.close()

        if result != []:
            return result
        else:
            return None


    def get_chat(self):

        if self.timefilter == "" or self.timefilter is None:
            convid=self.conversation_id()
            querie="""
SELECT 
    client_conversation_id, 
    client_message_id, 
    server_message_id, 
    client_resolution_id, 
    local_message_content_id,
    message_content, 
    message_state_type, 
    strftime('%Y-%m-%d %H:%M:%S.', "creation_timestamp"/1000, 'unixepoch') || ("creation_timestamp"%1000), 
    strftime('%Y-%m-%d %H:%M:%S.', "read_timestamp"/1000, 'unixepoch') || ("read_timestamp"%1000), 
    local_message_references, is_saved, is_viewed_by_user, remote_media_count, content_type, 
    content_read_release_policy, released_by_count, sender_id, is_released_by_user, release_state, 
    hidden_from_platform
FROM 
conversation_message"""

        else:
            times = str(self.timefilter).split()
            time1 = times[0]+" "+times[1]
            time2 = times[2]+" "+times[3]

            try:
                dateformat= "%Y-%m-%d %H:%M:%S"
                datetime.datetime.strptime(time1, dateformat)
                datetime.datetime.strptime(time2, dateformat)
            except Exception as e:
                error(time1 + " or "+time2+" is not in correct format", False)
                sys.exit(1)
            querie = """
            SELECT 
            client_conversation_id, 
            client_message_id, 
            server_message_id, 
            client_resolution_id, 
            local_message_content_id,
            message_content, 
            message_state_type, 
            strftime('%Y-%m-%d %H:%M:%S.', "creation_timestamp"/1000, 'unixepoch') || ("creation_timestamp"%1000), 
            strftime('%Y-%m-%d %H:%M:%S.', "read_timestamp"/1000, 'unixepoch') || ("read_timestamp"%1000), 
            local_message_references, 
            is_saved, 
            is_viewed_by_user, 
            remote_media_count, 
            content_type, 
            content_read_release_policy, 
            released_by_count, 
            sender_id, 
            is_released_by_user, 
            release_state, 
            hidden_from_platform
            FROM 
            conversation_message 
            WHERE 
            strftime('%Y-%m-%d %H:%M:%S.', "creation_timestamp"/1000, 'unixepoch') || ("creation_timestamp"%1000) 
            BETWEEN '{0}' AND '{1}' """.format(time1, time2)
        return querie
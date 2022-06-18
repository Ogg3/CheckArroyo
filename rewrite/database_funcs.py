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
            warning("Could not connect to "+str(self.database))
            error(e, True)
            return False

    def execute_querie(self, querie):
        """
        Execute a querie on a database
        If querie results is only one
        """
        try:
            result = []

            conn = self.connect_readonly()

            curs = conn.cursor()

            curs.execute(querie)

            for i in curs.fetchall():
                if len(i) == 1:
                    result.append(i[0])
                else:
                    result.append(i)

            conn.close()

            return result
        except Exception as e:
            error(e, True)


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
        tables = self.execute_querie("SELECT name FROM sqlite_master WHERE type='table'")

        if tables != []:
            return tables
        else:
            warning(self.database+" has no tables!")

    def get_rownames(self, table):

        rownames = self.execute_querie("PRAGMA table_info({})".format(table))

        if rownames != []:

            names = []

            for name in rownames:
                names.append(name[1])

            return names
        else:
            warning("{0} table {1} has no rownames".format(self.database, table))

    def get_amount_tables(self):
        tables = self.execute_querie("SELECT count(name) FROM sqlite_master WHERE type='table'")

        if tables != []:
            return tables[0]
        else:
            warning(self.database + " has no tables!")

    def get_amount_rows(self, table):
        rownames = self.execute_querie("PRAGMA table_info({})".format(table))

        if rownames != []:
            return len(rownames)
        else:
            warning("{0} table {1} has no rows".format(self.database, table))

    def get_row_position(self, table, rowname):
        rownames = self.execute_querie("PRAGMA table_info({})".format(table))

        if rownames != []:

            for name in rownames:
                if name[1] == rowname:
                    return name[0]
        else:
            warning("{0} table {1} has no row names {2}".format(self.database, table, rowname))

    def check_row(self, rowname, tablename):
        if self.get_row_position(tablename, rowname) != "":
            return True
        else:
            return False

    def check_table(self, tablename):
        if self.get_amount_rows(tablename) != 0:
            return True
        else:
            return False


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


class arroyo_queries():

    def __init__(self, snapchat_version, timefilter, systemtype):
        self.snapchat_version = snapchat_version
        self.timefilter = timefilter
        self.systemtype = systemtype

    def conversation_identifier(self):
        return ['client_conversation_id', 'server_conversation_id', 'client_resolution_id']

    def conversation_message(self):
        return ['client_conversation_id', 'conversation_metadata', 'send_state_type', 'creation_timestamp',
        'conversation_version', 'sync_watermark', 'tombstoned_at_timestamp', 'nullable_sync_watermark', 'has_more_messages',
        'source_page', 'last_senders']

    def known_tables_and_rows(self):
        text="""
        required_values
        ['key', 'value']

        send_state
        ['send_state_type']

        message_state
        ['state_type']

        conversation_identifier
        ['client_conversation_id', 'server_conversation_id', 'client_resolution_id']

        conversation ['client_conversation_id', 'conversation_metadata', 'send_state_type', 'creation_timestamp',
        'conversation_version', 'sync_watermark', 'tombstoned_at_timestamp', 'nullable_sync_watermark', 'has_more_messages',
        'source_page', 'last_senders']

        conversation_message ['client_conversation_id', 'client_message_id', 'server_message_id', 'client_resolution_id',
        'local_message_content_id', 'message_content', 'message_state_type', 'creation_timestamp', 'read_timestamp',
        'local_message_references', 'is_saved', 'is_viewed_by_user', 'remote_media_count', 'content_type',
        'content_read_release_policy', 'released_by_count', 'sender_id', 'is_released_by_user', 'release_state',
        'hidden_from_platform']

        local_message_content ['local_message_content_id', 'content', 'local_message_references', 'metrics_message_type',
        'platform_analytics', 'metrics_message_media_type', 'task_queue_id', 'state', 'client_resolution_id',
        'send_timestamp', 'content_type', 'save_policy', 'incidental_attachments', 'missing_last_response']

        flow_orchestration_task ['task_queue_id', 'order_id', 'starting_timestamp_ms', 'retry_count', 'mutation_type',
        'order_grouping', 'order_key', 'operation_attempt_type']

        conversation_local_message_content
        ['client_conversation_id', 'local_message_content_id', 'client_message_id']

        story_local_message_content
        ['story_id', 'local_message_content_id', 'destination_data']

        update_conversation_message ['reference_client_conversation_id', 'reference_client_message_id',
        'client_resolution_id', 'request', 'send_state_type', 'creation_timestamp', 'task_queue_id', 'update_case']

        update_conversation ['reference_client_conversation_id', 'client_resolution_id', 'message_content',
        'send_state_type', 'creation_timestamp', 'conversation_version', 'task_queue_id']

        feed_sync
        ['sentinel', 'token']

        feed_entry ['client_conversation_id', 'version_id', 'last_updated_timestamp', 'display_timestamp', 'message_type',
        'message_state', 'viewed', 'conversation_title', 'conversation_type', 'legacyConversationInfo',
        'legacyMigrationInfo', 'legacyNeedsSync', 'participants', 'lastActors', 'feedItemCreator', 'priority',
        'last_received_chat_id', 'last_viewed_chat_id', 'last_chat_sender', 'unviewed_silent_snaps', 'unviewed_audio_snaps',
        'unviewed_silent_snaps_timestamps', 'unviewed_audio_snaps_timestamps', 'last_sender', 'tombstoned', 'owning_snap',
        'clear_conversation_timestamp_ms', 'last_sent_chat_server_id', 'streak_count', 'streak_expiration_timestamp_ms',
        'streak_version', 'chat_notification_preference', 'game_notification_preference', 'is_friendlink_pending',
        'feed_visibility']

        user_conversation
        ['user_id', 'client_conversation_id', 'conversation_type']

        snap_download_status_info
        ['client_conversation_id', 'client_message_id', 'server_message_id', 'download_status']

        integer_id
        ['id_type', 'id_value']
            """
        return text

    def conversation_message(self):

        if self.timefilter == "" or self.timefilter is None:
            querie="""
SELECT 
    client_conversation_id, client_message_id, server_message_id, client_resolution_id, 
    local_message_content_id,message_content, message_state_type, 
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

    def conversation_message_description(self):
        description = """
        - Is a comment made by me, -- is from the snapchat devs
                    client_conversation_id 
                        - uniq conversation id
                    client_message_id 
                        - id for message
                    server_message_id 
                        - id for message 
                        -- server monotonically increasing id, nullable if pending message
                    client_resolution_id 
                        - unknown 
                        -- Not null. Intentionally not adding this as SQL constraint since we had null data, in the past during internal testing.
                    local_message_content_id integer
                        - unknown 
                        -- nullable if message wasn't created on this device
                    message_content 
                        - message
                    message_state_type 
                        - unknown, there i refrences to this in the message state table (PREPARING, SENDING, FAILED, PENDING_DECRYPTION, COMMITTED)
                    creation_timestamp
                    read_timestamp integer 
                        -- timestamp when the message is first marked read by any participants
                    local_message_references 
                        -- if the message originates from the device we keep local media reference around to have stable local cache ids
                    is_saved 
                        -- bool. set to true iff message_content.metadata().saved_by_size() > 0
                    is_viewed_by_user 
                        -- bool. set to true iff message.content.metadata().read_by() contains current user
                    remote_media_count 
                        -- size of the media reference list message.content.contents().media_reference_lists_size()
                    content_type 
                        -- type of the content as defined in message.content.contents().content_type()
                    content_read_release_policy 
                        -- type of the content read release policy as defined in message.content.release_policy()
                    released_by_count 
                        -- size of message.content.metadata().released_by_size() list
                    sender_id text
                        -- message.content.sender_id()
                    is_released_by_user
                        -- bool. true iff message is released by user,  message.content.metadata().released_by() contains current user id
                    release_state integer
                        -- enum. Release state of the message. Starts optional, not set for conversations that don't send release messages or messages that don't require individual release.
                    hidden_from_platform
                        default 0, -- bool Should hide this message from platform. Read/Release watermark and save state can override this value.

            primary key(client_conversation_id, client_message_id),
            unique (client_conversation_id, server_message_id),

            foreign key(client_conversation_id) references conversation_identifier(client_conversation_id),
            foreign key(message_state_type) references message_state(state_type),
            foreign key(local_message_content_id) references local_message_content(local_message_content_id)
        )
                    """
        return description

class cachecontroller():

    def __init__(self, snapchat_version, timefilter, systemtype):
        self.snapchat_version = snapchat_version
        self.timefilter = timefilter
        self.systemtype = systemtype

    def CACHE_FILE_METADATA(self):
        return ['USER_ID', 'CACHE_KEY', 'STORAGE_TYPE', 'TYPE', 'FILE_SIZE_BYTES', 'TOTAL_DISK_USED_BYTES',
         'KNOWN_CONTENT_LENGTH_BYTES', 'LAST_READ_TIMESTAMP_MILLIS', 'DELETED_TIMESTAMP_MILLIS', 'CHILDREN']

    def CACHE_FILE_CLAIM(self):
        return ['USER_ID', 'CACHE_KEY', 'MEDIA_CONTEXT_TYPE', 'EXTERNAL_KEY', 'IS_AUTHORITATIVE',
     'EXPIRATION_TIMESTAMP_MILLIS', 'DELETED_TIMESTAMP_MILLIS']



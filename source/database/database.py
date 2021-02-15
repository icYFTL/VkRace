import sqlite3
from .utils import dict_factory


class Database:
    def __init__(self):
        self.__conn = sqlite3.connect('database.db')
        self.__conn.row_factory = dict_factory
        self.__cursor = self.__conn.cursor()
        self.__create()

    def __create(self) -> None:
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY unique);')
        self.__cursor.execute(
            'CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY unique, conversation INTEGER, ts INTEGER, ot INTEGER, from_id INTEGER, FOREIGN KEY (conversation) REFERENCES conversations(id));')
        self.__conn.commit()

    def add_conversations(self, id: int) -> None:
        try:
            self.__cursor.execute(f'INSERT INTO conversations (id) VALUES ({id})')
        except sqlite3.IntegrityError:
            pass
        self.__conn.commit()

    def is_conversation_exists(self, id: int) -> bool:
        return bool(self.__cursor.execute('SELECT id FROM conversations WHERE id=' + str(id)).fetchone())

    def get_last_offset(self, id: int) -> int:
        result = self.__cursor.execute(f'SELECT max(ot) as ot FROM messages WHERE conversation={id}').fetchone()
        return result.get('ot', 0) if result.get('ot', 0) else 0

    def add_messages(self, messages: tuple) -> None:
        offset = messages[1] - 200
        for message in messages[0]['items']:
            try:
                self.__cursor.execute(
                    'INSERT INTO messages (id, conversation, ts, ot, from_id) VALUES ({}, {}, {}, {}, {});'.format(
                        message['id'],
                        message['peer_id'],
                        message['date'],
                        offset,
                        message['from_id']
                    ))
            except sqlite3.IntegrityError:
                pass
            finally:
                offset += 1
        self.__conn.commit()

    def get_min_ts(self) -> int:
        return self.__cursor.execute('SELECT min(ts) as ts FROM messages;').fetchone()['ts']

    def get_messages_in(self, ts_left, ts_right) -> list:
        return self.__cursor.execute(f'SELECT * FROM messages WHERE ts > {ts_left} AND ts < {ts_right}').fetchall()

    def get_total_messages(self):
        return self.__cursor.execute('SELECT count(1) as result FROM messages;').fetchone()['result']

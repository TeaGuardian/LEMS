from json import dump, load
from os.path import isfile
from threading import Thread
from base64 import b64encode, b64decode
from datetime import datetime
import hashlib
import gspread
import requests
import sqlite3
from oauth2client.service_account import ServiceAccountCredentials
scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]


def distance(a, b):
    n, m = len(a), len(b)
    if n > m:
        a, b = b, a
        n, m = m, n
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)
    return current_row[n]


def encrypt_str(message, key):
    encoded_bytes = message.encode('utf-8')
    key_bytes = key.encode('utf-8')
    cipher_bytes = bytearray()
    for i in range(len(encoded_bytes)):
        key_index = i % len(key_bytes)
        xor_val = encoded_bytes[i] ^ key_bytes[key_index]
        cipher_bytes.append(xor_val)
    cipher_b64 = b64encode(cipher_bytes)
    return cipher_b64.decode('utf-8')


def decrypt_str(encryption, key):
    cipher_b64 = encryption
    cipher_bytes = b64decode(cipher_b64)
    key_bytes = key.encode('utf-8')
    decoded_bytes = bytearray()
    for i in range(len(cipher_bytes)):
        key_index = i % len(key_bytes)
        xor_val = cipher_bytes[i] ^ key_bytes[key_index]
        decoded_bytes.append(xor_val)
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str


class Settings:
    def __init__(self):
        self.path = "data/user_data.json"
        self.data = {"local-id": 0, "hash": None, "key": "", "name": "", "mode": 0, "last": 1, "xy": (9 * 34, 16 * 34),
                     "ts": 28, "acive-rubi": False, "acive-in": False, "acive-down": False, "acive-re": False,
                     "acive-he": False, "acive-ca": False, "acive-rz": False, "inverse": -1}

    def read_init(self):
        if isfile(self.path):
            with open(self.path, "r") as read_file:
                self.data = load(read_file)

    def is_normal(self):
        if None in self.data.values():
            return False
        return True

    def set(self, key, val):
        self.data[key] = val

    def get(self, key):
        return self.data[key]

    def save(self):
        with open(self.path, "w+") as write_file:
            dump(self.data, write_file)


class EthernetPort:
    def __init__(self, json_key: str | dict):
        """json_key - file name or dictionary file data"""
        if type(json_key) is str:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)
        else:
            self.creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key)
        self.users, self.chat = None, None
        self.usernames, self.user = [], []

    def ethernet(self):
        try:
            d = requests.get('https://yandex.ru/').status_code
        except IOError:
            return False
        return True

    def try_init(self):
        if self.users is not None:
            return True, ""
        if self.ethernet():
            try:
                client = gspread.authorize(self.creds)
                self.users, self.chat = client.open("chat").worksheet("users"), client.open("chat").worksheet("chat")
                return True, ""
            except Exception as e:
                return False, e
        return False, "нет связи"

    def as_t_i(self, call, f):
        call(self.try_init())

    def async_try_int(self, call):
        thr = Thread(target=self.as_t_i, args=(call, 1))
        thr.start()

    def find_user(self, user):
        i, self.usernames = 1, []
        while i < 100:
            rez = self.users.row_values(i)
            if len(rez) == 0:
                return False, []
            self.usernames.append(rez[0])
            if rez[0] == user:
                return True, rez
            i += 1
        print("source/manager.EthernetPort.find_user HOW?!")
        return False, []

    def is_exist(self, user):
        if not len(self.user):
            rez = self.find_user(user)
            if rez[0]:
                self.user = rez[1]
                return True
            return False
        else:
            if self.user[0] not in self.usernames:
                return False
            return True

    def login(self, user, pas_hash):
        if not self.ethernet():
            return False, "статус: нет связи"
        if self.is_exist(user):
            if pas_hash == self.user[1]:
                return True, "статус: запуск.."
            else:
                print(self.user)
                return False, "статус: ошибка пароля"
        else:
            if not any(map(lambda g: distance(g, user) < 3, self.usernames)):
                self.users.insert_row([user, pas_hash], 1)
                return True, "статус: создан пользователь.."
            else:
                return False, "статус: похожее имя уже существует"

    def as_h(self, c, u, p):
        c(self.login(u, p))

    def async_login(self, call, user, pas_hash):
        thr = Thread(target=self.as_h, args=(call, user, pas_hash))
        thr.start()

    def send_message(self, mes, typee, owner, key):
        m = hashlib.sha256()
        m.update(key.encode())
        date = datetime.now().strftime("%d.%m-%H:%M")
        mes = encrypt_str(mes, key)
        self.chat.append_row([mes, typee, owner, date, m.hexdigest()])

    def get_message(self, n):
        try:
            return self.chat.row_values(n)
        except Exception as e:
            return []


class DataBaseCore:
    """id, mes, type, owner, date"""
    steck, buf = [], []

    def __init__(self, ethernet: EthernetPort, settings: Settings):
        self.current_table, self.e_port, self.settings = None, ethernet, settings

    def switch_table(self, table: str):
        m = hashlib.sha256()
        m.update(table.encode())
        con = sqlite3.connect("data/chat-data.db")
        cur = con.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS chat{m.hexdigest()}(id INTEGER, mes TEXT, type TEXT, owner TEXT, date TEXT);""")
        con.commit()
        con.close()
        if self.current_table is not None and self.current_table != m.hexdigest():
            self.settings.set("last", 1)
        self.current_table = m.hexdigest()

    def download_chat(self, ns):
        ni, ru = ns, True
        while ru:
            rez = self.e_port.get_message(ni)
            if len(rez) == 0:
                return False
            elif rez[4] == self.current_table:
                mes = decrypt_str(rez[0], self.settings.get("key"))
                self.write(ni, mes, rez[1], rez[2], rez[3])
                self.settings.set("last", ni)
            ni += 1

    def task_download_chat(self, ns):
        thr = Thread(target=self.download_chat, args=[ns])
        thr.start()
        self.update_buffer(ns)

    def exist(self, idd):
        con = sqlite3.connect("data/chat-data.db")
        cur = con.cursor()
        return len(cur.execute(f"""SELECT * FROM chat{self.current_table} WHERE id == {idd}""").fetchall()) > 0

    def write(self, idd, mes, typee, owner, date):
        if self.exist(idd):
            return 1
        con = sqlite3.connect("data/chat-data.db")
        cur = con.cursor()
        com = f"""INSERT INTO chat{self.current_table}(id, mes, type, owner, date) VALUES({idd}, '{mes}', '{typee}', '{owner}', '{date}');"""
        cur.execute(com)
        con.commit()
        con.close()

    def update_buffer(self, N):
        con = sqlite3.connect("data/chat-data.db")
        cur = con.cursor()
        na = "chat" + self.current_table
        rez = cur.execute(f"""SELECT * FROM {na} WHERE id <= {N} ORDER BY id DESC LIMIT 10""").fetchall()
        rez2 = cur.execute(f"""SELECT * FROM {na} WHERE id > {N} ORDER BY id DESC LIMIT 10""").fetchall()
        self.steck = list(rez[::-1] + rez2[::-1])

    def get_buffer(self):
        return self.steck


"""
key = 'my secret key'
message = 'Пример сообщения на русском языке'
encryption = encrypt_str(key, message)
print(encryption)

decryption = decrypt_str(encryption, key)
print(decryption)
"""

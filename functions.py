import random
import sqlite3
from settings import *
import telebot

def db_update(message, bot):
    if message.from_user.username != None and message.from_user.username != '':
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS users(teleid INTEGER PRIMARY KEY, username TEXT)')
        cur.execute(
            'CREATE TABLE IF NOT EXISTS blackjack(pl1 INTEGER, pl2 INTEGER, cards TEXT, pl1_score INTEGER, pl2_score INTEGER, pl1_status INTEGER, pl2_status INTEGER)')
        cur.execute("SELECT teleid FROM users WHERE teleid = ?", (message.from_user.id,))
        if cur.fetchone():
            cur.execute("UPDATE users SET username = ? WHERE teleid = ?",
                        (message.from_user.username, message.from_user.id))
        else:
            cur.execute("INSERT INTO users (teleid, username) VALUES (?, ?)",
                        (message.from_user.id, message.from_user.username))
        conn.commit()
        cur.close()
        conn.close()
    else:
        bot.send_message(message.from_user.id, 'Для использования этого бота у вас обязан быть @Username!')

def db_add(query, parametrs):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute(
        query,
        parametrs
    )
    conn.commit()
    cur.close()
    conn.close()

def get_teleid_by_username(username):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()

        cur.execute('SELECT teleid FROM users WHERE username = ?', (username,))
        result = cur.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            return None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None


def return_score(game_id):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        cur.execute("SELECT pl1_score, pl2_score FROM blackjack WHERE rowid = ?", (game_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0], result[1]
        else:
            return None, None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None, None

def get_players_by_rowid(rowid):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        cur.execute("SELECT pl1, pl2 FROM blackjack WHERE rowid = ?", (rowid,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            id1 = result[0]
            id2 = result[1]
            return id1, id2
        else:
            return None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None

import json

def save_cards_to_db(game_id, cards_list):
    cards_json = json.dumps(cards_list)
    db_add("UPDATE blackjack SET cards = ? WHERE rowid = ?", (cards_json, game_id))

def get_cards_from_db(game_id):
    conn = sqlite3.connect(database_name)
    cur = conn.cursor()
    cur.execute("SELECT cards FROM blackjack WHERE rowid = ?", (game_id,))
    result = cur.fetchone()
    conn.close()
    if result and result[0]:
        return json.loads(result[0])
    return []

def get_players_status(game_id):
    try:
        with sqlite3.connect(database_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT pl1_status, pl2_status FROM blackjack WHERE rowid = ?", (game_id,))
            result = cur.fetchone()
            if result:
                return result[0], result[1]
            else:
                return None, None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None, None

def get_players_ids(game_id):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        cur.execute("SELECT pl1, pl2 FROM blackjack WHERE rowid = ?", (game_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0], result[1]
        return None, None
    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None, None
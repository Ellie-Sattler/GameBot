from telebot import *
from telebot.types import *
import sqlite3
from settings import *
from functions import *

def bj_help(message, bot):
    rules = (
        "<b>Правила игры в Блэкджек</b>\n\n"
        "🎲 <b>Цель игры:</b> Набрать комбинацию карт, максимально близкую к 21 очку, но не превышающую его.\n\n"
        "🃏 <b>Как играть:</b>\n"
        "1. Вы и ваш соперник получаете по две карты.\n"
        "2. Вы видите свои карты и текущий счёт.\n"
        "3. Вы можете:\n"
        "   - <b>Взять ещё</b>: Получить дополнительную карту, чтобы увеличить счёт.\n"
        "   - <b>Остановиться</b>: Завершить свой ход, сохранив текущий счёт.\n"
        "4. После того как оба игрока остановятся, определяется победитель.\n\n"
        "📊 <b>Очки карт:</b>\n"
        "- Числовые карты (2–10): номинал карты (например, 5♠ = 5 очков).\n"
        "- Валет (J), Дама (Q), Король (K): 10 очков.\n"
        "- Туз (A): 11 очков.\n\n"
        "🏆 <b>Правила победы:</b>\n"
        "- Побеждает игрок, чей счёт ближе к 21, но не превышает его.\n"
        "- Если счёт > 21, игрок проигрывает (перебор).\n"
        "- Если оба игрока перебрали (> 21), побеждает тот, у кого счёт меньше.\n"
        "- При равных счётах объявляется ничья.\n\n"
        "🔥 <b>Начало игры:</b> Используйте команду /create_bj и укажите @username соперника, который уже запускал бота.\n\n"
        "Удачи в игре! 🃍"
    )
    bot.send_message(message.chat.id, rules)

def create_bj(message, bot):
    bot.send_message(message.chat.id, 'Напишите username игрока, с которым хотите поиграть. Пример: <code>@Ellie_Sattler</code>\nИгрок <b>обязательно</b> должен был запустить бота раньше!')
    bot.register_next_step_handler(message, lambda msg: user_check(msg, bot))

def card_random(cards_dealt):
    suit = suits[random.randint(0,3)]
    value = values[random.randint(0, len(values)-1)]
    card = value+suit
    while card in cards_dealt:
        suit = suits[random.randint(0, 3)]
        value = values[random.randint(0, len(values) - 1)]
        card = value + suit

    if value in ['J', 'Q', 'K']:
        score = 10
    elif value == 'A':
        score = 11
    else:
        score = int(value)
    return score, card

def user_check(message, bot):
    username = message.text[1:]
    teleid = get_teleid_by_username(username)
    if teleid:
        try:
            with open('games.txt', 'r') as file:
                numgame = int(file.read())
            numgame+=1
            with open('games.txt', 'w') as file:
                file.write(str(numgame))
            mk = InlineKeyboardMarkup()
            btn1 = InlineKeyboardButton(f'Принять', callback_data=f'bj{numgame}')
            mk.row(btn1)
            bot.send_message(teleid, f'Пользователь @{message.from_user.username} отправил вам запрос на игру в BlackJack', reply_markup=mk)
            bot.send_message(message.from_user.id, 'Ожидайте ответа от пользователя')
            db_add("INSERT INTO blackjack (pl1, pl2, cards, pl1_score, pl2_score, pl1_status, pl2_status) VALUES (?, ?, ?, ?, ?, ?, ?)", (message.from_user.id, teleid, None, 0, 0, 0, 0))
        except Exception as e:
            bot.send_message(message.from_user.id, 'Ошибка при отправке сообщения пользователю')
            for i in admins:
                bot.send_message(i, f'Ошибка у пользователя: @{message.from_user.username}, <b>{e}</b>')
    else:
        bot.send_message(message.from_user.id, 'Пользователь не зарегистрирован')


def get_winner(game_id):
    try:
        conn = sqlite3.connect(database_name)
        cur = conn.cursor()
        cur.execute("SELECT pl1, pl2, pl1_score, pl2_score FROM blackjack WHERE rowid = ?", (game_id,))
        result = cur.fetchone()
        if not result:
            cur.close()
            conn.close()
            return None, None

        pl1_id, pl2_id, pl1_score, pl2_score = result

        cur.execute("SELECT username FROM users WHERE teleid = ?", (pl1_id,))
        pl1_username_result = cur.fetchone()
        pl1_username = pl1_username_result[0] if pl1_username_result else None
        cur.execute("SELECT username FROM users WHERE teleid = ?", (pl2_id,))
        pl2_username_result = cur.fetchone()
        pl2_username = pl2_username_result[0] if pl2_username_result else None
        cur.close()
        conn.close()

        if pl1_score > 21 and pl2_score > 21:
            if pl1_score < pl2_score:
                return pl1_id, pl1_username
            elif pl2_score < pl1_score:
                return pl2_id, pl2_username
            else:
                return None, None
        elif pl1_score > 21:
            return pl2_id, pl2_username
        elif pl2_score > 21:
            return pl1_id, pl1_username
        elif pl1_score > pl2_score:
            return pl1_id, pl1_username
        elif pl2_score > pl1_score:
            return pl2_id, pl2_username
        else:
            return None, None

    except sqlite3.Error as e:
        print(f"Ошибка базы данных: {e}")
        return None, None
import sqlite3
from pyexpat.errors import messages
from random import choice

from telebot.types import *
from settings import *
from functions import *
from blackjack import *
from knb import *

bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
bot.send_message(MY_ID, 'Я тут')


@bot.message_handler(commands=['start'])
def start(message):
    welcome = (
        "<b>Добро пожаловать в Игрового бота! 🎲</b>\n\n"
        "Готовы испытать удачу и мастерство? 🃏 Здесь вы можете сразиться с друзьями в захватывающей игре в блэкджек!\n\n"
        "✨ <b>Что можно сделать:</b>\n"
        "- <b>/create_bj</b>: Начать новую игру, указав @username соперника.\n"
        "- <b>/bj_help</b>: Узнать правила игры.\n"
        "- <b>/id</b>: Посмотреть ваш Telegram ID и ID чата.\n\n"
        "⚡ <b>Важно:</b> Убедитесь, что у вас есть @Username, и ваш соперник уже запускал бота.\n\n"
        "Погнали выигрывать! 🏆 Напишите /create_bj, чтобы начать, или /bj_help, чтобы узнать правила!"
    )
    bot.send_message(message.chat.id, welcome)
    db_update(message, bot)


@bot.message_handler(commands=['id'])
def chat_id(message):
    bot.send_message(message.chat.id, f'Твой id: <code>{message.from_user.id}</code>\nId чата: <code>{message.chat.id}</code>')
    db_update(message, bot)

bot.message_handler(commands=['create_bj'])(lambda message: create_bj(message, bot))
bot.message_handler(commands=['bj_help'])(lambda message: bj_help(message, bot))
bot.message_handler(commands=['knb'])(lambda message: knb(message, bot))

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data.startswith('bj'):
        game_id = call.data[2:]
        card_dealt = []
        pl1_score1, pl1_card1 = card_random(card_dealt)
        card_dealt.append(pl1_card1)
        pl1_score2, pl1_card2 = card_random(card_dealt)
        card_dealt.append(pl1_card2)
        pl2_score1, pl2_card1 = card_random(card_dealt)
        card_dealt.append(pl2_card1)
        pl2_score2, pl2_card2 = card_random(card_dealt)
        card_dealt.append(pl2_card2)

        save_cards_to_db(game_id, card_dealt)

        pl1_score = pl1_score1+pl1_score2
        pl2_score = pl2_score1+pl2_score2

        pl1_id, pl2_id = get_players_by_rowid(game_id)

        db_add("UPDATE blackjack SET pl1_score = ?, pl2_score = ? WHERE rowid = ?", (pl1_score, pl2_score, game_id))

        pl1_card1_photo = open(f'images/{pl1_card1}.jpg', 'rb')
        pl1_card2_photo = open(f'images/{pl1_card2}.jpg', 'rb')
        pl2_card1_photo = open(f'images/{pl2_card1}.jpg', 'rb')
        pl2_card2_photo = open(f'images/{pl2_card2}.jpg', 'rb')

        bot.send_photo(pl1_id, pl1_card1_photo)
        bot.send_photo(pl1_id, pl1_card2_photo)
        bot.send_photo(pl2_id, pl2_card1_photo)
        bot.send_photo(pl2_id, pl2_card2_photo)
        markup1 = InlineKeyboardMarkup()
        markup2 = InlineKeyboardMarkup()

        btn1 = InlineKeyboardButton('Взять еще', callback_data=f'TM_{pl1_id}_{game_id}_pl1')
        btn2 = InlineKeyboardButton('Взять еще', callback_data=f'TM_{pl2_id}_{game_id}_pl2')

        btn3 = InlineKeyboardButton('Остановиться', callback_data=f'Stop_{pl1_id}_{game_id}_pl1')
        btn4 = InlineKeyboardButton('Остановиться', callback_data=f'Stop_{pl2_id}_{game_id}_pl2')

        markup1.row(btn1)
        markup1.row(btn3)

        markup2.row(btn2)
        markup2.row(btn4)

        bot.send_message(pl1_id, f'Ваш счёт: {pl1_score}\nЖелаете взять ещё или остановиться?', reply_markup=markup1)
        bot.send_message(pl2_id, f'Ваш счёт: {pl2_score}\nЖелаете взять ещё или остановиться?', reply_markup=markup2)
        keyboard = InlineKeyboardMarkup()
        b = InlineKeyboardButton('Игра уже сыграна!', callback_data='TRY')
        keyboard.row(b)
        bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=keyboard)
    elif call.data == 'TRY':
        bot.answer_callback_query(call.id, f"Игра уже сыграна!")


    elif call.data.startswith('TM'):
        callback = call.data.split('_')
        game_id = callback[2]
        pl_id = callback[1]
        pl_num = callback[3]
        card_dealt = get_cards_from_db(game_id)
        score, card = card_random(card_dealt)
        card_dealt.append(card)
        save_cards_to_db(game_id, card_dealt)
        pl1_score, pl2_score = return_score(game_id)
        if pl_num == 'pl1':
            pl1_score += score
        elif pl_num == 'pl2':
            pl2_score += score
        db_add("UPDATE blackjack SET pl1_score = ?, pl2_score = ? WHERE rowid = ?", (pl1_score, pl2_score, game_id))
        card_photo = open(f'images/{card}.jpg', 'rb')
        bot.send_photo(pl_id, card_photo)
        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton('Взять еще', callback_data=f'TM_{pl_id}_{game_id}_{pl_num}')
        btn3 = InlineKeyboardButton('Остановиться', callback_data=f'Stop_{pl_id}_{game_id}_{pl_num}')
        markup.row(btn1)
        markup.row(btn3)
        if pl_num == 'pl1':
            bot.send_message(pl_id, f'У вас теперь: {pl1_score}', reply_markup=markup)
        elif pl_num == 'pl2':
            bot.send_message(pl_id, f'У вас теперь: {pl2_score}', reply_markup=markup)
    elif call.data.startswith('Stop'):
        callback = call.data.split('_')
        game_id = callback[2]
        pl_id = callback[1]
        pl_num = callback[3]
        if pl_num == 'pl1':
            db_add("UPDATE blackjack SET pl1_status = ? WHERE rowid = ?", (1, game_id))
        elif pl_num == 'pl2':
            db_add("UPDATE blackjack SET pl2_status = ? WHERE rowid = ?", (1, game_id))
        bot.send_message(pl_id, 'Ожидайте соперника...')
        pl1_status, pl2_status = get_players_status(game_id)
        if pl1_status == pl2_status and int(pl1_status) == 1:
            win_id, win_username = get_winner(game_id)
            pl1_id, pl2_id = get_players_ids(game_id)
            pl1_score, pl2_score = return_score(game_id)
            if win_id == None:
                bot.send_message(pl1_id, f'У вас ничья. \nВаши очки:<b> {pl1_score}</b>\nОчки противника: <b>{pl2_score}</b>')
                bot.send_message(pl2_id, f'У вас ничья. \nВаши очки:<b> {pl2_score}</b>\nОчки противника: <b>{pl1_score}</b>')
            elif win_id == pl1_id:
                bot.send_message(pl1_id,
                                 f'Поздравляю! Вы победили. \nВаши очки:<b> {pl1_score}</b>\nОчки противника: <b>{pl2_score}</b>')
                bot.send_message(pl2_id,
                                 f'К сожалению, Вы проиграли. \nВаши очки:<b> {pl2_score}</b>\nОчки противника: <b>{pl1_score}</b>\n\nПобедитель: @{win_username}')
            elif win_id == pl2_id:
                bot.send_message(pl1_id,
                                 f'К сожалению, Вы проиграли. \nВаши очки:<b> {pl1_score}</b>\nОчки противника: <b>{pl2_score}</b>\n\nПобедитель: @{win_username}')
                bot.send_message(pl2_id,
                                 f'Поздравляю! Вы победили. \nВаши очки:<b> {pl2_score}</b>\nОчки противника:<b> {pl1_score}</b>')
    elif call.data.startswith('g_'):
        bot_choice = choice(['k', 'n', 'b'])
        if (call.data == 'g_k' and bot_choice == 'k') or (call.data == 'g_n' and bot_choice == 'n') or (call.data == 'g_b' and bot_choice == 'b'):
            bot.send_message(call.message.chat.id,f'Ничья. {knb_result(call.data, bot_choice)}')
        elif (call.data == 'g_k' and bot_choice == 'b') or (call.data == 'g_n' and bot_choice == 'k') or (call.data == 'g_b' and bot_choice == 'n'):
            bot.send_message(call.message.chat.id,f'К сожалению, вы проиграли. {knb_result(call.data, bot_choice)}')
        elif (call.data == 'g_k' and bot_choice == 'n') or (call.data == 'g_n' and bot_choice == 'b') or (call.data == 'g_b' and bot_choice == 'k'):
            bot.send_message(call.message.chat.id,f'Поздравляю с победой. {knb_result(call.data, bot_choice)}')


        #bot.send_message(call.message.chat.id, f'{call.data}|{bot_choice}')
bot.polling()
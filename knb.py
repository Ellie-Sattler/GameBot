from telebot import *
from telebot.types import *
import sqlite3
from settings import *
from functions import *
def knb(message, bot):
    kb = InlineKeyboardMarkup()
    k = InlineKeyboardButton('👊',callback_data='g_k')
    n = InlineKeyboardButton('✌️',callback_data='g_n')
    b = InlineKeyboardButton('✋',callback_data='g_b')
    kb.row(k, n, b)
    bot.send_message(message.from_user.id, 'Выберите Камень/ножницы/бумага', reply_markup=kb)
def knb_result(user_choice, bot_choice):
    text = 'Вы выбрали <code>'
    if user_choice == 'g_k':
        text += 'камень'
    elif user_choice == 'g_n':
        text += 'ножницы'
    elif user_choice == 'g_b':
        text += 'бумагу'
    text += '</code>, а бот выбрал <code>'
    if bot_choice == 'k':
        text += 'камень</code>.'
    elif bot_choice == 'n':
        text += 'ножницы</code>.'
    elif bot_choice == 'b':
        text += 'бумагу</code>.'
    return text
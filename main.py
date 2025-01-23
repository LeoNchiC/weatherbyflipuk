import telebot
import requests
import os
from googletrans import Translator
from datetime import datetime
from babel.dates import format_date, format_time
from dotenv import load_dotenv
from telebot.types import KeyboardButton

load_dotenv(dotenv_path='tokens.env')

API_TOKEN = os.getenv('TEST')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

bot = telebot.TeleBot(API_TOKEN)
translator = Translator()

selected_city = ""
user_steps = {}

city_translation = {
    "Надвор’е ў Мінску": ("Minsk", "Мінску"),
    "Надвор’е ў Брэсце": ("Brest", "Брэсце"),
    "Надвор’е ў Гомеле": ("Gomel", "Гомеле"),
    "Надвор’е ў Гродно": ("Grodno", "Гродно"),
    "Надвор’е ў Віцебске": ("Vitebsk", "Віцебске"),
    "Надвор’е ў Магілёве": ("Mogilev", "Магілёве")
}

def get_weather(city):
    try:
        url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return "Памылка пры атрыманні дадзеных аб надвор'і."

        temp = data['current']['temp_c']
        weather = data['current']['condition']['text']
        wind = data['current']['wind_kph']

        try:
            translated = translator.translate(weather, src='ru', dest='be')
            translated_text = translated.text
        except Exception:
            translated_text = weather

        now = datetime.now()
        formatted_date = format_date(now, locale='be')
        formatted_time = format_time(now, locale='be')

        return f"📆Cёння: {formatted_date}\n⏰Час: {formatted_time}\n\n🌥Надвор'е ў {city}🌥\n🌡Тэмпература: {temp}°C\n✨Стан: {translated_text}\n🌬Вецер: {wind} км/г"
    except requests.exceptions.RequestException as e:
        return f"Немагчыма атрымаць дадзеныя: {e}"
    except Exception as e:
        return f"Нечаканая памылка: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    country_button = KeyboardButton('🌍Выберыце краіну🌍')
    settings = KeyboardButton('⚙️Наладкі⚙️')
    markup.add(country_button, settings)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб выбраць краіну.",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '⚙️Наладкі⚙️')
def settings(message):
    bot.reply_to(message, 'У будучынні')


@bot.message_handler(func=lambda message: message.text == '🌍Выберыце краіну🌍')
def choose_country(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    belarus_button = KeyboardButton('Беларусь🇧🇾')
    back_button = KeyboardButton('Вярнуцца⬅️')
    markup.add(belarus_button, back_button)
    bot.send_message(message.chat.id, "Вылучыце краіну:", reply_markup=markup)



@bot.message_handler(func=lambda message: message.text == 'Беларусь🇧🇾')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    minsk = KeyboardButton('Надвор’е ў Мінску')
    brest = KeyboardButton('Надвор’е ў Брэсце')
    gomel = KeyboardButton('Надвор’е ў Гомеле')
    grodno = KeyboardButton('Надвор’е ў Гродно')
    vitebsk = KeyboardButton('Надвор’е ў Віцебске')
    mogilev = KeyboardButton('Надвор’е ў Магілёве')
    back_button = KeyboardButton('Вярнуцца⬅️')
    markup.add(minsk, brest, gomel, grodno, vitebsk, mogilev, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Мінску.",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Вярнуцца⬅️')
def go_back(message):
    step = user_steps.get(message.chat.id, 'start')
    if step == 'choose_city':
        choose_country(message)  
    elif step == 'choose_country':
        send_welcome(message) 
    else:
        send_welcome(message) 

@bot.message_handler(func=lambda message: message.text in city_translation)
def send_weather(message):
    global selected_city

    selected_city, city_belarusian = city_translation[message.text]
    weather_info = get_weather(selected_city)

    bot.reply_to(message, weather_info.replace(f"🌥Надвор'е ў {selected_city}🌥", f"🌥Надвор'е ў {city_belarusian}🌥"))

bot.polling()

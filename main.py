import telebot
import requests
import os
from googletrans import Translator
from datetime import datetime
from babel.dates import format_date, format_time
from dotenv import load_dotenv
from telebot.types import KeyboardButton

load_dotenv(dotenv_path='tokens.env')

API_TOKEN = os.getenv('API_TOKEN')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

bot = telebot.TeleBot(API_TOKEN)
translator = Translator()

selected_city = ""
user_steps = {}

city_translation = {
    "РќР°РґРІРѕСЂвЂ™Рµ Сћ РњС–РЅСЃРєСѓ": ("Minsk", "РњС–РЅСЃРєСѓ"),
    "РќР°РґРІРѕСЂвЂ™Рµ Сћ Р‘СЂСЌСЃС†Рµ": ("Brest", "Р‘СЂСЌСЃС†Рµ"),
    "РќР°РґРІРѕСЂвЂ™Рµ Сћ Р“РѕРјРµР»Рµ": ("Gomel", "Р“РѕРјРµР»Рµ"),
    "РќР°РґРІРѕСЂвЂ™Рµ Сћ Р“СЂРѕРґРЅРѕ": ("Grodno", "Р“СЂРѕРґРЅРѕ"),
    "РќР°РґРІРѕСЂвЂ™Рµ Сћ Р’С–С†РµР±СЃРєРµ": ("Vitebsk", "Р’С–С†РµР±СЃРєРµ"),
    "РќР°РґРІРѕСЂвЂ™Рµ Сћ РњР°РіС–Р»С‘РІРµ": ("Mogilev", "РњР°РіС–Р»С‘РІРµ")
}

def get_weather(city):
    try:
        url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}&lang=ru'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return "РџР°РјС‹Р»РєР° РїСЂС‹ Р°С‚СЂС‹РјР°РЅРЅС– РґР°РґР·РµРЅС‹С… Р°Р± РЅР°РґРІРѕСЂ'С–."

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

        return f"рџ“†CС‘РЅРЅСЏ: {formatted_date}\nвЏ°Р§Р°СЃ: {formatted_time}\n\nрџЊҐРќР°РґРІРѕСЂ'Рµ Сћ {city}рџЊҐ\nрџЊЎРўСЌРјРїРµСЂР°С‚СѓСЂР°: {temp}В°C\nвњЁРЎС‚Р°РЅ: {translated_text}\nрџЊ¬Р’РµС†РµСЂ: {wind} РєРј/Рі"
    except requests.exceptions.RequestException as e:
        return f"РќРµРјР°РіС‡С‹РјР° Р°С‚СЂС‹РјР°С†СЊ РґР°РґР·РµРЅС‹СЏ: {e}"
    except Exception as e:
        return f"РќРµС‡Р°РєР°РЅР°СЏ РїР°РјС‹Р»РєР°: {e}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    country_button = KeyboardButton('рџЊЌР’С‹Р±РµСЂС‹С†Рµ РєСЂР°С–РЅСѓрџЊЌ')
    settings = KeyboardButton('вљ™пёЏРќР°Р»Р°РґРєС–вљ™пёЏ')
    markup.add(country_button, settings)
    bot.send_message(message.chat.id, "Р’С–С‚Р°СЋ! РќР°С†С–СЃРЅС–С†Рµ РєРЅРѕРїРєСѓ, РєР°Р± РІС‹Р±СЂР°С†СЊ РєСЂР°С–РЅСѓ.",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'вљ™пёЏРќР°Р»Р°РґРєС–вљ™пёЏ')
def settings(message):
    bot.reply_to(message, 'РЈ Р±СѓРґСѓС‡С‹РЅРЅС–')


@bot.message_handler(func=lambda message: message.text == 'рџЊЌР’С‹Р±РµСЂС‹С†Рµ РєСЂР°С–РЅСѓрџЊЌ')
def choose_country(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    belarus_button = KeyboardButton('Р‘РµР»Р°СЂСѓСЃСЊрџ‡§рџ‡ѕ')
    back_button = KeyboardButton('Р’СЏСЂРЅСѓС†С†Р°в¬…пёЏ')
    markup.add(belarus_button, back_button)
    bot.send_message(message.chat.id, "Р’С‹Р»СѓС‡С‹С†Рµ РєСЂР°С–РЅСѓ:", reply_markup=markup)



@bot.message_handler(func=lambda message: message.text == 'Р‘РµР»Р°СЂСѓСЃСЊрџ‡§рџ‡ѕ')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    minsk = KeyboardButton('РќР°РґРІРѕСЂвЂ™Рµ Сћ РњС–РЅСЃРєСѓ')
    brest = KeyboardButton('РќР°РґРІРѕСЂвЂ™Рµ Сћ Р‘СЂСЌСЃС†Рµ')
    gomel = KeyboardButton('РќР°РґРІРѕСЂвЂ™Рµ Сћ Р“РѕРјРµР»Рµ')
    grodno = KeyboardButton('РќР°РґРІРѕСЂвЂ™Рµ Сћ Р“СЂРѕРґРЅРѕ')
    vitebsk = KeyboardButton('РќР°РґРІРѕСЂвЂ™Рµ Сћ Р’С–С†РµР±СЃРєРµ')
    mogilev = KeyboardButton('РќР°РґРІРѕСЂвЂ™Рµ Сћ РњР°РіС–Р»С‘РІРµ')
    back_button = KeyboardButton('Р’СЏСЂРЅСѓС†С†Р°в¬…пёЏ')
    markup.add(minsk, brest, gomel, grodno, vitebsk, mogilev, back_button)
    bot.send_message(message.chat.id, "Р’С–С‚Р°СЋ! РќР°С†С–СЃРЅС–С†Рµ РєРЅРѕРїРєСѓ, РєР°Р± Р°С‚СЂС‹РјР°С†СЊ РЅР°РґРІРѕСЂ'Рµ Сћ РњС–РЅСЃРєСѓ.",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Р’СЏСЂРЅСѓС†С†Р°в¬…пёЏ')
def go_back(message):
    step = user_steps.get(message.chat.id, 'start')
    if step == 'choose_city':
        choose_country(message)  # Р’РѕР·РІСЂР°С‰Р°РµРј Рє РІС‹Р±РѕСЂСѓ СЃС‚СЂР°РЅС‹
    elif step == 'choose_country':
        send_welcome(message)  # Р’РѕР·РІСЂР°С‰Р°РµРј РІ РЅР°С‡Р°Р»СЊРЅРѕРµ РјРµРЅСЋ
    else:
        send_welcome(message)  # РќР° СЃР»СѓС‡Р°Р№ РЅРµРєРѕСЂСЂРµРєС‚РЅРѕРіРѕ С€Р°РіР°

@bot.message_handler(func=lambda message: message.text in city_translation)
def send_weather(message):
    global selected_city

    selected_city, city_belarusian = city_translation[message.text]
    weather_info = get_weather(selected_city)

    bot.reply_to(message, weather_info.replace(f"рџЊҐРќР°РґРІРѕСЂ'Рµ Сћ {selected_city}рџЊҐ", f"рџЊҐРќР°РґРІРѕСЂ'Рµ Сћ {city_belarusian}рџЊҐ"))

bot.polling()

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
    "Мінск": ("Minsk", "Мінску"),
    "Брэст": ("Brest", "Брэсце"),
    "Гомель": ("Gomel", "Гомеле"),
    "Гродно": ("Grodno", "Гродно"),
    "Віцебск": ("Vitebsk", "Віцебске"),
    "Магілёв": ("Mogilev", "Магілёве"),
    "Масква": ("Moscow", "Маcкве"),
    "Санкт-Пецярбург": ("Saint-Petersburg", "Санкт-Пецярбурге"),
    "Новасібірск": ("Novosibirsk", "Новасібірску"),
    "Сочы": ("Sochi", "Сочы"),
    "Казань": ("Kazan", "Казані"),
    "Растоў На Доне": ("Rostov-na-Donu", "Растоў На Доне"),
    "Кіеў": ("Kyiv", "Кіеве"),
    "Адэса": ("Odessa", "Адэсе"),
    "Нур-Султан": ("Nur-Sultan", "Нур-Султане"),
    "Алматы": ("Almaty", "Алматы"),
    "Уральск": ("Oral", "Уральску"),
    "Варшава": ("Warsaw", "Варшаве"),
    "Кракаў": ("Krakov", "Кракаве"),
    "Берлін": ("Berlin", "Берліне"),
    "Нью-Ёрк": ("New York", "Нью-Ёрке"),
    "Вашынгтон": ("Washington", "Вашынгтоне"),
    "Севастопаль": ("Sevastopol", "Севастопле"),
    "Ялта": ("Yalta", "Ялце")
}


def get_weather(city):
    try:
        url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city},KZ&lang=ru&aqi=no'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'error' in data:
            return "Памылка пры атрыманні дадзеных аб надвор'і."

        temp = data['current']['temp_c']
        feels_like = data['current']['feelslike_c'] 
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

        return f"🌥Надвор'е ў {city}🌥\n\n📆Cёння: {formatted_date}\n⏰Час: {formatted_time}\n\n🌡Тэмпература: {temp}°C\n 🧖Адчуваецца як {feels_like}°C\n\n✨Стан: {translated_text}\n🌬Вецер: {wind} км/г"
    except requests.exceptions.RequestException as e:
        return f"Немагчыма атрымаць дадзеныя: {e}"
    except Exception as e:
        return f"Нечаканая памылка: {e}"


def get_currency():
    try:
        currencies = {
            "USD": "🇺🇸1 Даляр",
            "EUR": "🇪🇺1 Еўра",
            "RUB": "🇷🇺100 Расійскіх рубелёў",
            "UAH": "🇺🇦100 Грівен"
        }

        rates = {}
        for code in currencies.keys():
            url = f'https://api.nbrb.by/exrates/rates/{code}?parammode=2'
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            rates[code] = data.get('Cur_OfficialRate')

        if None in rates.values():
            return "Памылка пры атрыманні дадзеных аб валютах"

        return (
            f"{currencies['USD']} = {rates['USD']:.2f} BYN\n"
            f"{currencies['EUR']} = {rates['EUR']:.2f} BYN\n"
            f"{currencies['UAH']} = {rates['UAH']:.4f} BYN\n"
            f"{currencies['RUB']} = {rates['RUB']:.4f} BYN"
        )

    except requests.exceptions.RequestException as e:
        return f"Немагчыма атрымаць дадзеныя: {e}"
    except Exception as e:
        return f"Нечаканая памылка: {e}"

@bot.message_handler(commands=['start'])
def welcome(message):
    user_name = message.from_user.first_name 
    greeting = f"{user_name}"  


    with open("IMAGES/pic1.jfif", "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption=f"Вітаю, {greeting}, дзякуй, што карыстаешся гэтым ботам")

    menu(message)

@bot.message_handler(commands=['menu'])
def menu(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    country_button = KeyboardButton('🌍Вылучыце краіну🌍')
    currency_button = KeyboardButton('💵Курс валюты💵')
    settings = KeyboardButton('⚙️Наладкі⚙️')
    markup.add(country_button, currency_button, settings)
    bot.send_message(message.chat.id, "Вылучы дзеянне:", reply_markup=markup)

#@bot.message_handler(func=lambda message: message.text == "Дзякуй аўтару")
#def donate(message):
  #bot.send_message(message.chat.id, "🇧🇾4585 2200 0532 8231🇧🇾\n🇷🇺2200 7013 5273 0086🇷🇺")


@bot.message_handler(func=lambda message: message.text == '💵Курс валюты💵')
def send_currency(message):
    currency_info = get_currency()
    bot.send_message(message.chat.id, currency_info)

@bot.message_handler(func=lambda message: message.text == '⚙️Наладкі⚙️')
def settings(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    language = KeyboardButton('🌐Мова🌐')
    remembers = KeyboardButton('🔔Напамін🔔')
    themes = KeyboardButton('🖌Тэмы🖌')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(language, remembers, themes, back_button)
    bot.send_message(message.chat.id, "Вылучыце", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🌐Мова🌐')
def change_language(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    belarusian_button = KeyboardButton('🇧🇾Беларуская')
    russian_button = KeyboardButton('🇷🇺Русский')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(belarusian_button, russian_button, back_button)
    bot.send_message(message.chat.id, "Выберыце мову:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🌍Вылучыце краіну🌍')
def choose_country(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    belarus_button = KeyboardButton('🇧🇾Беларусь')
    russia_button = KeyboardButton('🇷🇺Расія')
    ukraine_button = KeyboardButton('🇺🇦Украіна')
    kazakhstan_button = KeyboardButton('🇰🇿Казахстан')
    poland_button = KeyboardButton('🇵🇱Польшча')
    germany_button = KeyboardButton('🇩🇪Нямеччына')
    usa_button = KeyboardButton('🇺🇸Злучаныя Штаты Амерыкі')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(belarus_button, russia_button, ukraine_button, kazakhstan_button, poland_button, germany_button,
               usa_button, back_button)
    bot.send_message(message.chat.id, "Вылучыце краіну:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇧🇾Беларусь')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    minsk = KeyboardButton('Мінск')
    brest = KeyboardButton('Брэст')
    gomel = KeyboardButton('Гомель')
    grodno = KeyboardButton('Гродно')
    vitebsk = KeyboardButton('Віцебск')
    mogilev = KeyboardButton('Магілёв')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(minsk, brest, gomel, grodno, vitebsk, mogilev, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Беларусі.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇷🇺Расія')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    moscow = KeyboardButton('Масква')
    saint_petersburg = KeyboardButton('Санкт-Пецярбург')
    novosibirsk = KeyboardButton('Новасібірск')
    kazan = KeyboardButton('Казань')
    sochi = KeyboardButton('Сочы')
    rnd = KeyboardButton('Растоў На Доне')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(moscow, saint_petersburg, novosibirsk, kazan, sochi, rnd, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Расіі.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇺🇦Украіна')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kyiv = KeyboardButton('Кіеў')
    odessa = KeyboardButton('Адэса')
    crimea = KeyboardButton('Крым')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(kyiv, odessa, crimea, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Украіне.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Крым')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    sevastopl = KeyboardButton('Севастопаль')
    yalta = KeyboardButton('Ялта')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(sevastopl, yalta, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Украіне.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇰🇿Казахстан')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    nur_sultan = KeyboardButton('Нур-Султан')
    almaty = KeyboardButton('Алматы')
    oral = KeyboardButton('Уральск')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(nur_sultan, almaty, oral, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Кахахстане.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇵🇱Польшча')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    warsaw = KeyboardButton('Варшава')
    krakov = KeyboardButton('Кракаў')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(warsaw, krakov, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Польшчы.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇩🇪Нямеччына')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    berlin = KeyboardButton('Берлін')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(berlin, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Нямеччыне.",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🇺🇸Злучаныя Штаты Амерыкі')
def send_weather(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    new_york = KeyboardButton('Нью-Ёрк')
    washington = KeyboardButton('Вашынгтон')
    back_button = KeyboardButton('⬅️Вярнуцца')
    markup.add(new_york, washington, back_button)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Злучаных Штатах Амерыкі",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '⬅️Вярнуцца')
def go_back(message):
    step = user_steps.get(message.chat.id, 'menu')
    if step == 'choose_city':
        choose_country(message)
    elif step == 'choose_country':
        menu(message)
    else:
        menu(message)


@bot.message_handler(func=lambda message: message.text in city_translation)
def send_weather(message):
    global selected_city

    selected_city, city_belarusian = city_translation[message.text]
    weather_info = get_weather(selected_city)

    bot.reply_to(message, weather_info.replace(f"🌥Надвор'е ў {selected_city}🌥", f"🌥Надвор'е ў {city_belarusian}🌥"))


bot.polling()

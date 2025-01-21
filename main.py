import telebot
import requests
from googletrans import Translator

API_TOKEN = ''
WEATHER_API_KEY = ''

bot = telebot.TeleBot(API_TOKEN)

translator = Translator()

def get_weather():
    url = f'http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q=Minsk&lang=ru'
    response = requests.get(url)
    data = response.json()

    if 'error' in data:
        return "Памылка пры атрыманні дадзеных аб надвор'і."

    temp = data['current']['temp_c']
    weather = data['current']['condition']['text']
    wind = data['current']['wind_kph']

    translated = translator.translate(weather, src='ru', dest='be')

    return f"🌥Надвор'е ў Мінску🌥\n🌡Тэмпература: {temp}°C\n✨Станоўчае: {translated.text}\n🌬Вецер: {wind} км/г"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item = telebot.types.KeyboardButton('Надвор’е ў Мінску')
    markup.add(item)
    bot.send_message(message.chat.id, "Вітаю! Націсніце кнопку, каб атрымаць надвор'е ў Мінску.",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == 'Надвор’е ў Мінску')
def send_weather(message):
    weather_info = get_weather()
    bot.reply_to(message, weather_info)

bot.polling()
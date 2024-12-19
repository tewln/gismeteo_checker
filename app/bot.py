import os
import telebot
from back import get_weather

APP_TOKEN = os.getenv("APP_TOKEN")

bot = telebot.TeleBot(APP_TOKEN)
old_users = set()

@bot.message_handler(commands=["start"])
def start(message):
    telegram_id = message.chat.id
    if not telegram_id in old_users:
        greeting(telegram_id)
    else:
        list_commands(telegram_id)
        
@bot.message_handler(commands=["weather"])
def give_away_weather(message):
    telegram_id = message.chat.id
    if len(message.text.split()) != 3:
        list_commands(telegram_id)
    command, date_, period = message.text.split()
    if telegram_id in old_users:
        if len(date_.split('.')) != 3 or int(period) < 1:
            list_commands(telegram_id)
        answer = get_weather(date_, int(period))
        if not answer:
            bot.send_message(telegram_id, "Ой, кажется, за это время у меня нет данных... Попробуй другое время!")
        else:
            bot.send_message(telegram_id, to_string(answer))
    else:
        bot.send_message(telegram_id, "Не так быстро, друг! Позволь представиться!")
        greeting(telegram_id)

@bot.message_handler(commands=["help"])
def get_help(message):
    list_commands(message.chat.id)

def list_commands(id):
    bot.send_message(id, "Ой, кажется, ты потерялся?\n Попробуй ввести команду /weather [начальная дата] [период]")

def greeting(id):
    old_users.add(id)
    bot.send_message(id,
                     "Привет! Я - бот-помощник по Окружающему миру!\n Если тебе нужны данные о погоде за какой-то период - обращайся ко мне!\n Для этого нужно всего-лишь ввести команду /weather [начальная дата] [период], где начальная дата - дата желаемого начала в формате ДД.ММ.ГГГГ, период - количество дней с начала.\n Если такие дни найдутся - я обязательно их отправлю тебе!"
                     )

def to_string(dictionary:dict):
    answer = str()
    for day, raw_data in dictionary:
        answer = answer + day + "\n\n"
        for time, dat in raw_data:
            answer = answer + time + " || "
            answer = answer + dat["temperature"] + " | "
            answer = answer + dat["pressure"] + " | "
            answer = answer + dat["cloudiness"] + " | "
            answer = answer + dat["precipitation"] + " | "
            answer = answer + dat["wind_speed"] + " | "
            answer = answer + dat["wind_direction"] + "\n"
        answer = answer + "\n"

if __name__ == "__main__":
    bot.polling(none_stop=True)
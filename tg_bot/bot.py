import os
import telebot
import datetime
import psycopg2

API_TOKEN = os.getenv("API_TOKEN")

bot = telebot.TeleBot(API_TOKEN)
old_users = set()

@bot.message_handler(commands=["start"])
def start(message):
    id = message.chat.id
    if not id in old_users:
        greeting(id)
    else:
        wrong_command(id)
        
@bot.message_handler(commands=["weather"])
def give_away_weather(message):
    id = message.chat.id
    if len(message.text.split(' ')) == 3:
        command, date_, period = message.text.split()
        if int(period) > 31:
            bot.send_message(id, "Извини, я не могу вернуть так много информации за раз! Попробуй ввести период меньше месяца!")
            return
        if id in old_users:
                if len(date_.split('.')) != 3 or int(period) < 1:
                    get_help(message)
                answer = get_weather(date_, int(period))
                if not answer:
                    bot.send_message(id, "Ой, кажется, за это время у меня нет данных... Попробуй другое время!")
                else:
                    bot.send_message(id, "Отправляю!")
                    bot.send_message(id, to_string(answer))
        else:
            bot.send_message(id, "Не так быстро, друг! Позволь представиться!")
            greeting(id)
    else:
        wrong_command(id)

@bot.message_handler(commands=["help"])
def get_help(message):
    id = message.chat.id
    if id in old_users:
        bot.send_message(id, "/weather [начальная дата] [период]\n/help\n\nПример правильной команды для поиска информации: /weather 22.12.2024 1 - данная команда вернёт погоду за 22-ое декабря 2024 года.")
    else:
        greeting(id)

def wrong_command(id):
    if id in old_users:
        bot.send_message(id, "Ой, кажется, ты потерялся?\nПопробуй ввести команду /weather [начальная дата] [период] или /help\nПример правильной команды для поиска информации: /weather 22.12.2024 1 - данная команда вернёт погоду за 22-ое декабря 2024 года.")
    else:
        bot.send_message(id, "Не так быстро, друг! Позволь представиться!")
        greeting(id)

def greeting(id):
    old_users.add(id)
    bot.send_message(id,
                     "Привет! Я - бот-помощник по Окружающему миру!\nЕсли тебе нужны данные о погоде за какой-то период - обращайся ко мне!\nДля этого нужно всего-лишь ввести команду /weather [начальная дата] [период], где начальная дата - дата желаемого начала в формате ДД.ММ.ГГГГ, период - количество дней с начала (но не более месяца).\nЕсли такие записи у меня найдутся - я обязательно отправлю их тебе!"
                     )
    
def to_string(dictionary):
    answer = "Формат записи:\n(Дата)\n Время суток || температура (*C) | давление (мм.рт.ст.) | облачность | осадки | скорость ветра | направление ветра |\n\n\nПогода по твоему запросу:\n\n"
    for day, raw_data in dictionary.items():
        answer += '(' + str(day) + ')' + '\n'
        for time, data in raw_data.items():
            data = dict(data)
            answer += str(time) + ' || ' + str(data['temperature']) + ' | ' + str(data['pressure']) + ' | ' + str(data['cloudiness']) + ' | ' + str(data['precipitation']) + ' | ' + str(data['wind_speed']) + ' | ' + str(data['wind_direction']) + ' |\n'
        answer += "\n"
    answer += "\nЕсли тут не всё, что ты искал - скорее всего, у меня нет информации за это время (но ты можешь попробовать уточнить её отдельно)"
    return answer

def get_weather(user_date: str, period: int):
    days, months, years = map(lambda x: int(x), user_date.split('.'))
    date_ = datetime.date(years, months, days)
    connection = get_db_connection()
    cursor = connection.cursor()
    answer = dict()
    cursor.execute(
        """
        SELECT * FROM weather WHERE date BETWEEN %s AND %s;
        """,
        (date_.isoformat(), (date_ + datetime.timedelta(period - 1)).isoformat())
    )
    rows = cursor.fetchall()
    for row in rows:
        answer.update({row[1]: {
            "День": {
                "temperature": row[2],
                "pressure": row[4],
                "cloudiness": row[6],
                "precipitation": ('Отсутствуют' if row[8] is None else row[8]),
                "wind_speed": row[10],
                "wind_direction": row[12]
            },
            "Вечер": {
                "temperature": row[3],
                "pressure": row[5],
                "cloudiness": row[7],
                "precipitation": ('Отсутствуют' if row[9] is None else row[9]),
                "wind_speed": row[11],
                "wind_direction": row[13]
            }
        }})
    cursor.close()
    connection.close()
    return answer

def get_db_connection():
    return psycopg2.connect(
        dbname='mydatabase',
        user='postgre',
        password='postgre',
        host='db',
        port='5432'
    )

if __name__ == "__main__":
    bot.polling(none_stop=True)
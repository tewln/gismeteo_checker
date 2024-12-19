import os
import psycopg2
import requests
from itertools import accumulate
from collections import Counter
from bs4 import BeautifulSoup
import datetime
import time

GISMETEO_URL = "https://www.gismeteo.ru/weather-chelyabinsk-4565/"

def get_db_connection():
    return psycopg2.connect(
        dbname='mydatabase',
        user='user',
        password='password',
        host='db',
        port='5432'
    )

def save_weather_to_db(weather_data: dict):
    date = list(weather_data.keys())[0]
    data = weather_data[date]

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO weather (
                date, temperature_morning, temperature_evening,
                pressure_morning, pressure_evening,
                cloudiness_morning, cloudiness_evening,
                wind_speed_morning, wind_speed_evening,
                wind_direction_morning, wind_direction_evening
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (date) DO NOTHING;
            """,
            (
                date,
                data[0]["temperature"], data[1]["temperature"],
                data[0]["pressure"], data[1]["pressure"],
                data[0]["cloudiness"], data[1]["cloudiness"],
                data[0]["wind_speed"], data[1]["wind_speed"],
                data[0]["wind_direction"], data[1]["wind_direction"]
            )
        )
        connection.commit()
    except Exception as e:
        print(f"Error while saving data to DB: {e}")
    finally:
        cursor.close()
        connection.close()

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
        (date_.isoformat(), (date_ + datetime.timedelta(period)).isoformat())
    )
    rows = cursor.fetchall()
    for row in rows:
        answer.update({row[0]: {
            "День": {
                "temperature": row[1],
                "pressure": row[3],
                "cloudiness": row[5],
                "precipitation": row[7],
                "wind_speed": row[9],
                "wind_direction": row[11]
            },
            "Вечер": {
                "temperature": row[2],
                "pressure": row[4],
                "cloudiness": row[6],
                "precipitation": row[8],
                "wind_speed": row[10],
                "wind_direction": row[12]
            }
        }})
    cursor.close()
    connection.close()
    return answer

def fetch_weather_data():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"}
    response = requests.get(GISMETEO_URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    def get_temperatures(soup: BeautifulSoup):
        temperatures = []
        for _slice in soup.find_all("div", attrs={"data-row": "temperature-air"}):
            for raw_temperatures in _slice.find("div", class_="values"):
                for temperature in raw_temperatures.find_all("temperature-value", attrs={"from-unit": "c"}):
                    temperatures.append(temperature["value"])
        return temperatures

    def get_pressures(soup: BeautifulSoup):
        pressures = []
        for pressure in soup.find_all("pressure-value", attrs={"from-unit": "mmhg"}):
            pressures.append(pressure["value"])
        return pressures

    def get_precipitations(soup: BeautifulSoup):
        precipitations = []
        for slice_ in soup.find_all("div", attrs={"data-row": "icon-tooltip"}):
            for raw_weather in slice_.find_all("div", class_="row-item"):
                weather = raw_weather["data-tooltip"]
                if weather.find(",") != -1:
                    if weather.find(",", weather.find(",") + 1) != -1:
                        precipitations.append(weather.replace("  ", " ")[weather.find(",") + 2: weather.find(",", weather.find(","))].capitalize())
                    else:
                        precipitations.append(weather.replace("  ", " ")[weather.find(",") + 2: len(weather)].capitalize())
                else:
                    precipitations.append("-")
        return precipitations

    def get_cloudiness(soup: BeautifulSoup):
        cloudiness = []
        for slice_ in soup.find_all("div", attrs={"data-row": "icon-tooltip"}):
            for raw_weather in slice_.find_all("div", class_="row-item"):
                weather = raw_weather["data-tooltip"]
                if weather.find(",") != -1:
                    cloudiness.append(weather[: weather.find(",")])
                else:
                    cloudiness.append(weather)
        return cloudiness

    def get_wind_speeds(soup: BeautifulSoup):
        wind_speeds = []
        for slice_ in soup.find_all("div", attrs={"data-row": "wind-speed"}):
            for raw_wind_speed in slice_.find_all("div", class_="row-item"):
                wind_speeds.append(raw_wind_speed.find("speed-value")["value"])
        return wind_speeds

    def get_wind_directions(soup: BeautifulSoup):
        wind_directions = []
        for wind_direction in soup.find_all("div", class_="direction"):
            wind_directions.append(wind_direction.text if wind_direction.text != "штиль" else "Ш")
        return wind_directions

    def get_average_values(list_with_numbers: list):
        amount = list(accumulate(list_with_numbers))
        average_morning = amount[len(amount) // 2 - 1] * 2 // len(amount)
        average_evening = (amount[-1] - amount[len(amount) // 2 - 1]) * 2 // len(amount)
        return [average_morning, average_evening]

    def get_average_word(list_with_strings: list):
        most_common_morning = Counter(list_with_strings[: len(list_with_strings) // 2]).most_common(1)[0][0]
        most_common_evening = Counter(list_with_strings[len(list_with_strings) // 2:]).most_common(1)[0][0]
        return [most_common_morning, most_common_evening]

    temperatures = get_average_values(list(map(lambda i: int(i), get_temperatures(soup))))
    pressures = get_average_values(list(map(lambda i: int(i), get_pressures(soup))))
    precipitations = get_average_word(get_precipitations(soup))
    cloudiness = get_average_word(get_cloudiness(soup))
    wind_speed = get_average_values(list(map(lambda i: int(i), get_wind_speeds(soup))))
    wind_directions = get_average_word(get_wind_directions(soup))
    current_date = datetime.date.today().isoformat()
    weather_per_day = dict()
    weather_per_day.update({current_date: dict()})
    for i in range(0, 2):
        weather_per_day[current_date].update({i: {
            "temperature": temperatures[i],
            "pressure": pressures[i],
            "cloudiness": cloudiness[i],
            "precipitation": precipitations[i],
            "wind_speed": wind_speed[i],
            "wind_direction": wind_directions[i]
        }})
    return weather_per_day

def main():
    while True:
        now = datetime.datetime.now()  # Текущее время
        next_wakeup = (now + datetime.timedelta(seconds=10))  # Изменить timedelta на days=1
        seconds_until_wakeup = int((next_wakeup - now).total_seconds())
        save_weather_to_db(fetch_weather_data())
        time.sleep(seconds_until_wakeup - 1)

if __name__ == "__main__":
    main()

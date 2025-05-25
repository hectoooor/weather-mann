import config
import requests
import json
import sys
from datetime import datetime
import sqlite3

api_key = config.api_key
db_name = "weather_db.db"

city_code = {
        "laguardia airport": "2627477",
        "london city airport": "2532754"
        }

sql_statements = [
    """CREATE TABLE IF NOT EXISTS weather_forecasts (
        call_date DATE PRIMARY KEY,
        forecast_date DATE NOT NULL,
        max_temp INTEGER NOT NULL,
        city_code INTEGER NOT NULL
    );"""
        ]

def get_url(city):
    location_key = city_code[city]
    url = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/" + location_key + "?apikey=" + api_key
    return url

# returns serialized json string
def call_api(url):
    response = requests.get(url)
    json_data = response.json()
    # s_data is serialized data
    s_data = json.dumps(json_data, indent=4)
    return s_data

def write_json(data, filename):
    with open(filename, "w") as ofile:
        ofile.write(data)

# returns python dictionary
def read_json(filename):
    with open(filename, "r") as ifile:
        # the file is read a TextIOWrapper type so we have to convert it to str
        content = ifile.read()
        # returns a dictionary inside a list inside a dictionary ie: dict{list[dict{data...} ] }
        return json.loads(content)

def consume_json_dict(json_dict):
    call_date = datetime.now().isoformat()
    date = json_dict["DailyForecasts"][0]["EpochDate"]
    date = datetime.fromtimestamp(date).isoformat()
    max_temp = json_dict["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
    return call_date, date, max_temp

def create_db():
    try:
        with sqlite3.connect(db_name) as conn:
            print("opened database")

    except sqlite3.OperationalError as e:
        print("error in create_db(): ", e)

def create_table_db():
    try:
        with sqlite3.connect(db_name) as conn:
            cursor = conn.cursor()

            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()

            print("tables created")

    except sqlite3.OperationalError as e:
        print("error in create_table(): ", e)

def add_forecast_db(conn, weather_forecasts):
    sql = ''' INSERT INTO weather_forecasts(call_date, forecast_date, max_temp, city_code)
              VALUES(?,?,?,?) '''

    cur = conn.cursor()

    cur.execute(sql, weather_forecasts)

    conn.commit()

    return cur.lastrowid

def insert_data_db(weather_data):
    try:
        with sqlite3.connect(db_name) as conn:
            # print(weather_data)
            weather_id = add_forecast_db(conn, weather_data)
            print("created a row of weather data", weather_id)

    except sqlite3.Error as e:
        print(e)

def main():
    create_db()
    create_table_db()
    city = "laguardia airport"
    url = get_url(city)
    cmd = int(sys.argv[1])
    if cmd == 1:
        data = call_api(url)
        print(data)
        write_json(data, "weather_data.json")
    elif cmd == 2:
        json_dict = read_json("weather_data.json")
        values = consume_json_dict(json_dict)
        values = list(values)
        values.append(city_code[city])
        values = tuple(values)
        for v in values:
            print(v)

        insert_data_db(values)

if __name__ == '__main__':
    main()

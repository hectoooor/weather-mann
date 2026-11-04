import json
import sqlite3
from datetime import datetime

import requests

station_data = "stationdata.json"
noaa_forecast_url = "https://api.weather.gov/gridpoints/{wfo}/{x},{y}/forecast"

#reads a json file and returns a dict
def read_json(filename):
    with open(filename, "r") as ifile:
        content = ifile.read()
        return json.loads(content)

    return -1

def get_url(city):
    json_dict = read_json(station_data)
    office = json_dict["cities"][city][1]
    gridpoints = json_dict["cities"][city][2]

    url = noaa_forecast_url.replace("{wfo}", office)
    url = url.replace("{x}", str(gridpoints[0]))
    url = url.replace("{y}", str(gridpoints[1]))

    return url

#t for type, function can return either json or str
def call_api(url, t):
    response = requests.get(url)
    json_data = response.json()
    if t == "json":
        return json_data

    #return string data
    s_data = json.dumps(json_data, indent=4)
    return s_data

def make_db(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS  weather (
            req_date TEXT,
            start_date TEXT,
            end_date TEXT,
            city TEXT,
            max_temp INTEGER,
            rain_chance INTEGER
        )
    """)

    conn.commit()

def insert_weather_data(conn, json_dict, city):
    cursor = conn.cursor()
    now = datetime.now().isoformat(timespec="seconds")

    #14 becuase the api call sends 14 forecasts
    for i in range(14):
        start_date = json_dict["properties"]["periods"][i]["startTime"]
        end_date = json_dict["properties"]["periods"][i]["endTime"]
        temp = json_dict["properties"]["periods"][i]["temperature"]
        rain = json_dict["properties"]["periods"][i]["probabilityOfPrecipitation"]["value"]
        #print(start_date, end_date, city, temp, rain)

        cursor.execute(
                "INSERT INTO weather (req_date, start_date, end_date, city, max_temp, rain_chance) VALUES (?, ?, ?, ?, ?, ?)",
                (now, start_date, end_date, city, temp, rain)
        )

    conn.commit()

def start(tar_city, db_name):
    json_dict = call_api(get_url(tar_city), "json")
    #s_data = json.dumps(json_dict["properties"]["periods"], indent=4)
    #print(s_data)

    conn = sqlite3.connect(db_name)

    make_db(conn)

    insert_weather_data(conn, json_dict, tar_city)

    conn.commit()
    conn.close()

#todo add more date formats functionality
def search_date(db_name, search_term):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # must be in "yyyy-mm-dd" format, ie: 2000-01-01
    cur.execute("""SELECT * FROM weather WHERE start_date LIKE ?""", (f"%{search_term}%",))
    res = cur.fetchall()

    conn.commit()
    conn.close()

    #returns whole row containing the start_date
    return res

#todo tommorow, configure github actions so that program runs on chron jobs, work more on scheduler and add context manager and exception handling

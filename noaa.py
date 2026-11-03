import requests
import json
import sqlite3
from datetime import datetime, timezone

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

def make_db(cur):
    #make pk datetime of the api call and add a query to search for a dates forecast then compare over time
    cur.execute("""
        CREATE TABLE IF NOT EXISTS  weather (
            req_date TEXT,
            start_date TEXT,
            end_date TEXT,
            city TEXT,
            max_temp INTEGER,
            rain_chance INTEGER
        )
    """)

def insert_weather_data(cur, json_dict, city):
    now = datetime.now().isoformat(timespec="seconds")

    for i in range(14):
        start_date = json_dict["properties"]["periods"][i]["startTime"]
        end_date = json_dict["properties"]["periods"][i]["endTime"]
        temp = json_dict["properties"]["periods"][i]["temperature"]
        rain = json_dict["properties"]["periods"][i]["probabilityOfPrecipitation"]["value"]
        #print(start_date, end_date, city, temp, rain)

        cur.execute(
                "INSERT INTO weather (req_date, start_date, end_date, city, max_temp, rain_chance) VALUES (?, ?, ?, ?, ?, ?)",
                (now, start_date, end_date, city, temp, rain)
        )

def search_date(cur, search_term):
    cur.execute("""SELECT * FROM weather WHERE start_date LIKE ?""", (f"%{search_term}%",))
    res = cur.fetchall()

    return res

def start(tar_city, db_name):
    json_dict = call_api(get_url(tar_city), "json")
    s_data = json.dumps(json_dict["properties"]["periods"], indent=4)
    #print(s_data)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    make_db(cursor)

    insert_weather_data(cursor, json_dict, tar_city)

    conn.commit()
    conn.close()

#todo tommorow, finish scheduler, push to github, configure github actions so that program runs on chron jobs

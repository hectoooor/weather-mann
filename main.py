import config
import requests
import json
import sys
from datetime import datetime

api_key = config.api_key

city_code = {
        "laguardia airport": "2627477",
        "london city airport": "2532754"
        }

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

def main():
    url = get_url("laguardia airport")
    cmd = int(sys.argv[1])
    if cmd == 1:
        data = call_api(url)
        print(data)
        write_json(data, "weather_data.json")
    elif cmd == 2:
        json_dict = read_json("weather_data.json")
        values = consume_json_dict(json_dict)
        for v in values:
            print(v)

if __name__ == '__main__':
    main()

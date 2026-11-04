import time

import schedule

import noaa


def search(db_name, date):
    query = noaa.search_date(db_name, date)

    for i in query:
        print(i)

def loop(city, db_name):
    schedule.every().hour.do(noaa.start, city, db_name)

    c = 0
    while True:
        c += 1
        print(c)
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    #search("noaa.db", "2026-10-31")


    #noaa.start("miami", "noaa.db")
    loop("miami", "noaa.db")

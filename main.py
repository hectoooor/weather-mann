import noaa

import schedule
import time

if __name__ == '__main__':
    schedule.every().hour.do(noaa.start, "miami", "noaa.db")

    c = 0
    while True:
        c += 1
        print(c)
        schedule.run_pending()
        time.sleep(10)

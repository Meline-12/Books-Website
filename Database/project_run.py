from mysql import create_db
from web_scraping import crawler
import datetime

if __name__ == "__main__":
    create_db()
    start = datetime.datetime.now()
    print(start)
    crawler(1, 10332)
    end = datetime.datetime.now()
    dif = end - start
    print(end)
    print(dif)

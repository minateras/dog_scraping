import os
import sys
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Appends the parent dir to the Python path.

from database import Database
from web_scraping import WebScraping


class SKK:
    __WS = WebScraping()
    BREED = 'Rhodesian ridgeback'
    SEPARATOR = '   '
    REGISTRATION_NUMBER = 'registration_number'
    KENNEL_NAME = 'kennel_name'
    DATE = 'date'
    titles = []


    def __init__(self, url):
        self.get(url)
        self.print_title()

        # Retrieves all valid titles.
        db = Database()
        db.execute("""SELECT title FROM title2""")
        for title in db.fetch_all():
            self.titles.append(title[0])
        db.close()


    def print_title(self):
        self.__WS.print_title()


    def get(self, url):
        self.__WS.get(url)


    def handle_exception(self, exception):
        if isinstance(exception, TimeoutException): print('A TimeoutException occurred.')
        else: print(exception)
        db = Database()
        db.execute("""INSERT INTO exception2(exception) VALUES (%s)""", (str(exception), ))
        db.close()


    def wait_until(self, value, by=By.ID):
        self.__WS.wait_until(value, by)


    def find_element(self, value, by=By.ID, parent=None):
        return self.__WS.find_element(value, by, parent)


    def select(self, value):
        return self.__WS.select(value)


    def find_elements(self, value, by=By.XPATH, parent=None):
        return self.__WS.find_elements(value, by, parent)


    def back(self):
        self.__WS.back()


    def randomized_delay(self, min=1, max=5):
        self.__WS.randomized_delay(min, max)


    def exit(self):
        self.__WS.quit()


    def validate_title(self, title):
        for dog_sport_title in self.titles:
            if title.strip().upper() == dog_sport_title.upper(): return dog_sport_title
        return None


    def normalize_kennel_name(self, kennel_name: str) -> str:
        kennel_name = list(kennel_name.title())
        for i in range(1, len(kennel_name)):
            previous = kennel_name[i - 1]
            current = kennel_name[i]
            next = kennel_name[i + 1] if (i + 1) < len(kennel_name) else None
            # If previous is an apostrophe, current is a letter, and next is a space (or the end):
            if previous == "'" and current.isalpha() and (next == ' ' or next is None):
                kennel_name[i] = current.lower()
        return ''.join(kennel_name)


    def save_dog(self, db, kennel_name, registration_number):
        db.execute("""SELECT id FROM dog2 WHERE kennel_name = %s""", (kennel_name, ))
        if db.fetch_one() is None:
            db.execute("""INSERT INTO dog2(kennel_name, registration_number) VALUES (%s, %s)""", (kennel_name, registration_number))


    def save_title(self, db, title, registration_number, date):
        db.execute("""SELECT date FROM title_dog2 WHERE title = (SELECT id FROM title2 WHERE title = %s) AND dog = (SELECT id FROM dog2 WHERE registration_number = %s) LIMIT 1""", (title, registration_number))
        if db.fetch_one() is None:
            db.execute("""INSERT INTO title_dog2(title, dog, date) VALUES ((SELECT id FROM title2 WHERE title = %s), (SELECT id FROM dog2 WHERE registration_number = %s), %s)""", (title, registration_number, date))


    def update_date(self):
        db = Database()
        db.execute("""DELETE FROM date2""")
        db.execute("""INSERT INTO date2(date) VALUES (%s)""", (datetime.today(), ))
        db.close()

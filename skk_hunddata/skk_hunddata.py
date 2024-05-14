import os
import sys

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Appends the parent dir to the Python path.

from database import Database
from web_scraping import WebScraping


class SkkHunddata:
    __WS = WebScraping()
    __DB = Database()
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
        self.execute("""SELECT title FROM title2""")
        for title in self.fetch_all():
            self.titles.append(title[0])


    def print_title(self):
        self.__WS.print_title()


    def get(self, url):
        self.__WS.get(url)


    def handle_exception(self, exception):
        if isinstance(exception, TimeoutException): print('A TimeoutException occurred.')
        else: print(exception)
        self.execute("""INSERT INTO exception2(exception) VALUES (%s)""", (str(exception), ))


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


    def execute(self, query, arguments=None):
        self.__DB.execute(query, arguments)


    def fetch_one(self):
        return self.__DB.fetch_one()


    def fetch_all(self):
        return self.__DB.fetch_all()


    def exit(self):
        self.__WS.quit()
        self.__DB.close()


    def validate_title(self, title):
        for dog_sport_title in self.titles:
            if title.strip().upper() == dog_sport_title.upper(): return dog_sport_title
        return None


    def normalize_kennel_name(self, kennel_name):
        return kennel_name.title().replace('\'S', '\'s')


    def save_dog(self, kennel_name, registration_number):
        self.execute("""SELECT id FROM dog2 WHERE registration_number = %s""", (registration_number, ))
        if self.fetch_one() is None:
            self.execute("""INSERT INTO dog2(kennel_name, registration_number) VALUES (%s, %s)""", (kennel_name, registration_number))


    def save_title(self, title, registration_number, date):
        self.execute("""SELECT date FROM title_dog2 WHERE title = (SELECT id FROM title2 WHERE title = %s) AND dog = (SELECT id FROM dog2 WHERE registration_number = %s) LIMIT 1""", (title, registration_number))
        if self.fetch_one() is None:
            self.execute("""INSERT INTO title_dog2(title, dog, date) VALUES ((SELECT id FROM title2 WHERE title = %s), (SELECT id FROM dog2 WHERE registration_number = %s), %s)""", (title, registration_number, date))

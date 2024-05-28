from datetime import date
from random import randint
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.wait import WebDriverWait


class WebScraping:
    __OPTIONS = webdriver.ChromeOptions()
    __driver = None
    __wait = None


    @staticmethod
    def get_next_year():
        return date.today().year + 1;


    def __init__(self):
        self.__OPTIONS.add_argument('--disable-gpu')
        self.__OPTIONS.add_argument('--headless')
        self.__OPTIONS.add_argument('--no-sandbox')
        self.__driver = webdriver.Chrome(self.__OPTIONS)
        self.__wait = WebDriverWait(self.__driver, 60)


    def print_title(self, title=None):
        print(f'CRAWLING {title if title is not None else self.__driver.title}...')


    def get(self, url):
        self.__driver.get(url)


    def wait_until(self, value, by=By.ID):
        self.__wait.until(presence_of_element_located((by, value)))


    def find_element(self, value, by=By.ID, parent=None):
        if parent is not None:
            return parent.find_element(by, value)
        return self.__driver.find_element(by, value)


    def select(self, value):
        return Select(self.find_element(value))


    def find_elements(self, value, by=By.XPATH, parent=None):
        if parent is not None:
            return parent.find_elements(by, value)
        return self.__driver.find_elements(by, value)


    def back(self):
        self.__driver.back()


    def randomized_delay(self, min=1, max=5):
        sleep(randint(min, max))


    def quit(self):
        self.__driver.quit()

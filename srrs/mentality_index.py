import json
import os
import sys
from enum import Enum

from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Appends the parent dir to the Python path.

from database import Database
from web_scraping import WebScraping


class MentalityIndex:
    __WS = WebScraping()
    __DB = Database()


    class Values(Enum):
        TABLE = "//div[@class='dogmi clearfix ']/table/tbody/child::*"
        ROW = 'child::*'


    def __init__(self, kennel_names):
        self.__WS.print_title('SRRS')

        for kennel_name in kennel_names:
            hyphenated_kennel_name = kennel_name.lower().replace(' of ', ' ').replace(' ', '-')
            self.__WS.get(f'http://www.srrs.org/srrs/rasen/hundar/{hyphenated_kennel_name}')

            self.__WS.wait_until(self.Values.TABLE.value, by=By.XPATH)
            table = self.__WS.find_elements(self.Values.TABLE.value)
            breeding_values = self.__WS.find_elements(self.Values.ROW.value, parent=table[1])
            confidence_values = self.__WS.find_elements(self.Values.ROW.value, parent=table[2])

            mentality_index = []
            for i in range(1, len(breeding_values)):
                if i == 1 and len(breeding_values[i].text) == 0: break
                mentality_index.append([breeding_values[i].text, confidence_values[i].text])
            if len(mentality_index) > 0:
                self.__DB.execute("""UPDATE dog SET mentality_index = %s WHERE kennel_name = %s""", (json.dumps(mentality_index), kennel_name))

            if kennel_name != kennel_names[len(kennel_names) - 1]: self.__WS.randomized_delay()

        self.__WS.quit()
        self.__DB.close()


if __name__ == '__main__':
    kennel_names = sys.argv[1:]
    if len(kennel_names) > 0: MentalityIndex(kennel_names)

import os
import sys
from datetime import datetime
from enum import Enum

from selenium.webdriver.common.by import By

# Appends the parent dirs to the Python path:
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from skk import SKK

from web_scraping import WebScraping


class SearchTitles(SKK):
    URL = 'https://hundar.skk.se/hunddata/Championat_sok.aspx'
    start_year = 2006
    END_YEAR = WebScraping.get_next_year()
    start_month = 1
    END_MONTH = 13


    class Values(Enum):
        SELECT_YEAR = 'bodyContent_ddlYear'
        SELECT_MONTH = 'bodyContent_ddlManad'
        SELECT_BREED = 'bodyContent_ddlRas'
        BUTTON_SEARCH = 'bodyContent_btnSearch'
        MESSAGE = 'bodyContent_Championat_lblMeddelande'
        TABLE = "//table[@class='tabelltext table-striped table']/tbody"
        ROWS = TABLE + '/child::*'
        COLUMNS = 'td/child::*'
        INPUT_REGISTRATION_NUMBER = 'bodyContent_txtRegnr'
        COMPETITION = 'bodyContent_btnTavling'
        ROWS_2 = "//table[@class='table table-striped']/tbody/child::*"
        COLUMN = 'td/a'


    def __init__(self):
        super().__init__(self.URL)
        self.execute("""SELECT MAX(date) FROM title_dog2""")
        date = self.fetch_one()[0]
        if date is not None:
            date = date
            self.start_year = date.year
            self.start_month = date.month

        try:
            self.__run()
            self.update_date()
        except Exception as exception:
            self.handle_exception(exception)
        finally:
            self.exit()


    def __cut_out_titles(self, dog_info):
        for i in range(1, len(dog_info)):
            previous = dog_info[i - 1]
            current = dog_info[i]
            next = dog_info[i + 1] if (i + 1) < len(dog_info) else None
            if previous == ' ' and current == current.upper() and ((next.isalpha() and next != next.upper()) or (next.isalpha() is False and next == "'")): return dog_info[i:len(dog_info)]


    def __separate_kennel_name_and_registration_number(self, dog_info):
        return dog_info.rsplit(' ', 1)


    def __run(self):
        missing_titles = []
        title_dog = {}

        self.wait_until(self.Values.SELECT_BREED.value) # Ensures that the select elements are present.
        select_breed = self.select(self.Values.SELECT_BREED.value)
        select_breed.select_by_visible_text(self.BREED)

        # For every year...
        for y in range(self.start_year, self.END_YEAR): # self.start_year, self.END_YEAR
            select_year = self.select(self.Values.SELECT_YEAR.value)
            select_year.select_by_visible_text(str(y))

            # For every month...
            for m in range(self.start_month, self.END_MONTH): # self.start_month, self.END_MONTH
                select_month = self.select(self.Values.SELECT_MONTH.value)
                select_month.select_by_value(str(m))

                search = self.find_element(self.Values.BUTTON_SEARCH.value)
                search.click()

                # Ensures that the table is present:
                self.wait_until(self.Values.MESSAGE.value)
                message = self.find_element(self.Values.MESSAGE.value)
                if message.text.strip() == 'Det finns inga registrerade championat för denna period/ras.':
                    self.randomized_delay()
                    continue
                self.wait_until(self.Values.TABLE.value, By.XPATH)

                rows = self.find_elements(self.Values.ROWS.value)
                for row in rows:
                    columns = self.find_elements(self.Values.COLUMNS.value, By.XPATH, row)
                    dog_info = self.__cut_out_titles(columns[0].text.strip())
                    titles = columns[len(columns) - 1].text.split(self.SEPARATOR)

                    kennel_name, registration_number = self.__separate_kennel_name_and_registration_number(dog_info)
                    # if registration_number[0] != 'S': # Don't include dogs that have come to Sweden to compete from another country.
                    #     break
                    date = datetime(y, m, 1)
                    dog = {
                        self.KENNEL_NAME: kennel_name,
                        self.REGISTRATION_NUMBER: registration_number,
                        self.DATE: date,
                    }

                    for title in titles:
                        # If the title is empty (i.e., missing):
                        if not title:
                            missing_titles.append(dog)
                            break
                        # Ensures that the title is a valid one (i.e., not a show title):
                        dog_sport_title = self.validate_title(title)
                        if dog_sport_title is not None:
                            if title_dog.get(dog_sport_title) is None: title_dog[dog_sport_title] = [dog]
                            else: title_dog[dog_sport_title].append(dog)

                if not (y == self.END_YEAR - 1 and m == self.END_MONTH - 1):
                    self.randomized_delay()

        for i in range(0, len(missing_titles)):
            dog = missing_titles[i]

            self.get('https://hundar.skk.se/hunddata/Hund_sok.aspx')

            self.wait_until(self.Values.INPUT_REGISTRATION_NUMBER.value) # Ensures that the select elements are present.
            registration_number = self.find_element(self.Values.INPUT_REGISTRATION_NUMBER.value)
            registration_number.send_keys(dog[self.REGISTRATION_NUMBER])
            search = self.find_element(self.Values.BUTTON_SEARCH.value)
            search.click()

            self.wait_until(f"//a[text()='{dog[self.REGISTRATION_NUMBER]}']", By.XPATH) # Ensures that the link to the dog has been loaded.
            test = self.find_element(f"//a[text()='{dog[self.REGISTRATION_NUMBER]}']", By.XPATH)
            test.click()

            self.wait_until(self.Values.COMPETITION.value) # Ensures that the button to the competition tab has been loaded.
            competition = self.find_element(self.Values.COMPETITION.value)
            competition.click()

            rows = self.find_elements(self.Values.ROWS_2.value)
            title = None
            for i in range(len(rows) - 1, -1, -1):
                row = rows[i]
                if row.get_attribute('class') == 'tabellrubrik':
                    column = datetime.strptime(self.find_element(self.Values.COLUMN.value, By.XPATH, row).text.strip()[0:10], '%Y-%m-%d')
                    if column.year >= dog[self.DATE].year and column.month > dog[self.DATE].month:
                        break
                else:
                    column = self.find_elements('child::*', By.XPATH, row)[1].text.strip().split(self.SEPARATOR)
                    if 'Godkänt championat' in column[0]:
                        title = column[1]

            # Ensures that the title is a valid one (i.e., not a show title):
            dog_sport_title = self.validate_title(title)
            if dog_sport_title is not None:
                if title_dog.get(dog_sport_title) is None: title_dog[dog_sport_title] = [dog]
                else: title_dog[dog_sport_title].append(dog)

            if i != len(missing_titles) - 1:
                self.randomized_delay()

        for title in title_dog:
            for dog in title_dog[title]:
                dog[self.KENNEL_NAME] = self.normalize_kennel_name(dog[self.KENNEL_NAME])
                self.save_dog(dog[self.KENNEL_NAME], dog[self.REGISTRATION_NUMBER])
                self.save_title(title, dog[self.REGISTRATION_NUMBER], dog[self.DATE])


if __name__ == '__main__':
    SearchTitles()

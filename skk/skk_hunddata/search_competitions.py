import json
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) # Appends the grandparent dir to the Python path.

from database import Database
from skk.SKK import SKK
from web_scraping import WebScraping


class SearchCompetitions(SKK):
    URL = 'https://hundar.skk.se/hunddata/Tavling_sok.aspx'
    start_year = 1994
    END_YEAR = WebScraping.get_next_year()
    START_MONTH = 1
    END_MONTH = 13
    prize_points_limit = None


    class Values(Enum):
        SELECT_DATE = 'bodyContent_txtTillfalle'
        SELECT_COMPETITION_TYPE = 'bodyContent_ddlTypkod'
        COMPETITION_TYPES = {
            'Bruksprov Int': {
                'sport': 6,
                'search_interval': [1998, 1999],
                'data_types': ['sport', 'klass', 'prize', 'points'],
            },
            'Bruksprov Nat': {
                'sport': 6,
                'search_interval': [1994],
                'data_types': ['sport', 'klass', 'prize', 'points'],
            },
            'Bruksprov Nat Plac.': {
                'sport': 6,
                'search_interval': [1999, 2000],
                'data_types': ['sport', 'klass', 'prize', 'points'],
            },
            'Lydnad Int.': {
                'sport': 5,
                'search_interval': [1993, 2016],
                'data_types': ['klass', 'points', 'prize'],
            },
            'Lydnad Nat.': {
                'sport': 5,
                'search_interval': [2010],
                'data_types': ['klass', 'points', 'prize'],
            },
            'Viltspårprov': {
                'sport': 14,
                'search_interval': [1994],
                'data_types': ['klass', 'prize'],
            },
        }
        SELECT_BREED = 'bodyContent_ddlRas'
        BUTTON_SEARCH = 'bodyContent_btnSearch'
        TABLE = "//table[@id='bodyContent_gridTavling']/tbody/child::*"
        TABLE2 = "//table[@class='table table-striped']/tbody/child::*"


    def __init__(self):
        super().__init__(self.URL)
        with open(Path(__file__).parent / 'prize_points_limit.json') as f:
            self.prize_points_limit = json.loads(f.read())

        try:
            self.__run()
            self.update_date()
        except Exception as exception:
            self.handle_exception(exception)
        finally:
            self.exit()


    def __normalize_sport(self, competition_type, sport):
        if 'Bruksprov' in competition_type: return sport
        elif 'Lydnad' in competition_type: return 'Lydnad'
        return 'Viltspår'


    def __normalize_klass(self, competition_type, klass, date):
        if 'Bruksprov' in competition_type:
            if klass == 'AKL': return 'Appellklass'
            elif klass == 'LKL': return 'Lägre klass'
            elif klass == 'HKL': return 'Högre klass'
            elif klass == 'EKL': return 'Elitklass'
        elif 'Lydnad' in competition_type:
            year = date.year
            if klass == 'Startklass': return klass
            elif klass == 'Klass 1':
                if year < 2017: return 'Startklass'
                return klass
            elif klass == 'Klass 2':
                if year < 2017: return 'Klass 1'
                return klass
            elif klass == 'Klass 3':
                if year < 2017: return 'Klass 2'
                return klass
            elif klass == 'EKL': return 'Klass 3'
        return klass


    def __normalize_prize(self, sport, klass, date, points, prize):
        def get_year():
            year = date.year
            if year >= 2017:
                if year >= 2023: return str(2023)
                return str(2017)
            return None


        try:
            if sport == 'Lydnad':
                for p, l in self.prize_points_limit[sport][get_year()][klass].items():
                    if l <= points: return p
            elif sport == 'Viltspår':
                for p, l in self.prize_points_limit[sport][klass].items():
                    if l == prize: return p
        except: pass # Can't use a finally clause.
        return None


    def __run(self):
        for competition_type, config in self.Values.COMPETITION_TYPES.value.items():
            sport = config.get('sport')
            db = Database()
            db.execute("""SELECT MAX(c.date) FROM competition_result2 AS c, klass2 AS k, sport2 AS s WHERE c.klass = k.id AND k.sport = s.id AND ((s.parent IS NULL AND s.id = %s) OR (s.parent IS NOT NULL AND s.parent = %s))""", (sport, sport, ))
            date = db.fetch_one()[0]
            db.close()
            start_year = self.start_year
            if date is not None:
                start_year = date.year
            search_interval = config.get('search_interval')
            data_types = config.get('data_types')
            competition_results = []

            self.wait_until(self.Values.SELECT_COMPETITION_TYPE.value) # Ensures that the select elements are present.
            select_type_of_competition = self.select(self.Values.SELECT_COMPETITION_TYPE.value)
            select_type_of_competition.select_by_visible_text(competition_type)
            select_breed = self.select(self.Values.SELECT_BREED.value)
            select_breed.select_by_visible_text(self.BREED)

            # For every year...
            for y in range(start_year if start_year != 1994 else search_interval[0], self.END_YEAR if len(search_interval) == 1 else search_interval[1]):
                # For every month...
                for m in range(self.START_MONTH, self.END_MONTH):
                    select_date = self.find_element(self.Values.SELECT_DATE.value)
                    select_date.clear()
                    select_date.send_keys(f"{y}-{str(m).rjust(2, '0')}")

                    search = self.find_element(self.Values.BUTTON_SEARCH.value)
                    search.click()

                    table_row_index = 0
                    last_page = False
                    new_page = False
                    while True:
                        table = None
                        i = 0
                        while True:
                            try:
                                table = self.find_elements(self.Values.TABLE.value)
                            finally:
                                if table is not None or i >= 6: break # If no rows.
                                sleep(1) # Gives the table a chance to load.
                                i += 1

                        row = None
                        try:
                            row = table[table_row_index]
                        except IndexError: # If only one page (i.e., no page navigator) and last row.
                            self.randomized_delay()
                            break

                        while 'white-space: nowrap;' in row.get_attribute('style'): # I.e., if first row (table heading).
                            table_row_index += 1
                            row = table[table_row_index]

                        if 'pagestyle' in row.get_attribute('class'): # I.e., if last row (page navigator).
                            table_row_index = 0
                            pages = self.find_elements('td/table/tbody/tr/child::*', parent=row)
                            number_of_pages = len(pages)
                            for i in range(0, number_of_pages):
                                # If last page:
                                if i == number_of_pages - 1:
                                    last_page = True
                                    break
                                else:
                                    page = pages[i]
                                    try:
                                        self.find_element('span', by=By.XPATH, parent=page) # Current page will contain a span element.
                                        next_page = self.find_element('a', by=By.XPATH, parent=pages[i + 1]) # Next page will thus be the next element in the list.
                                        next_page.click() # Navigates to the next page.
                                        new_page = True
                                        break
                                    except NoSuchElementException:
                                        continue
                            # Break the loop if last page:
                            if last_page: break
                            # Continue the loop from the beginning if next page:
                            elif new_page:
                                new_page = False
                                continue

                        link = self.find_element('td/a', By.XPATH, row) # Link to competition results page.
                        date = datetime.strptime(link.text[0:10], '%Y-%m-%d') # Extracts the competition date.
                        link.click() # Navigates to the competition results page.

                        # Within the competition results page:
                        self.wait_until(self.Values.TABLE2.value, By.XPATH) # Ensures that the table is present.
                        table2 = self.find_elements(self.Values.TABLE2.value)
                        competition_result = None
                        data_types_index = 0
                        for row2 in table2:
                            columns = self.find_elements('child::*', parent=row2)
                            if row2.get_attribute('class') == 'tabellrubrik': # I.e., if first row (table heading).
                                if competition_result is not None:
                                    competition_results.append(competition_result)
                                    data_types_index = 0
                                registration_number = self.find_element('a', By.XPATH, columns[0]).text
                                kennel_name = columns[1].text
                                competition_result = {
                                    'registration_number': registration_number,
                                    'kennel_name': kennel_name,
                                    'date': date,
                                }
                                for data_type in data_types: competition_result[data_type] = []
                            else:
                                values = columns[1].text.split(self.SEPARATOR)
                                value = values[len(values) - 1]
                                if 'Godkänt championat' in values[0]:
                                    if competition_result.get('title') is None: competition_result['title'] = [values[1]]
                                    else: competition_result['title'].append(values[1])
                                elif 'Domare' in value:
                                    data_types_index = 0
                                # Fix for obedience, where klass and placement are on the same column:
                                elif 'Lydnad' in competition_type and data_types_index == 0:
                                    competition_result[data_types[data_types_index]].append(values[0].split(':')[0])
                                    data_types_index += 1
                                # Irrelevant columns:
                                elif 'Lydnad' in competition_type and 'HP' in value: pass
                                elif competition_type == 'Viltspårprov' and ('Rörligt prov' in value or 'Ordinarie prov' in value or 'Godk skottprövning' in value or 'HP' in value): pass
                                # Fix for working dog trials, bug where sport is missing (id: 1998-04-18-011):
                                elif competition_type == 'Bruksprov Nat' and data_types_index == 0 and 'AKL' in value:
                                    competition_result[data_types[data_types_index]].append('SPÅR')
                                    data_types_index += 1
                                    competition_result[data_types[data_types_index]].append(value)
                                    data_types_index += 1
                                else:
                                    competition_result[data_types[data_types_index]].append(value)
                                    if data_types_index == len(data_types) - 1: data_types_index = 0 # Required considering that one dog can have multiple results from one competition.
                                    else: data_types_index += 1
                        if competition_result is not None: competition_results.append(competition_result)
                        self.back()
                        table_row_index += 1
                        self.randomized_delay()

            db = Database()
            for competition_result in competition_results:
                competition_result[self.KENNEL_NAME] = self.normalize_kennel_name(competition_result[self.KENNEL_NAME])
                self.save_dog(db, competition_result[self.KENNEL_NAME], competition_result[self.REGISTRATION_NUMBER])
                klass = competition_result['klass']
                sport = competition_result.get('sport')
                sport = sport if sport is not None else []
                points = competition_result.get('points')
                points = points if points is not None else []
                prize = competition_result.get('prize')
                prize = prize if prize is not None else []
                titles = competition_result.get('title')
                titles = titles if titles is not None else []
                for i in range(0, len(klass)):
                    if len(klass) == 0: break
                    klass2 = klass[i] if i < len(klass) else klass[len(klass) - 1]
                    klass2 = self.__normalize_klass(competition_type, klass2, competition_result[self.DATE])
                    sport2 = None if len(sport) == 0 else sport[i] if i < len(sport) else sport[len(sport) - 1]
                    sport2 = self.__normalize_sport(competition_type, sport2.title() if sport2 is not None else sport2)
                    points2 = str(0) if len(points) == 0 else points[i] if i < len(points) else points[len(points) - 1]
                    points2 = float(points2.replace(',', '.'))
                    prize2 = None if len(prize) == 0 else prize[i] if i < len(prize) else prize[len(prize) - 1]
                    prize2 = self.__normalize_prize(sport2, klass2, competition_result[self.DATE], points2, prize2)
                    print(competition_result[self.REGISTRATION_NUMBER], competition_result[self.KENNEL_NAME], competition_result[self.DATE], sport2, klass2, points2, prize2, sep='\n')
                    db.execute(
                        """SELECT * FROM competition_result2 WHERE klass = (SELECT id FROM klass2 WHERE klass = %s AND sport = (SELECT id FROM sport2 WHERE sport = %s)) AND dog = (SELECT id FROM dog2 WHERE kennel_name = %s) AND date = %s AND points = %s AND prize = %s""" if prize2 is not None else """SELECT * FROM competition_result2 WHERE klass = (SELECT id FROM klass2 WHERE klass = %s AND sport = (SELECT id FROM sport2 WHERE sport = %s)) AND dog = (SELECT id FROM dog2 WHERE kennel_name = %s) AND date = %s AND points = %s AND prize IS NULL""",
                        (klass2, sport2, competition_result[self.KENNEL_NAME], competition_result[self.DATE], points2, prize2) if prize2 is not None else (klass2, sport2, competition_result[self.KENNEL_NAME], competition_result[self.DATE], points2),
                    )
                    if db.fetch_one() is None:
                        db.execute(
                            """INSERT INTO competition_result2(klass, dog, date, points, prize) VALUES ((SELECT id FROM klass2 WHERE klass = %s AND sport = (SELECT id FROM sport2 WHERE sport = %s)), (SELECT id FROM dog2 WHERE kennel_name = %s), %s, %s, %s)""",
                            (klass2, sport2, competition_result[self.KENNEL_NAME], competition_result[self.DATE], points2, prize2),
                        )
                for title in titles:
                    # Ensures that the title is a valid one (i.e., not a show title):
                    dog_sport_title = self.validate_title(title)
                    if dog_sport_title is not None:
                        print(dog_sport_title)
                        self.save_title(db, dog_sport_title, competition_result[self.REGISTRATION_NUMBER], competition_result[self.DATE])
            db.close()


if __name__ == '__main__':
    SearchCompetitions()

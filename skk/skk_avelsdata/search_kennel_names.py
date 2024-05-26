import os
import sys
from enum import Enum

from selenium.webdriver.common.by import By

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # Appends the parent dir to the Python path.

from skk_hunddata import SkkHunddata


class SearchKennelNames(SkkHunddata):
    URL = 'https://hundar.skk.se/avelsdata/Flikar.aspx?sida=Ras_info&id=679'


    class Values(Enum):
        LINK = 'Ras_listor'
        SELECT_TYPE = 'bodyContent_TabContainerFlik_R679_ctl01_ddlTyp'
        KENNEL_NAME = 'AKTUELLA'
        SHOW = 'bodyContent_TabContainerFlik_R679_ctl01_btnVisa'
        TABLE = "//table[@id='bodyContent_TabContainerFlik_R679_ctl01_dgKennelnamn']/tbody/child::*"
        HEADER = 'datagridHeader'
        COLUMN = 'td/span'


    def __init__(self):
        super().__init__(self.URL)

        try:
            self.__run()
        except Exception as exception:
            self.handle_exception(exception)
        finally:
            self.exit()


    def __run(self):
        self.wait_until(self.Values.LINK.value)
        link = self.find_element(self.Values.LINK.value)
        link.click()

        self.wait_until(self.Values.SELECT_TYPE.value)
        select_type = self.select(self.Values.SELECT_TYPE.value)
        select_type.select_by_value(self.Values.KENNEL_NAME.value)

        self.wait_until(self.Values.SHOW.value)
        show = self.find_element(self.Values.SHOW.value)
        show.click()

        self.wait_until(self.Values.TABLE.value, By.XPATH)
        table = self.find_elements(self.Values.TABLE.value)
        for row in table:
            if row.get_attribute('class') != self.Values.HEADER.value:
                kennel_name = self.find_element(self.Values.COLUMN.value, By.XPATH, row).text
                self.execute(
                    """SELECT * FROM kennel2 WHERE name = %s""",
                    (kennel_name, ),
                )
                if self.fetch_one() is None:
                    self.execute(
                        """INSERT INTO kennel2(name) VALUES (%s)""",
                        (kennel_name, ),
                    )


if __name__ == '__main__':
    SearchKennelNames()


from dataclasses import dataclass
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By


@dataclass
class ParkFactor:
    id: int
    venue_name: str
    factor: int


class InvalidHeaderValueCount(Exception):
    """Exception raised when the number of header fields does not match the number of value fields in a table."""
    def __init__(self, header_count: int, value_count: int, table_name: str):
        self.header_count = header_count
        self.value_count = value_count
        self.table_name = table_name
        super().__init__(self.__str__())

    def __str__(self):
        return f"The number of header fields {self.header_count} does not equal the number of value fields {self.value_count} in the table {self.table_name}"


def get_park_factors(year: int, browser: selenium.webdriver.Firefox = None) -> {str: ParkFactor}:
    url = str.format("https://baseballsavant.mlb.com/leaderboard/statcast-park-factors?type=year&year={}&batSide=&stat=index_wOBA&condition=All&rolling=3&parks=mlb", year)

    if browser is None:
        browser = webdriver.Firefox()

    browser.get(url)

    table_name = "parkFactors"
    factors_table = browser.find_element(By.ID, table_name)
    header = factors_table.find_element(By.TAG_NAME, "thead")
    header_names = [x.text for x in header.find_elements(By.TAG_NAME, "th")]

    table_body = factors_table.find_element(By.TAG_NAME, "tbody")
    table_rows = table_body.find_elements(By.CLASS_NAME, "default-table-row   ")
    output_dict = dict()
    for row in table_rows:
        values = [x.text for x in row.find_elements(By.TAG_NAME, "td")]
        if len(values) != len(header_names):
            raise InvalidHeaderValueCount(len(header_names), len(values), table_name)
        table_dict = dict(zip(header_names, values))
        output_dict[table_dict["Team"]] = ParkFactor(id=int(row.get_attribute("data-id")), venue_name=table_dict["Venue"], factor=int(table_dict["Park Factor"]))

    return output_dict

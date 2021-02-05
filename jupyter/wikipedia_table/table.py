""" This module us used to model some tables in https://en.wikipedia.org/

Example:
   To dump to a CSV file run::

        $ python table.py

"""

import configparser
import csv
import logging
import os
import re
from typing import AnyStr, List

import coloredlogs
import numpy as np
import requests
from bs4 import BeautifulSoup
from dateparser.search import search_dates
from dateutil.parser import parse as dparse

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")
coloredlogs.install(milliseconds=True)


def clean_text(text: AnyStr):
    text = re.sub("<br />", " ", text)
    text = re.sub("<br>", " ", text)
    text = re.sub("\xa0", " ", text)
    return text


class BaseTableParser(object):
    def __init__(self, *args, **kwargs):
        self.host = kwargs.pop("host")
        self.url = f'{self.host}{kwargs.pop("path")}'
        self.table_index = kwargs.pop("table_index")
        html_classname = kwargs.pop("html_classname")

        self.rows = self.get_table(html_classname).findAll("tr")
        self.num_cols = max([len(r.findAll(["th", "td"])) for r in self.rows])
        self.num_rows = len(self.rows)
        self.matrix = np.array(
            [
                self._get_empty_list(self.num_cols)
                for i in range(self.num_rows)
            ],
            dtype="<U124",
        )

    def _get_empty_list(self, cols: int):
        return ["" for j in range(cols)]

    def get_table(self, class_name: AnyStr):
        """
        get table from wiki url
        :return:
        """
        response = requests.get(self.url)
        text = clean_text(response.text)
        soup = BeautifulSoup(text, "lxml")

        tables = soup.findAll("table", {"class": class_name})

        return tables[self.table_index]

    def is_date(self, string: AnyStr, fuzzy: bool = False) -> bool:
        """
        Can the string be converted into a date?
        :param string:
        :param fuzzy:
        :return:
        """
        try:
            dparse(string, fuzzy=fuzzy)
            return True
        except ValueError:
            return False

    def get_subset(self, col_indexes: List):
        return self.matrix[:, col_indexes]

    def delete_cols(self, cols: list):
        """
        Remove cols in matrix by list of col indexes
        :param cols:
        :return:
        """

        self.matrix = np.delete(self.matrix, cols, axis=1)
        self.headers = np.delete(self.headers, cols)
        self.num_cols = len(self.matrix[0])

    def delete_rows(self, rows: List):
        """
        Remove rows in matrix by list of row indexes
        :param rows:
        :return:
        """
        self.matrix = np.delete(self.matrix, rows, axis=0)
        self.num_rows = len(self.matrix)

    def add_rows(self):
        pass

    def add_cols(
        self,
        num_cols: int = 1,
        new_cols: np.array = None,
        dtype: AnyStr = "<U124",
    ):
        """
        Add new cols to right of matrix
        :param num_cols: number of cols to add
        :param new_cols: np array to add
        :param dtype:
        :return:
        """

        if new_cols is None:
            new_cols = np.array(
                [self._get_empty_list(num_cols) for i in range(self.num_rows)],
                dtype=dtype,
            )

        self.matrix = np.append(self.matrix, new_cols, axis=1)
        self.num_cols = len(self.matrix[0])

    def distinct_rows(self, inplace: bool = False):
        """
        Create a matrix of distinct rows from self.matrix
        :param inplace:
        :return:
        """
        logger.info("Getting unique rows")
        if inplace:
            self.matrix = np.unique(self.matrix, axis=0)
            self.num_rows = len(self.matrix)
        else:
            return np.unique(self.matrix, axis=0)

    def get_column(self, index: int):
        """
        Get a given column
        :param index:
        :return:
        """
        return self.matrix[:, index]

    def sort_by_col(self, col_index, inplace=False):
        """

        :param col_index:
        :param inplace:
        :return:
        """
        if inplace:
            self.matrix = self.matrix[np.argsort(self.matrix[:, col_index])]
            return self.matrix

        else:
            return self.matrix[np.argsort(self.matrix[:, col_index])]


class PrimeMinister(BaseTableParser):
    def __init__(self, *args, **kwargs):
        self.host = kwargs.pop("host")
        self.path = kwargs.pop("path")
        self.url = f"{self.host}{self.path}"
        self.birthday = None
        self.died = None
        self.info = self.get_pm_info()
        self.monarchs = []
        super().__init__(
            host=self.host,
            path=self.path,
            table_index=0,
            html_classname="infobox vcard",
        )
        self.parse()

    def get_pm_info(self):
        """
        Call a wikipedia url and return a table containing
        the details of a persons life
        :return:
        """
        logger.info("getting the PM page for %s", self.path)
        response = requests.get(self.url)
        text = clean_text(response.text)
        soup = BeautifulSoup(text, "lxml")
        return soup.find("table", {"class": "infobox vcard"})

    def parse(self):
        """
        Parse the table on the right hand side or a wiki page that
        holds the details of a person
        :return:
        """

        logger.info("parseing the PM page for %s", self.path)

        data = self.info.findAll("tr", text=True)
        for tr in self.info.findAll("tr"):
            invalid_items = ["\n", " ", "\t"]
            txt = tr.getText(separator="|")
            cells = [x for x in txt.split("|") if x not in invalid_items]

            # very cumbersome and slow, but there is some edge cases where unicode characters are near the date
            # https://en.wikipedia.org/wiki/Spencer_Compton,_1st_Earl_of_Wilmington has no month & day,
            # only the year and &thinspace; unicode next to it

            if "Born" in cells and self.birthday is None:

                # TODO: this is very slow, find a better way, this will find
                #  dates for the likes of 'now', 'today' etc
                dates = [
                    i
                    for i in map(
                        lambda x: search_dates(
                            (x.encode("ascii", "ignore")).decode("utf-8")
                        ),
                        cells,
                    )
                    if i is not None
                ]

                if dates:
                    # there may be multiple, but we want the first item in dates,
                    # then search_dates returns a list of tuples,
                    # so get the last item (we expect one only anyway) and get second item in tuple
                    self.birthday = dates[0][-1][-1]
            elif "Died" in cells and self.died is None:
                # TODO: this is very slow, find a better way
                dates = [
                    i
                    for i in map(
                        lambda x: search_dates(
                            (x.encode("ascii", "ignore")).decode("utf-8")
                        ),
                        cells,
                    )
                    if i is not None
                ]
                if dates and self.died is None:
                    self.died = dates[0][-1][-1]

            elif "Monarch" in cells and not self.monarchs:
                self.monarchs = cells[1:]


class PrimeMinisterTerms(BaseTableParser):
    """
    Table object to represent data from wikipedia table
    """

    def __init__(self, *args, **kwargs):
        parse = kwargs.pop("parse")
        super().__init__(*args, **kwargs)
        self.headers = self.matrix[-1]
        self.pm_info = {}
        if parse:
            self.parse()

    def parse(self):
        """
        Parse the table
        :return:
        """
        # TODO: Some optimisation, this is really inefficient, but it works
        logger.info("parsing for all PM's from %s ", self.url)
        for _row_num, row in enumerate(self.rows):
            sup = row.find(["sup"])
            if sup:
                sup.decompose()
            row_items = row.findAll(["td", "th"])
            for cell_index, cell in enumerate(row_items):

                # get the rowspams and/or colspans,
                # default to 1 if neither exists
                col_span = int(cell.get("colspan", 1))
                row_span = int(cell.get("rowspan", 1))
                a_tag = cell.find("a")

                href = None if not a_tag else a_tag["href"].replace(",", "¬")
                l = 0
                for rs in range(row_span):
                    # Go to the first empty cell
                    while self.matrix[_row_num + rs][cell_index + l]:
                        l += 1
                    for cs in range(col_span):
                        cell_n = cell_index + l + cs
                        row_n = _row_num + rs
                        # in some cases the colspan can overflow the table, in
                        # those cases just get the last item
                        cell_n = min(cell_n, len(self.matrix[row_n]) - 1)

                        # using † as a separator of tags because whitespace won't work as there
                        # is whitespace in a number of cells
                        _text = cell.get_text(
                            strip=True, separator="†"
                        ).replace("&nbsp;", " ")

                        text = _text if not a_tag else f"{_text}|{href}"
                        # inserting a character as we are
                        # only filling empty un accounted for cells with data
                        text = text if len(text) else text + "?"

                        self.matrix[row_n][cell_n] += text

        # remove cols not needed.
        self.delete_cols([8, 10])

        rows_to_keep = []

        for index, row in enumerate(self.matrix):
            from_date = row[3].replace("†", " ")
            to_date = row[4].replace("†", " ")
            to_delete = True
            if self.is_date(from_date) and self.is_date(to_date):
                row[3] = dparse(from_date)
                row[4] = dparse(to_date)
                to_delete = False

            elif self.is_date(from_date) and "incumbent" in to_date.lower():
                row[3] = from_date
                row[4] = "incumbent"
                to_delete = False

            if not to_delete:
                rows_to_keep.append(index)
                pm_details = row[2]
                details, pm_wiki_path = pm_details.split("|")
                pm_wiki_path = pm_wiki_path.replace("¬", ",").strip()
                details = details.split("†")
                name = ""
                title = ""
                if details:
                    if details[0].lower() == "sir":
                        name = f"{details.pop(1)}"
                    else:
                        name = f"{details.pop(0)}"

                    # last item may be title years of birth/death, or MP for
                    # constituency
                    title = details.pop(0)
                    year_regex = r"\(?(\d{4}|born|MP for)(\D\d{4}\)?)?"
                    if bool(re.search(year_regex, title)):
                        title = ""

                party, _ = row[7].split("|")
                party = party.split("†")[0]

                row[0] = name.strip()
                row[1] = title.strip()
                row[2] = pm_wiki_path
                row[5] = party.strip()
                _pm_info_cache = self.pm_info.get(pm_wiki_path, {})
                if not _pm_info_cache:
                    pm_info = PrimeMinister(
                        host=self.host,
                        path=pm_wiki_path,
                        x=0,
                        html_classname="infobox vcard",
                    )
                    _pm_info_cache = {
                        "dob": pm_info.birthday,
                        "death": pm_info.died,
                        "monarchs": pm_info.monarchs,
                    }
                    self.pm_info[pm_wiki_path] = _pm_info_cache

                row[-2] = _pm_info_cache["dob"]
                row[-1] = _pm_info_cache["death"]
                row[6] = "†".join([x for x in _pm_info_cache["monarchs"]])

        self.delete_rows(
            [
                y
                for y in [x for x in range(len(self.matrix))]
                if y not in rows_to_keep
            ]
        )

        self.distinct_rows(inplace=True)

        self.sort_by_col(3, True)
        ids = np.array([[j] for j in range(1, self.num_rows + 1)])
        self.add_cols(new_cols=ids)

    def dump_to_file(self, file_path: str = "table.csv", mode: str = "w"):
        """
        Dump the table data to a CSV file
        :param mode:
        :param data:
        :param file_path:
        :return:
        """
        logger.info("Dumping to file")
        with open(file_path, mode=mode) as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            for row in self.matrix:
                writer.writerow(row)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    ini_path = os.path.join(os.getcwd(), "config.ini")
    config.read(ini_path)
    host = config["WIKI"]["wiki_host"]

    terms = PrimeMinisterTerms(
        host=host,
        path=config["WIKI"]["table_path"],
        html_classname="wikitable",
        parse=True,
        table_index=1,
    )

    terms.dump_to_file()

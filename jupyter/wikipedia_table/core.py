"""This module us used to scrape data from the table containing the prime ministers in
https://en.wikipedia.org/wiki/List_of_prime_ministers_of_the_United_Kingdom

Example:
   To run the application run the command below::

        $ python core.py

"""

import configparser
import datetime
import logging
import os

import coloredlogs
import numpy as np
from dateutil.parser import parse as dparse

from database import MariaDBConnector
from table import PrimeMinisterTerms

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")
coloredlogs.install(milliseconds=True)

config = configparser.ConfigParser()

# Get the absolute path of ini file by doing os.getcwd() and joining it to
# config.ini
ini_path = os.path.join(os.getcwd(), "config.ini")
config.read(ini_path)

SEPARATOR = "†"
TABLE_COLUMN = {
    "name": 0,
    "title": 1,
    "wiki": 2,
    "start_term": 3,
    "end_term": 4,
    "party": 5,
    "monarch": 6,
    "dob": 7,
    "died": 8,
}

TITLES = {
    "Duke": "Duke",
    "Earl": "Earl",
    "Lord": "Lord",
    "Marquesses": "Marquesses",
    "Viscount": "Viscount",
    "Baron": "Baron",
    "Sir": "Knight",
    "Dame": "Dame",
}


def calculate_total_time(years, months, days, total_days):
    """presume 365 days in a year, 30 days in a month"""

    months += days // 30
    days = days % 30

    years += months // 12
    months = months % 12
    _total_days = (years * 365) + (months * 30) + days

    if _total_days < total_days:
        days += total_days - _total_days
        return calculate_total_time(years, months, days, total_days)

    elif _total_days > total_days:
        _days = _total_days - total_days
        _months = months
        _years = years
        if _days < 1:
            _days += 30
            _months = -1
            if _months < 1:
                _years -= 1
                _months += 12

            days = _days
            months = _months
            years = _years

        if _days < 1:
            _days += 30
            months = months - 1
            days = days

    return years, months, days, _total_days


def get_title(alias: str):
    """
    Get a title from a string
    :param alias:
    :return:
    """
    title = ""
    for k, v in TITLES.items():
        if k in alias:
            return v
    return title


def save_not_exists_single_column(
        table: str, column: str, inserts: iter, db_config: dict
):
    """
    insert into db if not exists
    :param table:
    :param column:
    :param inserts:
    :param db_config:
    :return:
    """

    with MariaDBConnector(**db_config) as cursor:
        logger.info("saving data to %s table ...", table)

        query = f"Select *  from {table};"
        cursor.execute(query)
        results = {v: k for k, v in cursor.fetchall()}
        _inserts = inserts
        inserts = [(x,) for x in inserts if x not in results.keys()]

        if inserts:
            query = f"INSERT INTO {table} ({column})  VALUES " + ",".join(
                "( %s)" for x in inserts
            )
            cursor.execute(query, [x for y in inserts for x in y])
            cursor.commit()

            query = f"Select *  from {table};"
            cursor.execute(query)
            results = {v: k for k, v in cursor.fetchall()}
    return results


def save_or_update_pm_data(data: np.array, parties: dict, db_config: dict):
    """
    Save or update the prime minister table with data
    :param data:
    :param parties:
    :param db_config:
    :return:
    """
    inserts = {}

    for pm in data:
        name = pm[0]
        _pm = inserts.get(name, None)

        if _pm is None:
            inserts[name] = pm
        elif (not _pm[1]) and pm[1] and (_pm[3] == pm[3]):
            inserts[name] = pm
    index = [x for x in range(1, len(data) + 1)]

    data = [
        (
            x[0],  # name
            x[1],  # alias
            get_title(x[1]),  # title
            parties[x[2]],  # party
            datetime.datetime.strptime(x[3][:10], "%Y-%m-%d"),  # born
            None
            if x[4] == "None"
            else datetime.datetime.strptime(x[4][:10], "%Y-%m-%d"),  # died
        )
        for x in inserts.values()
        if x[0].lower != "sir"
    ]

    data = [(index.pop(0),) + x for x in sorted(data, key=lambda x: x[4])]

    with MariaDBConnector(**db_config) as cursor:
        logger.info("saving data to prime_minister table...")
        sql = """INSERT INTO prime_minister (id,name, alias, title, party_id, birth_date ,death_date)
                 values (%s,%s,%s,%s,%s,%s,%s)
                 ON DUPLICATE KEY UPDATE
                     name=name,
                     title=title,
                     alias=alias,
                     party_id=party_id,
                     birth_date=birth_date,
                     death_date=death_date;"""

        cursor.executemany(sql, data)
        cursor.commit()
        query = "Select *  from prime_minister;"
        cursor.execute(query)
        return {x[1].strip(): x for x in cursor.fetchall()}


def save_or_update_pm_terms(data: np.array, db_config: dict):
    inserts = [
        (
            term[-1],
            dparse(term[3]),  # start
            None if term[4] == "incumbent" else dparse(term[4]),  # end
            term[0],  # pm id
            len(term[1]),  # did the PM have a title? True/False
        )
        for term in data
    ]

    with MariaDBConnector(**db_config) as cursor:
        logger.info("saving data to prime_minister_term table...")
        sql = """INSERT INTO prime_minister_term (id,start_date, end_date,  prime_minister_id,  had_title)
                 values (%s,%s,%s,%s,%s)
                 ON DUPLICATE KEY UPDATE
                     start_date=start_date,
                     end_date=end_date,
                     prime_minister_id=prime_minister_id,
                     had_title=had_title;"""

        cursor.executemany(sql, inserts)
        cursor.commit()
        sql = """SELECT * FROM prime_minister_term ;"""

        cursor.execute(sql)
        return cursor.fetchall()


def save_or_update_monarch_terms(data: np.array, db_config: dict):
    inserts = []

    for row in data:
        for monarch_id in row[TABLE_COLUMN["monarch"]].split(SEPARATOR):
            inserts.append((row[-1], (int(monarch_id))))

    with MariaDBConnector(**db_config) as cursor:
        logger.info("saving data to term_monarch table...")
        sql = """INSERT IGNORE  INTO term_monarch (term_id, monarch_id) values (%s,%s);"""
        cursor.executemany(sql, inserts)
        cursor.commit()


def main():
    """Wrapper around the main execution of the module"""
    config = configparser.ConfigParser()
    ini_path = os.path.join(os.getcwd(), "config.ini")
    config.read(ini_path)
    host = config["WIKI"]["wiki_host"]
    db_config = config["DATABASE"]

    terms = PrimeMinisterTerms(
        host=host,
        path=config["WIKI"]["table_path"],
        html_classname="wikitable",
        parse=True,
        table_index=1,
    )

    # monarchs are stored in the matrix as text separated values.
    # a term in office may overlap multiple monarchy's
    # TODO: simplify this
    monarchs = list(
        set(
            [
                i
                for j in map(
                lambda x: [x]
                if SEPARATOR not in x
                else x.split(SEPARATOR),
                terms.get_column(TABLE_COLUMN["monarch"]),
            )
                for i in j
            ]
        )
    )
    parties = terms.get_column(TABLE_COLUMN["party"])

    monarchs = save_not_exists_single_column(
        "monarch", "title", monarchs, db_config
    )
    parties = save_not_exists_single_column(
        "party", "party_name", np.unique(parties).tolist(), db_config
    )

    pm_data = terms.get_subset(
        [
            TABLE_COLUMN["name"],
            TABLE_COLUMN["title"],
            TABLE_COLUMN["party"],
            TABLE_COLUMN["dob"],
            TABLE_COLUMN["died"],
        ]
    )

    pm_data = save_or_update_pm_data(pm_data, parties, db_config)

    for row in terms.matrix:
        rm_monarchs = SEPARATOR.join(
            [
                str(monarchs[x])
                for x in row[TABLE_COLUMN["monarch"]].split(SEPARATOR)
            ]
        )
        row[TABLE_COLUMN["monarch"]] = rm_monarchs
        row[TABLE_COLUMN["party"]] = parties[row[TABLE_COLUMN["party"]]]
        row[TABLE_COLUMN["name"]] = pm_data[row[TABLE_COLUMN["name"]]][0]

    save_or_update_pm_terms(terms.matrix, db_config)
    save_or_update_monarch_terms(terms.matrix, db_config)

    logger.info("The data has been scraped and the database is populated...")


if __name__ == "__main__":
    main()

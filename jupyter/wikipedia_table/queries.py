import codecs
import configparser
import csv
import logging
import os
import re

import coloredlogs
import lxml
import numpy as np
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dparse

from database import MariaDBConnector

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")
coloredlogs.install(milliseconds=True)


CREATE_DATABASE = "CREATE DATABASE IF NOT EXISTS assignment2;"


def create_new_user(conn, username, password):
    return f"CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';"


CREATE_TABLE_MONARCH = """
CREATE TABLE IF NOT EXISTS monarch (
    monarch_id  INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL);
    """

CREATE_TABLE_PARTY = """
CREATE TABLE IF NOT EXISTS party (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL DISTINCT);
    """

CREATE_TABLE_PRIME_MINISTER = """
CREATE TABLE IF NOT EXISTS prime_minister (
    id INT  AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    birth_date DATE NOT NULL,
    death_date DATE,
    party_id INT NOT NULL,
    CONSTRAINT `fk_party_prime_minister`
    FOREIGN KEY (party_id) REFERENCES party (id)
    ON DELETE CASCADE
    ON UPDATE RESTRICT);
    """

CREATE_TABLE_TERM = """
CREATE TABLE IF NOT EXISTS prime_minister_term (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL);
    start_date NOT NULL,
    end_date DATE);
    prime_minister_id INT  NOT NULL,
    CONSTRAINT `fk_prime_minister_term_prime_minister`
    FOREIGN KEY (prime_minister_id) REFERENCES prime_minister (id)
    ON DELETE CASCADE
    ON UPDATE RESTRICT);
    """


if __name__ == "__main__":
    config = configparser.ConfigParser()
    ini_path = os.path.join(os.getcwd(), "config.ini")
    config.read(ini_path)
    db_config = config["DATABASE"]
    host = config["DATABASE"]["host"]
    username = config["DATABASE"]["username"]
    password = config["DATABASE"]["password"]
    database = config["DATABASE"]["database"]
    port = config["DATABASE"]["port"]
    db_conn = MariaDBConnector(**db_config)

"""
Basic database connector
"""

import logging
import sqlite3
import sys
from typing import AnyStr, Union

import coloredlogs

import mariadb

logger = logging.getLogger(__name__)
coloredlogs.install(level="DEBUG")
coloredlogs.install(milliseconds=True)


# TODO: Add Postgres connector and other DB's


class SQLiteConnector(object):
    """
    Class for handling MySQLite connections
    """

    def __init__(self, dbfname: AnyStr):
        """Add the database filename to the object."""
        self.dbfilename = dbfname

    def __enter__(self):
        """Connect to database and create a DB cursor."""

        self._conn = sqlite3.connect(self.dbfilename)
        self._cursor = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):

        try:
            logger.info("commit to db")
            self.connection.commit()
        except Exception as e:
            logger.exception("Failed to commit to db %s", e)
            self.connection.rollback()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def executemany(self, sql, params=None):
        self.cursor.executemany(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def query(self, sql, params=None):
        self.cursor.execute(sql, params or ())
        return self.fetchall()


class MariaDBConnector(SQLiteConnector):
    """
    Class for handling MariaDB connections
    """

    def __init__(
        self,
        host: AnyStr,
        username: AnyStr,
        password: AnyStr,
        database: AnyStr,
        port: Union[str, int] = 3306,
    ):
        """

        :param host:
        :param username:
        :param password:
        :param database:
        :param port:
        """

        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = int(port)

    def __enter__(self):
        """Connect to database and create a DB cursor."""

        try:
            self._conn = mariadb.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.database,
                port=self.port,
            )
            self._cursor = self._conn.cursor()
        except mariadb.Error as e:
            logger.exception("db connection error %s %s", self.host, e)
            sys.exit(1)
        logger.info("connection opened to db %s", self.host)
        return self

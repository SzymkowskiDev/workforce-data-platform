import sqlite3
import os
import logging


db = "wdp_database.db"
logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        """create connection to database"""
        self.connection = sqlite3.connect(os.getenv(db))
        self.cursor = self.connection.cursor()

    def __exit__(self):
        """close connection to database after function usage"""
        self.connection.close()

    def insert_sql(self, table, *values):
        """insert values into table

        :param table: name of db table
        :param values: values to insert
        :return: inserted values
        """
        self.cursor.execute(f"INSERT INTO '?' VALUES ({','.join(['?' for _ in values])})", (table, values))
        self.connection.commit()
        logger.debug(f'Row inserted to {table} ')

    def select_sql(self, table, condition, value):
        """select single condition equals value

        :param table: name of db table
        :param condition: name of WHERE statement condition
        :param value: value of WHERE statement
        :return: all rows which fulfill the WHERE statement
        """
        self.cursor.execute(f"SELECT * FROM '?' WHERE {f'?=?'}", (table, condition, value))
        result = self.cursor.fetchall()
        return logger.debug(result)

    def update_sql(self, table, id_column_name, id_num, *values):
        """update multiple values by id

        :param table: name of db table
        :param id_column_name: name of id column of selected table
        :param id_num: id number to update
        :param values: values to update
        :return: updated row
        """
        self.cursor.execute(f"UPDATE '?' SET ({','.join('?' for _ in values)}) WHERE '?'='?'",
                            (table, values, id_column_name, id_num))
        self.connection.commit()
        logger.debug(f"ID {id_num} updated by {','.join('?' for _ in values)} in {table}", values)

    def delete_sql(self, table, id_column_name, id_num):
        """name of db table

        :param table: name of db table
        :param id_column_name: name of id column of selected table
        :param id_num: id number to delete
        :return: deleted row
        """
        self.cursor.execute(f"DELETE FROM '?' WHERE '?'='?'", (table, id_column_name, id_num))
        self.connection.commit()
        logger.debug(f'ID {id_num} deleted from {table}')

    def select_sql_multiple(self, table, **conditions):
        """select multiple condition equals value

        :param table: name of db table
        :param conditions: dictionary of conditions and values for WHERE statement
        :return: all rows which fulfill the WHERE statement
        """
        values = conditions.values()
        columns = conditions.keys()
        result = self.cursor.fetchall()
        self.cursor.execute(
            f"SELECT * FROM '?' WHERE {' AND '.join(f'?=?' for _ in columns)}", (table, tuple(columns), tuple(values))
        )
        return logger.debug(result)

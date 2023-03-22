import sqlite3


class Database:
    def __init__(self, database_name="wdp_database.db"):
        # create connection to database
        self.connection = sqlite3.connect("wdp_database.db")
        self.cursor = self.connection.cursor()

    def __del__(self):
        # close connection to database after function usage
        self.connection.close()

    def insert_sql(self, table, *values):
        # insert values into table
        self.cursor.execute(f"INSERT INTO {table} VALUES ({','.join(['?' for _ in values])})", values)
        self.connection.commit()
        print(f'Row inserted to {table} ')

    def select_sql(self, table, condition, value):
        # select single condition equals value
        self.cursor.execute(f"SELECT * FROM {table} WHERE {f'{condition}=?'}", value)
        return print(self.cursor.fetchall())

    def update_sql(self, table, id_column_name, id_num, *values):
        # update multiple values by id
        self.cursor.execute(f"UPDATE {table} SET ({','.join(['?' for _ in values])}) WHERE {id_column_name}={id_num}",
                            values)
        self.connection.commit()
        print(f"ID {id_num} updated by {','.join(['?' for _ in values])} in {table}", values)

    def delete_sql(self, table, id_column_name, id_num):
        # delete record by id
        self.cursor.execute(f"DELETE FROM {table} WHERE {id_column_name}={id_num}")
        self.connection.commit()
        print(f'ID {id_num} deleted from {table}')

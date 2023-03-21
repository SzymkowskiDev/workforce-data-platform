import sqlite3

connection = sqlite3.connect("wdp_database.db")
cursor = connection.cursor()


def create_employee(employee):
    with connection:
        cursor.execute("INSERT INTO Employees VALUES (:employee_id,:first_name, :last_name, \
        :avatar_url, :job_title, :joined_on, :email, :phone, :birthday, :country, :city, :project_id, \
        :last_role, :role_preferred, :salary, :specification")
        return print('Record created')


def read_employee(employee):
    with connection:
        cursor.execute("SELECT * FROM Employees WHERE employee_id=:employee_id")
        return cursor.fetchall()


def delete_employee(employee):
    with connection:
        cursor.execute("DELETE FROM Employees WHERE employee_id=:employee_id")
        return print('Record deleted')


connection.close()

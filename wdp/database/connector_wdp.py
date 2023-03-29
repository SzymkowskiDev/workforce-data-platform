import sqlite3

valid_table = ('Employees', 'Clients', 'Projects', 'Skills', 'Roles', 'EmployeesSkillsRelations')
valid_column = ('employee_id', 'first_name', 'last_name', 'avatar_url', 'job_title', 'joined_on', 'email',
                'phone_number', 'birthday', 'country', 'city', 'project_id', 'last_role', ' role_preferred',
                'salary', 'specification', 'role_id', 'role_name', 'skill_id', 'skill_name', 'experience', 'client_id',
                'client_name', 'business', 'project_name', 'started_on', 'deadline_on', 'budget')


class Database:
    def __init__(self):
        """create connection to database"""
        self.connection = sqlite3.connect("wdp_database.db")
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")

    def __exit__(self):
        """close connection to database after function usage"""
        self.connection.close()

    def select(self, table, condition, value):
        """Select all from tabel where condition = value

        :param table: table name
        :param condition: column name for where condition
        :param value: value for where condition
        :return: select results
        """
        if condition not in valid_column:
            raise ValueError('Wrong condition')
        if table not in valid_table:
            raise ValueError('Wrong condition')
        self.cursor.execute(f"""SELECT * FROM {table} WHERE {condition} = ?""", (value,))
        result = self.cursor.fetchall()
        return print(result)

    def update(self, table, set_condition, where_condition, set_value, where_value):
        """

        :param table: table name
        :param set_condition: column name for update value
        :param where_condition: column name for where condition
        :param set_value: value for update
        :param where_value: value for where condition
        """
        if set_condition and where_condition not in valid_column:
            raise ValueError('Wrong condition')
        if table not in valid_table:
            raise ValueError('Wrong condition')
        self.cursor.execute(f"""UPDATE {table} SET {set_condition} = ? WHERE {where_condition} = ?""", (set_value,
                                                                                                        where_value))
        self.connection.commit()

    def delete(self, table, condition, value):
        """

        :param table: table name
        :param condition: column name for where condition
        :param value: value for where condition
        """
        if condition not in valid_column:
            raise ValueError('Wrong condition')
        if table not in valid_table:
            raise ValueError('Wrong condition')
        self.cursor.execute(f"""DELETE FROM {table} WHERE {condition} = ?""", (value,))
        self.connection.commit()

    def insert_one_employee(self, employee_id, first_name, last_name, avatar_url, job_title, joined_on,
                            email, phone_number, birthday, country, city, project_id, last_role, role_preferred,
                            salary, specification):
        """Insert one position into Employees table

        :param employee_id: integer
        :param first_name: first_name
        :param last_name: last_name
        :param avatar_url: avatar_url
        :param job_title: job_title
        :param joined_on: date "YYYY-MM-DD"
        :param email: email
        :param phone_number: 9 numbers starting with +
        :param birthday: date "YYYY-MM-DD"
        :param country: country name
        :param city: city name
        :param project_id: project_id
        :param last_role: role_id
        :param role_preferred: role_id
        :param salary: integer
        :param specification: specification
        """
        self.cursor.execute("""INSERT INTO Employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (employee_id, first_name, last_name, avatar_url, job_title, joined_on, email, phone_number,
                             birthday, country, city, project_id, last_role, role_preferred, salary, specification,))
        self.connection.commit()

    def insert_many_employees(self, emp_data):
        """Insert many positions into Employees table

        :param emp_data: employees dataset
        """
        self.cursor.execute('BEGIN TRANSACTION')
        for x in emp_data:
            self.cursor.execute("""INSERT INTO Employees VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                x)
        self.cursor.execute('COMMIT')

    def insert_one_client(self, client_id, client_name, city, country, business):
        """Insert one position into Clients table

        :param client_id: integer
        :param client_name: client name
        :param city: city name
        :param country: country name
        :param business: integer
        """
        self.cursor.execute("""INSERT INTO Clients VALUES (?, ?, ?, ?, ?)""", (client_id, client_name, city, country,
                                                                               business))
        self.connection.commit()

    def insert_many_clients(self, client_data):
        """Insert many positions into Clients table

        :param client_data: clients dataset
        """
        self.cursor.execute('BEGIN TRANSACTION')
        for x in client_data:
            self.cursor.execute("""INSERT INTO Clients VALUES (?, ?, ?, ?, ?)""", x)
        self.cursor.execute('COMMIT')

    def insert_one_project(self, project_id, project_name, client_id, started_on, deadline_on, budget):
        """Insert one position into Projects table

        :param project_id: integer
        :param project_name: project name
        :param client_id: integer
        :param started_on: date "YYYY-MM-DD"
        :param deadline_on: date "YYYY-MM-DD"
        :param budget: integer
        """
        self.cursor.execute("""INSERT INTO Projects VALUES (?, ?, ?, ?, ?, ?)""", (project_id, project_name, client_id,
                                                                                   started_on, deadline_on, budget))
        self.connection.commit()

    def insert_many_project(self, project_data):
        """Insert many positions into Projects table

        :param project_data: projects dataset
        """
        self.cursor.execute('BEGIN TRANSACTION')
        for x in project_data:
            self.cursor.execute("""INSERT INTO Projects VALUES (?, ?, ?, ?, ?, ?)""", x)
        self.cursor.execute('COMMIT')

    def insert_one_skill(self, skill_id, skill_name, experience):
        """Insert one position into Skills table

        :param skill_id: integer
        :param skill_name: skill name
        :param experience: integer
        """
        self.cursor.execute("""INSERT INTO Skills VALUES (?, ?, ?)""", (skill_id, skill_name, experience))
        self.connection.commit()

    def insert_many_skill(self, skill_data):
        """Insert many positions into Skills table

        :param skill_data: skills dataset
        """
        self.cursor.execute('BEGIN TRANSACTION')
        for x in skill_data:
            self.cursor.execute("""INSERT INTO Skills VALUES (?, ?, ?)""", x)
        self.cursor.execute('COMMIT')

    def insert_one_role(self, role_id, role_name):
        """Insert one position into Roles table

        :param role_id: integer
        :param role_name: role name
        """
        self.cursor.execute("""INSERT INTO Roles VALUES (?, ?)""", (role_id, role_name))
        self.connection.commit()

    def insert_many_role(self, role_data):
        """Insert many positions into Roles table

        :param role_data: roles dataset
        """
        self.cursor.execute('BEGIN TRANSACTION')
        for x in role_data:
            self.cursor.execute("""INSERT INTO Roles VALUES (?, ?)""", x)
        self.cursor.execute('COMMIT')

    def insert_one_relation(self, employee_id, skill_id):
        """Insert one position into EmployeesSkillsRelations table

        :param employee_id: integer
        :param skill_id:
        """
        self.cursor.execute("""INSERT INTO EmployeesSkillsRelations VALUES (?, ?)""", (employee_id, skill_id))
        self.connection.commit()

    def insert_many_relation(self, rel_data):
        """Insert many positions into EmployeesSkillsRelations table

        :param rel_data: relations dataset
        """
        self.cursor.execute('BEGIN TRANSACTION')
        for x in rel_data:
            self.cursor.execute("""INSERT INTO EmployeesSkillsRelations VALUES (?, ?)""", x)
        self.cursor.execute('COMMIT')

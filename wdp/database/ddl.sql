--Creating databse
CREATE DATABASE wdp_database

--Creating Employees table
CREATE TABLE Employees(
	employee_id INTEGER AUTO_INCREMENT,
	first_name VARCHAR(250) NOT NULL,
	last_name VARCHAR(250) NOT NULL,
	avatar_url VARCHAR(250) NOT NULL,
    job_title VARCHAR(20),
	joined_on DATE NOT NULL,
	email VARCHAR(250) NOT NULL UNIQUE,
	phone_number VARCHAR(12) NOT NULL UNIQUE,
	birthday DATE NOT NULL,
	country VARCHAR(50) NOT NULL,
	city VARCHAR(250) NOT NULL,
	project_id INTEGER,
	last_role INTEGER,
	role_preferred INTEGER NOT NULL,
	salary INTEGER,
	specification VARCHAR(250),
	PRIMARY KEY (employee_id),
	CHECK (joined_on > birthday),
	FOREIGN KEY (project_id) REFERENCES Projects(project_id),
	FOREIGN KEY (last_role) REFERENCES Roles(role_id),
	FOREIGN KEY (role_preferred) REFERENCES Roles(role_id)
)

--Creating Roles table
CREATE TABLE Roles(
	role_id INTEGER AUTO_INCREMENT,
	role_name VARCHAR(250),
	PRIMARY KEY (role_id)
)

--Creating Skills table
CREATE TABLE Skills(
	skill_id INTEGER AUTO_INCREMENT,
	skill_name VARCHAR(250),
	experience INTEGER,
	PRIMARY KEY (skill_id)
)

--Creating relation table for many-to-many relation between Employees and Skills
CREATE TABLE EmployeesSkillsRelations(
	employee_id INTEGER,
	skill_id INTEGER,
	FOREIGN KEY (employee_id) REFERENCES Employees(employee_id),
	FOREIGN KEY (skill_id) REFERENCES Skills(skill_id)
)

--Creating Clients table
CREATE TABLE Clients(
	client_id INTEGER AUTO_INCREMENT,
	client_name VARCHAR(250),
	city VARCHAR(250),
	country VARCHAR(50),
	business VARCHAR(250),
	PRIMARY KEY (client_id)
)

--Creating Projects table 
CREATE TABLE Projects(
	project_id INTEGER AUTO_INCREMENT,
	project_name VARCHAR(250) NOT NULL,
	client_id INTEGER NULL,
	started_on DATE,
	deadline_on DATE,
	budget INTEGER,
	PRIMARY KEY (project_id),
	FOREIGN KEY (client_id) REFERENCES Clients(client_id)
)
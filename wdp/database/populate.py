import connector_wdp


d1 = connector_wdp.Database()


emp_data = [
    (1, 'Adam', 'Nowak', 'www.strona1.com', 'Senior Data Engineer', '2020-11-01', 'adam1@email.com', '+48123456789',
     '1980-30-03', 'Poland', 'Warsaw', 1, 2, 2, 25000, 'ETL'),
    (2, 'Adam', 'Kowalski', 'www.strona2.com', 'Data Scientist', '2021-04-21', 'akowalski@email.com', '+48223456789',
     '1989-03-12', 'Poland', 'Wroclaw', 1, 1, 7, 11000, 'AI'),
    (3, 'Tom', 'Nowak', 'www.strona3.com', 'Senior Data Analyst', '2022-08-01', 'tomn@email.com', '+48323456789',
     '1980-30-03', 'England', 'London', 2, 3, 1, 13856, 'Visualisation'),
    (4, 'Jay', 'High', 'www.strona4.com', 'Cloud Specialist', '2021-01-01', 'jj@email.com', '+48423456789',
     '1992-18-09', 'USA', 'Portland', 3, 10, 11, 25000, 'AWS'),
    (5, 'Robbie', 'Frank', 'www.strona5.com', 'DevOps with Docker', '2018-12-31', 'frankie@email.com', '+48523456789',
     '1990-15-04', 'USA', 'Chicago', 4, 1, 3, 15000, 'Devops'),
    (6, 'Georg', 'Herrmnan', 'www.strona6.com', 'Junior Frontend Cool', '2023-02-01', 'gh@email.com', '+48623456789',
     '1998-15-07', 'Germany', 'Dortmund', 5, 15, 17, 6000, 'PHP'),
    (7, 'Ivan', 'Dudko', 'www.strona7.com', 'Junior Backend Ninja', '2022-09-09', 'dudko@email.com', '+48723456789',
     '1993-08-08', 'Belarus', 'Minsk', 6, 16, 14, 4500, 'Python'),
    (8, 'Piotr', 'Pawlak', 'www.strona8.com', 'QA Manager', '2015-03-01', 'pp213214@email.com', '+48823456789',
     '1962-11-03', 'Poland', 'Warsaw', 7, 12, 13, 9300, 'Testing'),
    (9, 'Tim', 'Van Dijk', 'www.strona9.com', 'UI/UX Hero', '2018-05-05', 'vantim@email.com', '+48923456789',
     '1975-12-12', 'Holland', 'Den Haag', 8, 9, 8, 13000, 'SQL'),
    (10, 'Henryk', 'Popiel', 'www.strona10.com', 'Junior PM', '2023-03-03', 'hp@email.com', '+48023456789',
     '2000-10-03', 'Poland', 'Opole', 7, 6, 5, 5000, 'Scrum')
]

role_data = [
    (1, 'Data Scientist'),
    (2, 'Data Engineer'),
    (3, 'Data Analyst'),
    (4, 'Web Developer'),
    (5, 'Scrum Master'),
    (6, 'Project Manager'),
    (7, 'Product Owner'),
    (8, 'Database Administrator'),
    (9, 'UX Designer'),
    (10, 'Cloud Engineer'),
    (11, 'DevOps'),
    (12, 'QA Tester'),
    (13, 'Data Quality Manager'),
    (14, 'Software Architect'),
    (15, 'Fronted Developer'),
    (16, 'Backend Developer'),
    (17, 'Fullstack Developer')
]

client_data = [
    (1, 'Company A', 'Warsaw', 'Poland', 'Consulting'),
    (2, 'Company B', 'New York', 'USA', 'Finances'),
    (3, 'Company C', 'Berlin', 'Germany', 'Automotive'),
    (4, 'Company D', 'London', 'England', 'Entertainment')
]

project_data = [
    (1, 'Project A', 1, '2019-02-15', '2023-10-10', 35000000),
    (2, 'Project B', 2, '2022-07-22', '2025-01-30', 435000000),
    (3, 'Project C', 2, '2020-05-10', '2024-11-05', 158990000),
    (4, 'Project D', 3, '2023-02-15', '2031-12-01', 600000000),
    (5, 'Project E', 3, '2015-09-18', '2023-06-24', 579000000),
    (6, 'Project F', 4, '2021-06-12', '2025-02-10', 98000000),
    (7, 'Project G', 4, '2021-01-04', '2024-03-19', 111000000),
    (8, 'Project H', 4, '2023-01-06', '2023-12-28', 50000000),
]

skill_data = [
    (1, 'Python', 1),
    (2, 'Python', 2),
    (3, 'Python', 3),
    (4, 'Python', 4),
    (5, 'Python', 5),
    (6, 'SQL', 1),
    (7, 'SQL', 2),
    (8, 'SQL', 3),
    (9, 'SQL', 4),
    (10, 'SQL', 5),
    (11, 'Tableau', 1),
    (12, 'Power BI', 2),
    (13, 'Excel', 3),
    (14, 'Java', 4),
    (15, 'Java', 5),
    (16, 'C++', 1),
    (17, 'C++', 2),
    (18, 'Ruby', 2),
    (19, 'Ruby', 3),
    (20, 'Azure Cloud', 2),
    (21, 'AWS Cloud', 2),
    (22, 'Google Cloud', 3),
    (23, 'Spark', 3),
    (24, 'Kafka', 2),
]

rel_data = [
    (1, 5),
    (1, 10),
    (1, 15),
    (1, 23),
    (1, 24),
    (2, 4),
    (2, 9),
    (3, 8),
    (3, 11),
    (3, 12),
    (3, 13),
    (4, 20),
    (4, 21),
    (5, 22),
    (6, 6),
    (6, 16),
    (6, 18),
    (7, 1),
    (7, 14),
    (8, 2),
    (9, 3),
    (9, 17),
    (10, 7),
    (10, 18)
]

d1.insert_many_role(role_data=role_data)
d1.insert_many_skill(skill_data=skill_data)
d1.insert_many_clients(client_data=client_data)
d1.insert_many_project(project_data=project_data)
d1.insert_many_employees(emp_data=emp_data)
d1.insert_many_relation(rel_data=rel_data)

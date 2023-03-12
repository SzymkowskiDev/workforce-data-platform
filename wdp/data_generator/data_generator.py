"""
Generate bulk data for file drops to input_and_output/uploads
to test the behavior and performance of the entire data engineering solution.
Types of data generated:
- population of employees
- skills surveys
note paramaters for random generation should be used to modify proportion of various characteristics
values for these parameters should be found by the data science research team
e.g. what proportion of job offers is for specialization X e.g. Frontend Developer
"""
from faker.config import AVAILABLE_LOCALES
from phone_gen import PhoneNumber
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from faker import Faker
import random
import json
import os

__default_config__ = {
    "illegal_locales": ["fr_QC"],

    "employee.output_name": "employee",
    "employee.uid_length": 8,
    "employee.salary_min": 1000,
    "employee.salary_max": 30_000,
}


def _get_data_from_json(file_path) -> dict:
    """ Read and return data as dict from file. """
    with open(file_path, "r") as file:
        return json.load(file)
 
def _save_data_to_json(file_path, content):
    """ Save content to json file. """
    if not os.path.exists(file_path):
        open(file_path, "a+").close()

    with open(file_path, "w") as file:
        json.dump(content, file, indent=4, separators=(',', ': '))

def _get_available_roles() -> list:
    """ Get and return roles from ../control_panel/roles.json """
    roles_path = "../control_panel/roles.json"
    available_roles = _get_data_from_json(roles_path)['Roles']
    return available_roles

def _get_available_specializations() -> dict:
    """ Get and return roles from ../control_panel/fields_and_skills.json """
    sepcializations_path = "../control_panel/fields_and_skills.json"
    available_specializations = _get_data_from_json(sepcializations_path)
    return available_specializations

def get_avatar_from_job(job) -> str:
    return f"../control_panel/avatars/{job.lower().replace(' ', '_')}.png"

def readable_datetime(date: datetime, sep="/") -> str:
    return date.strftime(f"%d{sep}%m{sep}%Y")

def normalize_phone_number(number: str) -> str:
    normal = "".join([n for n in number if n in "+0123456789"])
    return normal

def current_date_for_file_name() -> str:
    date = datetime.now()
    return date.strftime("%d_%m_%Y %H:%M:%S")

UPLOADS_PATH = "../input_and_output/uploads/"
ROLES = _get_available_roles()
SPECIALIZATIONS = _get_available_specializations()
CONFIG = __default_config__ #TODO: read actual config.
AVAILABLE_LOCALES.remove("fr_QC")


class RandomGenerators:
    def uid(length=8) -> int:
        uid = str(random.randint(1, 9))
        for _ in range(length):
            uid += str(random.randint(1, 9))
        return int(uid)
    
    def salary(min=1000, max=30_000) -> float:
        return float(f"{random.randint(min, max)}.{random.randint(0, 99)}")

    def join_date(birthdate: datetime) -> datetime:
        date = datetime(
            random.randint(birthdate.year + 20, datetime.now().year-1),
            random.randint(1, 12),
            random.randint(1, 28)
        )
        return readable_datetime(date)

    def phone_number(country: str) -> str:
        """ Generate random phone number based on country. Number starts with +. """
        number = PhoneNumber(country).get_number()
        return normalize_phone_number(number)

    def project_name() -> str:
        """ Generate random project name in english. """
        return Faker("en_US").bs().title()


@dataclass
class _PseudoSeed:
    locale: str
    job: str
    birthdate: datetime

class GeneratedEmployee:

    @staticmethod
    def generate_pseudo_seed() -> _PseudoSeed:
        """ Some of parameters depends on one data like (e.g. locale, birthdate...).
        Generate seed that contains: locale, job(from roles), birthdate """
        locale = random.choice(AVAILABLE_LOCALES)
        job = random.choice(ROLES)
        birthdate = datetime(random.randint(1950, 2000), random.randint(1, 12), random.randint(1, 28))

        return _PseudoSeed(
            locale, job, birthdate
        )

    def __init__(self):
        """ Generate random data and set it as parameters. """
        pseudo_seed = GeneratedEmployee.generate_pseudo_seed()

        # Random numbers.
        self.uid = RandomGenerators.uid()
        self.salary = RandomGenerators.salary()

        # Locale based.
        locale_based_faker = Faker(pseudo_seed.locale)
        self.phone = RandomGenerators.phone_number(locale_based_faker.current_country_code())
        self.country = locale_based_faker.current_country()
        self.first_name = locale_based_faker.first_name()
        self.last_name = locale_based_faker.last_name()
        self.email = locale_based_faker.email()
        self.city = locale_based_faker.city()

        # Job based.
        self.job_title = pseudo_seed.job
        self.avatar = get_avatar_from_job(self.job_title)

        # Birthdate based.
        self.joining_date = RandomGenerators.join_date(pseudo_seed.birthdate)
        self.birthdate = readable_datetime(pseudo_seed.birthdate)
        
        self.last_role = random.choice(ROLES)
        self.preferred_role = random.choice(ROLES)
        self.current_project = RandomGenerators.project_name()
        self.specialization = random.choice(list(SPECIALIZATIONS.keys()))

    def as_dict(self) -> dict:
        return vars(self)
    

@dataclass
class EmployeesGroup:
    employees: Iterable[GeneratedEmployee]

    def export_json(self):
        """ Export all employees into IO/uploads. """
        file_name = "employee-" + current_date_for_file_name()
        file_path = UPLOADS_PATH + file_name
        content = {"employees": self.employees}
        _save_data_to_json(file_path, content)
    

def generate_employees(amount) -> EmployeesGroup:
    """ Returns EmployeesGroup that contains GeneratedEmployee(s). """
    group = [GeneratedEmployee() for _ in range(amount)]
    return group

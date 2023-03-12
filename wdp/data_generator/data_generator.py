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

"""
TODO:
surveys
"""

from faker.config import AVAILABLE_LOCALES
from phone_gen import PhoneNumber
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from faker import Faker
import logging
import random
import json
import csv
import os

LOGGER = logging.getLogger(__name__)

__all__ = (
    'Config',
    'GeneratedEmployee',
    'EmployeesGroup',
    'generate_employees'
)

__default_config__ = {
    "illegal_locales": ["fr_QC"],

    "employee_output_name": "employee",
    "employee_uid_length": 8,
    "employee_salary_min": 1000,
    "employee_salary_max": 30_000,
}

@dataclass
class Config:
    illegal_locales: list[str]

    employee_output_name: str
    employee_uid_length: int
    employee_salary_min: float
    employee_salary_max: float

    @staticmethod
    def parse_conifg() -> "Config":
        """ Read data from config.json and create Config object.
        Values from keys that were not found in file will be set
        with default value from __default_config__ """

        config_path = "config.json"
        config_content: dict = _get_data_from_json(config_path)
        final_config = __default_config__

        for key, value in config_content.items():
            if key in final_config:
                final_config[key] = value
                LOGGER.debug(f'Config: non-default value: "{key}"="{value}"')

        LOGGER.info("Config: Loaded.")
        return Config(
            final_config["illegal_locales"],
            final_config["employee_output_name"],
            final_config["employee_uid_length"],
            final_config["employee_salary_min"],
            final_config["employee_salary_max"],
        )


def _get_data_from_json(file_path) -> dict:
    """ Read and return data as dict from file. """
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
 
def _save_data_to_json(file_path, content):
    """ Save content to json file. """
    if not os.path.exists(file_path):
        open(file_path, "a+").close()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(content, file, indent=4, separators=(',', ': '))

def _get_available_roles() -> list:
    """ Get and return roles from ../control_panel/roles.json """
    roles_path = "../control_panel/roles.json"
    available_roles = _get_data_from_json(roles_path)['Roles']
    LOGGER.debug(f"Available roles found: {available_roles}")
    return available_roles

def _get_available_specializations() -> dict:
    """ Get and return roles from ../control_panel/fields_and_skills.json """
    sepcializations_path = "../control_panel/fields_and_skills.json"
    available_specializations = _get_data_from_json(sepcializations_path)
    LOGGER.debug(f"Available specializations found: {available_specializations}")
    return available_specializations

def get_avatar_from_job(job) -> str:
    """ Convert job title into path for it's avatar. """
    return f"../control_panel/avatars/{job.lower().replace(' ', '_')}.png"

def readable_datetime(date: datetime, sep="/") -> str:
    """ Convert datetime object into date with format: dd/mm/YYYY """
    return date.strftime(f"%d{sep}%m{sep}%Y")

def normalize_phone_number(number: str) -> str:
    """ Remove all junk stuff from number. """
    normal = "".join([n for n in number if n in "+0123456789"])
    return normal

def timestamp_for_file_name() -> str:
    date = datetime.now()
    return date.strftime("%d_%m_%Y %H_%M_%S")


UPLOADS_PATH = "../input_and_output/uploads/"
ROLES = _get_available_roles()
CONFIG = Config.parse_conifg()
SPECIALIZATIONS = _get_available_specializations()


class RandomGenerators:
    """ Contains methods to generate random attributes. 
    Random ranges and other parameters can be modified in config. """

    def uid() -> int:
        """ Generate random UID that contains only numbers (non-zero leading) """
        length = CONFIG.employee_uid_length
        uid = str(random.randint(1, 9))
        for _ in range(length-1):
            uid += str(random.randint(0, 9))
        return int(uid)
    
    def salary() -> float:
        """ Generate random salary based on config's values. """
        min = CONFIG.employee_salary_min
        max = CONFIG.employee_salary_max 
        return float(f"{random.randint(min, max)}.{random.randint(0, 99)}")

    def join_date(birthdate: datetime) -> datetime:
        """ Generate random comp. join date from range: <birthday + 20 years, now - 1 year> """
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
class _EmployeeBase:
    """ Contains attributes that are base for other attributes. 
    (e.g. "locale" is being used to create: phone, country, city etc.) 
    Rest of data is randomly generated or picked. """
    locale: str
    job: str
    birthdate: datetime

class GeneratedEmployee:

    @staticmethod
    def generate_pseudo_seed() -> _EmployeeBase:
        """ Some of parameters depends on one data like (e.g. locale, birthdate...).
        Generate seed that contains: locale, job(from roles), birthdate """
        legal_locales = AVAILABLE_LOCALES
        for loc in CONFIG.illegal_locales:
            if loc in legal_locales:
                legal_locales.remove(loc)
        LOGGER.debug(f"Pseudo seed: {len(CONFIG.illegal_locales)} illegal locales found ({len(AVAILABLE_LOCALES)}-{len(CONFIG.illegal_locales)})")

        locale = random.choice(legal_locales)
        job = random.choice(ROLES)
        birthdate = datetime(random.randint(1950, 2000), random.randint(1, 12), random.randint(1, 28))

        return _EmployeeBase(
            locale, job, birthdate
        )

    def __init__(self):
        """ Generate random data and set it as attributes. """
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
        
        # Rest.
        self.last_role = random.choice(ROLES)
        self.preferred_role = random.choice(ROLES)
        self.current_project = RandomGenerators.project_name()
        self.specialization = SPECIALIZATIONS[random.choice(list(SPECIALIZATIONS.keys()))]

    def as_dict(self) -> dict:
        """ Turn all attributes and their values into dict. """
        return vars(self)

@dataclass
class EmployeesGroup:
    """ Contains list of employees and methods to manage them. """
    employees: Iterable[GeneratedEmployee]

    def export_json(self):
        """ Export all employees contained in this group
        to IO/uploads in JSON format. """
        file_name = CONFIG.employee_output_name + "-" + timestamp_for_file_name() + ".json"
        file_path = UPLOADS_PATH + file_name

        employees_content = [e.as_dict() for e in self.employees]
        content = {"employees": employees_content}
        _save_data_to_json(file_path, content)
        LOGGER.info(f"Exported employees group into: (JSON) {file_name}")

    def export_csv(self):
        """ Export all employees contained in this group
        to IO/uploads in CSV format."""
        file_name = CONFIG.employee_output_name + "-" + timestamp_for_file_name() + ".csv"
        file_path = UPLOADS_PATH + file_name

        employees_content = [e.as_dict() for e in self.employees]
        fields = list(employees_content[0].keys())
        with open(file_path, "w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fields)
            writer.writeheader()
            writer.writerows(employees_content)

        LOGGER.info(f"Exported employees group into: (CSV) {file_name}")


def generate_employees(amount) -> EmployeesGroup:
    """ Returns EmployeesGroup that contains GeneratedEmployee(s). 
    Time needed to generate one employee ~0.25s (4 employees/s)"""
    group = [GeneratedEmployee() for _ in range(amount)]
    return EmployeesGroup(group)

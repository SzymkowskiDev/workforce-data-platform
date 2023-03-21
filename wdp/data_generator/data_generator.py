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
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from faker import Faker
import logging
import random
import json
import csv
import os


dir_name = os.path.dirname(__file__)

roles_path = os.path.join(dir_name, "..\\control_panel\\roles.json")
sepcializations_path = os.path.join(dir_name, "..\\control_panel\\fields_and_skills.json")
UPLOADS_PATH = os.path.join(dir_name, "..\\input_and_output\\uploads\\")
LOGGER = logging.getLogger(__name__)

__all__ = (
    'Config',
    'EmployeesGroup',
    'generate_employees',
    'SurveysResultsGroup',
    'generate_surveys_results'
)

__default_config__ = {
    "illegal_locales": ["fr_QC"],
    "uid_length": 8,

    "employee_output_name": "employee",
    "employee_salary_min": 1000,
    "employee_salary_max": 30_000,
    "employee_phone_number_length": 9,

    "survey_output_name": "survey"
}

@dataclass
class Config:
    illegal_locales: list[str]
    uid_length: int

    employee_output_name: str
    employee_salary_min: float
    employee_salary_max: float
    employee_phone_number_length: int

    survey_output_name: str

    @staticmethod
    def parse_conifg() -> "Config":
        """ Read data from config.json and create Config object.
        Values from keys that were not found in file will be set
        with default value from __default_config__ """

        config_path = "wdp/data_generator/config.json"
        config_content: dict = _get_data_from_json(config_path)
        final_config = __default_config__

        for key, value in config_content.items():
            if key in final_config:
                final_config[key] = value
                LOGGER.debug(f'Config: non-default value: "{key}"="{value}"')

        LOGGER.info("Config: Loaded.")
        return Config(
            final_config["illegal_locales"],
            final_config["uid_length"],
            final_config["employee_output_name"],
            final_config["employee_salary_min"],
            final_config["employee_salary_max"],
            final_config["employee_phone_number_length"],
            final_config["survey_output_name"]
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

def _get_avatar_path_from_job(job) -> str:
    """ Convert job title into path for it's avatar. """
    return f"wdp/control_panel/avatars/{job.lower().replace(' ', '_')}.png"

def _readable_datetime(date: datetime, sep="/") -> str:
    """ Convert datetime object into date with format: dd/mm/YYYY """
    return date.strftime(f"%d{sep}%m{sep}%Y")

def _timestamp_for_file_name() -> str:
    """ Generate string that contains current date and time in savable version. """
    date = datetime.now()
    return date.strftime("%d_%m_%Y %H_%M_%S")


CONFIG = Config.parse_conifg()
ROLES = _get_data_from_json(roles_path)['Roles']
SPECIALIZATIONS = _get_data_from_json(sepcializations_path)

class RandomGenerators:
    """ Contains methods to generate random attributes. 
    Random ranges and other parameters can be modified in config. """

    def uid() -> int:
        """ Generate random UID that contains only numbers (non-zero leading) """
        length = CONFIG.uid_length
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
        return _readable_datetime(date)

    def phone_number() -> str:
        """ Generate random phone number starting with +. """
        number = "+" + "".join([random.randint(1, 9) for _ in range(2)]) + "".join([random.randint(1, 9) for _ in range(CONFIG.employee_phone_number_length)])
        return number

    def project_name() -> str:
        """ Generate random project name in english. """
        return Faker("en_US").bs().title()

    def specializations(only_single=False) -> list[str] | str:
        """ Generate list of skills's according to random specialization. """
        all_skills = SPECIALIZATIONS[random.choice(list(SPECIALIZATIONS.keys()))]
        if only_single:
            return random.choice(all_skills)
        else:
            return all_skills 


# --- EMPLOYEES --- #

@dataclass
class _EmployeeBase:
    """ Contains attributes that are base for other attributes. 
    (e.g. "locale" is being used to create: phone, country, city etc.) 
    Rest of employee's data is randomly generated or picked. """
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
        self.phone = RandomGenerators.phone_number()
        self.country = locale_based_faker.current_country()
        self.first_name = locale_based_faker.first_name()
        self.last_name = locale_based_faker.last_name()
        self.email = locale_based_faker.email()
        self.city = locale_based_faker.city()

        # Job based.
        self.job_title = pseudo_seed.job
        self.avatar = _get_avatar_path_from_job(self.job_title)

        # Birthdate based.
        self.joining_date = RandomGenerators.join_date(pseudo_seed.birthdate)
        self.birthdate = _readable_datetime(pseudo_seed.birthdate)
        
        # Rest.
        self.last_role = random.choice(ROLES)
        self.preferred_role = random.choice(ROLES)
        self.current_project = RandomGenerators.project_name()
        self.specialization = RandomGenerators.specializations()

    def as_dict(self) -> dict:
        """ Turn all attributes and their values into dict. """
        return vars(self)

@dataclass
class EmployeesGroup:
    """ Contains list of employees and methods to export them.
    Instance of this object should be generated using `generate_employees` function.
    """
    employees: Iterable[GeneratedEmployee]

    def export_json(self):
        """ Export all employees contained in this group
        to IO/uploads in JSON format. """
        file_name = CONFIG.employee_output_name + "-" + _timestamp_for_file_name() + ".json"
        file_path = UPLOADS_PATH + file_name

        employees_content = [e.as_dict() for e in self.employees]
        content = {"employees": employees_content}
        _save_data_to_json(file_path, content)
        LOGGER.info(f"Exported {len(self.employees)} employees group into: (JSON) {file_name}")

    def export_csv(self):
        """ Export all employees contained in this group
        to IO/uploads in CSV format."""
        file_name = CONFIG.employee_output_name + "-" + _timestamp_for_file_name() + ".csv"
        file_path = UPLOADS_PATH + file_name

        employees_content = [e.as_dict() for e in self.employees]
        fields = list(employees_content[0].keys())
        with open(file_path, "w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fields)
            writer.writeheader()
            writer.writerows(employees_content)

        LOGGER.info(f"Exported {len(self.employees)} employees group into: (CSV) {file_name}")


# --- SURVEYS --- #

class GeneratedSurveyResult:
    
    def __init__(self) -> None:
        self.uid = RandomGenerators.uid()
        self.specialization = RandomGenerators.specializations(only_single=True)
        self.experience_months = random.randint(1, 60)

    def as_dict(self) -> dict:
        return vars(self)
    
@dataclass
class SurveysResultsGroup:
    surveys_results: Iterable[GeneratedSurveyResult]

    def export_json(self):
        """ Export all results contained in this group
        to IO/uploads in JSON format. """
        file_name = CONFIG.survey_output_name + "-" + _timestamp_for_file_name() + ".json"
        file_path = UPLOADS_PATH + file_name

        results_content = [s.as_dict() for s in self.surveys_results]
        content = {"surveys": results_content}
        _save_data_to_json(file_path, content)
        LOGGER.info(f"Exported {len(self.surveys_results)} surveys results group into: (JSON) {file_name}")

    def export_csv(self):
        """ Export all results contained in this group
        to IO/uploads in CSV format."""
        file_name = CONFIG.survey_output_name + "-" + _timestamp_for_file_name() + ".csv"
        file_path = UPLOADS_PATH + file_name

        results_content = [s.as_dict() for s in self.surveys_results]
        fields = list(results_content[0].keys())
        with open(file_path, "w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fields)
            writer.writeheader()
            writer.writerows(results_content)

        LOGGER.info(f"Exported {len(self.surveys_results)} surveys results group into: (CSV) {file_name}")



# --- INTERFACE --- #

def generate_employees(amount: int) -> EmployeesGroup:
    """ Returns EmployeesGroup that contains GeneratedEmployee(s). 
    Time required to generate one employee: ~0.25s (4 employees/s)
    
    :param amount: Amount of employees to generate.
    :type amount: int
    :return: EmployeesGroup object that contains generated employees.
    :rtype: EmployessGroup

    Export employess to JSON or CSV:
        >>> employees = generate_employees(3)
        >>> employees.export_json()
        >>> employees.export_csv()

        (If You don't need to manage generated `employees`, You can
        just export object returned by `generate_employees` without
        assigning value to `employees`.)
        
        >>> generate_employees(5).export_json()
        >>> generate_employees(10).export_csv()
    """
    group = [GeneratedEmployee() for _ in range(amount)]
    return EmployeesGroup(group)

def generate_surveys_results(amount: int) -> SurveysResultsGroup:
    """ Return SurveysResultsGroup object that contains GeneratedSurveyResult(s).
    Time required to generate one survey: ~0.0015s (667 results/s)

    :param amount: Amount of surveys results to generate.
    :type amount: int
    :return: SurveysResultsGroup that contains generated surveys results.
    :rtype: SurveysResultsGroup

    Export results to CSV or JSON:
        >>> results = generate_surveys_results(6)
        >>> results.export_json()
        >>> results.export_csv()

        Shorter version (skip value assignment):
        >>> generate_survyes_results(20).export_json()
        >>> generate_survyes_results(34).export_csv()
    """
    group = [GeneratedSurveyResult() for _ in range(amount)]
    return SurveysResultsGroup(group)

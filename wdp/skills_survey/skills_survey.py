"""
Text-based User Interface (TUI), extensible and limitable
forms' generator. It allows the employee to fill in the created forms.

General usage (to ask about UID, SKILLS(from list), EXPERIENCE).
        Generate Form object with preprepared fields.
    >>> form = generate_default_form() 

        Enquire user.
    >>> form.enquire()

        Export given responses into csv file in IO/uploads dir.
    >>> form.export_responses()
"""

from wdp.skills_survey.validators import Validator, LengthValidator, NumberValidator, InCollectionValidator
from wdp.skills_survey.config import get_config
from wdp.utilities import app_path
from dataclasses import dataclass
from datetime import datetime

import wdp.skills_survey.style as Style
import time
import json
import csv

Style.setup_colors()
CONFIG = get_config()


@dataclass
class Field:
    key: str
    question: str
    validators: tuple[Validator] | list[Validator] = ()

    def validate_answer(self, answer: str) -> tuple[bool | str, list[str]]:
        messages = []
        status = True

        for validator in self.validators:
            validation = validator(answer)
            if not bool(validation):
                status = False
                messages.append(validator.error_message)

            elif isinstance(validation, str):
                status = validation

        return status, messages


def _ask_until_valid(field: Field) -> str:
    """ Get and validate user's input with field's requirements. """
    prompt = Style.generate_prompt()

    while 1:
        response = input(prompt)
        validation_status, error_messages = field.validate_answer(response)

        if bool(validation_status):
            print(Style.valid_answer())

            if isinstance(validation_status, str):
                response = validation_status
            return response

        print(Style.invalid_answer(error_messages))


@dataclass
class Form:
    fields: tuple | list
    responses: dict[str, str] = None

    def enquire(self) -> dict | None:
        """ Ask user all questions one by one, validate answers 
        with given validators before accepting response.

        WARNING: This method will create WHILE TRUE loop!

        :return: Dictionary with {field.key: response} or None in case
                 of form cancelation (KeyboardInterrupt)
        :rtype: dict | None
        """
        self.start_time = time.time()
        total_questions_amount = len(self.fields)
        responses = {}

        Style.clear_screen()
        print(Style.form_header(total_questions_amount))

        for index, field in enumerate(self.fields):
            print(Style.question_header(index + 1, total_questions_amount, field.question))

            try:
                answer = _ask_until_valid(field)
                responses[field.key] = answer

            except KeyboardInterrupt:
                print(f"\n\n{Style.Formats.red('Form canceled.')}")
                return None

        total_time_sec = (time.time() - self.start_time) + 0.1
        print(Style.form_ending(total_time_sec))

        self.responses = responses
        return responses

    def export_responses(self):
        """ Export responses passed by user inputs in enquire() method
        to csv file localized in IO/uploads directory. """
        answers = self.responses
        if answers is None:
            raise ValueError("No answers provided.")

        file_name = CONFIG["output_name"] + "-" + datetime.now().strftime("%d_%m_%Y %H_%M_%S") + ".csv"
        file_path = app_path(CONFIG["output_path"]) / file_name

        fields = list(answers.keys())
        with open(file_path, "w", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fields)
            writer.writeheader()
            writer.writerow(answers)


def generate_default_form() -> Form:
    """ Generate default form with preprapared fields:
    UID: number, length=(from config)
    SKILL: string, One of items in fields_and_skills.json from control_panel.
    EXPRERIENCE: number, length in range <1, 3>

    :return: Generated Form object
    :rtype: Form
    """
    _skills_path = app_path("control_panel\\fields_and_skills.json")
    with open(_skills_path, "r") as skills_file:
        categorized_skills = json.load(skills_file)

    available_skills = []
    for part in categorized_skills.values():
        available_skills.extend(part)
    available_skills = list(set(available_skills))

    UID_field = Field("uid", "Your UID:", [LengthValidator(CONFIG["restrictions"]["uid_length"]), NumberValidator])
    SKILL_field = Field("skill", "Choose your skill:", [InCollectionValidator(available_skills)])
    EXPERIENCE_field = Field("experience", "Your experience in months:",
                             [LengthValidator(range(1, 4)), NumberValidator])

    return Form([UID_field, SKILL_field, EXPERIENCE_field])

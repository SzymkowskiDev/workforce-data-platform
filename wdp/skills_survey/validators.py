"""
Contains functions to validate user responses.
"""
from typing import Any, Callable, Sequence
from dataclasses import dataclass


def __in_collection_casefolded(phrase, collection) -> str:
    casefolded_collection = [str(i).casefold() for i in collection]
    phrase = phrase.casefold()

    if phrase in casefolded_collection:
        index = casefolded_collection.index(phrase)
        return collection[index]

    return ""


def _number_type(answer: str, _):
    return answer.isnumeric()


def _correct_length(answer: str, required: int | range):
    if isinstance(required, int):
        return len(answer) == required
    if isinstance(required, range):
        return len(answer) in required


def _in_collection(answer: str, required: Sequence):
    return __in_collection_casefolded(answer, required)


@dataclass
class Validator:
    validation_function: Callable
    error_message: str
    _value: Any = None

    def validate(self, answer: str) -> tuple[bool, str | None]:
        return self.validation_function(answer, self._value)

    def __call__(self, answer: str) -> tuple[bool, str | None]:
        return self.validate(str(answer))


NumberValidator = Validator(_number_type, "Not a number")
LengthValidator = lambda lng: Validator(_correct_length, f"Invalid answer's length ({lng})", lng)
InCollectionValidator = lambda coll: Validator(_in_collection, "Answer is not inside required collection.", coll)

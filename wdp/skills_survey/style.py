"""
Styles module contains console screen manipulation and 
TUI generation methods.
"""

from wdp.skills_survey.config import get_config
import platform
import ctypes
import sys
import os

FORMAT_END = "\033[0m"
CONFIG = get_config()
CH = CONFIG["characters"]
MSG = CONFIG["messages"]


def clear_screen():
    os.system("cls || clear")

def setup_colors():
    if not sys.stdout.isatty():
        for _ in dir():
            if isinstance(_, str) and _[0] != "_":
                locals()[_] = ""
    else:
        if platform.system() == "Windows":
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            del kernel32


class Formats:

    def bolder(text: str) -> str:
        return f"\033[1m{text}{FORMAT_END}"

    def red(text: str) -> str:
        return f"\033[0;31m{text}{FORMAT_END}"

    def green(text: str) -> str:
        return f"\033[0;32m{text}{FORMAT_END}"

    def blue(text: str) -> str:
        return f"\033[0;34m{text}{FORMAT_END}"

    def purple(text: str) -> str:
        return f"\033[;35m{text}{FORMAT_END}"


def generate_prompt() -> str:
    return CH["br"] + line_prefix("input") + " "


def form_header(questions_amount) -> str:
    formatted_header = CH["nw"] + CH["hl"] * 3 + Formats.blue(CH["dot"]) + "\n" +\
                       CH["vl"] + "\n" + \
                       CH["br"] + " " + Formats.bolder(MSG["header"]) + "\n" +\
                       CH["br"] + " Total questions: " + Formats.bolder(Formats.blue(str(questions_amount))) + "\n" +\
                       CH["vl"] + "\n" + \
                       CH["sw"] + CH["hl"] * 3 + Formats.blue(CH["dot"]) + "\n"
    return formatted_header


def form_ending(total_time_s) -> str:
    clear_screen()
    formatted_header = CH["nw"] + CH["hl"] * 3 + Formats.blue(CH["dot"]) + "\n" +\
                       CH["vl"] + "\n" + \
                       CH["br"] + " " + Formats.bolder(MSG["ending"]) + "\n" +\
                       CH["br"] + " Time spent: " + Formats.bolder(Formats.blue(str(round(total_time_s, 2)))) + " sec \n" +\
                       CH["vl"] + "\n" + \
                       CH["sw"] + CH["hl"] * 3 + Formats.blue(CH["dot"]) + "\n"
    return formatted_header


def question_header(question_index, questions_amount, question_content):
    count = f"{question_index} / {questions_amount}"
    question_content = f" {question_content} "
    inner_space = len(question_content)

    if len(question_content) < len(count):
        raise ValueError

    border = CH["nw"] + CH["hl"] * inner_space + CH["ne"] + "\n" +\
             CH["vl"] + count.center(inner_space) + CH["vl"] + "\n" +\
             CH["br"] + CH["hl"] * inner_space + CH["bl"] + "\n" +\
             CH["vl"] + Formats.purple(question_content) + CH["vl"] + "\n" +\
             CH["br"] + CH["hl"] * inner_space + CH["se"]

    return border


def line_prefix(action: str) -> str:
    if action not in ("input", "invalid", "valid"):
        raise ValueError("Invalid 'action' parameter's value.")

    prefix = Formats.blue(CH["dot"]) if action == "input" else \
             Formats.red(CH["dot"]) if action == "invalid" else \
             Formats.green(CH["dot"])

    suffix = CH["in"] if action == "input" else CH["out"]

    return prefix + suffix


def valid_answer() -> str:
    content = CH["vl"] + "\n" + CH["sw"] + \
              line_prefix("valid") + " " + Formats.green(MSG["ans_valid"]) + "\n"
    return content


def invalid_answer(errors: tuple[str]) -> str:
    content = CH["br"] + line_prefix("invalid") + " " + \
              Formats.red(MSG["ans_invalid"]) + ", ".join(errors)
    return content

"""
Module contains function to get content of config as dict.

CONFIG EXPLANATION:

"output_name" - Prefix of saved file.
"output_path" - Relative path used with app_path
                to responses output directory.

[restrictions]
"uid_length" - Required length of UID field.

[messages]
"header", "ending" - Messages shown before and after form.
"ans_invalid", "ans_valid" - Messages show according to 
                             response validity.

[characters]
Used in TUI generation. 
"br" - Break Right (├)
"bl" - Break Left (┤)
"vl" - Vertical Line (│)
"sep" - Separator (⋮)
"hl" - Horizontal Line (─)
"dot" - Used as suffix in many places (•)
"nw", "sw", "ne", "se" - Corners (╭, ╰, ╮, ╯).
"out" - Suffix for outputs.
"in" - Suffix for inputs.
"""
from wdp.utilities import app_path
import json

CONFIG_PATH = app_path("skills_survey\\config.json")


def get_config() -> dict:
    """ Get and return content of config.json """
    with open(CONFIG_PATH, "r", encoding="UTF8") as file:
        return json.load(file)

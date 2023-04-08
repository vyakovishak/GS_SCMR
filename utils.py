# utils.py
import json
from PySide6.QtGui import QScreen


def load_settings():
    with open("Settings.json", "r") as settings_file:
        all_operators = json.load(settings_file)

        return all_operators['Operators']['ALL']


def get_res_code():
    with open("res_codes.json", "r") as res:
        res_codes = json.load(res)
        return res_codes

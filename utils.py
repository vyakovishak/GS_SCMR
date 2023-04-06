# utils.py
import json
from PySide6.QtGui import QScreen


def load_settings():
    with open("Settings.json", "r") as settings_file:
        all_operators = json.load(settings_file)

        return all_operators['Operators']['ALL']


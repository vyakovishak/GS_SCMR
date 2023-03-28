# utils.py
import json


def load_settings():
    with open("Settings.json", "r") as settings_file:
        all_operators = json.load(settings_file)

        return all_operators['Operators']['ALL']

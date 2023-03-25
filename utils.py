# utils.py
import json

def load_settings():
    with open("Settings.json", "r") as settings_file:
        operators = json.load(settings_file)
        all_operators = {'ARA': operators["Operators"]["ARA"], 'CA': operators["Operators"]["CA"], 'ALL': []}
        for operator in all_operators['ARA'] + all_operators['CA']:
            if operator not in all_operators['ALL']:
                all_operators['ALL'].append(operator)
        return all_operators

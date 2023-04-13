# utils.py
import json
from PySide6.QtGui import QScreen


def load_agents(agent_names_only=False):
    with open("Agents.json", "r") as settings_file:
        all_operators = json.load(settings_file)

    print(agent_names_only)
    agents_list = []
    if agent_names_only:
        for group, agents in all_operators["Agents"].items():
            for agent_name in agents.keys():
                agents_list.append(agent_name)
        return agents_list
    else:
        return all_operators


def get_res_code():
    with open("res_codes.json", "r") as res:
        res_codes = json.load(res)
        return res_codes

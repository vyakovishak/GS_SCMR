# ---- start for utils.py ---- #
import json

def load_agents(hours_type=None, agent_names_only=True):
    with open("./Dependents/GS_Files/Agents.json") as f:
        data = json.load(f)

    if agent_names_only:
        agent_names = []
        for region in data["Agents"].values():
            for agent in region.keys():
                agent_names.append(agent)
        return agent_names
    elif hours_type is not None:
        agent_hours = {}
        for region in data["Agents"].values():
            for agent, hours in region.items():
                if hours_type.lower() == "weekly":
                    agent_hours[agent] = hours["Weekly"]
                elif hours_type.lower() == "monthly":
                    agent_hours[agent] = hours["Monthly"]
                else:
                    raise ValueError("Invalid hours_type. Accepted values are 'weekly' or 'monthly'.")
        return agent_hours
    else:
        return data


def get_res_code():
    with open("./Dependents/GS_Files/res_codes.json", "r") as res:
        res_codes = json.load(res)
        return res_codes

# ---- End for utils.py ---- #
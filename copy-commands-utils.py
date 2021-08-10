'''
Utilities for copy-commands
'''

import os
import json
from json.decoder import JSONDecodeError
import uuid

dir_name = os.path.dirname(__file__)
json_path = os.path.join(dir_name, ".commands.json")

def _add_to_json(name, line, categories, json_path=json_path):
    '''
    Adds a new command to the JSON file that store all of them
    Inputs:
    - name: name of the command (string)
    - line: text of the command or line (string)
    - categories: categories to which the user added the line (list of string)
    - json_path: path to the JSON file (string)
    - 
    '''
    com_id = uuid.uuid1().hex
    com_dict = {
    com_id: {
        "name": name,
        "line": line,
        "categories": categories
        }   
    }

    if not os.path.exists(json_path):
        with open(json_path, "w+") as json_file:
            print("[DEBUG] File created")
            pass
    if os.stat(json_path).st_size == 0:
        print("[DEBUG] File empty")
        with open(json_path, "w") as json_file:
            json.dump(com_dict, json_file, indent=4)
    else:
        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file) # JSON -> dict
        with open(json_path, "w") as json_file:
            json_dict[com_id] = com_dict[com_id]
            json.dump(json_dict, json_file, indent=4) # dict -> JSON


if __name__ == "__main__":
    _add_to_json("name_test", "line_test", [])

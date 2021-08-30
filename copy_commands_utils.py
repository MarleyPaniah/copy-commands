'''
Utilities for copy-commands
'''

import os
import json
import time
from json.decoder import JSONDecodeError
import uuid

dir_name = os.path.dirname(__file__)
json_path = os.path.join(dir_name, ".commands.json")

def check_file(json_path=json_path):
    '''
    Checks if the file exists and if it is empty
    '''
    if not os.path.exists(json_path):
        with open(json_path, "w+") as json_file:
            print(f"[DEBUG] File created")
    if os.stat(json_path).st_size == 0:
        print("[DEBUG] File empty")
        return 0
    else:
        return 1

def get_all_categories():
    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict.keys()

def create_backup():
    '''
    Do a backup of the .commands.json, just in case
    '''
    #TODO
    pass



def add_to_json(name, line, category, json_path=json_path):
    '''
    Adds a new command to the JSON file that stores all of them
    Inputs:
    - name: name of the command (string)
    - line: text of the command or line (string)
    - category: category to which the user added the line (list of string)
    - json_path: path to the JSON file (string)
    Outputs:
    - com_id: ID of the line (uuid.uuid1().hex)
    - 
    '''
    com_id = uuid.uuid1().hex
    com_dict = {
        category: {
            com_id: {
                "name": name,
                "line": line,
            }   
        }
    }

    if check_file() == 0:
        with open(json_path, "w") as json_file:
            json.dump(com_dict, json_file, indent=4)

    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file) # JSON -> dict
    with open(json_path, "w") as json_file:
        json_dict[category][com_id] = com_dict[category][com_id]
        json.dump(json_dict, json_file, indent=4) # dict -> JSON
    
    return com_id
    
def delete_from_json(category, com_id):
    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file)
    with open(json_path, "w") as json_file:
        del json_dict[category][com_id]
        json.dump(json_dict, json_file, indent=4)

def recover_json(json_path=json_path):
    '''
    Opens .commands.json if it exists to show saved commands/lines in the GUI\n
    Output:
    - json_dict: the JSON in a dictionary form (dict)
    '''
    if check_file() == 0:
            json_dict = {}
    else:
        with open(json_path, 'r') as json_file:
            json_dict = json.load(json_file)
    return json_dict

def edit_saved_json(com_id, category, field, entry, json_path=json_path):
    '''
    Edit the values (name, line or category) of a command identified by an id in the JSON\n
    Inputs:
    - com_id: ID of the command (uuid.uuid1().hex)
    '''
    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file)

    json_dict[category][com_id][field] = entry

    with open(json_path, "w") as json_file:
        json.dump(json_dict, json_file, indent=4)

if __name__ == "__main__":
    #add_to_json("name_test", "line_test", [])
    #recover_json()
    pass

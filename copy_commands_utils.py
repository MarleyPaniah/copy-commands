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

def init_json(json_path=json_path):
    '''
    Initialize the .commands.json file
    '''
    def _create_json(json_path):
        with open(json_path, "w+") as json_file:
            
            json_dict = {"@null@":{}}
            json.dump(json_dict, json_file, indent=4)

    try:
        if os.path.exists(json_path):
            print("[DEBUG] File already exists.")
            if os.stat(json_path).st_size != 0:
                print("[DEBUG] File is not empty.")
            else:
                print("[DEBUG] File filled.")
                _create_json(json_path)
        else:
            print("[DEBUG] File created.")
            _create_json(json_path)
    except JSONDecodeError as err:
        print(err)

def create_backup():
    '''
    Do a backup of the .commands.json, just in case
    '''
    #TODO + add exception handling with a copy of the json_dict (see decorators in main)
    pass


#region JSON editing
#TODO: find a way to reduce the copy and pasting of open(json_path, 'r') and open(json_path, 'w')
def add_line_json(name, line, category, json_path=json_path):
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

    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file) # JSON -> dict
    with open(json_path, "w") as json_file:
        json_dict[category][com_id] = com_dict[category][com_id]
        json.dump(json_dict, json_file, indent=4) # dict -> JSON
    
    return com_id
    
def delete_line_json(category, com_id, json_path=json_path):
    try:
        with open(json_path, "r") as json_file:
            json_dict = json.load(json_file)
        with open(json_path, "w") as json_file:
            del json_dict[category][com_id]
            json.dump(json_dict, json_file, indent=4)
    except KeyError:
        print("[DEBUG] (delete_line_json) line not found")
        with open(json_path, "w") as json_path:
            json.dump(json_dict, json_file, indent=4)

def edit_line_json(com_id, category, field, entry, json_path=json_path):
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

def add_category_json(category, json_path=json_path):
    with open(json_path, 'r') as json_file:
        json_dict = json.load(json_file)
    json_dict[category] = {}
    with open(json_path, 'w') as json_file:
        json.dump(json_dict, json_file, indent=4)

def delete_category_json(category, json_path=json_path):
    with open(json_path, 'r') as json_file:
        json_dict = json.load(json_file)
    del json_dict[category]
    with open(json_path, 'w') as json_file:
        json.dump(json_dict, json_file, indent=4)
#endregion

#region getters JSON info 
def get_json(json_path=json_path):
    '''
    Opens .commands.json if it exists to show saved commands/lines in the GUI\n
    input: 
    - json_path (optional): path to json, default is .commands.json
    output:
    - json_dict: the JSON in a dictionary form (dict)
    '''
    with open(json_path, 'r') as json_file:
        json_dict = json.load(json_file)
    return json_dict

def get_all_categories():
    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict.keys()
#endregion

# Test 
if __name__ == "__main__":
    json_dict = get_json()
    print(json_dict)

import json
import os

def readSettingJson(filename):
    root_dir = os.getcwd()
    path = os.path.join(root_dir, 'settings.json')
    print(f'readfile_{path}')
    if os.path.isfile(path):

        json_open = open(path, 'r', encoding='utf-8')
        json_data = json.load(json_open)

        return json_data[filename]

    return ''



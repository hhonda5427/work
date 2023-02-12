import json
import os
import pathlib

def readSettingJson(filename):
# .exeの場合　
    root_dir = os.getcwd()
    print(root_dir)
# main.pyの場合
    # root_dir = pathlib.Path(__file__).parents[1]

    path = os.path.join(root_dir, 'settings.json')
    if os.path.isfile(path):

        json_open = open(path, 'r', encoding='utf-8')
        json_data = json.load(json_open)

        return json_data[filename]

    return 'no file'

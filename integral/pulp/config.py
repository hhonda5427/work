import os, sys, json

# pyinstallerで実行ファイルを作った場合，このディレクトリは実行ファイルのある場所を基準に取得される
# このプログラムではconfig.pyがmain.pyと同じ階層にあるのでどちらでも大丈夫
# 病院端末にディレクトリを作成する場合は.exeファイルとsettings.jsonを同じ階層に置く
def readSettingJson(filename):
# main.pyの場合
    # root_dir = pathlib.Path(__file__).parents[1]
# .exeの場合　
    root_dir = os.getcwd()
    path = os.path.join(root_dir, 'settings.json')

    if not os.path.isfile(path):
        print(f'dir_{root_dir} is not file_settings.json')
        return 'not file'

    json_open = open(path, 'r', encoding='utf-8')
    json_data = json.load(json_open)

    return json_data[filename]



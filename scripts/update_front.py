import os
import shutil
import yaml
import json

def update_front_end():
    # Send Build Folder
    copy_folders_to_front_end("./build","../front/front_end/src/chain-info")
    # Sending to the front end our config un JSON format
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("../front/front_end/src/brownie-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json)
        print("Front End Updated")

def copy_folders_to_front_end(src, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest)

def main():
    update_front_end()

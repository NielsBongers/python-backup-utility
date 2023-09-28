import os
import yaml
import time
import shutil
import hashlib
import subprocess
from pathlib import Path


def get_config():
    with open("config.yaml", "r") as f:
        try:
            file_contents = yaml.safe_load(f)
            return file_contents
        except yaml.YAMLError as exception:
            print(f"Exception: {exception}")


def get_password():
    with open("password.yaml", "r") as f:
        try:
            file_contents = yaml.safe_load(f)
            return file_contents
        except yaml.YAMLError as exception:
            print(f"Exception: {exception}")


def main():
    config = get_config()
    password = get_password()["password"]

    # command = (
    #     config["veracrypt_folder"]
    #     + "\\"
    #     + config["veracrypt_command"].replace("[password]", password)
    # )

    # try:
    #     subprocess.run(command, check=True)
    # except subprocess.CalledProcessError:
    #     raise

    # try:
    #     if not Path(config["target_disk"]).exists():
    #         raise OSError(f"Path {config['target_disk']} does not exist.")
    # except:
    #     raise

    # time.sleep(5)

    source_folder_root = Path(config["source_folder"])
    source_folder_paths = source_folder_root.glob("**/*")

    relative_folder_paths = []

    for file_path in source_folder_paths:
        if file_path.is_file:
            relative_path = file_path.relative_to(source_folder_root)
            relative_folder_paths.append(relative_path)

    relative_folder_paths = sorted(relative_folder_paths)


if __name__ == "__main__":
    main()

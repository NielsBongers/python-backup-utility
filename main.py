import os
import yaml
import time
import tqdm
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


def hash_file(source_path):
    with open(source_path, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(65536):
            file_hash.update(chunk)
    return file_hash.hexdigest()


def get_file_structure(source_folder_root, excluded_folders=None, hashing=True):
    source_folder_paths = list(source_folder_root.glob("**/*"))

    relative_folder_paths = []

    for file_path in tqdm.tqdm(
        iterable=source_folder_paths,
        total=len(source_folder_paths),
        desc="Converting to relative paths".ljust(50),
    ):
        if file_path.is_file():
            relative_path = file_path.relative_to(source_folder_root)
            top_level_folder = relative_path.parts[0]

            if excluded_folders:
                if top_level_folder in excluded_folders:
                    continue

            relative_folder_paths.append(relative_path)

    sorted_relative_folder_paths = sorted(relative_folder_paths)

    folder_structure_hash = {}

    for file_path in tqdm.tqdm(
        iterable=sorted_relative_folder_paths,
        total=len(sorted_relative_folder_paths),
        desc="Saving file names".ljust(50),
    ):
        absolute_path = Path(source_folder_root, file_path)

        if hashing:
            file_hash = hash_file(absolute_path)
        else:
            file_hash = None
        folder_structure_hash[file_path] = file_hash

    return folder_structure_hash


def copy_file_tree(
    source_folder_structure_hash, source_folder_root, destination_root_path
):
    for file_path in tqdm.tqdm(
        iterable=source_folder_structure_hash.keys(),
        desc="Copying files",
        total=len(source_folder_structure_hash.keys()),
    ):
        absolute_source_file_path = Path(source_folder_root, file_path)
        absolute_destination_file_path = Path(destination_root_path, file_path)
        absolute_destination_file_path.parent.mkdir(exist_ok=True, parents=True)

        shutil.copy(absolute_source_file_path, absolute_destination_file_path)


def get_hash_list(folder_structure_hash):
    for file_hash in folder_structure_hash.values():
        print(file_hash)


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

    # time.sleep(10)

    # try:
    #     if not Path(config["target_disk"]).exists():
    #         raise OSError(f"Path {config['target_disk']} does not exist.")
    # except:
    #     raise

    source_folder_root = Path(config["source_folder"])
    excluded_folders = config["excluded_folders"]
    target_disk = config["target_disk"]

    source_folder_structure_hash = get_file_structure(
        source_folder_root, excluded_folders, hashing=True
    )

    destination_root_path = Path(target_disk, "28092023")

    copy_file_tree(
        source_folder_structure_hash, source_folder_root, destination_root_path
    )

    destination_folder_structure_hash = get_file_structure(
        destination_root_path, hashing=True
    )

    get_hash_list(source_folder_structure_hash)


if __name__ == "__main__":
    main()

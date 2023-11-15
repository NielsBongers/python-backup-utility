import datetime
import hashlib
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import tqdm
import yaml

from logging_setup import get_logger


def get_config():
    logger = get_logger(__name__)
    with open("config/config.yaml", "r") as f:
        try:
            file_contents = yaml.safe_load(f)
            return file_contents
        except yaml.YAMLError as exception:
            logger.exception(f"Exception: {exception}")


def get_password():
    logger = get_logger(__name__)
    with open("config/password.yaml", "r") as f:
        try:
            file_contents = yaml.safe_load(f)
            return file_contents
        except yaml.YAMLError as exception:
            logger.exception(f"Exception: {exception}")


def hash_file(source_path):
    logger = get_logger(__name__)
    try:
        with open(source_path, "rb") as f:
            file_hash = hashlib.md5()
            while chunk := f.read(65536):
                file_hash.update(chunk)
    except Exception as e:
        logger.exception(f"Encountered exception while hashing {source_path}: {e}")
    return file_hash.hexdigest()


def get_file_structure(
    source_folder_root, excluded_folders=None, hashing=True, save_to_file=False
):
    logger = get_logger(__name__)

    source_folder_paths = list(source_folder_root.glob("**/*"))

    relative_folder_paths = []

    for file_path in tqdm.tqdm(
        iterable=source_folder_paths,
        total=len(source_folder_paths),
        desc="Converting to relative paths".ljust(50),
    ):
        if file_path.is_file():
            relative_path = file_path.relative_to(source_folder_root)
            parent_folder = relative_path.parent

            if excluded_folders:
                if str(parent_folder) in excluded_folders:
                    continue

            relative_folder_paths.append(relative_path)

    sorted_relative_folder_paths = sorted(relative_folder_paths)

    folder_structure_hash = {}

    logger.info("Starting file hashing.")

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

    logger.info("Finished hashing all the files.")

    if save_to_file:
        current_date = datetime.datetime.now().strftime("%d%m%Y")
        folder_structure_hash_logging_path = Path(
            "file_hashes", current_date + " - " + str(uuid.uuid4()) + ".csv"
        )

        folder_structure_hash_logging_path.parent.mkdir(exist_ok=True, parents=True)

        try:
            with open(folder_structure_hash_logging_path, "w", encoding="utf-8") as f:
                f.write("path,hash\n")
                for key, value in folder_structure_hash.items():
                    f.write(f"\"{key}','{value}\"\n")
        except Exception as e:
            logger.exception(f"Failed to open {folder_structure_hash_logging_path}.")

    return folder_structure_hash


def copy_file_tree(
    source_folder_structure_hash, source_folder_root, destination_root_path
):
    logger = get_logger(__name__)
    for file_path in tqdm.tqdm(
        iterable=source_folder_structure_hash.keys(),
        desc="Copying files".ljust(50),
        total=len(source_folder_structure_hash.keys()),
    ):
        absolute_source_file_path = Path(source_folder_root, file_path)
        absolute_destination_file_path = Path(destination_root_path, file_path)
        absolute_destination_file_path.parent.mkdir(exist_ok=True, parents=True)

        try:
            shutil.copy(absolute_source_file_path, absolute_destination_file_path)
        except Exception as e:
            logger.exception(f"Encountered exception while copying {file_path}: {e}")


def get_hash_list(folder_structure_hash):
    logger = get_logger(__name__)

    combined_hash = ""

    try:
        for file_hash in folder_structure_hash.values():
            combined_hash += file_hash

        folder_hash = hashlib.sha1()
        folder_hash.update(combined_hash.encode())
    except Exception as e:
        logger.exception(
            f"Encountered exception while hashing the folder structure: {e}"
        )
    return folder_hash.hexdigest()


def open_drive(veracrypt_folder, veracrypt_command, password, target_folder):
    logger = get_logger(__name__)
    logger.info("Mounting VeraCrypt volume.")

    command = (
        veracrypt_folder + "\\" + veracrypt_command.replace("[password]", password)
    )

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.exception(e)
        raise

    time.sleep(10)

    try:
        if not Path(target_folder).exists():
            raise OSError(f"Path {target_folder} does not exist.")
    except OSError as e:
        logger.exception(e)
        raise


def close_drive(veracrypt_folder):
    logger = get_logger(__name__)
    logger.info("Dismounting VeraCrypt volume.")

    command = veracrypt_folder + "\\" + "veracrypt /dismount /quit"

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logger.exception(e)
        raise


def create_backup():
    logger = get_logger(__name__)

    logger.info(f"Starting backup.")

    config = get_config()
    password = get_password()["password"]

    veracrypt_folder = config["veracrypt_folder"]
    veracrypt_command = config["veracrypt_command"]
    target_folder = config["target_folder"]

    source_folder_root = Path(config["source_folder"])
    excluded_folders = config["excluded_folders"]

    use_veracrypt = config["use_veracrypt"]
    compare_hashes = config["compare_hashes"]

    if use_veracrypt:
        open_drive(veracrypt_folder, veracrypt_command, password, target_folder)

    source_folder_structure_hash = get_file_structure(
        source_folder_root, excluded_folders, hashing=compare_hashes, save_to_file=True
    )

    current_date = datetime.datetime.now().strftime("%d%m%Y")
    destination_folder_name = current_date
    destination_root_path = Path(target_folder, destination_folder_name)

    if destination_root_path.exists():
        logger.warning(
            f"Warning: path already exists. Appending UUID to prevent overwriting."
        )
        destination_root_path = Path(destination_root_path / Path(str(uuid.uuid4())))

    copy_file_tree(
        source_folder_structure_hash, source_folder_root, destination_root_path
    )

    destination_folder_structure_hash = get_file_structure(
        destination_root_path, hashing=compare_hashes, save_to_file=True
    )

    source_folder_hash = get_hash_list(source_folder_structure_hash)
    destination_folder_hash = get_hash_list(destination_folder_structure_hash)

    try:
        if source_folder_hash == destination_folder_hash:
            logger.info(
                f"The source folder ({source_folder_root}) and destination folder ({destination_root_path}) hashes are the same: {destination_folder_hash}."
            )
        else:
            raise ValueError(
                f"The source folder hash: {source_folder_hash} and destination folder hash: {destination_folder_hash} do not match."
            )
    except ValueError as e:
        logger.exception(e)

    if use_veracrypt:
        close_drive(veracrypt_folder)


def main():
    create_backup()
    close_drive("D:\\VeraCrypt")


if __name__ == "__main__":
    main()

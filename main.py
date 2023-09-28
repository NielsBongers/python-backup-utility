import yaml
import shutil
from pathlib import Path


def main():
    with open("config.yaml", "r") as f:
        try:
            file_contents = yaml.safe_load(f)

            print(file_contents)
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == "__main__":
    main()

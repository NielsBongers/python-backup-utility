import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def check_latest_hashes():
    file_hash_lists = Path("file_hashes").glob("**/*.csv")

    file_data = []

    for file_hash_list in file_hash_lists:
        file_name = file_hash_list.stem

        date_string = re.search("([0-9]+)", file_name)

        if date_string is None:
            continue

        date_string = date_string.group()
        date = datetime.strptime(date_string, "%d%m%Y")
        entry_data = {"file_path": file_hash_list, "file_name": file_name, "date": date}
        file_data.append(entry_data)

    df = pd.DataFrame(file_data)
    df = df.sort_values("date", ascending=False)

    latest_date = df["date"].max()
    latest_files = df[df["date"] == latest_date]

    data_frame_list = []
    for file_path in latest_files["file_path"]:
        data_frame_list.append(pd.read_csv(file_path))

    df = pd.concat(data_frame_list)

    df["duplicated"] = df["hash"].duplicated(keep=False)
    df = df[df["duplicated"] == False]

    return df

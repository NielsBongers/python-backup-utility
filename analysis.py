from pathlib import Path

import pandas as pd

# file_path_list = [
#     Path("file_hashes/18102023 - 048cf1f6-f1ab-46a6-8c94-9e461e05da49.csv"),
#     Path("file_hashes/18102023 - 4f09f645-8162-45ca-880d-98379018d6eb.csv"),
# ]

# for file_path in file_path_list:
#     with open(file_path, "r", encoding="utf8") as f:
#         with open(
#             "file_hashes/" + file_path.stem + " - corrected" + file_path.suffix,
#             "w",
#             encoding="utf8",
#         ) as g:
#             for line in f:
#                 if len(line) < 33:
#                     g.write(line)
#                     continue

#                 file_path = line[0:-34]
#                 uuid = line[-33:].strip()
#                 corrected_csv_line = f'"{file_path}","{uuid}"'
#                 g.write(corrected_csv_line)
#                 g.write("\n")


df1 = pd.read_csv("file_hashes/13112023 - 2215dd83-9053-4984-915c-3a4c5d5bb1ec.csv")
df2 = pd.read_csv("file_hashes/13112023 - 29623e69-23fa-45eb-a925-b236d3f2c7d6.csv")

df = pd.concat([df1, df2])
df["duplicated"] = df["hash"].duplicated(keep=False)
df = df[df["duplicated"] == False]

print(df)

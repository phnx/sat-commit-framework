import os
import sys

import ftfy


def convert_to_utf8_and_replace(target_file: str):
    with open(target_file, "rb") as f:
        rawdata = f.read()
        fixed_text = ftfy.fix_text(rawdata.decode("utf-8", errors="replace"))

    with open(target_file, "w", encoding="utf-8") as f:
        f.write(fixed_text)
        # print(f"Converted {target_file} to UTF-8")


def convert_folder(target_path: str):
    for root, dirs, files in os.walk(target_path):
        # exclude system and hidden folders
        dirs[:] = [
            d for d in dirs if not d.startswith(".") and not d.startswith("__")
        ]
        print("converting files in:", root)
        for filename in files:
            target_file = os.path.join(root, filename)
            if os.path.isfile(target_file):
                convert_to_utf8_and_replace(target_file=target_file)

    print("conversion completed")


if __name__ == "__main__":
    args = sys.argv[1:]

    target_path = args[0]
    convert_folder(target_path=target_path)

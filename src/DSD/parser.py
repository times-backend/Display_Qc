import os
import pandas as pd

def open_file():
    folder = os.path.abspath("downloads")
    xlsx_files = [f for f in os.listdir(folder) if f.endswith(".xls")]

    if not xlsx_files:
        raise FileNotFoundError("No .xlsx file found in downloads folder.")

    if len(xlsx_files) > 1:
        raise FileExistsError("Multiple .xlsx files found in downloads folder. Expected only one.")

    return os.path.join(folder, xlsx_files[0])

def read_file(lineitem_name):
    try:
        file_path = open_file()
        print(file_path)
        xls = pd.ExcelFile(file_path)

        for sheet_name in xls.sheet_names:
            df = xls.parse(sheet_name=sheet_name)
            df = df.dropna(axis=1, how='all')
            match = df[df.isin([lineitem_name]).any(axis=1)]
            if not match.empty:
                matched_row = match.iloc[0]
                row_dict = matched_row.to_dict()

                for key, value in row_dict.items():
                    if isinstance(value, str):
                        row_dict[key] = value.split(",")
                        if len(row_dict[key]) == 1:
                            row_dict[key] = row_dict[key][0].strip()
                        elif len(row_dict[key]) == 0:
                            row_dict[key] = "TBD"
                    else:
                        value
                return row_dict

        print(f"'{lineitem_name}' not found in any sheet.")
        return None

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
import os
import pandas as pd

def clean_number(val):
    try:
        if isinstance(val, str):
            val = val.replace(",", "").replace("₹", "").strip()
        return float(val)
    except:
        return ""

def extract_til_and_geo_rowwise():
    all_rows = []
    folder = os.path.abspath("downloads")

    for file in os.listdir(folder):
        if not file.endswith(".xlsx"):
            continue

        file_path = os.path.join(folder, file)
        try:
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                try:
                    df_raw = xls.parse(sheet_name, header=None)
                    if df_raw.empty:
                        print(f"Skipping empty sheet: {file} - {sheet_name}")
                        continue

                    # ===== Step 1: Extract Expresso ID =====
                    expresso_id = ""
                    for r in range(min(20, len(df_raw))):
                        for c in range(len(df_raw.columns)):
                            cell_val = str(df_raw.iat[r, c]).strip()
                            if cell_val.lower() == "expresso id":
                                if c + 1 < len(df_raw.columns):
                                    id_val = df_raw.iat[r, c + 1]
                                    if pd.notna(id_val):
                                        expresso_id = str(id_val).strip()
                                break
                        if expresso_id:
                            break

                    # ===== Step 2: Identify Header Row and Column Indices =====
                    header_row_idx = None
                    col_indices = {
                        'til': None, 'geo': None, 'kpi': None, 'audience': None,
                        'fcap': None, 'site': None, 'sizes': None, 'platform': None,
                        'start_date': None, 'end_date': None, 'clicks': None,
                        'rate': None, 'amount': None, 'impressions': None,
                        'days': None
                    }

                    for r in range(len(df_raw)):
                        row = df_raw.iloc[r].astype(str).str.strip().str.lower()
                        if "til package name" in row.values:
                            header_row_idx = r
                            for c, val in enumerate(row):
                                val_clean = val.lower()
                                if "til package name" in val_clean:
                                    col_indices['til'] = c
                                elif val_clean == "geo":
                                    col_indices['geo'] = c
                                elif "kpi" in val_clean:
                                    col_indices['kpi'] = c
                                elif "audience" in val_clean:
                                    col_indices['audience'] = c
                                elif val_clean == "fcap":
                                    col_indices['fcap'] = c
                                elif any(keyword in val_clean.lower() for keyword in ("site", "portal")):
                                    col_indices['site'] = c
                                elif "size" in val_clean:
                                    col_indices['sizes'] = c
                                elif val_clean == "platform":
                                    col_indices['platform'] = c
                                elif val_clean == "start date":
                                    col_indices['start_date'] = c
                                elif val_clean == "end date":
                                    col_indices['end_date'] = c
                                elif "click" in val_clean:
                                    col_indices['clicks'] = c
                                elif "rate" in val_clean:
                                    col_indices['rate'] = c
                                elif "amount" in val_clean:
                                    col_indices['amount'] = c
                                elif any(keyword in val_clean.lower() for keyword in ("impression", "imp", "total")):
                                    col_indices['impressions'] = c
                                elif "no of days" in val_clean:
                                    col_indices['days'] = c
                            break

                    if header_row_idx is None or col_indices['til'] is None:
                        print(f"Header not found in: {file} - {sheet_name}")
                        continue

                    # ===== Step 3: Loop over data rows =====
                    for row_idx in range(header_row_idx + 1, len(df_raw)):
                        til_val = df_raw.iat[row_idx, col_indices['til']]
                        if pd.isna(til_val):
                            continue
                        til_text = str(til_val).strip()
                        if not til_text or til_text.lower().startswith("total"):
                            break

                        def safe_get(idx):
                            try:
                                val = df_raw.iat[row_idx, idx]
                                return str(val).strip() if pd.notna(val) else ""
                            except:
                                return ""

                        row_data = {
                            "expresso_id": expresso_id,
                            "file_name": file,
                            "package_name": til_text,
                            "geo": safe_get(col_indices['geo']),
                            "KPI": safe_get(col_indices['kpi']),
                            "FCAP": safe_get(col_indices['fcap']),
                            "Site": safe_get(col_indices['site']),
                            "Audience": safe_get(col_indices['audience']),
                            "Sizes": safe_get(col_indices['sizes']),
                            "Platform": safe_get(col_indices['platform']),
                            "Start Date": safe_get(col_indices['start_date']),
                            "End Date": safe_get(col_indices['end_date']),
                            "Clicks": safe_get(col_indices['clicks']),
                            "Rate": clean_number(safe_get(col_indices['rate'])),
                            "Amount": clean_number(safe_get(col_indices['amount'])),
                            "Total Impression": safe_get(col_indices['impressions']),
                            "No Of Days": safe_get(col_indices['days']),
                        }
                        non_empty_count = sum(1 for v in row_data.values() if v and (not isinstance(v, str) or v.strip() != ''))

                        if non_empty_count > 4 :
                            all_rows.append(row_data)

                except Exception as sheet_error:
                    print(f"Error processing sheet {sheet_name} in file {file}: {sheet_error}")

        except Exception as file_error:
            print(f"Error reading file {file_path}: {file_error}")
    return all_rows

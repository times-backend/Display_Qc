from dateutil import parser
from dateutil.tz import gettz  #  correct import for timezones
from datetime import datetime, date
from src.line_item_details.expresso import fetch_full_expresso_details
from src.DSD.parser import extract_til_and_geo_rowwise
from src.DSD.download import Dsd_Download


def parse_date(date_input):
    if not date_input:
        return None

    # If already a date or datetime object, just format it
    if isinstance(date_input, (datetime, date)):
        return date_input.strftime("%Y-%m-%d")

    try:
        # Handle strings (with possible timezones like GMT)
        tzinfos = {"GMT": gettz("GMT")}  # ✅ correct usage
        parsed = parser.parse(str(date_input).strip(), tzinfos=tzinfos, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Failed to parse date: {date_input}\nError: {e}")
        return None


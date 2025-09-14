# Getting combined data form expresso and dsd

from src.DSD.parser import extract_til_and_geo_rowwise
from src.line_item_details.expresso import fetch_full_expresso_details
from src.helper.dsd_vs_expresso import clean_line_item_name , dsd_vs_expresso

#def combine_data(line_item_name:str):
#    dsd_data = extract_til_and_geo_rowwise()
#    line_item_name = clean_line_item_name(line_item_name)
#    line_item_data = fetch_full_expresso_details(line_item_name)

dsd_vs_expresso("28101110DOMEBUREAUTILROSINATFCPMTOIMRECWBMWBDAVPMRECPKG214620")
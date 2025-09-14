from src.line_item_details.expresso import fetch_full_expresso_details
from src.DSD.parser import extract_til_and_geo_rowwise
from src.api.utils import parse_date
from logger.log import setup_logger
from typing import Tuple, Dict
from googleads import ad_manager
from final_data_details.line_item_details_in_gam import get_line_items_details_by_name
from dotenv import load_dotenv
import os


load_dotenv()
NEW_GAM = os.environ.get("NEW_GAM")

logger = setup_logger("expresso_vs_dsd")
client = ad_manager.AdManagerClient.LoadFromStorage(NEW_GAM)

def clean_line_item_name(name: str) -> str:
    while len(name) >= 5 and not name[-5:].isdigit():
        name = name[:-1]
    return name


#def compare_line_item_to_dsd(lineitem_data: Dict, dsd_item: Dict) -> Dict[str, Dict]:
#    try:
#        dsd_package_name = dsd_item.get("package_name", "")
#        gam_package_name = lineitem_data.get("package_name", "")
#
#        if dsd_package_name and gam_package_name:
#            # Case-insensitive word-level fuzzy match
#            dsd_words = dsd_package_name.lower().split()
#            gam_name_lower = gam_package_name.lower()
#            match = any(word in gam_name_lower for word in dsd_words)
#            print(gam_name_lower, dsd_words)
#        else:
#            match = False
#        return {
#            "package_name": {
#                "match": match,
#                "expresso": gam_package_name,
#                "dsd": dsd_package_name
#            },
#            "start_date": {
#                "match": parse_date(dsd_item.get("Start Date")) == parse_date(lineitem_data.get("lineitem_start_date")),
#                "expresso": lineitem_data.get("lineitem_start_date"),
#                "dsd": dsd_item.get("Start Date")
#            },
#            "end_date": {
#                "match": parse_date(dsd_item.get("End Date")) == parse_date(lineitem_data.get("lineitem_end_date")),
#                "expresso": lineitem_data.get("lineitem_end_date"),
#                "dsd": dsd_item.get("End Date")
#            },
#            "geo": {
#                "match": dsd_item.get("geo") == lineitem_data.get("billable_state"),
#                "expresso": lineitem_data.get("billable_state"),
#                "dsd": dsd_item.get("geo")
#            },
#            "daily_rate": {
#                "match": round(float(dsd_item["Rate"])) if str(dsd_item.get("Rate", "")).replace('.', '', 1).isdigit() else dsd_item.get("Rate", "") == round(float(lineitem_data.get("rate_card_inr", 0))),
#                "expresso": lineitem_data.get("rate_card_inr"),
#                "dsd": dsd_item.get("Rate")
#            },
#            "impressions": {
#                "match": (
#                    round(float(dsd_item.get("Total Impression", 0))) == round(float(lineitem_data.get("quantity", 0)))
#                    if str(dsd_item.get("Total Impression", "")).replace('.', '', 1).isdigit()
#                    and str(lineitem_data.get("quantity", "")).replace('.', '', 1).isdigit()
#                    else False
#                ),
#                "expresso": lineitem_data.get("quantity"),
#                "dsd": dsd_item.get("Total Impression")
#            },
#            "amount": {
#                "match": (
#                    round(float(dsd_item.get("Amount", 0))) == round(float(lineitem_data.get("SP_inr", 0)))
#                    if str(dsd_item.get("Amount", "")).replace('.', '', 1).isdigit()
#                    and str(lineitem_data.get("SP_inr", "")).replace('.', '', 1).isdigit()
#                    else False
#                ),
#                "expresso": lineitem_data.get("SP_inr"),
#                "dsd": dsd_item.get("Amount")
#            },
#
#            "site": {
#                "match": dsd_item.get("Site", "").lower() in lineitem_data.get("Website_with_platform", "").lower(),
#                "expresso": lineitem_data.get("Website_with_platform"),
#                "dsd": dsd_item.get("Site")
#            }
#        }
#    except Exception as e:
#        logger.exception(f"Comparison failed: {str(e)}")
#        return {"error": str(e)}
#
#
#def dsd_vs_expresso(lineitem_name: str) -> tuple[dict, int]:
#    try:
#        lineitem_name = clean_line_item_name(lineitem_name)
#        if not lineitem_name:
#            return {"error": "Missing or invalid 'lineitem_name' parameter"}, 400
#
#        logger.info(f"Starting comparison for line item: {lineitem_name}")
#        expresso_data = fetch_full_expresso_details(lineitem_name=lineitem_name)
#        if not expresso_data:
#            return {"error": "No data found in Expresso for this line item"}, 404
#
#        line_item = expresso_data[0]
#
#        dsd_data = extract_til_and_geo_rowwise()
#        if not dsd_data:
#            return {"error": "No DSD data available"}, 404
#        #print(dsd_data)
#        for dsd_item in dsd_data:
#            comparison_result = compare_line_item_to_dsd(line_item, dsd_item)
#
#            if comparison_result.get("package_name", {}).get("match"):
#                logger.info("First matching DSD row found. Returning comparison.")
#
#                # Keys already covered by the comparison
#                compared_keys = {
#                    "package_name", "start_date", "end_date", "geo",
#                    "daily_rate", "impressions", "amount", "site"
#                }
#
#                # Convert keys to match DSD field casing
#                dsd_field_map = {
#                    "package_name": "package_name",
#                    "start_date": "Start Date",
#                    "end_date": "End Date",
#                    "geo": "geo",
#                    "daily_rate": "Rate",
#                    "impressions": "Total Impression",
#                    "amount": "Amount",
#                    "site": "Site"
#                }
#
#                excluded_fields = {dsd_field_map[key] for key in compared_keys if key in dsd_field_map}
#
#                # Build dsd_raw with only non-compared fields
#                dsd_raw = {k: v for k, v in dsd_item.items() if k not in excluded_fields}
#
#                # Attach dsd_raw to the result
#                comparison_result["dsd_extra_fields"] = dsd_raw
#                comparison_result["dsd_raw"] = dsd_item
#                print(comparison_result)
#                
#                return comparison_result, 200
#
#        logger.warning("No matching DSD entry found for the given line item.")
#        return {"error": "No matching DSD entry found"}, 404
#
#    except Exception as e:
#        logger.exception(f"Exception occurred during comparison: {str(e)}")
#        return {"error": "Internal server error"}, 500
#
##data = dsd_vs_expresso("28101110DOMEBUREAUTILROSINATFCPMTOIMRECWBMWBDAVPMRECPKG214620")
##print(data)
#def data_vs_gam(line_item_name: str):
#    """
#    Compares line item data from internal DSD source vs Google Ad Manager (GAM) line item details.
#    Logs matching fields and optionally allows checking completed line items.
#
#    Args:
#        line_item_name (str): The name of the line item to compare.
#
#    Returns:
#        List[Dict]: A list containing budget and goal comparisons for matching line items.
#    """
#    line_item_name = clean_line_item_name(line_item_name)
#    data = dsd_vs_expresso(line_item_name)
#    gam_data = get_line_items_details_by_name(client, line_item_name)
#
#    dsd_data = data[0].get("dsd_raw")
#    #print()
#    #print(dsd_data)
#    dsd_start_date = dsd_data.get("Start Date")
#    dsd_end_date = dsd_data.get("End Date")
#    dsd_geo = dsd_data.get("geo")
#    dsd_fcap = dsd_data.get("FCAP")
#    dsd_site = dsd_data.get("Site")
#    dsd_audience = dsd_data.get("Audience")
#    dsd_sizes = dsd_data.get("Sizes")
#    dsd_platform = dsd_data.get("Platform")
#    dsd_rate = dsd_data.get("Rate")
#    dsd_amt = dsd_data.get("Amount")
#    dsd_total_goal = dsd_data.get("Total Impression")
#
#    logger.info(f"{line_item_name} Package has {len(gam_data)} lines to process.")
#
#    inputs = []
#
#    for fields in gam_data:
#        status = fields.get("status")
#        line_name = fields.get("name")
#
#        #if status == "COMPLETED":
#            #take_input = str(input("This line is completed. Do you still want to QC this line? (yes/no): "))
#        #    if take_input.lower() != "yes":
#        #        logger.info("You chose to skip the line as status is COMPLETED.")
#        #        continue
#
#        if line_item_name in line_name:
#            logger.info("Line name matched")
#
#        if dsd_start_date == fields.get('start_date'):
#            logger.info(f"Start date matched: {dsd_start_date} == {fields.get('start_date')}")
#
#        if dsd_end_date == fields.get('end_date'):
#            logger.info(f"End date matched: {dsd_end_date} == {fields.get('end_date')}")
#
#        # Handle geo logic
#        targeted_geo = fields.get('targeted_geo', [])
#        excluded_geo = fields.get('excluded_geo', [])
#        if dsd_geo in targeted_geo or (dsd_geo in excluded_geo and "india" in ' '.join(targeted_geo).lower()):
#            logger.info(
#                f"Geo matched.\n"
#                f"→ DSD Geo: {dsd_geo}\n"
#                f"→ In Targeted: {dsd_geo in targeted_geo}\n"
#                f"→ In Excluded: {dsd_geo in excluded_geo}"
#            )
#
#        # Check priority for CPM lines
#        if "cpm" in line_item_name.lower():
#            if fields.get("priority") in (6, 8, 10):
#                logger.info("CPM priority is valid")
#
#        # FCAP match
#        if dsd_fcap and int(dsd_fcap) == int(fields.get("fcap", 0)):
#            logger.info("FCAP matched")
#
#        # Append budget and goal for manual review
#        inputs.append({"line_budget": {line_name: fields.get("line_budget")}})
#        inputs.append({"goal": {line_name: fields.get("goal")}})
#    #print(inputs)
#    return inputs
#
#        #print(gam_data)
#        #print(dsd_data)
#        
#
##data_vs_gam("28101110DOMEBUREAUTILROSINATFCPMTOIMRECWBMWBDAVPMRECPKG214620")
##dsd_vs_expresso("27651110DOMEINTERATILBOTHINALLCPMVERNEWSSTDBANFY23TILSTANDARDBANNERPKG215107")


def compare_package_name(expresso, dsd):
    dsd_package_name = dsd.get("package_name", "")
    gam_package_name = expresso.get("package_name", "")
    if dsd_package_name and gam_package_name:
        dsd_words = dsd_package_name.lower().split()
        gam_name_lower = gam_package_name.lower()
        match = any(word in gam_name_lower for word in dsd_words)
    else:
        match = False
    return {
        "match": match,
        "expresso": gam_package_name,
        "dsd": dsd_package_name
    }

def compare_start_date(expresso, dsd):
    return {
        "match": parse_date(dsd.get("Start Date")) == parse_date(expresso.get("lineitem_start_date")),
        "expresso": expresso.get("lineitem_start_date"),
        "dsd": dsd.get("Start Date")
    }

def compare_end_date(expresso, dsd):
    return {
        "match": parse_date(dsd.get("End Date")) == parse_date(expresso.get("lineitem_end_date")),
        "expresso": expresso.get("lineitem_end_date"),
        "dsd": dsd.get("End Date")
    }

def compare_geo(expresso, dsd):
    return {
        "match": dsd.get("geo") == expresso.get("billable_state"),
        "expresso": expresso.get("billable_state"),
        "dsd": dsd.get("geo")
    }

def compare_daily_rate(expresso, dsd):
    dsd_rate = dsd.get("Rate", "")
    expresso_rate = expresso.get("gross_rate_inr", 0)
    try:
        match = round(float(dsd_rate)) == round(float(expresso_rate))
    except:
        match = dsd_rate == expresso_rate
    return {
        "match": match,
        "expresso": expresso_rate,
        "dsd": dsd_rate
    }

def compare_impressions(expresso, dsd):
    dsd_imp = dsd.get("Total Impression", "")
    expresso_imp = expresso.get("quantity", "")
    try:
        match = round(float(dsd_imp)) == round(float(expresso_imp))
    except:
        match = False
    return {
        "match": match,
        "expresso": expresso_imp,
        "dsd": dsd_imp
    }

def compare_amount(expresso, dsd):
    dsd_amt = dsd.get("Amount", "")
    expresso_amt = expresso.get("SP_inr", "")
    try:
        match = round(float(dsd_amt)) == round(float(expresso_amt))
    except:
        match = False
    return {
        "match": match,
        "expresso": expresso_amt,
        "dsd": dsd_amt
    }

def compare_site(expresso, dsd):
    dsd_site = dsd.get("Site", "").lower()
    expresso_site = expresso.get("Website_with_platform", "").lower()
    match = dsd_site in expresso_site
    return {
        "match": match,
        "expresso": expresso.get("Website_with_platform"),
        "dsd": dsd.get("Site")
    }

FIELD_COMPARATORS = {
    "package_name": compare_package_name,
    "start_date": compare_start_date,
    "end_date": compare_end_date,
    "geo": compare_geo,
    "daily_rate": compare_daily_rate,
    "impressions": compare_impressions,
    "amount": compare_amount,
    "site": compare_site
}

def dsd_vs_expresso(lineitem_name: str) -> tuple[dict, int]:
    try:
        lineitem_name = clean_line_item_name(lineitem_name)
        if not lineitem_name:
            return {"error": "Missing or invalid 'lineitem_name' parameter"}, 400

        logger.info(f"Starting comparison for line item: {lineitem_name}")
        expresso_data = fetch_full_expresso_details(lineitem_name=lineitem_name)
        if not expresso_data:
            return {"error": "No data found in Expresso for this line item"}, 404

        line_item = expresso_data[0]

        dsd_data = extract_til_and_geo_rowwise()
        if not dsd_data:
            # TODO: Plug in fallback DSD fetch logic here
            logger.warning("Primary DSD source returned empty.")
            return {"error": "No DSD data available"}, 404

        for dsd_item in dsd_data:
            comparison_result = {}
            for field_name, comparator in FIELD_COMPARATORS.items():
                comparison_result[field_name] = comparator(line_item, dsd_item)

            # Use package_name match to determine if this row qualifies
            if comparison_result["package_name"]["match"]:
                logger.info("First matching DSD row found. Returning comparison.")

                # Identify which DSD fields have already been compared
                compared_keys = FIELD_COMPARATORS.keys()
                dsd_raw = {k: v for k, v in dsd_item.items() if k not in {
                    "package_name", "Start Date", "End Date", "geo",
                    "Rate", "Total Impression", "Amount", "Site"
                }}

                comparison_result["dsd_extra_fields"] = dsd_raw
                comparison_result["dsd_raw"] = dsd_item

                return comparison_result, 200

        logger.warning("No matching DSD entry found for the given line item.")
        return {"error": "No matching DSD entry found"}, 404

    except Exception as e:
        logger.exception(f"Exception occurred during comparison: {str(e)}")
        return {"error": "Internal server error"}, 500

from src.final_data_details.line_item_details_in_gam import get_line_items_details_by_name , client

def finalData_vs_gamData(lineitem_name: str):
    results, status_code = dsd_vs_expresso(lineitem_name)
    expresso_data = fetch_full_expresso_details(lineitem_name=lineitem_name)
    gam_dict = get_line_items_details_by_name(client, lineitem_name)

    fields_to_check = {}

    if status_code == 200:
        if isinstance(results, dict):
            results = [results]

        for item in results:
            if not isinstance(item, dict):
                continue

            for key, value_dict in item.items():
                if key in ('dsd_extra_fields', 'dsd_raw'):
                    fields_to_check[key] = value_dict
                    continue

                if isinstance(value_dict, dict):
                    if value_dict.get("match") is True:
                        fields_to_check[key] = value_dict.get("dsd", None)
                    else:
                        fields_to_check[key] = value_dict.get("expresso", None)

        # Add additional fields from expresso
        if expresso_data:
            fields_to_check["currency_code"] = expresso_data[0].get("currency_code")
            fields_to_check["cpd_daily_rate"] = expresso_data[0].get("rate_card_inr")
            fields_to_check["total_amt"] = expresso_data[0].get("SP_inr")
            fields_to_check["goal"] = expresso_data[0].get("cpd_total_qty") if "cpd" in lineitem_name.lower() else "TBD"
            fields_to_check["cpd_booked_dates"] = [d.strip() for d in expresso_data[0].get("cpd_booked_dates") .split("|")]
    #  Now perform comparison with GAM
    comparison = compare_final_and_gam(fields_to_check, gam_dict)
    data = {
        "final_data": fields_to_check,
        "gam_data": [gam_data for gam_data in gam_dict],
        "comparison": comparison
    }
    
    return data

def compare_final_and_gam(final_data: dict, gam_data_list: list):
    if not gam_data_list:
        return {}

    results = {}

    for idx, gam_data in enumerate(gam_data_list, start=1):
        comparison_fields = {}

        # Case-insensitive key match
        common_keys = set(k.lower() for k in final_data) & set(k.lower() for k in gam_data)

        for key in common_keys:
            final_key = next(k for k in final_data if k.lower() == key)
            gam_key = next(k for k in gam_data if k.lower() == key)

            final_value = final_data.get(final_key)
            gam_value = gam_data.get(gam_key)

            if isinstance(final_value, list) and isinstance(gam_value, list):
                comparison_fields[final_key] = {
                    "match": sorted(final_value) == sorted(gam_value),
                    "final_data": final_value,
                    "gam_data": gam_value,
                }
            else:
                norm_final = normalize_value(final_value)
                norm_gam = normalize_value(gam_value)
                comparison_fields[final_key] = {
                    "match": norm_final == norm_gam,
                    "final_data": final_value,
                    "gam_data": gam_value,
                }

        # Custom cross-field comparison for cpd_booked_dates vs day_parting_dates[0]["dates"]
        if "cpd_booked_dates" in final_data and "day_parting_dates" in gam_data:
            final_dates = sorted(final_data.get("cpd_booked_dates") or [])
            gam_dates = sorted(
                gam_data["day_parting_dates"][0].get("dates", [])
                if gam_data["day_parting_dates"] else []
            )

            comparison_fields["cpd_booked_dates"] = {
                "match": final_dates == gam_dates,
                "final_data": final_dates,
                "gam_data": gam_dates,
            }

        # Build extra info fields with fallbacks
        extra_info = {
            "excluded_geo": gam_data.get("excluded_geo") or "Not excluded_geo",
            "fcap": gam_data.get("fcap") or "Not fcap",
            "targetedAdUnits": gam_data.get("targetedAdUnits") or "there might be a problem to get targetedAdUnits",
            "excludedAdUnits": gam_data.get("excludedAdUnits") or "Not excludedAdUnits",
            "targetedPlacementIds": gam_data.get("targetedPlacementIds") or "Not targetedPlacementIds",
            "audience": gam_data.get("audience") or "Not audience",
        }

        # Add day_parting_dates details (assuming first element)
        if gam_data.get("day_parting_dates"):
            dpd = gam_data["day_parting_dates"][0]
            extra_info.update({
                "day_parting_days": dpd.get("days", "Not days"),
                "day_parting_startTime": dpd.get("startTime", "Not startTime"),
                "day_parting_endTime": dpd.get("endTime", "Not endTime"),
            })
        else:
            extra_info.update({
                "day_parting_days": "Not days",
                "day_parting_startTime": "Not startTime",
                "day_parting_endTime": "Not endTime",
            })

        # Use GAM 'name' as label if present
        gam_name = gam_data.get("name", f"gam_{idx}")
        comparison_key = f"comparison_{gam_name}"

        results[comparison_key] = {
            "matched_gam": gam_data,
            "fields": comparison_fields,
            "extra_info": extra_info,
        }

    return results



def normalize_value(value):
    if isinstance(value, str):
        return value.strip().lower()
    elif isinstance(value, list):
        return sorted([str(v).strip().lower() for v in value])
    elif isinstance(value, (int, float)):
        return value
    elif value is None:
        return ""
    else:
        return str(value).strip().lower()

#finalData_vs_gamData("28283440DOMEINFORMTILHOMEINATFCPDNBTRCHPWBWPVNNGDVPMRECPKG215877")
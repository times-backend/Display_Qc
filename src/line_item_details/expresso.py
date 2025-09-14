import json
from line_item_details.auth_utils import generate_jwt, fetch_package_details
from line_item_details.bq_line_item_details import get_rows_by_lineitem_name
from src.constants import EXPRESSO_TABLE
from dotenv import load_dotenv
import os
from logger.log import setup_logger
from DSD.download import Dsd_Download

load_dotenv()
logger = setup_logger("expresso_details")

# user credentials for log in
username=os.environ.get("email")
plaintext_password=os.environ.get("plaintext_password")

def fetch_full_expresso_details(lineitem_name):
    """
    Get comprehensive information about an expresso campaign from multiple sources
    
    Args:
        expresso_id: The expresso ID to lookup
    
    Returns:
        A dictionary containing the extracted campaign details
    """
   
    logger.info("\n===== Expresso API Data =====")
    expresso_id = lineitem_name[:6]
    try:        
        # Generate JWT token
        jwt_token = generate_jwt(username, plaintext_password)
        
        # Fetch package details from API
        api_data = fetch_package_details(jwt_token, expresso_id)
        
        if api_data:
            logger.info("Successfully retrieved data from Expresso API")
        else:
            logger.critical("Failed to retrieve data from Expresso API")
    except Exception as e:
        logger.error(f"Error fetching API data: {str(e)}")
        api_data = None
    
    # Combine and save all data to a comprehensive JSON file
    logger.info("\n===== Generating Combined Report =====")
    # Extract the campaign details from the nested API response for easier access
    campaign_details =[]
    if api_data and isinstance(api_data, dict):
        for key, package_data in api_data.items():
         if isinstance(package_data, dict):
            campaign_details.append(package_data)
    Website_with_platform = None
    
    for item in campaign_details:
        for key , value in item.items():
            if key == "Website(s) with platform":
                Website_with_platform = value
          

    lineitem_details = get_rows_by_lineitem_name(
                            lineitem_name=lineitem_name,
                            table_id=EXPRESSO_TABLE
                        )
    
    for detail in lineitem_details:
        detail["Website_with_platform"]=Website_with_platform
    logger.info(f"lineitem_details are \n{lineitem_details}")
    if lineitem_details:
        return lineitem_details
    return campaign_details
  
#if __name__ == "__main__":
#    fetch_full_expresso_details(
#        lineitem_name="27879510DOMEDIRECTTILHOMEINALLCPDTOIMRECHPWEBWAPDAVPMRECPKG213484"
#        )


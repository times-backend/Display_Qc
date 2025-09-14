from google.cloud import bigquery
import os
from dotenv import load_dotenv
from src.constants import EXPRESSO_TABLE, BOOKING_TABLE
from logger.log import setup_logger

logger = setup_logger("bq_logger")

load_dotenv()

G_CREDS = os.getenv("G_CREDS")
if not G_CREDS or not os.path.exists(G_CREDS):
    logger.error("Google CREDS is not set or file not found")
    raise Exception("G_CREDS is not set or file not found.")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = G_CREDS

# Initialize BigQuery client
client = bigquery.Client()

def get_rows_by_lineitem_name(lineitem_name: str, table_id: str) -> list[dict]:
    """
    Queries BigQuery table for all rows where `lineitem_name` matches the given value.
    
    Args:
        lineitem_name (str): The line item name to search for.
        table_id (str): Full table ID in the form `project.dataset.table`.
        
    Returns:
        List[Dict]: List of matching rows as dictionaries.
    """

    query = f"""
    SELECT *
    FROM `{table_id}`
    WHERE lineitem_name = @search_value
    """ 

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("search_value", "STRING", lineitem_name)
        ]
    )

    try:
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        rows = [dict(row) for row in results]

        logger.info(f"\n Found {len(rows)} row(s) for lineitem_name = '{lineitem_name}'")
        return rows

    except Exception as e:
        print(f"\n Error querying BigQuery: {e}")
        return []
    
#table = get_rows_by_lineitem_name("27651110DOMEINTERATILBOTHINALLCPMVERNEWSSTDBANFY23TILSTANDARDBANNERPKG215107", "acoe21.til_strategic.expresso_ro_li_pricing_parent_only")
#print(table)
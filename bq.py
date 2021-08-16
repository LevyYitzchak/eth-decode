import logging
from google.cloud import bigquery

BQ_ETH_LOGS = "`bigquery-public-data.crypto_ethereum.logs`"

# Construct a BigQuery client object.
client = bigquery.Client()

def get_logs(address, func_sign, limit=100, print_query=True):    
    query = f"""
            SELECT * 
            FROM {BQ_ETH_LOGS}, 
            UNNEST(topics) t 
            WHERE 
            t in (  "{','.join(func_sign)}"   )
            AND address in ( "{','.join(address)}" ) 
            AND DATE(block_timestamp) >= "2020-01-01"
            """

    if limit:
        query += f"LIMIT {limit}"
    
    query_job = client.query(query)  # Make an API request.
    if print_query: print(query)
    return query_job.result().to_dataframe()

def insert_rows(dataset_name, table_name, rows_list):
    rows_n = len(rows_list)
    table_ref = client.dataset(dataset_name).table(table_name)
    table = client.get_table(table_ref)
    response_list = client.insert_rows(table, rows_list)
    if len(response_list) > 0:
        







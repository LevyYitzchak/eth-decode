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


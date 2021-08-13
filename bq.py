from google.cloud import bigquery

BQ_ETH_LOGS = "`bigquery-public-data.crypto_ethereum.logs`"

# Construct a BigQuery client object.
client = bigquery.Client()
test = "usa_names"
query = f"""
        SELECT * 
        FROM {BQ_ETH_LOGS}, 
        UNNEST(topics) t 
        WHERE t = "0x3bb1ff40e32fd6b2e3b81f6a7441852a5c72ec25d116b141b1a1a2e8f0404095" 
        AND address in ( "0xab647b8fd9e370448d4eeb96582fe839f3d0bb24" ) 
        AND DATE(block_timestamp) >= "2020-01-01"
        LIMIT 10
        """
query_job = client.query(query)  # Make an API request.

print("The query data:")
for row in query_job:
    # Row values can be accessed by field name or index.
    print(row)



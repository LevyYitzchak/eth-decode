import logging
import typing
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import pandas as pd

BQ_ETH_LOGS = "`bigquery-public-data.crypto_ethereum.logs`"

# Construct a BigQuery client object.
client = bigquery.Client()
project = client.project

class BQ_table:
    def __init__(
        self,
        dataset_name : str,
        table_name : str):

        self.dataset_name = dataset_name
        self.table_name = table_name
        self.project = project

        self.table_id = ".".join([
            self.project, 
            self.dataset_name, 
            self.table_name])

        self._check_exists()
    
    def _check_exists(self):
        try:
            self._assign()    
        except NotFound:
            self.exists = False

    
    def _assign(self):
        table_ref = client.dataset(self.dataset_name).table(self.table_name)
        self.table = client.get_table(table_ref)  # API request
        self.exists = True

    def uplaoad_df_to_bq(
        self,
        df : pd.DataFrame):
        rows_list = [row_dict 
        for index, row_dict
        in df.to_dict(orient="index").items()]

        return self.insert_rows(rows_list)
    
    def download_table(self, limit=100, print_query=True):
        query = f"""
                SELECT * 
                FROM `{self.table_id}` 
                """

        if limit:
            query += f"LIMIT {limit}"
        
        query_job = client.query(query) # Make an API request.
        if print_query: print(query)

        return query_job.result().to_dataframe()

    
    def insert_rows(
        self, 
        rows_list : typing.List[dict]
        ) -> list:
        
        self._assign()

        rows_n = len(rows_list)
        response_list = client.insert_rows(self.table, rows_list)
        errors_n = len(response_list)
        if errors_n > 0:
            logging.error(f"""
            Big Query insert errors - 
            From {rows_n} to be inserted, {errors_n} failed.""")
            logging.error(f"""First error example - 
            {response_list[0]}""")

            if errors_n > 1:
                logging.error(f"""Last error example - 
                {response_list[-1]}""")
        
        return response_list

    def _create_schema_from_df(self, df):
        self.schema = create_bq_schema(df)
        self.schema_list = []
        for key, d_type in self.schema.items():
                self.schema_list.append(
                    bigquery.SchemaField(
                        key,
                        d_type,
                        mode="NULLABLE"))
    
    def create_table_from_df(
        self, 
        df, 
        partitioned_day=False):
        self._create_schema_from_df(df)
        table = bigquery.Table(
            self.table_id, 
            schema=self.schema_list)
        if partitioned_day:
            # https://googleapis.dev/python/bigquery/latest/generated/google.cloud.bigquery.table.TimePartitioning.html
            # https://cloud.google.com/bigquery/docs/creating-partitioned-tables#python
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY,
                field=None,  # If not set, the table is partitioned by pseudo column `_PARTITIONTIME`
                expiration_ms=None,
            )

            
        table = client.create_table(table) # API request


    def delete_table(self):
        client.delete_table(
            self.table_id, 
            not_found_ok=True)
        self._check_exists()
        
        return self.exists
        



########## Utils

def create_bq_schema(df : pd.DataFrame) -> dict:
    '''
    Take df and return a dict with form:
        {col_name : bq_dtpye}
        Being bq_dtpyes: [STRING, FLOAT, BOOL, INTEGER]
    '''
    schema_dict = {}
    for col in df.columns:
        dtype = 'STRING' # base case
        mode = 'NULLABLE'
        s = df[col]
        if pd.api.types.is_float_dtype(s):
            dtype = 'FLOAT'
        elif pd.api.types.is_bool_dtype(s):
            dtype = 'BOOL'
        elif pd.api.types.is_integer_dtype(s):
            dtype = 'INTEGER'
        schema_dict[col] = dtype

    return schema_dict



def create_bq_view(
        dataset_name:str, 
        view_name:str, 
        view_statement:str):

        shared_dataset_ref = client.dataset(dataset_name)
        view_ref = shared_dataset_ref.table(view_name)
        view = bigquery.Table(view_ref)
        view.view_query = view_statement
        view = client.create_table(view)  # API request
        print("Successfully created view at {}".format(view.full_table_id))
        


def get_logs(
    address:list, 
    func_sign:list, 
    limit=100, 
    print_query=True):
        
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

def insert_rows(
    dataset_name : str,
    table_name : str, 
    rows_list : typing.List[dict]) -> list:

    rows_n = len(rows_list)
    table_ref = client.dataset(dataset_name).table(table_name)
    table = client.get_table(table_ref)
    response_list = client.insert_rows(table, rows_list)
    errors_n = len(response_list)
    if errors_n > 0:
        logging.error(f"""
        Big Query insert errors - 
        From {rows_n} to be inserted, {errors_n} failed.""")
        logging.error(f"""First error example - 
        {response_list[0]}""")

        if errors_n > 1:
            logging.error(f"""Last error example - 
            {response_list[-1]}""")
    
    return response_list


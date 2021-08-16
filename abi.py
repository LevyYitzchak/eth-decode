import json
import pandas as pd

from _const import * # paths 
from _func import * # lambdas

class Abi:
    def __init__(self, abi_json_path):
        with open(abi_json_path) as json_file:
            self.abi_obj = json.load(json_file)

    def create_events_df(self):
        df = pd.DataFrame(self.abi_obj)
        df = df[df["type"] == "event"]
        df["types"] = df.apply(lambda_get_types, axis=1)
        df["names"] = df.apply(lambda_get_names, axis=1)
        df["indexed"] = df.apply(lambda_get_indexed, axis=1)
        df["types_data"] = df.apply(lambda_get_types_data, axis=1)
        df["types_topics"] = df.apply(lambda_get_types_topics, axis=1)
        
        df["signature"] = df.apply(lambda_get_signature, axis=1)
        df["hash"] = df.apply(lambda_get_hash, axis=1)
        df = df.drop(COLS_TO_DROP_EVENTS, axis=1)

        self.df = df

        return df

    def _split_topics_data(self):
        types_data_list = []
        types_topics_list = []
        for _, x in self.df.iterrows():        
            tmp_list = list(zip(x['types'], x['indexed']))
            types_topics = []
            types_data = []
            for arg_type, indexed in tmp_list:    
                if indexed:
                    types_topics.append(arg_type)
                else:
                    types_data.append(arg_type)

            if not types_topics: types_topics = None
            if not types_data: types_data = None
            types_topics_list.append(types_topics)
            types_data_list.append(types_data)

        self.df['types_topics'] = types_topics_list
        self.df['types_data'] = types_data_list


class Log:
    
    def __init__(self, df):
        '''
        Events dataframe with types already added
        '''
        self.df = df

    def decode_date(self):
        pass
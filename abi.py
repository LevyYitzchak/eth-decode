
from typing import List
import json
import pandas as pd
from eth_utils import decode_hex
from bq import get_logs
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
        
        ''' Discard this two for `_add_types` 
        Seem to not work due to not adding None for empty entries.
        '''
        # df["types_data"] = df.apply(lambda_get_types_data, axis=1)
        # df["types_topics"] = df.apply(lambda_get_types_topics, axis=1)
        
        df["signature"] = df.apply(lambda_get_signature, axis=1)
        df["hash"] = df.apply(lambda_get_hash, axis=1)
        df = df.drop(COLS_TO_DROP_EVENTS, axis=1)
        self.df = df
        self._add_types()
        
        return df

    def _add_types(self):
        # TODO: Improve logic
        types_data_list = []
        types_topics_list = []
        names_topics_list = []
        names_data_list = []

        for _, x in self.df.iterrows():
            tmp_list = list(zip(x['types'], x['indexed'], x['names']))
            types_topics = []
            types_data = []
            names_topics = []
            names_data = []
            for arg_type, indexed, name in tmp_list:    
                if indexed:
                    types_topics.append(arg_type)
                    names_topics.append(name)
                else:
                    types_data.append(arg_type)
                    names_data.append(name)

            if not types_topics: types_topics = None
            if not types_data: types_data = None
            if not names_topics: names_topics = None
            if not names_data: names_data = None

            types_topics_list.append(types_topics)
            types_data_list.append(types_data)
            names_topics_list.append(names_topics)
            names_data_list.append(names_data)

        self.df['types_topics'] = types_topics_list
        self.df['types_data'] = types_data_list
        self.df['names_topics'] = names_topics_list
        self.df['names_data'] = names_data_list


class LogTable:
    def __init__(
        self, 
        addresses : List[str],
        df_events : pd.DataFrame,
        functions_names : List[str] = []
        ):
        '''
        - Contract `addresses` which functions emit events to be decoded.
        - `df_events` contains info needed for decoding (based on ABI).
        - `functions_names` to be decoded, 
            if [] -> decode all functions from contract.
        '''
        self.addresses = addresses
        self.functions_names = functions_names
        self.df_events = df_events
        self.funcs_signs = (list(
            self.df_events[self.df_events['name']
            .isin(self.functions_names)]['hash']))
        
        if  self.functions_names:
            self.funcs_signs = (
                list(
                self.df_events[self.df_events['name']
                .isin(self.functions_names)]['hash']))
        else:
            # Take all if not specified
            self.funcs_signs = list(set(self.df_events['hash']))

    def _get_bq_log(self):
        self.df_logs = get_logs(
            address=self.addresses, 
            func_sign=self.funcs_signs)
    
    def _explode_data_decoded(self):
        df_new_cols = (self.df_logs.apply(lambda x: dict(
            # map name and values in a dict
            zip(x['names_data'], x['data_decoded'])), axis=1) 
            # transform dicts in columns (one per data attribute)
            .apply(pd.Series))
        df_new_cols.columns = ["data__" + col for col in df_new_cols.columns ]
        self.df_logs = pd.concat([self.df_logs, df_new_cols], axis=1)

    def get_data(self):
        '''
        Download and decode from BQ.
        Explode: create new col. for each data attribute.
        '''
        self._get_bq_log()
        self.df_logs = self.df_logs.merge(
            self.df_events, 
            left_on='t', 
            right_on='hash')

        self.df_logs['data_decoded'] = self.df_logs.apply(
            lambda_decode_data, axis=1)

        self._explode_data_decoded()
        
        return self.df_logs
   
####
lambda_decode_data = (lambda x: decode_abi(x['types_data'],
                                        decode_hex(x['data'])))


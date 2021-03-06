import json
import requests
from pathlib import Path
URL = 'https://api.thegraph.com/subgraphs/name/aragon/aragon-court-v2-mainnet'

r = requests.get(URL)


class GraphQuery:
    QUERY_FIRST = '1000'
    QUERY_SKIP = 'null'
    def __init__(
        self, 
        query_path:Path,
        api_url:str,
        query_first:str=QUERY_FIRST,
        query_skip:str=QUERY_SKIP):

        if not isinstance(query_path, Path):
            query_path = Path(query_path)
        
        self.query_path = query_path
        self.api_url = api_url
        self.q_name = query_path.parts[-1].split(".")[0]
        with open(query_path) as f:
            self.query_txt = f.read()

        self.query_first = query_first
        self.query_skip = query_skip

    def _post_request(self, query_txt):
        r = requests.post(
                self.api_url,
                json={'query': query_txt})
        return r

    def _parse_response(self, r):
        data = json.loads(r.text).get('data')
        data = data.get(self.q_name)
        if data: 
            return data
        else:
            raise f'{r.text}'

    def post(
        self, 
        paginate=False):
        '''
        If `paginate` = True, string text is expected to
        have $first and $skip params to be replaced accordingly.
        It is assumes only one entity per query.

        - first: max. response length
        - skip: 
        '''
        if paginate:
            return self._post_paginated()

        else: # Single query
            r = self._post_request(self.query_txt)
            data = self._parse_response(r)
            return data
    
    def _post_paginated(self):
        data_list = []
        # Initialize for first iteration 
        r_len = self.query_first
        _skip = self.query_skip
        # Continue until responses are smaller than max. available
        while str(r_len) == self.query_first:
            temp_q_text = (
                self.query_txt
                .replace('$first', self.query_first)
                .replace('$skip', str(_skip))
                )
            r = self._post_request(temp_q_text)
            data = self._parse_response(r)
            data_list.extend(data)
            r_len = len(data)
            # Update params for pagination
            if _skip == self.query_skip:
                # First iteration
                _skip = int(self.query_first)
            else:
                # Iter to next pagination
                _skip += int(self.query_first)
        
        return data_list

    



        





    
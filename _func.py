from re import X
from Crypto.Hash import keccak
from eth_abi import decode_abi

lambda_get_types = lambda x: [i['type'] for i in x['inputs']]
lambda_get_names = lambda x: [i['name'] for i in x['inputs']]
lambda_get_indexed = lambda x: [i['indexed'] for i in x['inputs']]

lambda_get_types_data = lambda x: [t for i in x['indexed'] for t in x['types'] 
                                if not i]

lambda_get_types_topics = lambda x: [t for i in x['indexed'] for t in x['types'] 
                                if i]

lambda_get_signature = (lambda x: x['name']
+ '(' 
+ ','.join([t for t in x['types']]) 
+ ')'
)
lambda_get_hash = (lambda x: "0x" + keccak.new(digest_bits=256)
.update(f"{x['signature']}".encode())
.hexdigest())


lambda_decode_data = lambda x: decode_abi(x['types_data'], x['data'])

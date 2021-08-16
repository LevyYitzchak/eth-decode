var Web3 = require('web3');

var web3 = new Web3();

var data_types = ['uint64', 'uint256']
var data_hex = '0x00000000000000000000000000000000000000000000000000000000000000bb00000000000000000000000000000000000000000000000753f835f3bdb4d0ed'

var res = web3.eth.abi.decodeParameters(data_types,
    data_hex);


console.log(res)





import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const APIURL = "https://api.studio.thegraph.com/query//<SUBGRAPH_NAME>/";

const tokensQuery = `
  query {
    tokens {
      id
      tokenID
      contentURI
      metadataURI
    }
  }
`

const client = new ApolloClient({
  uri: APIURL,
  cache: new InMemoryCache()
});

client.query({
  query: gql(tokensQuery)
})
.then(data => console.log("Subgraph data: ", data))
.catch(err => { console.log("Error fetching data: ", err) });

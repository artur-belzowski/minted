import requests
import json

# Wczytanie pliku JSON z adresami kolekcji
with open('collection_addresses.json', 'r') as f:
    collection_addresses = json.load(f)

# Wyświetlenie dostępnych kolekcji
print("Dostępne kolekcje:")
for index, collection_name in enumerate(collection_addresses.keys()):
    print(f"{index + 1}. {collection_name}")

# Wybór kolekcji przez użytkownika
selected_collection_index = int(input("Wybierz numer kolekcji: "))
selected_collection_name = list(collection_addresses.keys())[selected_collection_index - 1]
selected_collection_address = collection_addresses[selected_collection_name]


body = {
  "operationName": "getCollectionAssets",
  "variables": {
    "address": selected_collection_address,
    "chain": "CRONOS",
    "first": 20,
    "filter": {
      "chain": "CRONOS",
      "listingType": None,
      "priceRange": None,
      "attributes": None,
      "rarityRange": None,
      "nameOrTokenId": None
    },
    "sort": "LOWEST_PRICE"
  },
  "query": "query getCollectionAssets($address: EvmAddress!, $chain: Blockchain!, $first: Int!, $sort: AssetSort!, $after: String, $filter: AssetFilterInput) {\n  collection(address: $address, chain: $chain) {\n    ...CollectionIdentifyFields\n    assets(first: $first, after: $after, filter: $filter, sort: $sort) {\n      totalCount\n      edges {\n        node {\n          ...AssetDetailFields\n          bids(first: 1) {\n            edges {\n              node {\n                ...OrderFields\n                __typename\n              }\n              cursor\n              __typename\n            }\n            pageInfo {\n              ...PageInfoFields\n              __typename\n            }\n            totalCount\n            __typename\n          }\n          __typename\n        }\n        cursor\n        __typename\n      }\n      pageInfo {\n        ...PageInfoFields\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CollectionIdentifyFields on AssetCollection {\n  address\n  name\n  chain {\n    name\n    __typename\n  }\n  status\n  __typename\n}\n\nfragment AssetDetailFields on Asset {\n  name\n  tokenId\n  image {\n    url\n    __typename\n  }\n  animatedImage {\n    url\n    __typename\n  }\n  owner {\n    ...UserFields\n    __typename\n  }\n  ask {\n    ...OrderFields\n    __typename\n  }\n  collection {\n    ...CollectionIdentifyFields\n    __typename\n  }\n  rarityRank\n  __typename\n}\n\nfragment UserFields on UserAccount {\n  evmAddress\n  name\n  avatar {\n    url\n    __typename\n  }\n  nonce\n  __typename\n}\n\nfragment OrderFields on MakerOrder {\n  hash\n  chain\n  isOrderAsk\n  collection\n  tokenId\n  currency\n  strategy\n  startTime\n  endTime\n  minPercentageToAsk\n  nonce\n  price\n  amount\n  status\n  signer\n  encodedParams\n  paramTypes\n  signature\n  __typename\n}\n\nfragment PageInfoFields on PageInfo {\n  hasPreviousPage\n  hasNextPage\n  startCursor\n  endCursor\n  __typename\n}"
}
resp = requests.post(url="https://api.minted.network/graphql", json=body)

import pprint

for edge in resp.json()['data']['collection']['assets']['edges']:
    price = edge['node']['ask']['price']
    price_cro = int(price) / 1000000000000000000
    print("Price: " + str(price_cro) + " cro")
    print("NFT: " + edge['node']['name'])
    print("Rarity: " + edge['node']['rarityRank'])
    print(50 * '*')


# pprint.pprint(resp.json()['data'])

# pprint.pprint(resp.json()['data']['collection']['assets']['edges'][0]['node']['ask']['price'])
# pprint.pprint(resp.json()['data']['collection']['assets']['edges'][0]['node']['name'])
# pprint.pprint(resp.json()['data']['collection']['assets']['edges'][0]['node']['rarityRank'])


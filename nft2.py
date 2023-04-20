import requests
from flask import Flask, render_template, request
import json

class Collection:
    def __init__(self, name, address, assetCount, change24, reward_points, floor_price):
        self.name = name
        self.address = address
        self.assetCount = assetCount
        self.change24 = change24
        self.reward_points = reward_points
        self.floor_price = floor_price

# class Nft(Collection):
#     def __init__(self, token_id, rarity_rank, nft_price):
#         self.token_id = token_id
#         self.rarity_rank = rarity_rank
#         self.nft_price = nft_price

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    body = {
        "operationName": "getCollections",
        "variables": {
            "first": 5,
            "filter": {
                "chains": [
                    "CRONOS",
                    # "ETHEREUM"
                ],
                "verifiedOnly": None
            },
            "sort": {
                "field": "VOLUME_ONE_DAY",
                "isAscending": None
            }
        },
        "query": "query getCollections($sort: CollectionSortInput, $filter: CollectionFilterInput, $after: String, $first: Int!) {\n  collections(first: $first, filter: $filter, sort: $sort, after: $after) {\n    edges {\n      node {\n        ...CollectionDetailFields\n        ...CollectionPriceFields\n        ...CollectionVolumeFields\n        rewardPoints\n        __typename\n      }\n      cursor\n      __typename\n    }\n    pageInfo {\n      ...PageInfoFields\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CollectionDetailFields on AssetCollection {\n  ...CollectionIdentifyFields\n  name\n  logo {\n    url\n    __typename\n  }\n  banner {\n    url\n    __typename\n  }\n  creator {\n    ...UserFields\n    __typename\n  }\n  description\n  assetCount\n  ownerCount\n  raritySource\n  isRarityEnable\n  isCollectionOfferEnable\n  highestCollectionOffer\n  __typename\n}\n\nfragment CollectionIdentifyFields on AssetCollection {\n  address\n  name\n  chain {\n    name\n    __typename\n  }\n  status\n  __typename\n}\n\nfragment UserFields on UserAccount {\n  evmAddress\n  name\n  avatar {\n    url\n    __typename\n  }\n  nonce\n  __typename\n}\n\nfragment CollectionPriceFields on AssetCollection {\n  floorPrice {\n    change24h\n    latestFloorPrice\n    latestFloorPriceNative\n    globalFloorPrice7dNative\n    globalFloorPrice24hNative\n    globalFloorPrice30dNative\n    globalFloorPriceAllNative\n    __typename\n  }\n  __typename\n}\n\nfragment CollectionVolumeFields on AssetCollection {\n  volume {\n    change24h\n    volume7d\n    volume24h\n    volume30d\n    volumeAll\n    globalVolume7dNative\n    globalVolume24hNative\n    globalVolume30dNative\n    globalVolumeAllNative\n    __typename\n  }\n  __typename\n}\n\nfragment PageInfoFields on PageInfo {\n  hasPreviousPage\n  hasNextPage\n  startCursor\n  endCursor\n  __typename\n}"
    }

    resp = requests.post(url="https://api.minted.network/graphql", json=body)
    lin = resp.json()
    collections = []
    nft_addresses = []
    for nft in lin['data']['collections']['edges']:
        name = nft['node']['name']
        address = nft['node']['address']
        assetCount = nft['node']['assetCount']
        if nft['node']['floorPrice']['change24h'] is not None:
            change24 = float(nft['node']['floorPrice']['change24h'])
            change24 = str(round(change24, 1))
        else:
            change24 = 0
        reward_points = nft['node']['rewardPoints']
        if nft['node']['floorPrice']['latestFloorPriceNative'] is not None:
            floor_price = int(nft['node']['floorPrice']['latestFloorPriceNative']) / 1000000000000000000
        else:
            floor_price = 0
        collection = Collection(name, address, assetCount, change24, reward_points, floor_price)
        collections.append(collection.__dict__)
        print(collection.name)
        nft_address = {'name':collection.name,'address': collection.address}
        nft_addresses.append(nft_address)

    with open('collection_addresses2.json', 'w') as f:
        json.dump(nft_addresses, f)

    return render_template('index.html', collections=collections, change24=change24, reward_points=reward_points, floor_price=floor_price)
@app.route('/<collection_name>/')
def floor_price(collection_name):

    with open('collection_addresses2.json', 'r') as f:
        collections = json.load(f)

    # Wyświetlenie dostępnych kolekcji

    for index, collection in enumerate(collections):
        print(f"{index + 1}. {collection['name']}")

    selected_collection = next((c for c in collections if c['name'] == collection_name), None)
    if selected_collection is None:
        return 'Nie znaleziono kolekcji o nazwie {}'.format(collection_name)

    body = {
      "operationName": "getCollectionAssets",
      "variables": {
        "address": selected_collection['address'],
        "chain": "CRONOS",
        "first": 10,
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

    nft_data = []
    for edge in resp.json()['data']['collection']['assets']['edges']:
        token_id = edge['node']['ask']['tokenId']
        nft_price = edge['node']['ask']['price']
        rarity_rank = edge['node']['rarityRank']
        nft_data.append({'token_id': token_id, 'nft_price': nft_price, 'rarity_rank': rarity_rank})

    return render_template('collection.html', collection_name=collection_name, nft_data=nft_data)

if __name__ == '__main__':
    app.run(debug=True)
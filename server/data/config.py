import pymongo

client = pymongo.MongoClient('localhost')
database = client['chatapp']
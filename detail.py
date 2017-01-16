from pymongo import MongoClient
import json

client = MongoClient()
db = client.qzone
person = db.person

items = json.load()
result = person.insert_many(items)
print('Multiple insert: {}'.format(result.inserted_ids))



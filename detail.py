from pymongo import MongoClient
import json

client = MongoClient()
db = client.qzone
person = db.person

items = json.load()
person.insert_many(items)



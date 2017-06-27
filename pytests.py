
import pymongo

client=pymongo.MongoClient("localhost",27017)
db=client.test
print(db.my_collection)
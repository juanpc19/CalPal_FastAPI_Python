from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
 

uri = "mongodb+srv://juanpesca19:murcielagoLP2019.@calpal.cpho4.mongodb.net/?retryWrites=true&w=majority&appName=CalPal"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

db = client.CalPal
alimentos_base_collection=db["alimentos_base"]




# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
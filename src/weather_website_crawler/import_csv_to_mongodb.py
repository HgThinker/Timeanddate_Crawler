import argparse
from pymongo import MongoClient,DESCENDING
import pymongo
import csv
import os

parser = argparse.ArgumentParser()
parser.add_argument('--website_name', type=str, required=True)
args = parser.parse_args()

website_name = args.website_name.split('.')[0]

dir_path = os.path.join(os.getcwd(),'data',f'{website_name}','preprocessed')

# MongoDB connection settings
mongo_uri = "mongodb://localhost:27017/"

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[website_name]# name database as website name 
# Iterate over each CSV file in the directory
for filename in os.listdir(dir_path):
    if filename.endswith(".csv"):
        collection_name = os.path.splitext(filename)[0]  # Use CSV filename as collection name
        collection = db[collection_name]
        collection.create_index([("Time", DESCENDING)], unique=True)

        csv_file = os.path.join(dir_path, filename)

        # Read data from CSV file and insert into MongoDB collection
        with open(csv_file, "r", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                removed_key = next(iter(row))
                row.pop(removed_key)
                # Insert each row as a document into the collection
                try:
                    collection.insert_one(row)
                except pymongo.errors.DuplicateKeyError:
                    print(f"{row['Time']} is a duplicate and was not inserted!!")
        print(f"CSV data from '{filename}.csv' imported into collection '{collection_name}'.")
# Close MongoDB connection
client.close()

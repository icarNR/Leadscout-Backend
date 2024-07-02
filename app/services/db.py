from typing import Optional,List
from pymongo import MongoClient, errors
import sys
from app.models.user_model import User,Results
from bson import ObjectId
from passlib.context import CryptContext


class DatabaseConnection:
    def __init__(self,collection_name):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        try:
            # Replace the placeholder data with your actual Atlas connection string
            atlas_connection_string = "mongodb+srv://nisalRavindu:tonyStark#117@cluster0.wsf6jk3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

            # Create a connection to MongoDB Atlas
            self.client = MongoClient(atlas_connection_string)
        except errors.ConfigurationError:
            print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")
            sys.exit(1)

        # Access a database from your Atlas cluster (replace 'mydatabase' with your database name)
        self.db = self.client.Cluster0
        self.collection = self.db[collection_name]
        #self.collection.drop()


    def calculate_averages(self):
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,  # Grouping by null to calculate the average across all documents
                        "extraversion": {"$avg": "$extraversion"},
                        "agreeableness": {"$avg": "$agreeableness"},
                        "conscientiousness": {"$avg": "$conscientiousness"},
                        "neuroticism": {"$avg": "$neuroticism"},
                        "openness": {"$avg": "$openness"}
                    }
                }
            ]
            result = list(self.collection.aggregate(pipeline))
            if result:
                # Remove the '_id' field from the result for cleaner output
                result[0].pop('_id', None)
                return result[0]
            else:
                print("No data found to calculate averages.")
                return None
        except Exception as e:
            print("An error occurred while calculating averages: ", e)
            return None

    def close(self):
        # Close the connection to the database
        self.client.close()
           
    def add_document(self, document):
        try:
            result = self.collection.insert_one(document)
            print("Document inserted with id: ", result.inserted_id)
        except Exception as e:
            print("An error occurred while inserting the document: ", e)
    
    def update_attribute_by_id(self, document_id, attribute, new_value):
        try:
            # Update the attribute in the document
            result = self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": {attribute: new_value}}
            )
            
            if result.modified_count != 1:
                print("Document updated successfully.")
            else:
                print("No documents matched the filter. Document was not updated.")
        except Exception as e:
            print("An error occurred while updating the document: ", e)
    
    def replace_document_by_id(self, document_id, new_document):
        try:
            result = self.collection.replace_one({"_id": ObjectId(document_id)}, new_document)
            if result.modified_count == 1:
                print("Document replaced successfully.")
            else:
                print("No documents matched the filter. Document was not replaced.")
        except Exception as e:
            print("An error occurred while replacing the document: ", e)

    def get_document_by_id(self, document_id):
        try:
            document = self.collection.find_one({"_id": ObjectId(document_id)})
            if document is not None:
                print("Document found: ", document)
                return document
            else:
                print("No documents matched the filter.")
        except Exception as e:
            print("An error occurred while finding the document: ", e)
    
    def get_document_by_attribute(self, attribute, value):
        try:
            document = self.collection.find_one({attribute: value})
            if document is not None:
                print("Document found by attribute: ", document)
                return document
            else:
                print("No documents matched the filter.")
        except Exception as e:
            print("An error occurred while finding the document: ", e)

    def find_id_by_attribute(self, attribute, value):
        try:
            document = self.collection.find_one({attribute: value})
            if document is not None:
                print("Document found: ", str(document["_id"]))
                return str(document["_id"]) # return the the document
            else:
                print("No documents matched the filter.")
                return None  # return None if no document is found
        except Exception as e:
            print("An error occurred while finding the document: ", e)
    
    def get_attribute_by_attribute(self, sattribute, value, fattribute):
        try:
            document = self.collection.find_one({sattribute: value})
            if document is not None:
                print("Document found: ", str(document[fattribute]))
                return str(document[fattribute]) # return the the document
            else:
                print("No documents matched the filter.")
                return None  # return None if no document is found
        except Exception as e:
            print("An error occurred while finding the document: ", e)
    
    def delete_document_by_id(self, document_id):
        try:
            result = self.collection.delete_one({"_id": ObjectId(document_id)})
            if result.deleted_count == 1:
                print("Document deleted successfully.")
            else:
                print("No documents matched the filter. Document was not deleted.")
        except Exception as e:
            print("An error occurred while deleting the document: ", e)


    def get_all_documents(self):
        try:
            documents = []
            for document in self.collection.find({}):
                documents.append(document)
            return documents
        except Exception as e:
            print("An error occurred while getting all documents: ", e)
    
    def get_attribute_value_by_id(self, document_id, attribute):
        try:
            # Find the document by its _id
            document = self.collection.find_one({"_id": ObjectId(document_id)})
            
            # Check if the document exists
            if document is not None:
                # Check if the attribute exists in the document
                if attribute in document:
                    print(f"The value of {attribute} is: ", document[attribute])
                    return document[attribute]
                else:
                    print(f"The attribute {attribute} does not exist in the document.")
            else:
                print("No documents matched the filter.")
        except Exception as e:
            print("An error occurred while getting the attribute value: ", e)
    
    def get_documents_by_attribute(self, attribute, value, fields):
        try:    
            query = {attribute: value}
            projection = {field: 1 for field in fields}
            projection["_id"] = 0  # Exclude _id from the result
            documents = self.collection.find(query, projection)
            count = self.collection.count_documents({attribute: value})
            # Check if any documents were found
            if documents is not None:
                    print(f"Found {count} documents.")
                    return list(documents)
            else:
                    print("No documents matched the filter.")
                    return None  # return None if no documents are found
        except Exception as e:
            print("An error occurred while getting the documents: ", e)

            

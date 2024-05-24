from pymongo import MongoClient, errors
import sys
from models.user_model import User,Results
from bson import ObjectId
from models.user_model import User, Results

class DatabaseConnection:
    def __init__(self,collection_name):
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
            count = self.collection.count_documents(query)
            # Check if any documents were found
            if documents is not None:
                    print(f"Found {count} documents.")
                    return list(documents)
            else:
                    print("No documents matched the filter.")
                    return None  # return None if no documents are found
        except Exception as e:
            print("An error occurred while getting the documents: ", e)


# document_id = document = db.find_document_by_attribute(attribute, value)  # replace with your document's _id
# value = db.get_attribute_value(document_id, attribute)
# answers=[2] * 44
# user = User(
#     user_id="001",
#     attempts=0,  # replace with actual number of attempts
#     supervisor="002",  # replace with actual supervisor if any
#     requested=False,  # replace with actual requested status
#     answers=answers,
#     results=Results(
#         Openness=0,
#         Conscientiousness=0,
#         Extraversion=0,
#         Agreeableness=0,
#         Neuroticism=0,
#     )
# )
# db = DatabaseConnection("users")
# db.update_document(db.find_document_by_attribute("user_id","001"), "answers", answers)

# # Insert the User object into the MongoDB database
# db.add_document(user.model_dump())

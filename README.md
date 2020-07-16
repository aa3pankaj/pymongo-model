Pymongo Model
==================================================== 

With pymongo-model, it will be easier for you to use pymongo, as you will get a local copy of mongoDB document, you can do any change in the local copy (python object), changes will be committed from local copy to mongoDB only when you invoke save method like it happens in any ORM library.\
\
SimpleModel object provides basic feature of updating mongo document locally and commiting at once.\
\
Also, 
You can use below models for document history tracking feature (that can be used for operations like undo)
1. In DiffHistoryModelV1, we are storing a new document (in delta collection) which consists of version details as well as original document everytime it is updated.
2. In DiffHistoryModelV2, we are using [json-diff](https://github.com/fzumstein/jsondiff) for calculating difference in the versions and storing just the difference object instead of entire document for versioning.

Installation
------------

Supports Python 3+
To install, simply use pip
```
$ pip install pymongo-model
```

Usage
-----

```python
import pymongo
from bson.objectid import ObjectId
from pymongo_model import SimpleModel, DiffHistoryModelV1, DiffHistoryModelV2

MONGO_KEY = os.getenv('MONGO_KEY')
client = pymongo.MongoClient(MONGO_KEY)
db = client["your_database"]
```

##### Using SimpleModel
```python
""" A simple model that wraps mongodb document 
"""
class YourSimpleModel(SimpleModel):
    collection = db.your_collection   #mongo collection object


#Creating new document
player = Player({"username":"pankajsingh.08","name": "Pankaj Singh", "age": 25,"runs":300})    
player.save()  #commited in db

#Updating old document
player = Player({"_id":ObjectId("provide_doc_id_here")})    #provide mongo document id for fetching
player.reload()     #this fetches data from db and maps to local dict object   
player["city"] = "Hyderabad"  #adding new key to document in local copy
player["username"] = "aa3pankaj" #updating old key in local copy
del player["age"]  #deleting old key in local copy
player.save()  #now everything will be committed at once in db

```

##### Using DiffHistoryModelV1
```python

""" A simple model that wraps mongodb document, 
    Also creates a delta_collection for document revision tracking,
    In this version of DiffHistoryModel, it creates below document in the delta_collection for each update i.e after invoking save method 
    {
       "collection_name": name of the collection of the document for which revision is being done,
       "document_id" : mongo id of document for which revision is being done,
       "document": original document object from your collection for which revision is being done,
       "_version": revision number of the document,
       "is_latest":Boolean, true only for latest
    }
"""
class Match(DiffHistoryModelV1):
    #Refer https://api.mongodb.com/python/current/tutorial.html for creating db object
    db_object = db                                #mongo client object
    collection = db.your_collection               #mongo collection object
    delta_collection_name = "_delta_collection"   #give any name for delta collection where revisions will be stored, it will be created automatically in the db

#Creating new document
match = Match({"username":"pankajsingh.08","name": "Pankaj Singh", "age": 25})    
match.save()  #commited in db

#Updating old document
match = Match({"_id":ObjectId("provide_doc_id_here")})    #provide mongo document id for fetching
match.reload()     #this fetches data from db and maps to local dict object   
match["city"] = "Pune"  #adding new key to document in local copy
match.save()  #commited in original collection, Also a new document is created in the delta_collection

#helper methods
doc_latest = match.get_latest_revision()  #latest record in db
match.delete_latest_revision()  #deletes latest record in delta_collection, and makes previos record as latest but original document will not be touched
match.undo()   #deletes latest record in delta_collection, and makes previos record as latest, Also original document will be updated
```

##### Using DiffHistoryModelV2
```python

""" A simple model that wraps mongodb document, 
    Also creates a delta_collection for document revision tracking, Only difference from DiffHistoryModelV1 is here instead of saving entire document, just difference is stored in diff.
    In this version of DiffHistoryModel, it creates below document in the delta_collection for each update i.e after invoking save method 
    {
       "collection_name": name of the collection of the document for which revision is being done,
       "document_id" : mongo id of document for which revision is being done,
       "diff": diff object generated from json-diff library (https://github.com/fzumstein/jsondiff)
       "_version": revision number of the document,
    }
"""

class Match(DiffHistoryModelV2):
    #Refer https://api.mongodb.com/python/current/tutorial.html for creating db object
    db_object = db                                #mongo client object
    collection = db.your_collection               #mongo collection object
    delta_collection_name = "_delta_collection"   #give any name for delta collection where revisions will be stored, it will be created automatically in the db

#Creating new document
match = Match({"username":"pankajsingh08","name": "Pankaj Singh", "age": "25"})    
match.save()  #commited in db

#Updating old document
match = Match({"_id":ObjectId("provide_doc_id_here")})    #provide mongo document id for fetching
match.reload()     #this fetches data from db and maps to local dict object   
match["city"] = "Pune"  #adding new key to document in local copy
match.save()  #commited in original collection, Also a new document is created in the delta_collection

```

Projects using pymongo-model
----------------------------
1. [PexaBot]("https://github.com/aa3pankaj/PexaBot") : A chatbot for cricket match scoring and stats analysis
    
Support
-------
Find me on [Linkedin](https://www.linkedin.com/in/aa3pankaj/)
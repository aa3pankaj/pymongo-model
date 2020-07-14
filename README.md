Pymongo Model
==================================================== 

With pymongo-model, it will be easier for you to use pymongo, as you will get a local copy of mongodb document, you can do any changes in the local copy i.e python dict, changes will be committed from local copy to mongoDB only when you invoke save method like it happens in any other model based library.\
SimpleModel object provides basic feature of updating mongo document locally and commiting at once.
\
You can use below models for document history tracking feature e.g can be used in undo operation\
In DiffHistoryModelV1, we are storing a new document (in delta collection) which consists of version details as well as original document everytime it is updated.\
In DiffHistoryModelV2, we are using [json-diff](https://github.com/fzumstein/jsondiff) for calculating difference in the versions and storing just the difference object instead of entire document for versioning.

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
from pymongo_model import SimpleModel, DiffHistoryModelV1, DiffHistoryModelV2

MONGO_KEY = os.getenv('MONGO_KEY')
client = pymongo.MongoClient(MONGO_KEY)
db = client["your_database"]
```

#### Using SimpleModel
```python
""" A simple model that wraps mongodb document 
"""
class YourSimpleModel(SimpleModel):
    collection = db.your_collection   #mongo collection object


#Creating new document
sample = YourSimpleModel({"username":"pankajsingh08","name": "Pankaj Singh", "age": "25"})    
sample.save()  #commited in db

#Updating old document
sample = Match({"_id":ObjectId("provide_mongo_id_here")})    #provide mongo document id for fetching
sample.reload()     #this fetches data from db and maps to local dict object   
sample["city"] = "Hyderabad"  #adding new key to document in local copy
sample["username"] = "aa3pankaj" #updating old key in local copy
del sample["age"]  #deleting old key in local copy
sample.save()  #now everything will be committed at once in db

```

#### Using DiffHistoryModelV1
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
class YourDiffModel1(DiffHistoryModelV1):
    #Refer https://api.mongodb.com/python/current/tutorial.html for creating db object
    db_object = db                                #mongo client object
    collection = db.your_collection               #mongo collection object
    delta_collection_name = "_delta_collection"   #give any name for delta collection where revisions will be stored, it will be created automatically in the db

#Creating new document
sample = YourDiffModel1({"username":"pankajsingh08","name": "Pankaj Singh", "age": "25"})    
sample.save()  #commited in db

#Updating old document
sample = Match({"_id":ObjectId("provide_mongo_id_here")})    #provide mongo document id for fetching
sample.reload()     #this fetches data from db and maps to local dict object   
sample["city"] = "Pune"  #adding new key to document in local copy
sample.save()  #commited in original collection, Also a new document is created in the delta_collection

#helper methods
doc_latest = sample.get_latest_revision()  #latest record in db
sample.delete_latest_revision()  #deletes latest record in delta_collection, and makes previos record as latest but original document will not be touched
sample.undo()   #deletes latest record in delta_collection, and makes previos record as latest, Also original document will be updated
```

#### Using DiffHistoryModelV2
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

class YourDiffModel2(DiffHistoryModelV2):
    #Refer https://api.mongodb.com/python/current/tutorial.html for creating db object
    db_object = db                                #mongo client object
    collection = db.your_collection               #mongo collection object
    delta_collection_name = "_delta_collection"   #give any name for delta collection where revisions will be stored, it will be created automatically in the db

#Creating new document
sample = YourDiffModel2({"username":"pankajsingh08","name": "Pankaj Singh", "age": "25"})    
sample.save()  #commited in db

#Updating old document
sample = Match({"_id":ObjectId("provide_mongo_id_here")})    #provide mongo document id for fetching
sample.reload()     #this fetches data from db and maps to local dict object   
sample["city"] = "Pune"  #adding new key to document in local copy
sample.save()  #commited in original collection, Also a new document is created in the delta_collection

```

## Support
Find me on [Linkedin](https://www.linkedin.com/in/aa3pankaj/)
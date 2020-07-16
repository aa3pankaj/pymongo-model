from jsondiff import diff
from bson.objectid import ObjectId
from bson.json_util import dumps

class SimpleModel(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__
   
    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)

    def reload(self):
        if self._id:
            self.update(self.collection\
                    .find_one({"_id": ObjectId(self._id)}))

    def remove(self):
        if self._id:
            self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()

class DiffHistoryModelV2(SimpleModel):
    """
    A simple model that wraps mongodb document, 
    Also creates a delta_collection for document revision tracking
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def undo(self):
        pass
    def __get_diff(self):
        doc_copy = self.collection.find_one({"_id": ObjectId(self._id)})
        diff_object = diff(dumps(doc_copy),dumps(self),load=True, dump=True)
        return diff_object
        
    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            diff = self.__get_diff()
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
            
            delta_collection = self.db_object[self.delta_collection_name]
            delta_collection.insert_one({ "collection_name": self.name,
                                                "document_id" : self._id,
                                                "diff": diff,
                                                "_version": delta_collection.count()+1
            }
            )

class DiffHistoryModelV1(SimpleModel):
    """
    A simple model that wraps mongodb document, 
    Also creates a delta_collection for document revision tracking,
    In this version of DiffHistoryModel, it creates below document for each update i.e after invoking save()
    {
       "collection_name": name of the collection of the document for which revision is being done,
       "document_id" : mongo id of document for which revision is being done,
       "document": entire document object for which revision is being done,
       "_version": revision number of document,
       "is_latest":Boolean, true only for latest
    }
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def undo(self):
        self.delete_latest_revision()
        doc_latest = self.get_latest_revision()
        self.clear()
        self._id = doc_latest["_id"]
        self.__reload_latest_from_delta()
        super().save()
        
    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            delta_collection = self.db_object[self.delta_collection_name]
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
            result = delta_collection.find({"document_id":self._id})
            result_count = result.count()
            current_version = result_count + 1
            delta_collection.insert_one({"collection_name": self.delta_collection_name,
                                           "document_id" : self._id,
                                           "document":self,
                                           "_version": current_version,
                                           "is_latest":True
                                            })
            if current_version > 1:
                delta_collection.update_one({"document_id":self._id,"_version":current_version-1},{"$set":{"is_latest":False}})

    def __reload_latest_from_delta(self):
        delta_collection = self.db_object[self.delta_collection_name]
        doc = delta_collection.find_one({"_id": ObjectId(self._id)})['document']
        self._id = doc["_id"]
        self.update(doc)

    def get_latest_revision(self):
        delta_collection = self.db_object[self.delta_collection_name]
        return delta_collection.find_one({"document_id":self._id,"is_latest":True})

    def delete_latest_revision(self):
        delta_collection = self.db_object[self.delta_collection_name]
        delta_collection.remove({"document_id":self._id,"is_latest":True})
        result = delta_collection.find({"document_id":self._id})
        result_count = result.count()
        delta_collection.update_one({"document_id":self._id,"_version":result_count},{"$set":{"is_latest":True}})
        


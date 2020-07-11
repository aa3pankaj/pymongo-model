from jsondiff import diff
from bson.objectid import ObjectId
from bson.json_util import dumps
import json

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
    Also creates a delta collection for document revision tracking
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def undo(self):
        pass
    def __diff_update(self):
        match_copy = self.collection.find_one({"_id": ObjectId(self._id)})
        diff_object = diff(dumps(match_copy),dumps(self),load=True, dump=True)
        return diff_object
        
    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            diff = self.__diff_update()
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
            
            _delta_collection_name = "_delta"+"_"+self.name
            _delta_collection = self.db_object[_delta_collection_name]
            _delta_collection.insert_one({ "collection_name": self.name,
                                                "document_id" : self._id,
                                                "diff": diff,
                                                "_version": _delta_collection.count()+1,
                                                "reason":"update"
            }
            )

class DiffHistoryModelV1(SimpleModel):
    """
    A simple model that wraps mongodb document, 
    Also creates a _delta_collection for document revision tracking,
    In this version of DiffHistoryModel, it creates below document for each update i.e after invoking save()
    {
       "collection_name": name of the collection of the document for which revision is being done,
       "document_id" : mongo id of document for which revision is being done,
       "document": entire document object for which revision is being done,
       "_version": revision number of document,
       "reason": "update",
       "is_latest":Boolean, true only for latest
    }
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__


    def undo(self):
        self.delete_latest_revision()
        match_latest = self.get_latest_revision()
        self.clear()
        self._id = match_latest["_id"]
        self.__reload_latest_from_delta()
        super().save()
        
    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            _delta_collection = self.db_object[self._delta_collection_name]
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
            result = _delta_collection.find({"document_id":self._id})
            result_count = result.count()
            _delta_collection.insert_one({"collection_name": self.name,
                                           "document_id" : self._id,
                                           "document":self,
                                           "_version": result_count+1,
                                           "reason":"update",
                                           "is_latest":True
                                            })
            result_count = _delta_collection.find({"document_id":self._id}).count()
            if result_count > 1:
                _delta_collection.update_one({"document_id":self._id,"_version":result_count-1},{"$set":{"is_latest":False}})

    def __reload_latest_from_delta(self):
        _delta_collection = self.db_object[self._delta_collection_name]
        doc = _delta_collection.find_one({"_id": ObjectId(self._id)})['document']
        self._id = doc["_id"]
        self.update(doc)

    def get_latest_revision(self):
        _delta_collection = self.db_object[self._delta_collection_name]
        return _delta_collection.find_one({"document_id":self._id,"is_latest":True})

    def delete_latest_revision(self):
        _delta_collection = self.db_object[self._delta_collection_name]
        _delta_collection.remove({"document_id":self._id,"is_latest":True})
        result = _delta_collection.find({"document_id":self._id})
        result_count = result.count()
        _delta_collection.update_one({"document_id":self._id,"_version":result_count},{"$set":{"is_latest":True}})
        


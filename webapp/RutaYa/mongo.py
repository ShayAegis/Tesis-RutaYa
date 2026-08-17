from django.conf import settings
from pymongo import MongoClient
from pymongo.collection import Collection

_client = None


def get_bus_positions_collection() -> Collection:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client[settings.MONGO_DB][settings.MONGO_COLLECTION]

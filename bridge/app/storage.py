import logging

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import CollectionInvalid

from app import config

logger = logging.getLogger(__name__)


def get_collection() -> Collection:
    client = MongoClient(config.MONGO_URI)
    db = client[config.MONGO_DB]

    if config.MONGO_COLLECTION not in db.list_collection_names():
        try:
            db.create_collection(
                config.MONGO_COLLECTION,
                timeseries={
                    "timeField": "timestamp",
                    "metaField": "metadata",
                    "granularity": "seconds",
                },
            )
            logger.info("coleccion timeseries '%s' creada", config.MONGO_COLLECTION)
        except CollectionInvalid:
            logger.debug(
                "coleccion '%s' creada por otro proceso", config.MONGO_COLLECTION
            )

    collection = db[config.MONGO_COLLECTION]
    collection.create_index([("metadata.placa", 1), ("timestamp", -1)])
    collection.create_index([("location", "2dsphere")])
    return collection

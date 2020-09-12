from pymongo import MongoClient, ReturnDocument
from random import choice
from string import ascii_letters
from datetime import datetime


def _get_key(length=6):
    return ''.join(choice(ascii_letters) for _ in range(length))


class URLShortener:
    db = MongoClient().get_database(name="URL_shortener")

    def create_new(self, url: str):
        key = _get_key()
        password = _get_key(8)
        self.db.data.insert_one({
            "key": key,
            "url": url,
            "password": password,
            "creation_type": datetime.utcnow(),
            "counter": 0
        })
        return key, password

    def get_object(self, key, inc_count=True):
        return self.db.data.find_one_and_update(
            {"key": key},
            {"$inc": {"count": 1 if inc_count else 0}},
            return_document=ReturnDocument.AFTER
        )

    def remove_obj(self, key, password):
        self.db.data.delete_one({
            "key": key,
            "password": password
        })

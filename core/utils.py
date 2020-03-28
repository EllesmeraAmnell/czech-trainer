import logging
import os

from core.word import Word
from pymongo import MongoClient
from random import Random

logger = logging.getLogger(__name__)

host = os.environ['MONGO_HOST'] if 'MONGO_HOST' in os.environ else 'localhost'
client = MongoClient(host, 27017)
collection = client.czech.words
collection.create_index('rus')


def save_word(word):
    logger.info(f'Saving word: {word}')
    if word._id:
        collection.update_one({'_id': word._id}, {'$set': word.get_dict()})
    else:
        collection.insert_one(word.get_dict())


def delete_word(word):
    logger.info(f'Deleting word: {word}')
    res = collection.delete_one({'_id': word._id})
    return res.deleted_count if res else None


def get_words_list(limit=None, skip=None):
    res = collection.find()
    if limit:
        res = res.limit(limit)
    if skip:
        res = res.skip(skip)
    return list(res) if res else None


def get_random_words(count):
    n = collection.count_documents({})
    if n < count:
        logger.error(f'Not enough words in database: {n}. Requested: {count}.')
        raise Exception(f'ERROR: Not enough words in database: {n}. Requested: {count}.')
    used_indexes = []
    random_words = []
    random = Random()
    for _ in range(count):
        new_index = random.randint(0, n - 1)
        while new_index in used_indexes:
            new_index = random.randint(0, n - 1)
        used_indexes.append(new_index)
        words_list = get_words_list(limit=1, skip=new_index)
        word = Word(words_list[0])
        random_words.append(word)
    return random_words


def is_exception():
    raise NotImplemented

import logging

from core.word import Word
from pymongo import MongoClient
from random import Random

logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
client = MongoClient('localhost', 27017)
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
    collection.delete_one({'_id': word._id})


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

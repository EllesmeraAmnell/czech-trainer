import logging

from core.words import Word
from pymongo import MongoClient
from random import Random

logging.basicConfig(filename='debug.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)
client = MongoClient('localhost', 27017)
collection = client.czech.words
collection.create_index('rus')


def save_word(word):
    logger.info(f'Saving word: {word}')
    res = collection.find_one({'rus': word.rus})
    if res:
        collection.update_one({'rus': word.rus}, {'$set': word.get_dict()})
    else:
        collection.insert_one(word.get_dict())


def delete_word(word):
    logger.info(f'Deleting word: {word}')
    collection.delete_one({'rus': word.rus})


def get_words_list(limit=None, skip=None):
    res = collection.find()
    if limit:
        res = res.limit(limit)
    if skip:
        res = res.skip(skip)
    return list(res) if res else None


def get_options_list(count):
    n = collection.count_documents({})
    if n < count:
        logger.error(f'Not enough words in database: {n}. Requested: {count}.')
        raise Exception(f'ERROR: Not enough words in database: {n}. Requested: {count}.')
    used_indexes = []
    options_list = []
    random = Random()
    for i in range(0, count):
        new_index = random.randint(0, n - 1)
        while new_index in used_indexes:
            new_index = random.randint(0, n - 1)
        used_indexes.append(new_index)
        words_list = get_words_list(limit=1, skip=new_index)
        word = Word(words_list[0])
        options_list.append(word)
    return options_list

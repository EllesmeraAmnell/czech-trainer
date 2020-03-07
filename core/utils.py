from random import Random

from pymongo import MongoClient
from core.words import Word

client = MongoClient('localhost', 27017)
collection = client.czech.words
collection.create_index('rus')


def add_new_word(word):
    res = collection.find_one({'rus': word.rus})
    if res:
        collection.update_one({'rus': word.rus}, {'$set': word.get_dict()})
    else:
        collection.insert_one(word.get_dict())


def get_words_list(limit=None, skip=None):
    res = collection.find()
    if limit:
        res = res.limit(limit)
    if skip:
        res = res.skip(skip)
    return list(res) if res else None


def get_new_variant(count):
    n = collection.count_documents({})
    if n < count:
        raise Exception("Error: not enough words in DB")
    rand_numbers = []
    variant = []
    random = Random()
    for i in range(0, count):
        rand_index = random.randint(0, n - 1)
        while rand_index in rand_numbers:
            rand_index = random.randint(0, n - 1)
        rand_numbers.append(rand_index)
        record = get_words_list(limit=1, skip=rand_index)
        word = Word(record[0])
        variant.append(word)
    return variant

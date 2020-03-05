from pymongo import MongoClient

service = "http://localhost:5000/"
client = MongoClient('localhost', 27017)
collection = client.czech.words

collection.create_index('rus')


class Word:
    def __init__(self, rus, ch, part_of_speech, gender=None, form=None):
        self.rus = rus
        self.ch = ch
        self.part_of_speech = part_of_speech
        self.gender = gender if part_of_speech == 'noun' else None
        self.form = form if part_of_speech == 'noun' else None

    def __str__(self):
        return f'{self.rus}, {self.ch}, {self.part_of_speech}, {self.gender}, {self.form}'

    def get_dict(self):
        return {
            'rus': self.rus,
            'ch': self.ch,
            'part_of_speech': self.part_of_speech,
            'gender': self.gender,
            'form': self.form
        }


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

from bson.objectid import ObjectId


class Word:
    def __init__(self, dictionary):
        self._id = ObjectId(dictionary['_id']) if '_id' in dictionary and dictionary['_id'] else None
        self.rus = dictionary['rus']
        self.cz = dictionary['cz']
        self.part_of_speech = dictionary['part_of_speech']
        self.gender = dictionary['gender'] if self.part_of_speech == 'noun' else None
        self.form = dictionary['form'] if self.part_of_speech == 'noun' else None

    def __str__(self):
        return f'{self._id}, {self.rus}, {self.cz}, {self.part_of_speech}, {self.gender}, {self.form}'

    def get_dict(self):
        res = {
            'rus': self.rus,
            'cz': self.cz,
            'part_of_speech': self.part_of_speech,
            'gender': self.gender,
            'form': self.form
        }
        if self._id:
            res['_id'] = self._id
        return res

class Word:
    def __init__(self, dictionary):
        self.rus = dictionary['rus']
        self.ch = dictionary['ch']
        self.part_of_speech = dictionary['part_of_speech']
        self.gender = dictionary['gender']
        self.form = dictionary['form']

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

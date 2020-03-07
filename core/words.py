class Word:
    def __init__(self, dictionary):
        self.rus = dictionary['rus']
        self.cz = dictionary['cz']
        self.part_of_speech = dictionary['part_of_speech']
        self.gender = dictionary['gender'] if self.part_of_speech == 'noun' else None
        self.form = dictionary['form'] if self.part_of_speech == 'noun' else None

    def __str__(self):
        return f'{self.rus}, {self.cz}, {self.part_of_speech}, {self.gender}, {self.form}'

    def get_dict(self):
        return {
            'rus': self.rus,
            'cz': self.cz,
            'part_of_speech': self.part_of_speech,
            'gender': self.gender,
            'form': self.form
        }

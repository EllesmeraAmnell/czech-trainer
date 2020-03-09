from core.const import Time, VerbType, ConjugationType, CZECH_LONG_VOWEL, OVAT_ENDINGS, OUT_ENDINGS, AT_ENDINGS, \
    IT_ET_ENDINGS, EST_EZT_ENDINGS, LONG_VOWEL_REPLACEMENT


# from core.utils import is_exception

class Word:
    def __init__(self, dictionary):
        self.rus = Word.normalize_string(dictionary['rus'])
        self.cz = Word.normalize_string(dictionary['cz'])
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

    def normalize_string(str_to_normalize):
        return str_to_normalize.strip()[0].upper() + str_to_normalize.strip()[1:]


class Verb(Word):
    def __init__(self, dictionary):
        super().__init__(dictionary)

    def get_variants(self, conjugation_type, time):
        if time == Time.FUTURE or time == Time.PAST:
            raise NotImplementedError
        elif time == Time.PRESENT:
            return self.__get_variants_for_present(conjugation_type)

    def __get_variants_for_present(self, conjugation_type):
        # if is_exception(self, PARTS_OF_SPEECH['verb']):
        #     raise Exception("Verb is exception, not implemented yet")
        word_type = self.__check_type()
        correct_word = self.__get_correct_variant(word_type, conjugation_type)
        return correct_word

    def __check_type(self):
        n = len(self.cz)
        if self.cz[n - 4:] == 'ovat':
            return VerbType.OVAT

        ending = self.cz[n - 3:]
        if ending == 'out':
            return VerbType.OUT
        if ending == 'ést' or ending == 'ézt':
            return VerbType.EST_EZT

        ending = self.cz[n - 2:]
        if ending == 'at':
            return VerbType.AT
        if ending == 'it' or ending == 'et' or ending == 'ět':
            return VerbType.IT_ET

        if ending[0] in CZECH_LONG_VOWEL and ending[1] == 't':
            return VerbType.SHORT

    def __get_correct_variant(self, word_type, conjugation_type):
        if word_type == VerbType.OVAT:
            return self.correct_ovat(conjugation_type)
        if word_type == VerbType.OUT:
            return self.correct_out(conjugation_type)
        if word_type == VerbType.AT:
            return self.correct_at(conjugation_type)
        if word_type == VerbType.IT_ET:
            return self.correct_it_et(conjugation_type)
        if word_type == VerbType.EST_EZT:
            return self.correct_est_ezt(conjugation_type)
        if word_type == VerbType.SHORT:
            return self.correct_short(conjugation_type)
        raise Exception("Unknow type of verb!")

    # TODO: дополнить разделением на литературную и разговорную версии
    def correct_ovat(self, conjugation_type):
        n = len(self.cz)
        word_skelet = self.cz[:n - 4]
        return word_skelet + OVAT_ENDINGS[conjugation_type]

    def correct_out(self, conjugation_type):
        n = len(self.cz)
        word_skelet = self.cz[:n - 3]
        return word_skelet + OUT_ENDINGS[conjugation_type]

    def correct_at(self, conjugation_type):
        n = len(self.cz)
        word_skelet = self.cz[:n - 2]
        return word_skelet + AT_ENDINGS[conjugation_type]

    def correct_it_et(self, conjugation_type):
        n = len(self.cz)
        word_skelet = self.cz[:n - 2]
        return word_skelet + IT_ET_ENDINGS[conjugation_type]

    def correct_est_ezt(self, conjugation_type):
        n = len(self.cz)
        word_skelet = self.cz[:n - 1]
        word_skelet = word_skelet.replace('é', 'e')
        return word_skelet + EST_EZT_ENDINGS[conjugation_type]

    def correct_short(self, conjugation_type):
        n = len(self.cz)
        word_skelet = self.cz[:n - 1]
        long_vow = word_skelet[n-2]
        word_skelet = word_skelet.replace(long_vow, LONG_VOWEL_REPLACEMENT[long_vow])   # а вот тут вполне может быть ошибка, но пока предположу, что всё заебись
        return word_skelet + 'j' + EST_EZT_ENDINGS[conjugation_type]    # не ошибка, у них действительно нет отличий, кроме j у коротких слов

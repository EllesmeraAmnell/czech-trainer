from enum import Enum

FORMS = {
    'singular': 'Единственное',
    'plural': 'Множественное',
}

GENDERS = {
    'masculine_inanimate': 'Мужской (неодушевленный)',
    'masculine_animate': 'Мужской (одушевленный)',
    'feminine': 'Женский',
    'neuter': 'Средний',
    'no': 'Отсутсвует'
}

PARTS_OF_SPEECH = {
    'verb': 'Глагол',
    'noun': 'Существительное',
    'adjective': 'Прилагательное',
    'numeral': 'Числительное',
    'adverb': 'Наречие'
}


class Time(Enum):
    PAST = -1
    PRESENT = 0
    FUTURE = 1


class VerbType(Enum):
    OVAT = 0
    AT = 1
    IT_ET = 2
    OUT = 3
    EST_EZT = 4
    SHORT = 5


class ConjugationType(Enum):
    FIRST_SG = 'ja'
    SECOND_SG = 'ty'
    THIRD_SG = 'on'
    FIRST_PL = 'my'
    SECOND_PL = 'vy'
    THIRD_PL = 'oni/ony'


# TODO: дополнить разделением на литературную и разговорную версии
OVAT_ENDINGS = {
    ConjugationType.FIRST_SG: 'uju',
    ConjugationType.SECOND_SG: 'uješ',
    ConjugationType.THIRD_SG: 'uje',
    ConjugationType.FIRST_PL: 'ujeme',
    ConjugationType.SECOND_PL: 'ujete',
    ConjugationType.THIRD_PL: 'uji'
}

OUT_ENDINGS = {
    ConjugationType.FIRST_SG: 'u',
    ConjugationType.SECOND_SG: 'eš',
    ConjugationType.THIRD_SG: 'e',
    ConjugationType.FIRST_PL: 'eme',
    ConjugationType.SECOND_PL: 'ete',
    ConjugationType.THIRD_PL: 'ou'
}

AT_ENDINGS = {
    ConjugationType.FIRST_SG: 'ám',
    ConjugationType.SECOND_SG: 'áš',
    ConjugationType.THIRD_SG: 'á',
    ConjugationType.FIRST_PL: 'áme',
    ConjugationType.SECOND_PL: 'áte',
    ConjugationType.THIRD_PL: 'ají'
}

IT_ET_ENDINGS = {
    ConjugationType.FIRST_SG: 'ím',
    ConjugationType.SECOND_SG: 'íš',
    ConjugationType.THIRD_SG: 'í',
    ConjugationType.FIRST_PL: 'íme',
    ConjugationType.SECOND_PL: 'íte',
    ConjugationType.THIRD_PL: 'í'
}

EST_EZT_ENDINGS = {
    ConjugationType.FIRST_SG: 'u',
    ConjugationType.SECOND_SG: 'eš',
    ConjugationType.THIRD_SG: 'e',
    ConjugationType.FIRST_PL: 'eme',
    ConjugationType.SECOND_PL: 'ete',
    ConjugationType.THIRD_PL: 'ou'
}

RUS_WORD_RE = r'\A[а-яА-ЯёЁ\s]+\Z'
CZECH_WORD_RE = r'\A[a-zA-ZéěýúůíóářťšďžćčňĚÝÚŮÍÓÁŘŤŠĎŽĆČŇ\s]+\Z'

CZECH_LONG_VOWEL = "éýúůíóá"

LONG_VOWEL_REPLACEMENT = {
    'é': 'e',
    'ý': 'y',
    'ú': 'u',
    'ů': 'u',
    'í': 'i',
    'ó': 'o',
    'á': 'a'
}

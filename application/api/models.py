from flask_restplus import fields

from application.api import api
from core.user import ValidationResults, get_user

creds = api.model('creds', {
    'login': fields.String(required=True, description='Users login or e-mail'),
    'password': fields.String(required=True, description='User password')
})

del_word = api.model('del_word', {
    '_id': fields.String(required=True, description='Id, needed if change or delete'),
})

new_word = api.model('new_word', {
    'rus': fields.String(required=True, description='Russian word'),
    'cz': fields.String(required=True, description='Czech word'),
    'part_of_speech': fields.String(required=True, description='Part of speech'),
    'gender': fields.String(required=False, description='Gender, only for nouns'),
    'form': fields.String(required=False, description='Form, only for nouns')
})

put_word = api.inherit('put_word', del_word, {
    'rus': fields.String(required=False, description='Russian word'),
    'cz': fields.String(required=False, description='Czech word'),
    'part_of_speech': fields.String(required=False, description='Part of speech'),
    'gender': fields.String(required=False, description='Gender, only for nouns'),
    'form': fields.String(required=False, description='Form, only for nouns')
})

login = api.model('login', {
    'login': fields.String(required=True, description='Login or e-mail for identification'),
})


class RegistrarionData:
    data = api.model('registration_data', {
        'login': fields.String(required=True, description='User login'),
        'email': fields.String(required=True, description='User e-mail to verify registration'),
        'password': fields.String(required=True, description='User password'),
        'name': fields.String(required=True, description='User name'),
        'surname': fields.String(required=True, description='Users surname')
    })

    @staticmethod
    def validate(data):
        error_messages = []
        if not (data.get('login') and data.get('email') and data.get('password') and data.get('name') and data.get(
                'surname')):
            error_messages.append(ValidationResults.EMPTY_FIELDS)
        if get_user(data.get('login'), 'login'):
            error_messages.append(ValidationResults.LOGIN_EXISTS)
        if get_user(data.get('email'), 'email'):
            error_messages.append(ValidationResults.EMAIL_EXISTS)
        if len(data.get('password')) < 8:
            error_messages.append(ValidationResults.SHORT_PASSWORD)
        return error_messages if error_messages else [ValidationResults.SUCCESS]

import logging
import os
import requests

from bson import ObjectId
from enum import Enum
from flask import json, current_app, url_for
from flask_login import UserMixin
from flask_mail import Message
from hashlib import md5
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

host = os.environ['MONGO_HOST'] if 'MONGO_HOST' in os.environ else 'localhost'
client = MongoClient(host, 27017)
collection = client.czech.users
collection.create_index('email')
collection.create_index('login')


class UserRoles(Enum):
    ADMIN = 2
    MODERATOR = 1
    USER = 0


class User(UserMixin):
    def __init__(self, dictionary):
        self.id = ObjectId(dictionary.get('_id')) if '_id' in dictionary else None
        self.name = dictionary.get('name').lower().capitalize()
        self.surname = dictionary.get('surname').lower().capitalize()
        self.login = dictionary.get('login').lower()
        self.email = dictionary.get('email').lower()
        self.password = dictionary.get('password')
        self.role = UserRoles(dictionary.get('role')) if 'role' in dictionary else UserRoles.USER
        self.confirmed = dictionary.get('confirmed')

    def protect_password(self, password):
        self.password = generate_password_hash(password, method='sha256')

    def change_password(self, password):
        self.password = generate_password_hash(password, method='sha256')
        collection.update_one({'_id': self.id}, {'$set': {'password': self.password}})

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return self.login

    def get_dict(self):
        res = {
            'login': self.login,
            'email': self.email,
            'password': self.password,
            'name': self.name,
            'surname': self.surname,
            'role': self.role.value,
            'confirmed': self.confirmed
        }
        if self.id:
            res['_id'] = self.id
        return res

    def get_role_description(self):
        if self.role == UserRoles.USER:
            return 'Пользователь'
        if self.role == UserRoles.MODERATOR:
            return 'Модератор'
        if self.role == UserRoles.ADMIN:
            return 'Администратор'
        return ''

    def get_avatar(self, size=150):
        """Docs: https://en.gravatar.com/site/implement/images/"""
        digest = md5(self.email.encode('UTF-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=mp&s={}'.format(digest, size)


def get_user(value, param='_id'):
    value = value.lower() if param != '_id' else value
    res = collection.find_one({param: value})
    return User(res) if res else None


def update_user(user):
    collection.update_one({'_id': user.id}, {'$set': user.get_dict()})


def add_new_user(user):
    user.protect_password(user.password)
    res = collection.insert_one(user.get_dict())
    user.id = res.inserted_id


class ValidationResults(Enum):
    NO_CAPTCHA = 'Запрос не содержит данных для проверки капчи'
    BAD_CAPTCHA = 'Ошибка при проверке капчи'
    CAPTCHA_SUCCESS = 'Капча подтверждена'
    EMPTY_FIELDS = 'Пожалуйста, заполните все поля'
    LOGIN_EXISTS = 'Выбранный логин занят'
    EMAIL_EXISTS = 'Пользователь с таким e-mail уже существует'
    DIFFERENT_PASSWORDS = 'Введённые пароли не совпадают'
    SHORT_PASSWORD = 'Слишком короткий пароль'
    SUCCESS = 'Успешная валидация'
    WRONG_CREDS = 'Неверный логин и/или пароль'
    WRONG_ROLE = 'У Вас недостаточно прав для просмотра этой страницы'
    NOT_AUTHORIZED = 'Для просмотра страницы необходимо авторизоваться'


class ValidationError:
    def __init__(self, text):
        self.value = text


CAPTCHA_ERROR_CODES = {
    'missing-input-secret': ValidationError('Отсутсвует секретный ключ в переданной форме'),
    'invalid-input-secret': ValidationError('Секретный ключ недействителен или имеет неправильный формат'),
    'missing-input-response': ValidationError('Пожалуйста, подтвердите, что Вы не робот'),
    'invalid-input-response': ValidationError('Подтверждение недействительно или имеет неправильный формат'),
    'bad-request': ValidationError('Запрос недействителен'),
    'timeout-or-duplicate': ValidationError('Капча не действительна (устарела либо уже использована)')
}


def validate_captcha(form):
    """ Docs: https://developers.google.com/recaptcha/docs/verify """
    if 'g-recaptcha-response' not in form:
        return [ValidationResults.NO_CAPTCHA]
    data = {
        'secret': current_app.config.get('GOOGLE_SERVER_KEY'),
        'response': form.get('g-recaptcha-response')
    }
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    response_dict = json.loads(response.content)
    if response_dict.get('success'):
        return [ValidationResults.CAPTCHA_SUCCESS]
    error_codes = response_dict.get('error-codes')
    if error_codes:
        return [CAPTCHA_ERROR_CODES.get(error_code) for error_code in error_codes]
    return [ValidationResults.BAD_CAPTCHA]


def validate_registration_form(form):
    validation_result = validate_captcha(form)
    if ValidationResults.CAPTCHA_SUCCESS not in validation_result:
        return validation_result
    flash_messages = []
    if not (form.get('login') and form.get('email') and form.get('password') and form.get('confirm') and
            form.get('name') and form.get('surname')):
        flash_messages.append(ValidationResults.EMPTY_FIELDS)
    if get_user(form.get('login'), 'login'):
        flash_messages.append(ValidationResults.LOGIN_EXISTS)
    if get_user(form.get('email'), 'email'):
        flash_messages.append(ValidationResults.EMAIL_EXISTS)
    if form.get('password') != form.get('confirm'):
        flash_messages.append(ValidationResults.DIFFERENT_PASSWORDS)
    if len(form.get('password')) < 8:
        flash_messages.append(ValidationResults.SHORT_PASSWORD)
    form.pop('password', None)
    form.pop('confirm', None)
    return flash_messages if flash_messages else [ValidationResults.SUCCESS]


def generate_confirmation_mail(email, token):
    msg = Message('Czech Trainer: подтверждение регистрации', sender='Czech Trainer', recipients=[email])
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = 'Вы получили это письмо, так как данный адрес электронной почты был указан при регистрации на ' \
               'сайте Czech Trainer (http://194.67.90.186/).\nЕсли это были не Вы, проигнорируйте это письмо.\n\n' \
               'Для завершения регистрации перейдите по адресу ниже (ссылка действительна в течение часа):\n' \
               '{} \n\n'.format(link)
    return msg

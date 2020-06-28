from random import Random
from smtplib import SMTPRecipientsRefused

from flask import jsonify, current_app
from flask_login import current_user, login_user, logout_user
from flask_restplus import Resource, abort
from flask_restplus._http import HTTPStatus

from application import mail
from application.api import api
from application.api.models import creds, RegistrarionData, del_word, put_word, new_word, login
from application.web.routes import s
from core.user import get_user, ValidationResults, User, generate_confirmation_mail, add_new_user, UserRoles
from core.utils import get_random_words, get_words_list, save_word, delete_word, get_word
from core.word import Word


@api.route('/profile')
class Profile(Resource):
    @api.doc(responses={
        HTTPStatus.OK: 'Success',
        HTTPStatus.FORBIDDEN: 'Not authorized'
    })
    def get(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.FORBIDDEN, message='Not authorized')
        return jsonify(name=current_user.name, surname=current_user.surname, login=current_user.login,
                       email=current_user.email, role=current_user.get_role_description())

    @api.doc(responses={
        HTTPStatus.OK: 'Success',
        HTTPStatus.BAD_REQUEST: 'User not found',
    })
    @api.expect(login)
    def post(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.FORBIDDEN, message='Not authorized')
        login = api.payload['login']
        user = get_user(login, 'login') or get_user(login, 'email')
        if not user:
            abort(HTTPStatus.BAD_REQUEST, message="User not found")
        return jsonify(name=user.name, surname=user.surname, login=user.login,
                       email=user.email, role=user.get_role_description())


@api.route('/login')
class Login(Resource):
    @api.expect(creds, validate=True)
    @api.doc(responses={
        HTTPStatus.OK: 'Success',
        HTTPStatus.UNAUTHORIZED: 'Wrong credentials',
        HTTPStatus.METHOD_NOT_ALLOWED: 'User is authorized',
        HTTPStatus.FORBIDDEN: 'Unconfirmed account'
    })
    def post(self):
        if current_user.is_authenticated:
            return abort(HTTPStatus.METHOD_NOT_ALLOWED, message='Already logged in')
        login = api.payload['login']
        password = api.payload['password']
        user = get_user(login, 'login') or get_user(login, 'email')
        if user and user.confirmed and user.check_password(password=password):
            login_user(user)
            return jsonify(result='Login successful')
        if user and not user.confirmed:
            return abort(HTTPStatus.FORBIDDEN, message='Unconfirmed account')
        abort(HTTPStatus.UNAUTHORIZED, message=ValidationResults.WRONG_CREDS.value)


@api.route('/logout')
class Logout(Resource):
    @api.doc(responses={
        HTTPStatus.OK: 'Success',
        HTTPStatus.METHOD_NOT_ALLOWED: 'Already logged out'
    })
    def post(self):
        if not current_user.is_authenticated:
            return abort(HTTPStatus.METHOD_NOT_ALLOWED, message='Already logged out')
        logout_user()
        return jsonify(result='Logout successful')


@api.route('/signup')
class Signup(Resource):
    @api.expect(RegistrarionData.data, validate=True)
    @api.doc(responses={
        HTTPStatus.OK: 'Success',
        HTTPStatus.BAD_REQUEST: 'Validation error',
        HTTPStatus.METHOD_NOT_ALLOWED: 'User is authorized',
        HTTPStatus.INTERNAL_SERVER_ERROR: 'Internal server error'
    })
    def post(self):
        if current_user.is_authenticated:
            return abort(HTTPStatus.METHOD_NOT_ALLOWED, message='You must logout first')
        validation_result = RegistrarionData.validate(api.payload)
        if ValidationResults.SUCCESS in validation_result:
            try:
                user = User(api.payload)
                token = s.dumps(user.email, salt=current_app.config.get('MAIL_SALT'))
                msg = generate_confirmation_mail(user.email, token)
                mail.send(msg)
                add_new_user(user)
                return jsonify(message='Registration successful. Verification mail sent.')
            except SMTPRecipientsRefused as ex:
                abort(HTTPStatus.BAD_REQUEST, message='Incorrect e-mail')
            except Exception as ex:
                abort(HTTPStatus.INTERNAL_SERVER_ERROR, message=repr(ex))
        error_list = [res.value for res in validation_result]
        return abort(HTTPStatus.BAD_REQUEST, message=str(error_list))


@api.route('/quiz')
class Quiz(Resource):
    @api.doc(responses={
        HTTPStatus.OK: 'Success',
        HTTPStatus.FORBIDDEN: 'Not authorized'
    })
    def get(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.FORBIDDEN, message='Not authorized')
        words = get_random_words(4)
        random_option = Random().choice(words)
        question, answer = random_option.rus, random_option.cz
        options = [word.cz for word in words]
        return jsonify(question=question, answer=answer, options=options)


@api.route('/words')
@api.doc(responses={
    HTTPStatus.OK: 'Success',
    HTTPStatus.UNAUTHORIZED: 'Not authorized',
    HTTPStatus.BAD_REQUEST: 'Bad request'
})
class Words(Resource):
    def get(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.UNAUTHORIZED, message='Not authorized')
        words_list = get_words_list()
        words = dict()
        for w in words_list:
            id = str(w.pop('_id'))
            words[id] = w
        return jsonify(count=len(words_list), words=words)

    @api.expect(put_word)
    def put(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.UNAUTHORIZED, message='Not authorized')
        if current_user.role.value < UserRoles.MODERATOR.value:
            abort(HTTPStatus.FORBIDDEN, ValidationResults.WRONG_ROLE.value)
        try:
            if not get_word(api.payload['_id']):
                raise Exception('Cannot find word with such id')
            word = Word(api.payload)
            save_word(word)
            return jsonify(message='Word updated successfully', word=word.get_dict(str_id=True))
        except Exception as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    @api.expect(new_word, validate=True)
    def post(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.UNAUTHORIZED, message='Not authorized')
        if current_user.role.value < UserRoles.MODERATOR.value:
            abort(HTTPStatus.FORBIDDEN, ValidationResults.WRONG_ROLE.value)
        try:
            if '_id' in api.payload:
                api.payload.pop('_id')
            word = Word(api.payload)
            save_word(word)
            return jsonify(message='Word added successfully', word=word.get_dict(str_id=True))
        except Exception as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

    @api.expect(del_word)
    def delete(self):
        if not current_user.is_authenticated:
            abort(HTTPStatus.UNAUTHORIZED, message='Not authorized')
        if current_user.role.value < UserRoles.MODERATOR.value:
            abort(HTTPStatus.FORBIDDEN, ValidationResults.WRONG_ROLE.value)
        try:
            word = get_word(api.payload['_id'])
            if not word or not delete_word(word):
                raise Exception('Cannot find word with such id')
            return jsonify(message='Word deleted successfully', word=word.get_dict(str_id=True))
        except Exception as e:
            abort(HTTPStatus.BAD_REQUEST, message=str(e))

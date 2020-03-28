import logging

from bson import ObjectId
from core.user import get_user, User, add_new_user, validate_registration_form, ValidationResults, UserRoles, \
    generate_confirmation_mail, update_user
from core.word import Word
from core.utils import save_word, get_words_list, delete_word, get_random_words
from core.const import GENDERS, PARTS_OF_SPEECH, FORMS
from flask import Flask, render_template, request, send_from_directory, flash, redirect, url_for, session, abort
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_mail import Mail
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from random import Random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_json('config.json')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

mail = Mail()
mail.init_app(app)
s = URLSafeTimedSerializer(app.config.get('MAIL_SECRET'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(".", 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/img/prague.jpg')
def jpg():
    return send_from_directory("static", 'img/prague.jpg')


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/profile', methods=['GET'])
@login_required
def profile():
    return render_template('profile.html')


@app.route('/quiz', methods=['GET'])
@login_required
def quiz():
    words = get_random_words(4)
    random_option = Random().choice(words)
    question, answer = random_option.rus, random_option.cz
    options = [word.cz for word in words]
    return render_template('quiz.html', question=question, answer=answer, options=options)


@app.route('/words', methods=['GET'])
@login_required
def words():
    words_list = get_words_list()
    return render_template('words.html', words_list=words_list, genders=GENDERS, parts_of_speech=PARTS_OF_SPEECH,
                           forms=FORMS)


@app.route('/edit_words', methods=['POST', 'GET'])
@login_required
def edit_words():
    if current_user.role.value < UserRoles.MODERATOR.value:
        abort(403, ValidationResults.WRONG_ROLE.value)
    form_data = None
    if request.method == 'POST':
        word = Word(request.form)
        try:
            if 'saveButton' in request.form:
                save_word(word)
                flash('Слово успешно сохранено!', category='success')
                form_data = request.form
            if 'deleteButton' in request.form and delete_word(word):
                flash('Слово успешно удалено!', category='success')
        except Exception as e:
            flash('Ошибка!', category='error')
            logger.error(str(e))
    words_list = get_words_list()
    return render_template('edit_words.html', form_data=form_data, words_list=words_list, genders=GENDERS,
                           parts_of_speech=PARTS_OF_SPEECH, forms=FORMS)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login = ''
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        user = get_user(login, 'login') or get_user(login, 'email')
        if user and user.confirmed and user.check_password(password=password):
            login_user(user)
            next_page = session.get('next_page', '/')
            session['next_page'] = ''
            return redirect(next_page or url_for('words'))
        if not user.confirmed:
            session['email_to_confirm'] = user.email
            return redirect(url_for('finish_signup'))
        flash(ValidationResults.WRONG_CREDS.value)
    return render_template('login.html', form_data=login)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form_data = {}
    if request.method == 'POST':
        validation_result = validate_registration_form(request.form.to_dict())
        if ValidationResults.SUCCESS in validation_result:
            user = User(request.form)
            token = s.dumps(user.email, salt=app.config.get('MAIL_SALT'))
            msg = generate_confirmation_mail(user.email, token)
            mail.send(msg)
            add_new_user(user)
            session['email_to_confirm'] = user.email
            return redirect(url_for('finish_signup'))
        for message in validation_result:
            flash(message.value)
        form_data = request.form
    return render_template('signup.html', google_client_key=app.config.get('GOOGLE_CLIENT_KEY'), form_data=form_data)


@app.route('/finish_signup', methods=['GET', 'POST'])
def finish_signup():
    if current_user.is_authenticated and not session.get('email_to_confirm'):
        return redirect(url_for('index'))
    if request.method == 'POST' and session.get('email_to_confirm'):
        token = s.dumps(session.get('email_to_confirm'), salt=app.config.get('MAIL_SALT'))
        msg = generate_confirmation_mail(session.get('email_to_confirm'), token)
        session['email_to_confirm'] = ''
        mail.send(msg)
    return render_template('finish_signup.html', resent_available=True if session.get('email_to_confirm') else False)


@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt=app.config.get('MAIL_SALT'), max_age=3600)
        session['email_to_confirm'] = ''
        user = get_user(email, 'email')
        user.confirmed = True
        update_user(user)
        flash('Адрес электронной почты подтверждён успешно!')
        login_user(user)
        return redirect(url_for('login'))
    except SignatureExpired:
        abort(401, 'Невозможно заершить регистрацию, так как ссылка устарела.')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    logout_user()
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    if user_id:
        return get_user(ObjectId(user_id))
    return None


@login_manager.unauthorized_handler
def unauthorized():
    flash(ValidationResults.NOT_AUTHORIZED.value)
    session['next_page'] = request.path
    return redirect(url_for('login'))


@app.errorhandler(403)
def error_403(error_info):
    return render_template('error_page.html', title='403', error_info=error_info, error_code=' 403',
                           error_text='недостаточно прав', content=error_info), 403


@app.errorhandler(404)
def error_404(error_info):
    return render_template('error_page.html', title='404', error_info=error_info, error_code=' 404',
                           error_text='страница не найдена'), 404


@app.errorhandler(500)
@app.errorhandler(Exception)
def error_500(error_info):
    return render_template('error_page.html', title='500', error_info=error_info, error_code=' 500',
                           error_text='внутренняя ошибка сервера'), 500


if __name__ == '__main__':
    logger.info('*' * 80)
    app.run(host='0.0.0.0', port=4000, passthrough_errors=True, debug=False)  # for public
    # app.run(port=4000, passthrough_errors=False, debug=True)  # for debug

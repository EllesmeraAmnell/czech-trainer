import logging

from core.word import Word
from core.utils import save_word, get_words_list, delete_word, get_random_words
from core.const import GENDERS, PARTS_OF_SPEECH, FORMS
from flask import Flask, render_template, request, send_from_directory
from random import Random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(".", 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/quiz', methods=['POST', 'GET'])
def quiz():
    words = get_random_words(4)
    random_option = Random().choice(words)
    question, answer = random_option.rus, random_option.cz
    options = [word.cz for word in words]
    return render_template('quiz.html', question=question, answer=answer, options=options)


@app.route('/edit_db', methods=['GET'])
def show_db():
    words_list = get_words_list()
    return render_template('show_db.html', words_list=words_list, genders=GENDERS, parts_of_speech=PARTS_OF_SPEECH,
                           forms=FORMS)


@app.route('/edit_db_super_secret_pf8wls', methods=['POST', 'GET'])
def edit_db():
    result = None
    if request.method == 'POST':
        word = Word(request.form)
        try:
            if 'saveButton' in request.form:
                save_word(word)
                result = 'Слово успешно сохранено!'
            if 'deleteButton' in request.form and delete_word(word):
                result = 'Слово успешно удалено!'
        except Exception as e:
            result = 'Ошибка!'
            logger.error(str(e))
    words_list = get_words_list()
    return render_template('edit_db.html', result=result, words_list=words_list,
                           genders=GENDERS, parts_of_speech=PARTS_OF_SPEECH, forms=FORMS)


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

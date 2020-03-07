import logging

from core.words import Word
from core.utils import save_word, get_words_list, delete_word
from core.const import GENDERS, PARTS_OF_SPEECH, FORMS
from flask import Flask, render_template, request

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST', 'GET'])
def add():
    result = None
    if request.method == 'POST':
        word = Word(request.form)
        try:
            if 'saveButton' in request.form:
                save_word(word)
                result = 'Слово успешно сохранено!'
            if 'deleteButton' in request.form:
                delete_word(word)
                result = 'Слово успешно удалено!'
        except Exception as e:
            result = 'Ошибка!'
            logger.error(str(e))
    words_list = get_words_list()
    return render_template('add.html', result=result, words_list=words_list,
                           genders=GENDERS, parts_of_speech=PARTS_OF_SPEECH, forms=FORMS)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


if __name__ == '__main__':
    logger.info('*'*80)
    # app.run(host='0.0.0.0', port=4000, passthrough_errors=True, debug=False)  # for public
    app.run(port=4000, passthrough_errors=False, debug=True)  # for debug

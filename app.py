from common import Word, add_new_word, get_words_list, delete_word
from const import GENDERS, PARTS_OF_SPEECH, FORMS
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
def index():
    return render_template('index.html')


@app.route('/add', methods=['POST', 'GET'])
def add():
    result = None
    if request.method == 'POST':
        rus = request.form['inputRus']
        ch = request.form['inputCz']
        word_type = request.form['selectPartOfSpeech']
        gender = request.form['selectGender']
        form = request.form['selectForm']
        word = Word(rus, ch, word_type, gender, form)
        try:
            if 'saveButton' in request.form:
                add_new_word(word)
                result = 'Слово успешно сохранено!'
            if 'deleteButton' in request.form:
                delete_word(word)
                result = 'Слово успешно удалено!'
        except:
            result = 'Ошибка!'
    words_list = get_words_list()
    return render_template('add.html', result=result, words_list=words_list,
                           genders=GENDERS, parts_of_speech=PARTS_OF_SPEECH, forms=FORMS)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=4000, passthrough_errors=True, debug=False)  # for public
    app.run(port=4000, passthrough_errors=False, debug=True)  # for debug

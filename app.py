from common import Word, add_new_word, get_words_list
from const import GENDERS, PARTS_OF_SPEECH, FORMS
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@app.route('/add', methods=['POST', 'GET'])
def index():
    word = None
    if request.method == 'POST':
        rus = request.form['inputRus']
        ch = request.form['inputCh']
        word_type = request.form['selectPartOfSpeech']
        gender = request.form['selectGender']
        form = request.form['selectForm']
        word = Word(rus, ch, word_type, gender, form)
        add_new_word(word)
    words_list = get_words_list()
    return render_template('index.html', result=word, words_list=words_list,
                           genders=GENDERS, parts_of_speech=PARTS_OF_SPEECH, forms=FORMS)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', title='404'), 404


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=4000, passthrough_errors=True, debug=False)  # for public
    app.run(port=4000, passthrough_errors=False, debug=True)  # for debug

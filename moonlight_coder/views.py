from flask import g, render_template

from . import app
from .db import get_db
from .util import load_cards

# app = Flask(__name__)


class MoonLightCoder:

    def __init__(self):
        self.questions = load_cards()
        print(f'loaded {len(self.questions)} questions')

    def get_question(self):
        return self.questions[0]


mlc = MoonLightCoder()


@app.route('/')
def learn_python(name=None):
    return render_template('main.html', name=name, file='home.html')


@app.route('/cards')
def flash_cards(name=None):
    return render_template('main.html', name=mlc.get_question(), file='home.html')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
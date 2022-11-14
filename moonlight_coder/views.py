import flask
import flask_login
from flask import g, render_template, request, redirect, url_for
from flask_login import login_user, login_required
from random import choice, shuffle, sample

from . import app
from .db import *
from .user import User
from .util import load_cards, FlashCard

# app = Flask(__name__)


class MoonLightCoder:

    def __init__(self):
        self.questions = load_cards()
        print(f'loaded {len(self.questions)} questions')

    def get_question(self) -> FlashCard:
        key = choice(list(self.questions))
        return self.questions[key]

    def check_answer(self, question_uuid: str, answer: list) -> bool:
        try:
            question = self.questions[question_uuid]  # type: FlashCard
        except KeyError:
            print("this question does not exist!")
            raise
        return question.check_answer(answer)


mlc = MoonLightCoder()



@app.route('/')
def learn_python(name=None):
    return render_template('main.html', name=name, file='home.html')


@app.route('/login')
def login():
    # example here: https://flask-login.readthedocs.io/en/latest/
    username = 'nlespera'
    login_user(User(username))
    flask.flash(f"Logged in user {username} successfully")
    return redirect('/')


@app.route('/cards')
# @login_required
def flash_cards(name=None):
    db = get_db()
    username = flask_login.current_user.id
    print(f'current user: {username}')
    previous_uuid = request.args.get('uuid')
    if previous_uuid is not None:
        print(f"previous questions: {previous_uuid}")
        answers = request.args.get('answer')
        print(f"previous answers: {answers}")
        correct = mlc.check_answer(previous_uuid, [answers])
        if correct:
            print("nice job!")
        else:
            print("no good!")
        update_user_result(db, username, previous_uuid, correct)
    flash_card = mlc.get_question()
    options = flash_card.answers + flash_card.incorrect
    shuffle(options)
    return render_template('card.html', question=flash_card.question, length=len(options), answers=options,
                           uuid=flash_card.uuid)


@app.route('/db')
# @login_required
def test_database():
    db = get_db()
    results = get_user_answers(db, "nlespera")
    if not results:
        create_new_user(db, "nlespera", "nicholai", "lesperance")
        results = get_user_answers(db, "nlespera")
    return results


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
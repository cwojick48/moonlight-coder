from random import choice, shuffle
from urllib.parse import urlparse, urljoin

import flask
import flask_login
from flask import g, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required

from . import app
from .db import *
from .user import User
from .util import load_cards, FlashCard


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


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.login_manager.user_loader
def load_user(user_id):
    return User(user_id)


@app.login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.route('/')
def learn_python(name=None):
    user = flask_login.current_user
    print(user)
    if user.is_authenticated:
        username = flask_login.current_user.id
        print(f'current user: {username}')
    else:
        print(f'no user logged in')

    # TODO: what is "name"=name? where does this come into play in the template
    return render_template('main.html', name=name, file='home.html')


# TODO: needs a lot of development. need to handle the reditect to "next"
@app.route('/login', methods=['GET'])
def login():
    # TODO: first check if already signed in
    return render_template('main.html', file="login.html")


@app.route('/login', methods=['POST'])
def attempt_login():
    db = get_db()
    username = request.form.get('username')
    if not check_if_user_exists(db, username):
        print(f'username {username} does not exist')
        print(f'all users: {get_all_usernames(db)}')
        # TODO: show some kind of error that this user doesnt exist
        return redirect(url_for("signup"))
    else:
        print('b')
        login_user(User(username))
        flask.flash(f"Logged in user {username} successfully")
        print(f'loggined in user {username}')
        print(flask_login.current_user)
        next = flask.request.args.get('next')
        if not is_safe_url(next):
            print('c')
            return flask.abort(400)
        print('d')
        return flask.redirect(next or url_for('learn_python'))


@app.route('/signup', methods=['GET'])
def signup():
    # example here: https://flask-login.readthedocs.io/en/latest/
    return render_template("main.html", file="signup.html")


@app.route('/signup', methods=['POST'])
def new_user():
    db = get_db()
    username = request.form.get('first_name')
    try:
        create_new_user(db, username=username, email=request.form.get('email'),
                        first_name=request.form.get('first_name'), last_name=request.form.get('last_name'))
    except:
        # TODO make this show an error
        return render_template("main.html", file="signup.html")
    else:
        login_user(User(username))
        return render_template('main.html', name=username, file='home.html')


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('learn_python'))


# this route will be flushed out with a template and design, precursor to the main "use case" of the app
@app.route('/cards')
@login_required
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
    return render_template('main.html', file='card.html', question=flash_card.question, length=len(options),
                           answers=options, uuid=flash_card.uuid)


# this route is just for testing the database functions, not for production
@app.route('/db')
@login_required
def test_database():
    db = get_db()
    results = get_user_answers(db, "nlespera")
    if not results:
        create_new_user(db, "nlespera", "nicholai", "lesperance")
        results = get_user_answers(db, "nlespera")
    return results


@app.route('/about')
def about():
    return render_template('main.html', file='about.html')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

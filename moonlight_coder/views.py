from collections import Counter
from random import choice, shuffle
from typing import Dict
from urllib.parse import urlparse, urljoin

import flask
from flask import g, render_template, request, redirect, url_for
import flask_login
from flask_login import login_user, logout_user, login_required

from . import app
from .config import MODULE_1_DIFFICULTY, STREAK_MINIMUM, PASSING_GRADE
from .db import *
from .user import User
from .util import load_cards, FlashCard, CARD_TEMPLATES, CardType


class MoonLightCoder:

    def __init__(self):
        self.all_questions = load_cards()
        self.module_questions = dict()  # type: Dict[int, Dict[str, FlashCard]]
        self.module_questions[0] = {uuid: q for uuid, q in self.all_questions.items(
        ) if q.difficulty < MODULE_1_DIFFICULTY}
        self.module_questions[1] = {uuid: q for uuid, q in self.all_questions.items(
        ) if q.difficulty >= MODULE_1_DIFFICULTY}
        print(f'loaded {len(self.all_questions)} questions')

        self.users = dict()

    def get_question(self, module: int, uuid: str) -> FlashCard:
        return self.module_questions[module][uuid]

    def get_random_question(self, module: int) -> FlashCard:
        uuid = choice(list(self.module_questions[module]))
        return self.get_question(module, uuid)

    def check_answer(self, question_uuid: str, answer: list) -> bool:
        try:
            question = self.all_questions[question_uuid]  # type: FlashCard
        except KeyError:
            print("this question does not exist!")
            raise
        return question.check_answer(answer)

    def get_answer(self, question_uuid: str):
        try:
            question = self.all_questions[question_uuid]  # type: FlashCard
        except KeyError:
            print("this question does not exist!")
            raise
        return question.answers

    def get_module_summary(self, module: int, username: str) -> Dict[str, int]:
        module_questions = self.module_questions[module]
        category_denom = Counter(
            card.category.value for card in module_questions.values())
        db = get_db()
        completed_uuids = {uuid for uuid, results in get_user_answers(db, username).items()
                           if uuid in module_questions and results['streak'] >= STREAK_MINIMUM}
        category_numer = Counter(
            module_questions[uuid].category.value for uuid in completed_uuids)

        results = {category: int(category_numer.get(category, 0) / denom * 100)
                for category, denom in category_denom.items()}

        remaining = {}
        i =0
        for category, n in category_denom.items():
            
            #print(str(category_numer.get(category, 0)) + "/" + str(n))
            remaining[i] = str(category_numer.get(category, 0)) + "/" + str(n)
            i+=1
        return (results, remaining)

    def get_single_choice_module_questions(self, module: int):
        module_questions = self.module_questions[module]
        return [question for question in module_questions.values() if question.question_type == CardType.SINGLE_CHOICE]


mlc = MoonLightCoder()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.login_manager.user_loader
def load_user(user_id):
    if user_id not in mlc.users:
        user = User(user_id)
        mlc.users[user_id] = user
    return mlc.users[user_id]


@app.login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)


@app.route('/')
def learn_python(name=None):
    user = flask_login.current_user
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
        login_user(User(username))
        flask.flash(f"Logged in user {username} successfully")
        print(f'loggined in user {username}')
        print(flask_login.current_user)
        next = flask.request.args.get('next')
        if not is_safe_url(next):
            return flask.abort(400)
        return flask.redirect(next or url_for('profile'))


@app.route('/signup', methods=['GET'])
def signup():
    # example here: https://flask-login.readthedocs.io/en/latest/
    return render_template("main.html", file="signup.html")


@app.route('/signup', methods=['POST'])
def new_user():
    db = get_db()
    username = request.form.get('username')
    try:
        create_new_user(db, username=username, email=request.form.get('email'),
                        first_name=request.form.get('first_name'), last_name=request.form.get('last_name'))
    except:
        # TODO make this show an error
        return render_template("main.html", file="signup.html")
    else:
        login_user(User(username))
        return flask.redirect(url_for('profile'))


@app.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('learn_python'))


# this route will be flushed out with a template and design, precursor to the main "use case" of the app
@login_required
@app.route('/module<module>/cards', methods=['GET'])
def flash_cards(module: str):
    user = flask_login.current_user  # type: User
    print(f'current user: {user.id} {user.first_name}')
    total_cards = len(mlc.module_questions[int(module)])
    remaining_cards = user.count_remaining_cards(int(module))

    if remaining_cards == 0:
        return profile(message=f"Congratulations, you completed all Module {module} flash cards!")

    flash_card = mlc.get_question(int(module), user.get_next_card(int(module)))
    options = flash_card.answers + flash_card.incorrect
    shuffle(options)

    card_template = CARD_TEMPLATES[flash_card.question_type.value]

    response = request.args.get('response') or "&nbsp"
    return render_template('main.html', file='cards/card.html', question=flash_card.question, length=len(options),
                           answers=options, uuid=flash_card.uuid, card_template=card_template, total_cards=total_cards,
                           remaining_cards=remaining_cards, response=response, module=module)


@login_required
@app.route('/module<module>/shuffle')
def shuffle_cards(module: str):
    user = flask_login.current_user  # type: User
    user.shuffle_deck(module)
    return redirect(url_for('flash_cards', module=module, response="The deck is shuffled!"))


@login_required
@app.route('/module<module>/reset')
def restart_module(module: str):
    db = get_db()
    user = flask_login.current_user  # type: User
    clear_user_streaks(db, user.id, int(module))
    user.module_cards = None
    return redirect(url_for('flash_cards', module=module))


@login_required
@app.route('/module<module>/cards', methods=['POST'])
def submit_answer(module):
    db = get_db()
    user = flask_login.current_user  # type: User
    answers = [answer for key, answer in request.form.items() if key.startswith('answer')]
    uuid = request.form.get('uuid')
    correct = mlc.check_answer(uuid, answers)

    if correct:
        response = "Correct, nice job!"
    else:
        answers = mlc.get_answer(uuid)
        if len(answers) == 1:
            response = f"Not quite! The correct answer was '{answers[0]}'."
        else:
            response = f"Not quite! The correct answers were: {', '.join(answers)}."

    completed = update_user_result(db, user.id, uuid, correct)
    if completed:
        user.remove_card(int(module), uuid)

    return redirect(url_for('flash_cards', module=module, response=response))


@app.route('/module<module>/quiz', methods=['GET'])
@login_required
def quiz(module: str):
    print(f"questions for quiz loading...")
    flash_cards = mlc.get_single_choice_module_questions(int(module))
    questions = [(card.uuid, card.question) for card in flash_cards]
    return render_template('main.html', file='quiz.html', module=module, questions=questions)


@app.route('/module<module>/quiz', methods=['POST'])
@login_required
def grade_quiz(module: str):
    answers = {key.split(':')[1]: answer for key, answer in request.form.items() if key.startswith('answer:')}
    correct = [mlc.check_answer(uuid, [answer]) for uuid, answer in answers.items()]
    grade = int(round(sum(correct) / len(correct), 2) * 100)
    if grade >= PASSING_GRADE:
        db = get_db()
        username = flask_login.current_user.id
        profile_message = f"Congratulations, you completed Module {module} with a score of {grade}%!"
        mark_module_completed(db, username, int(module))
    else:
        profile_message = f"Dang! You scored {grade}%, not enough to pass. Keep trying!"
    return profile(profile_message)



# this route is just for testing the database functions, not for production
@app.route('/db')
@login_required
def test_database():
    db = get_db()
    results = get_user_answers(db, "nlespera")
    if not results:
        create_new_user(db, "nlespera", "nlespera@stevens.edu",
                        "nicholai", "lesperance")
        results = get_user_answers(db, "nlespera")
    return results


@app.route('/about')
def about():
    return render_template('main.html', file='about.html')


@app.route('/profile')
@login_required
def profile(message: str = ""):
    db = get_db()
    user = flask_login.current_user  # type: User

    module_results = [mlc.get_module_summary(mod, user.id)[0] for mod in mlc.module_questions]
    remaining = [mlc.get_module_summary(mod, user.id)[1] for mod in mlc.module_questions]

    card_completions = {n for n, results in enumerate(module_results) if set(results.values()) == {100}}
    quiz_completions = get_user_completions(db, user.id)

    m1_total_cards = len(mlc.module_questions[0])
    m1_remaining_cards = user.count_remaining_cards(0)

    m2_total_cards = len(mlc.module_questions[1])
    m2_remaining_cards = user.count_remaining_cards(1)

    cardCount = [{"total": m1_total_cards, "remaining": m1_remaining_cards}, {"total":m2_total_cards, "remaining": m2_remaining_cards}]
    print(remaining)

    return render_template('main.html', file='profile.html', user=user, module_results=module_results,
                           level=user.get_level(), card_completions=card_completions, quiz_completions=quiz_completions,
                           message=message, card_count=cardCount, remaining=remaining)


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

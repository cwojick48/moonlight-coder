from flask import Flask
from flask_login import LoginManager

from moonlight_coder.user import User

login_manager = LoginManager()
app = Flask(__name__)
app.secret_key = 'foobar'
login_manager.init_app(app)

import moonlight_coder.views


@app.login_manager.user_loader
def load_user(user_id):
    return User(user_id)

from flask_login import UserMixin

from .db import get_db, get_user, check_if_user_exists


class User(UserMixin):

    def __init__(self, username):
        self.id = username
        self.authenticated = False

        db = get_db()
        if check_if_user_exists(db, username):
            self.authenticated = True

            user_data = get_user(db, username)[0]
            self.first_name = user_data['first_name']
            self.last_name = user_data['last_name']
            self.email = user_data['email']

        else:
            self.first_name = None
            self.last_name = None
            self.email = None

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

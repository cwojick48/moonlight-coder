from flask_login import UserMixin
from numpy.random import permutation
from typing import Optional, Dict

from .config import MODULE_1_DIFFICULTY
from .db import get_db, get_user, check_if_user_exists, get_remaining_questions, get_user_completions


class User(UserMixin):

    def __init__(self, username):
        print('creating user object')
        self.id = username
        self.authenticated = False
        self.module_cards = None  # type: Optional[Dict[int, str]]
        self.module_current_card = dict()

        db = get_db()
        if check_if_user_exists(db, username):
            self.authenticated = True

            user_data = get_user(db, username)[0]
            self.first_name = user_data['first_name']
            self.last_name = user_data['last_name']
            self.email = user_data['email']

            print('loading cards for user...')
            self._load_decks()
            for mod in self.module_cards:
                self.module_current_card[mod] = 0

        else:
            self.first_name = None
            self.last_name = None
            self.email = None

    def _load_decks(self):
        db = get_db()
        if self.module_cards is None:
            self.module_cards = {
                0: get_remaining_questions(db, self.id, max_difficulty=MODULE_1_DIFFICULTY - 1),
                1: get_remaining_questions(db, self.id, min_difficulty=MODULE_1_DIFFICULTY),
            }
            print(f"I loaded these cards: {self.module_cards}")

    def get_next_card(self, module) -> str:
        if self.module_cards is None:
            self._load_decks()

        cards = self.module_cards[module]
        if len(cards) < 1:
            raise Exception("there are no cards left in the deck")
        index = self.module_current_card.setdefault(module, 0)
        if index >= len(cards):
            index = 0

        self.module_current_card[module] = index + 1
        return self.module_cards[module][index]

    def shuffle_deck(self, module):
        self.module_cards[int(module)] = list(permutation(self.module_cards[int(module)]))

    def count_remaining_cards(self, module):
        if self.module_cards is None:
            self._load_decks()

        return len(self.module_cards[module])

    def remove_card(self, module, uuid):
        if self.module_cards is None:
            self._load_decks()

        try:
            self.module_cards[module].remove(uuid)
            self.module_current_card[module] -= 1
        except ValueError:
            print(f"tried to remove {uuid=} that does not exist. {self.module_cards[module]=}")
        except:
            print(self.module_cards)
            raise

    def get_completed_modules(self):
        db = get_db()
        return get_user_completions(db, self.id)

    def get_level(self):
        return len(self.get_completed_modules())

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

from dataclasses import dataclass, asdict
from enum import Enum
from importlib.resources import files, as_file
import json
from pathlib import Path
# from uuid import uuid4, UUID


class CardType(str, Enum):
    SINGLE_CHOICE = 'single'
    MULTIPLE_CHOICE = 'multiple'
    NUMERICAL = 'numerical'

    # would be a great use of 3.10 case statement...
    @staticmethod
    def from_str(string: str):
        if string == 'single':
            return CardType.SINGLE_CHOICE
        elif string == 'multiple':
            return CardType.MULTIPLE_CHOICE
        elif string == 'numerical':
            return CardType.NUMERICAL
        else:
            raise ValueError(f"invalid card type, {string} is not supported")


class QuestionCategory(str, Enum):
    MISC = 'misc'
    OBJECTS = 'objects'
    OPERATORS = 'operators'

    # would be a great use of 3.10 case statement...
    @staticmethod
    def from_str(string: str):
        if string == 'misc':
            return QuestionCategory.MISC
        elif string == 'objects':
            return QuestionCategory.OBJECTS
        elif string == 'operators':
            return QuestionCategory.OPERATORS
        else:
            raise ValueError(f"invalid category, {string} is not supported")


@dataclass
class FlashCard:
    question_type: CardType
    question: str
    answers: list  # length 1 for single/numerical
    incorrect: list  # length 0 for numerical
    category: QuestionCategory
    difficulty: int  # 0-10
    uuid: str

    def __post_init__(self):
        if not len(self.answers):
            raise Exception("must be at least one correct answer")
        if not 0 <= self.difficulty <= 10:
            raise Exception(f"invalid difficulty ({self.difficulty}). must be between 0-10 inclusive")

    @staticmethod
    def from_dict(data: dict):
        data['question_type'] = CardType.from_str(data['question_type'])
        data['category'] = QuestionCategory.from_str(data['category'])
        return FlashCard(**data)


def make_json(cards):
    return json.dumps([asdict(card) for card in cards])


def load_cards(path: Path):
    source = files('moonlight-coder/data').joinpath('questions.json')
    with as_file(source) as test:
        print(test.read_text())

    # data = json.load(path)
    # return [FlashCard.from_dict(card) for card in data]



#--------------------------------------------------------------------------------------#
#----------------------------------EXAMPLES--------------------------------------------#

# q0 = FlashCard(
#     question_type=CardType.SINGLE_CHOICE,
#     question="A Python object is most similar to a:",
#     answers=["noun"],
#     incorrect=['verb', 'adjective', 'union',],
#     category=QuestionCategory.OBJECTS,
#     difficulty=0,
#     uuid=str(uuid4())
# )
#
# q1 = FlashCard(
#     question_type=CardType.MULTIPLE_CHOICE,
#     question="Select the built-in object types:",
#     answers=["int", "str", "list", "set"],
#     incorrect=["vec", "vector", "double",],
#     category=QuestionCategory.OBJECTS,
#     difficulty=1,
#     uuid=str(uuid4()),
# )
#
# q2 = FlashCard(
#     question_type=CardType.NUMERICAL,
#     question="What is the the value of c: \na=5\nb=2\nc=a**b",
#     answers=[25],
#     incorrect=list(),
#     category=QuestionCategory.OPERATORS,
#     difficulty=2,
#     uuid=str(uuid4())
# )
#




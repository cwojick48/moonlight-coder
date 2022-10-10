from dataclasses import dataclass, asdict
from enum import Enum
import json
from uuid import uuid4, UUID


class CardType(Enum):
    SINGLE_CHOICE = 'single'
    MULTIPLE_CHOICE = 'multiple'
    NUMERICAL = 'numerical'


class QuestionCategory(Enum):
    MISC = 'misc'
    OBJECTS = 'objects'
    OPERATORS = 'operators'


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


def make_json(cards):
    return json.dumps([asdict(card) for card in cards])


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




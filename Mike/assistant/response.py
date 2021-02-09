from enum import Enum, auto
from abc import ABCMeta, abstractmethod, abstractproperty
import random
from typing import List
import inspect


class ResponseType(metaclass=ABCMeta):
    def __init__(self, assistant) -> None:
        self.assistant = assistant

    @abstractmethod
    def execute(self,  *args, **kwargs) -> None:
        ...

    @abstractproperty
    def interruptable(self) -> bool:
        ...

    @property
    def responses(self) -> List[str]:
        responses = []
        for cls in inspect.getmro(self.__class__):
            if cls == ResponseType:
                break
            responses += cls._responses
        return responses

    def confirm(self):
        response = random.choice(self.responses)
        if self.interruptable:
            self.assistant.say(response)
        else:
            self.assistant._say(response)


class InterruptableResponse(ResponseType):
    interruptable = True


class ConfirmResponse(ResponseType):
    interruptable = False
    _responses = [
        '. okay boss',
        '. yes chief',
        '. sure',
        '. affirmative',
        '. got it',
    ]

    def execute(self, *args, **kwargs):
        self.confirm()


class InterruptResponse(ConfirmResponse):
    _responses = [
        '. shut up, will i? yes i will',
        '. will i ever shut up?',
        '. guess i\'ll just shut up',
    ]


class Response():

    class Type(Enum):
        GREETING = auto()
        ERROR = auto()
        UNKNOWN = auto()
        CONFIRM = auto()

    def __init__(self, restype) -> None:
        self.type = restype

        # self.response = self.get_response(restype)

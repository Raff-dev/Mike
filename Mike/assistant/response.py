from abc import ABCMeta, abstractclassmethod, abstractmethod, abstractproperty
import random
from typing import List
import inspect

import Mike.assistant.assistant as assistant


class ResponseType(metaclass=ABCMeta):

    @abstractproperty
    def interruptable(self) -> bool:
        ...

    @abstractmethod
    def execute(self,  *args, **kwargs) -> None:
        ...

    @abstractproperty
    def _responses(self) -> List[str]:
        ...

    @property
    def responses(self) -> List[str]:
        responses = []
        for cls in inspect.getmro(self.__class__):
            if cls == ResponseType:
                break
            responses += cls._responses
        return responses


class ConfirmResponse(ResponseType):
    interruptable = False
    _responses = []

    def execute(self, *args, **kwargs):
        response = random.choice(self.responses)
        if self.interruptable:
            assistant.Assistant().say(response)
        else:
            assistant.Assistant()._say(response)


class UnknownResponse(ConfirmResponse):
    _responses = [
        ". sorry i didn't get that",
        ". i didn't catch that",
        ". can't quite figure out what you mean",
        ". this was quite unambigious",
    ]


class ErrorResponse(ConfirmResponse):
    _responses = [
        ". there was an error",
        ". an error comming through",
        ". i have come across a problem analysing your request",
    ]


class InterruptResponse(ConfirmResponse):
    _responses = [
        ". okay boss",
        ". yes chief",
        ". sure",
        ". affirmative",
        ". got it",
        ". shut up, will i? yes i will",
        ". will i ever shut up?",
        ". guess i'll just shut up",
    ] + ['']*20


class WakeUpResponse(ConfirmResponse):
    _responses = [
        ". yes chief?",
        ". ready for action",
        ". how can i help?",
        ". yes boss?"
    ]


class TerminateResponse(ConfirmResponse):
    _responses = [
        ". see you next time",
        ". power off",
        ". Mike is shitting down",
        ". executing protocol sleeperoo"
    ]

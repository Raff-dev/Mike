from __future__ import annotations
from typing import Iterable, List, Tuple, Union
import inspect
import abc

import Mike.assistant.response as responses
import Mike.assistant.assistant as assistant


class ActionMeta(abc.ABCMeta):
    actions = set()

    def __new__(cls, *args, **kwargs):
        klass = super(ActionMeta, cls).__new__(cls, *args, **kwargs)
        if not inspect.isabstract(klass) and klass is not ActionMeta:
            ActionMeta.actions.add(klass)
        return klass


class Action(metaclass=ActionMeta):

    @abc.abstractproperty
    def key_words(self) -> List[Union[str, Tuple[str]]]:
        ...

    @abc.abstractmethod
    def execute(self) -> None:
        ...

    @classmethod
    def match(cls, text) -> bool:
        print(cls.key_words)
        for key in cls.key_words:
            if isinstance(key, tuple) and key <= text:
                return True
            if isinstance(key, str) and key in text:
                return True
        return False

    @staticmethod
    def get_matching_actions(text) -> List[Action]:
        return [action for action in ActionMeta.actions if action.match(text)]


class ResponseAction(Action):
    key_words = []

    @abc.abstractproperty
    def response(self):
        ...

    def execute(self):
        self.response().execute()


class UnknownAction(ResponseAction):
    response = responses.UnknownResponse


class ErrorAction(ResponseAction):
    response = responses.ErrorResponse


class WakeUpAction(ResponseAction):
    key_words = ['mike']
    response = responses.WakeUpResponse


class InterruptAction(ResponseAction):
    key_words = ['ok', 'okay', 'enough', 'shut up', 'stop', 'nevermind']
    response = responses.InterruptResponse


class ShutDownAction(Action):
    key_words = ['shut down', 'terminate']

    def execute(self):
        assistant.Assistant().terminate()
        responses.TerminateResponse().execute()


class SearchAction(Action):
    key_words = ['what', 'search']

    def execute(self):
        responses.WakeUpResponse().execute()


class LocationAction(Action):
    key_words = ['find', 'locate']

    def execute(self):
        responses.WakeUpResponse().execute()


class PlaybackAction(Action):
    key_words = ['stop', 'play', 'resume', 'quiet', 'turn down', 'turn up']

    def execute(self):
        responses.InterruptResponse().execute()

from __future__ import annotations
from Mike.assistant.response import ErrorResponse
import abc
import time

from speech_recognition import UnknownValueError, WaitTimeoutError, RequestError
import Mike.assistant.action as actions


class State(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def handle_input(self, text, *args, **kwargs) -> State:
        ...

    @abc.abstractmethod
    def handle_exception(self, exception) -> State:
        ...


class DormantState(State):

    def handle_input(self, text, *args, **kwargs) -> State:
        print(f'text: {text}')
        matches = actions.Action.get_matching_actions(text)
        names = [match.__name__ for match in matches]
        print(f'matched: {names}')
        if actions.WakeUpAction in matches:

            if matches == [actions.WakeUpAction]:
                actions.WakeUpAction().execute()
                return AwakeState()

            matches.remove(actions.WakeUpAction)
            action = matches[0]
            action().execute()
            return ResponseState()
        return DormantState()

    def handle_exception(self, exception):
        return self


class AwakeState(State):
    dormant_delay = 10

    def __init__(self):
        self.enter = time.time()

    def handle_input(self, text, *args, **kwargs) -> State:
        if time.time() - self.enter > self.dormant_delay:
            return DormantState().handle_input(text, *args, **kwargs)

        matches = actions.Action.get_matching_actions(text)
        if matches:
            if matches == [actions.WakeUpAction]:
                actions.WakeUpAction().execute()
                return AwakeState()
            else:
                if actions.WakeUpAction in matches:
                    matches.remove(actions.WakeUpAction)
                action = matches[0]
                action().execute()
                return ResponseState()

        actions.UnknownAction().execute()
        return AwakeState()

    def handle_exception(self, exception) -> State:
        if time.time() - self.enter > self.dormant_delay:
            return DormantState().handle_exception(exception)
        if isinstance(exception, UnknownValueError):
            actions.UnknownAction().execute()
        else:
            actions.ErrorAction().execute()
        return self


class ResponseState(AwakeState):
    pass

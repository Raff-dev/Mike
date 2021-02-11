from speech_recognition import UnknownValueError, RequestError, WaitTimeoutError

import Mike.assistant.response as responses
import Mike.assistant.action as actions


class ActionManager:

    def evaluate(self, text):
        matches = self.get_matching_actions(text)
        names = [match.__name__ for match in matches]
        print(f'matched: {names}')
        if not matches:
            responses.UnknownResponse().execute()
        else:
            matches[0].execute(text)

    def get_matching_actions(self, text):
        return [action for action in actions.ActionMeta.actions if action.match(text)]

    def handle_exception(self, exception: Exception) -> None:
        if isinstance(exception, UnknownValueError):
            responses.UnknownResponse().execute()
        elif isinstance(exception, RequestError):
            responses.ErrorResponse().execute()
        elif isinstance(exception, WaitTimeoutError):
            return
        else:
            raise exception

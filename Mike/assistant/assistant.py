import multiprocessing
import pyttsx3
import speech_recognition as sr
from speech_recognition import UnknownValueError, WaitTimeoutError, RequestError

from Mike.utils.Singleton import Singleton
import Mike.assistant.response as responses
import Mike.assistant.action as actions
import Mike.assistant.state as state


class Assistant(metaclass=Singleton):
    james = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_enAU_JamesM'

    def __init__(self) -> None:
        self._speaker = pyttsx3.init()
        self._recognizer = sr.Recognizer()
        self._state = state.DormantState()
        self._running = True
        self.set_up()

    def set_up(self):
        self._speaker.setProperty('rate', 200)
        self._speaker.setProperty('voice', self.james)

    def terminate(self):
        self._running = False

    @staticmethod
    def _say(text):
        speaker = Assistant()._speaker
        speaker.say(text)
        speaker.runAndWait()

    def say(self, text):
        process = multiprocessing.Process(target=Assistant._say, args=(text,))
        process.start()
        while process.is_alive():
            if self.detect(actions.InterruptAction.key_words):
                process.terminate()
                process.join()
                responses.InterruptResponse(self).execute()

    def listen(self):
        with sr.Microphone() as source:
            while self._running:
                audio = self._recognizer.listen(source)
                try:
                    text = self._recognizer.recognize_google(audio).lower()
                    print(text)
                    self._state = self._state.handle_input(text)
                except (UnknownValueError, WaitTimeoutError, RequestError) as exception:
                    print(exception)
                    self._state = self._state.handle_exception(exception)

    def detect(self, command):
        with sr.Microphone() as source:
            try:
                audio = self._recognizer.listen(source, phrase_time_limit=1)
                data = self._recognizer.recognize_google(audio)
                return any(keyword in data for keyword in command)
            except Exception:
                return False

    def test(self):
        for _ in range(5):
            responses.WakeUpResponse().execute()

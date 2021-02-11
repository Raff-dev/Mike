import multiprocessing
import speech_recognition as sr
import pyttsx3

from Mike.utils.Singleton import Singleton
import Mike.assistant.actionmanager as actionmanager
import Mike.assistant.response as responses
import Mike.assistant.action as actions


class Assistant(metaclass=Singleton):
    james = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_enAU_JamesM'

    def __init__(self) -> None:
        self._speaker = pyttsx3.init()
        self._recognizer = sr.Recognizer()
        self._action_manager = actionmanager.ActionManager()
        self._awake = False
        self._running = True
        self.set_up()

    def set_up(self):
        self._speaker.setProperty('rate', 200)
        self._speaker.setProperty('voice', self.james)

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
                audio = self._recognizer.listen(source, timeout=10)
                self.recognize(audio)

    def recognize(self, audio):
        try:
            text = self._recognizer.recognize_google(audio).lower()
            print(text)
            if not self._awake and not actions.WakeUpAction.match(text):
                return
            self._action_manager.evaluate(text)
        except Exception as exception:
            if self._awake:
                self._action_manager.handle_exception(exception)
                self._awake = False

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

    def test_listen(self):
        with sr.Microphone() as source:
            while True:
                try:
                    audio = self._recognizer.listen(source)
                    text = self._recognizer.recognize_google(audio)
                    print(text)
                except sr.UnknownValueError:
                    responses.UnknownResponse().execute()
                except sr.RequestError:
                    responses.ErrorResponse().execute()

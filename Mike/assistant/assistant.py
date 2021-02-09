from os import stat
import sys
from pathlib import Path
import multiprocessing
import speech_recognition as sr
import pyttsx3

if __package__ is None:
    DIR = Path(__file__).resolve().parent
    sys.path.insert(0, str(DIR.parent))
    __package__ = DIR.name

from utils.Singleton import Singleton
from response import Response, ConfirmResponse, InterruptResponse
from command.command import Command


class Assistant(metaclass=Singleton):
    james = 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_enAU_JamesM'

    def __init__(self) -> None:
        self.speaker = pyttsx3.init()
        self.speaker.setProperty('rate', 200)
        self.speaker.setProperty('voice', self.james)
        self.recognizer = sr.Recognizer()
        self.running = True

    @staticmethod
    def _say(text):
        speaker = Assistant().speaker
        speaker.say(text)
        speaker.runAndWait()

    def say(self, text):
        process = multiprocessing.Process(target=Assistant._say, args=(text,))
        process.start()
        while process.is_alive():
            if self.detect(Command.INTERRUPT):
                process.terminate()
                process.join()
                InterruptResponse(self).execute()

    def listen(self):
        with sr.Microphone() as source:
            while self.running:
                audio = self.recognizer.listen(source)
                response = self.recognize(audio)
                response.execute(self)
                self.awaken = False

    def recognize(self, audio):
        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return Response(Response.Type.UNKNOWN)
        except sr.RequestError:
            return Response(Response.Type.ERROR)

    def detect(self, command):
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, phrase_time_limit=1)
                data = self.recognizer.recognize_google(audio)
                return any(keyword in data for keyword in command)
            except Exception:
                return False

    def test(self):
        for _ in range(5):
            InterruptResponse(self).execute()


if __name__ == '__main__':
    text = """
    The number 42 is, in The Hitchhiker's Guide to the Galaxy by Douglas Adams, the "Answer to the Ultimate Question of Life, the Universe, and Everything", calculated by an enormous supercomputer named Deep Thought over a period of 7.5 million years. Unfortunately, no one knows what the question is. Thus, to calculate the Ultimate Question, a special computer the size of a small planet was built from organic components and named "Earth". The Ultimate Question "What do you get when you multiply six by nine"[26] was found by Arthur Dent and Ford Prefect in the second book of the series, The Restaurant at the End of the Universe. This appeared first in the radio play and later in the novelization of The Hitchhiker's Guide to the Galaxy. The fact that Adams named the episodes of the radio play "fits", the same archaic title for a chapter or section used by Lewis Carroll in The Hunting of the Snark, suggests that Adams was influenced by Carroll's fascination with and frequent use of the number. The fourth book in the series, the novel So Long, and Thanks for All the Fish, contains 42 chapters. According to the novel Mostly Harmless, 42 is the street address of Stavromula Beta. In 1994 Adams created the 42 Puzzle, a game based on the number 42.
    """
    # Assistant().say()
    Assistant().test()

    l1 = 'asd'
    l2 = 'asd'
    l3 = [*a for a in [l1, l2]]

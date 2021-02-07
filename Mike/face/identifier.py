from typing import Dict
import os
from PIL import Image

import cv2
import face_recognition
import numpy as np

from face import Face
from video import capture
from contextlib import contextmanager


class Identifier:
    def __init__(self, color=[0, 255, 0]) -> None:
        self.color = color
        self.thickness = 1
        self.tolerance = 0.6
        self.label_config = {
            'fontFace': cv2.FONT_HERSHEY_SIMPLEX,
            'fontScale': 0.5,
            'color': (200, 200, 200),
        }

    def frame(self, image, location, name=None):
        """creates a frame around a face with a name label"""
        top, right, bot, left = location
        color = (10, 220, 10) if name else (220, 10, 10)

        cv2.rectangle(image, (top, left), (bot, right), color)
        cv2.putText(image, name, (bot, left), **self.label_config)

    def run(self, *known_faces):
        """
        Captures video images, detects faces, and marks
        known_faces:
        """
        known_encodings = list(map(lambda face: face.encoding, known_faces))

        for image in capture():
            locations = face_recognition.face_locations(image)
            encodings = face_recognition.face_encodings(image, locations)

            for location, encoding in zip(locations, encodings):
                results = face_recognition.compare_faces(known_encodings, encoding[0], self.tolerance)
                if True in results:
                    match = known_faces[results.index(True)]
                    self.frame(image, location, match.name)
                else:
                    self.frame(image, location)


if __name__ == '__main__':
    identifier = Identifier()
    faces = identifier.get_known()
    identifier.load(faces)
    identifier.run()

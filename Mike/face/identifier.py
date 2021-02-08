from typing import List
from itertools import compress
import time

import cv2
import face_recognition as fr
from PIL import Image


from face import Face
from video import capture
from loader import Loader


class Identifier:
    RED = (200, 10, 10)
    GREEN = (10, 200, 10)
    UNKNOWN = 'Unknown'

    def __init__(self) -> None:
        self.record_time = 20
        self.tolerance = 0.6
        self.label_config = {
            'fontFace': cv2.FONT_HERSHEY_SIMPLEX,
            'fontScale': 0.5,
            # 'color': (200, 200, 200),
        }

    def frame(self, image, location, name=None) -> None:
        """
        creates a frame around a face with a name label
        image: image to draw the frame to
        name:  name of the recognised face
        """
        top, right, bot, left = location
        color = (10, 220, 10) if name else (220, 10, 10)
        name = name or self.UNKNOWN
        cv2.rectangle(image, (top, right), (bot, left), color)
        cv2.putText(image, name, (bot, left), color=(200, 200, 200), **self.label_config)

    def run(self, known_faces: List[Face]) -> None:
        """
        Captures video images, detects faces, and marks them
        known_faces: list of faces to identify
        """
        known_encodings = list(map(lambda face: face.encoding, known_faces))

        for image in capture():

            locations = fr.face_locations(image)
            encodings = fr.face_encodings(image, locations)

            for displayed, (location, encoding) in enumerate(zip(locations, encodings)):
                results = [
                    True in fr.compare_faces(known_encoding, encoding, self.tolerance)
                    for known_encoding in known_encodings
                ]
                matches = list(compress(known_faces, results))
                recognised = len(matches) > 0

                text_location = (20, 20*(displayed+1))
                text = f'{matches[0].name}: {len(matches)}' if recognised else self.UNKNOWN
                color = self.GREEN if recognised else self.RED
                cv2.putText(image, text, text_location, color=color, **self.label_config)

    def identify(self, encoding):
        results = [
            sum(True in fr.compare_faces([known], encoding, self.tolerance)
                for known in face.encodings)
            for face in self.faces
        ]
        matches = list(compress(self.faces, results))
        return [match.name for match in matches] or self.UNKNOWN

    def record(self, name) -> Face:
        face = Face(name)
        self.faces = [face]
        start_time = None

        for image in capture():
            encodings = fr.face_encodings(image)
            assert len(encodings) < 2, "There has been more than one face detected"

            if encodings:
                start_time = start_time or time.time()

                if self.identify(encodings[0]) == self.UNKNOWN:
                    filename = f'{name}{len(face.entries)}'
                    face.add(filename, encodings[0])

                cv2.putText(image, 'Active', (20, 20), color=(20, 200, 20), **self.label_config)
            else:
                cv2.putText(image, 'Inactive', (20, 20), color=(20, 20, 200), **self.label_config)

            cv2.putText(image, f'Face entries: {len(face.entries)}', (20, 40), color=(200, 20, 20), **self.label_config)
            if start_time:
                recording = time.time() - start_time
                cv2.putText(image, f'Time recording: {recording:.2f}', (20, 60), color=(200, 20, 20), **self.label_config)

        return face


if __name__ == '__main__':
    loader = Loader()
    faces = loader.load()
    identifier = Identifier()
    identifier.run(faces)
    # face = identifier.record('Raff')
    # loader.dump(face)

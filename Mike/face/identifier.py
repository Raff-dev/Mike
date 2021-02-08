from typing import List
from itertools import compress
import time

import cv2
import face_recognition as fr
from PIL import Image


from face import Face
from video import capture
from loader import FaceLoader


class FaceIdentifier:
    RED = (10, 10, 200)
    GREEN = (10, 200, 10)
    BLUE = (200, 10, 10)
    WHITE = (200, 200, 200)

    UNKNOWN = 'Unknown'

    def __init__(self) -> None:
        self.record_time = 20
        self.tolerance = 0.6
        self.record_tolerance = 0.5
        self.label_config = {
            'fontFace': cv2.FONT_HERSHEY_SIMPLEX,
            'fontScale': 0.5,
        }

    def frame(self, image, location, label=None) -> None:
        """
        creates a frame around a face with a name label
        image: image to draw the frame to
        label:  frame label
        """
        top, right, bot, left = location
        color = self.GREEN if label else self.RED
        label = label or self.UNKNOWN
        cv2.rectangle(image, (left, top), (right, bot), color)
        cv2.putText(image, label, (left, bot+10), color=self.WHITE, **self.label_config)

    def identify(self, encoding, tolerance=None):
        results = [
            sum(True in fr.compare_faces([entry.encoding], encoding, tolerance or self.tolerance)
                for entry in face)
            for face in self.faces
        ]
        matches = list(compress(self.faces, results))
        entries_matched = [results[self.faces.index(match)] for match in matches]
        return [face for face in matches] or self.UNKNOWN, entries_matched

    def run(self, known_faces: List[Face]) -> None:
        """
        Captures video images, finds and frames detected faces
        known_faces: list of faces to identify
        """
        self.faces = known_faces
        for image in capture():
            locations = fr.face_locations(image)
            encodings = fr.face_encodings(image, locations)

            for location, encoding in zip(locations, encodings):
                faces, counts = self.identify(encoding)
                if faces == self.UNKNOWN:
                    text = self.UNKNOWN
                else:
                    text = f'{faces[0].name} matched: {counts[0]} of {len(faces[0].entries)}'

                self.frame(image, location, text)

    def record(self, name) -> Face:
        face = Face(name)
        self.faces = [face]
        start_time = None

        for image in capture():
            encodings = fr.face_encodings(image)
            assert len(encodings) < 2, "There has been more than one face detected"

            if encodings:
                start_time = start_time or time.time()

                if self.identify(encodings[0], self.record_tolerance) == self.UNKNOWN:
                    filename = f'{name}{len(face.entries)}'
                    face.add(filename, encodings[0])

                cv2.putText(image, 'Active', (20, 20), color=self.GREEN, **self.label_config)
            else:
                cv2.putText(image, 'Inactive', (20, 20), color=self.RED, **self.label_config)

            cv2.putText(image, f'Face entries: {len(face.entries)}', (20, 40), color=self.BLUE, **self.label_config)
            if start_time:
                recording = time.time() - start_time
                cv2.putText(image, f'Time recording: {recording:.2f}', (20, 60), color=self.BLUE, **self.label_config)

        return face


if __name__ == '__main__':
    loader = FaceLoader()
    identifier = FaceIdentifier()
    faces = loader.load('Raff')
    print(faces)
    identifier.run(faces)
    # face = identifier.record('Raff')
    # loader.dump(face)

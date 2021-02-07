import os
import pickle
from typing import List
import face_recognition

from face import Face
from video import capture


class Loader:
    DATA_DIR = './Mike/face/data'
    PICKLE_DIR = DATA_DIR + '/pickle'

    @staticmethod
    def get_faces(images_dir: str) -> List[Face]:
        """
        Finds faces on the images, returns list of Face objects
        images_dir: directory consisting of name/[,filename] image files
        """
        faces = []

        for name in os.listdir(images_dir):
            for filename in os.listdir(f'{images_dir}/{name}'):
                image = face_recognition.load_image_file(f'{images_dir}/{name}/{filename}')
                location = face_recognition.face_locations(image)

                if location:
                    encoding = face_recognition.face_encodings(image, location)
                    filename = os.splitext(filename)[0]
                    face = Face(name, filename, location, encoding)
                    faces.append(face)
        return faces

    def record(self):
        for image in capture(max_frames=50):
            raise NotImplementedError()

    def dump(self, *faces, pickle_dir=None) -> None:
        """pickles Faces"""
        pickle_dir = pickle_dir or self.PICKLE_DIR
        for face in faces:
            try:
                os.mkdir(f'{pickle_dir}/{face.name}')
            except FileExistsError:
                pass
            with open(f'{pickle_dir}/{face.name}/{face.filename}.pkl', 'wb') as output_file:
                pickle.dump(face, output_file)

    def load(self, pickle_dir=None) -> List[Face]:
        """loads pickled faces to list"""
        pickle_dir = pickle_dir or self.PICKLE_DIR
        faces = []
        for name in os.listdir(pickle_dir):
            for filename in os.listdir(f'{pickle_dir}/{name}'):
                with open(f'{pickle_dir}/{name}/{filename}.pkl', 'rb') as input_file:
                    face = pickle.load(input_file)
                    faces.append(face)
        return faces


if __name__ == '__main__':
    loader = Loader()
    faces = loader.get_faces(Loader.PICKLE_DIR + '/images')
    loader.dump(faces)

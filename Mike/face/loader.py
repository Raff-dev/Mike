import os
import pickle
from typing import List
import face_recognition

from face import Face
from video import capture


class FaceLoader:
    DATA_DIR = './Mike/face/data'
    IMAGES_DIR = DATA_DIR + '/images'
    PICKLE_DIR = DATA_DIR + '/pickle'

    @staticmethod
    def get_faces(images_dir: str) -> List[Face]:
        """
        Finds faces on the images, returns list of Face objects
        images_dir: directory consisting of name/[,filename] image files
        """
        faces = []
        for name in os.listdir(images_dir):
            faces.append(Face(name))
            for filename in os.listdir(f'{images_dir}/{name}'):
                image = face_recognition.load_image_file(f'{images_dir}/{name}/{filename}')
                location = face_recognition.face_locations(image)

                if location:
                    encoding = face_recognition.face_encodings(image, location)
                    filename = os.path.splitext(filename)[0]
                    faces[-1].add(filename, encoding, location)
        return faces

    def dump(self, *faces, pickle_dir=None) -> None:
        """pickles Faces"""
        pickle_dir = pickle_dir or self.PICKLE_DIR
        for face in faces:
            with open(f'{pickle_dir}/{face.name}.pkl', 'wb') as output_file:
                pickle.dump(face, output_file)

    def load(self, names=None, pickle_dir=None) -> List[Face]:
        """loads pickled Faces to list"""
        pickle_dir = pickle_dir or self.PICKLE_DIR
        faces = []
        for name in os.listdir(pickle_dir):
            if names and os.path.splitext(name)[0] not in names:
                continue
            with open(f'{pickle_dir}/{name}', 'rb') as input_file:
                face = pickle.load(input_file)
                faces.append(face)
        return faces


if __name__ == '__main__':
    loader = FaceLoader()
    faces = loader.get_faces(FaceLoader.IMAGES_DIR)
    loader.dump(*faces)
    # faces = loader.load()

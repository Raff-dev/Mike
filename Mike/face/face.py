class Face:
    def __init__(self, name, filename, locations, encoding, image=None) -> None:
        self.name = name
        self.filename = filename
        self.locations = locations
        self.encoding = encoding
        self.image = image

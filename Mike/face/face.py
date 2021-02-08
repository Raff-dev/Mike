
class Face:

    class FaceEntry:
        __slots__ = ['filename', 'location', 'encoding', 'image']

        def __init__(self, filename, encoding, location=None,  image=None) -> None:
            self.filename = filename
            self.encoding = encoding
            self.location = location
            self.image = image

    def __init__(self, name) -> None:
        self.name = name
        self.entries = []

    def add(self, filename, encoding, location=None):
        self.entries.append(self.FaceEntry(filename, encoding, location))

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        singular = name.removesuffix('s')
        if singular in self.FaceEntry.__slots__:
            mlist = list(map(lambda entry: getattr(entry, singular), self.entries))
            return mlist
        else:
            raise AttributeError

    def __iter__(self):
        for entry in self.entries:
            yield entry

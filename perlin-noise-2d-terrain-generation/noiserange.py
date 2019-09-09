
class NoiseRange:
    """
    Defines where a range begins and ends.

    Also contains a helpful name tag eg. water, mountain, etc.
    """
    def __init__(self, name, threshold):
        self.name = name
        self.threshold = threshold

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'name', self.name
        yield 'threshold', self.threshold

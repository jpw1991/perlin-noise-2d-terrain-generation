
class NoiseRange:
    """
    Defines where a range begins and ends and also which character
    it should use to display and its color.

    Also contains a helpful name tag eg. water, mountain, etc.
    """
    def __init__(self, name, threshold, character):
        self.name = name
        self.threshold = threshold
        self.character = character

    def print(self):
        # print with end='' to stop automatic newline
        print(self.character, end='')

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'name', self.name
        yield 'threshold', self.threshold
        yield 'character', self.character

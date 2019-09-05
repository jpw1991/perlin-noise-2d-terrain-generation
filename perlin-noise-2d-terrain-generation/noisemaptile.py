
class NoiseMapTile:
    """
    A tile in a noise map. Consists of an X and Y position
    as well as a noise value that can be interpreted however
    you like.

    A low noise value = low terrain, a high one = high terrain.
    """

    def __init__(self, x, y, noise_value):
        self.x = x
        self.y = y
        self.noise_value = noise_value

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'x', self.x
        yield 'y', self.y
        yield 'noise_value', self.noise_value


import sys
import uuid # for map naming
import argparse # for nice argument parsing
import colorama, termcolor # for color print output
import json
import click # for simple y/n prompt
from noise import pnoise2, snoise2


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


class NoiseMap:
    """
    A map of NoiseMapTiles.
    """
    def __init__(self, width, height, ranges, tiles=[]):
        """
        ranges = the number ranges for the different kinds of tiles
        eg. water 0.1, sand 0.25, etc as a dictionary
        """
        self.width = width
        self.height = height
        self.ranges = ranges
        self.tiles = tiles
    
    def append(self, tiles):
        self.tiles += tiles
    
    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'width', self.width
        yield 'height', self.height
        yield 'ranges', [dict(noise_range) for noise_range in self.ranges]
        yield 'tiles', [dict(tile) for tile in self.tiles]

    def display(self):
        """
        Print the map to the terminal.
        """
        def chunks(target_list, chunk_size):
            """
            Break a big list into smaller lists.
            """
            for i in range(0, len(target_list), chunk_size):
                yield target_list[i:i + chunk_size]
        
        colorama.init()
        
        # break the tiles into lines and print each tile with its range character
        lines = chunks(self.tiles, self.width)
        for line in lines:
            for tile in line:
                for noise_range in self.ranges:
                    if tile.noise_value <= noise_range.threshold:
                        noise_range.print()
                        break

                # print uncolored black after the last character to stop color run off
                print('', end='')
                    
            print('') # print new line to finish with

    def save(self, file_name):
        """
        Save the map as JSON to a file.
        """
        with open(file_name, 'w', encoding='utf8') as file:
            json.dump(dict(self), file, indent=4)
            file.close()

    @classmethod
    def load(cls, file_name) -> 'NoiseMap':
        """ Load an existing JSON map """
        with open(file_name, 'r', encoding='utf8') as file:
            data = json.load(file)

            # parse map info
            width = data['width']
            height = data['height']

            # parse tiles
            #tiles = data['tiles']
            tiles = [NoiseMapTile(x, y, noise_value) for x, y, noise_value in data['tiles']]
            #for tile in tiles:
            #    pass

            # parse noise ranges
            ranges = [NoiseRange(name, threshhold, termcolor.colored(char)) for name, threshhold, char in data['ranges']]

            file.close()

            return cls(width, height, ranges, tiles)


class NoiseRange:
    """
    Defines where a range begins and ends and also which character
    it should use to display and its color.

    Also contains a helpful name tag eg. water, mountain, etc.
    """
    def __init__(self, name, threshold, character_termcolor):
        self.name = name
        self.threshold = threshold
        self.character_termcolor = character_termcolor

    def print(self):
        # print with end='' to stop automatic newline
        print(self.character_termcolor, end='')

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'name', self.name
        yield 'threshold', self.threshold
        yield 'character_termcolor', self.character_termcolor


def main():
    parser = argparse.ArgumentParser(description='Generate or view a noise map')
    
    parser.add_argument('-v', '--view', help="Display an existing map.", type=str)
    parser.add_argument('-f', '--file', help="File name to generate", type=str, default='noise_map_%s.json' % uuid.uuid4())
    parser.add_argument('-o', '--octaves', help="Octaves used for generation.", type=int, default=8)
    parser.add_argument('--width', help="Map width to generate.", type=int, default=164)
    parser.add_argument('--height', help="Map height to generate.", type=int, default=32)
    parser.add_argument('--frequency', help="Noise frequency.", type=float, default=4.0)
    parser.add_argument('--algorithm', choices=['perlin', 'simplex'], help="Noise algorithm.", type=str, default='perlin')
    
    parser.add_argument('--water', help="Height level of the water", type=float, default=0.02)
    parser.add_argument('--shallowwater', help="Height level of the shallow water", type=float, default=0.05)
    parser.add_argument('--sand', help="Height level of the sand", type=float, default=0.1)
    parser.add_argument('--land', help="Height of normal grass/land/forest", type=float, default=0.25)
    parser.add_argument('--mountain', help="Height of mountains", type=float, default=0.3)
    parser.add_argument('--hugemountain', help="Height of huge mountains", type=float, default=0.4)

    args = parser.parse_args()

    noise_map = None

    if args.view is not None:
        # load existing
        noise_map = NoiseMap.load(args.view)
        noise_map.display()

    else:
        # generate
        file = args.file
        octaves = args.octaves
        width = args.width
        height = args.height
        frequency = args.frequency * octaves
        algorithm = args.algorithm
        
        ranges = [
            NoiseRange('water', args.water, termcolor.colored('≈', 'blue', 'on_blue', attrs=['dark'])),
            NoiseRange('shallowwater', args.shallowwater, termcolor.colored('~', 'blue', 'on_blue')),
            NoiseRange('sand', args.sand, termcolor.colored('.', 'white', 'on_yellow')),
            NoiseRange('land', args.land, termcolor.colored('.', 'white', 'on_green')),
            NoiseRange('mountain', args.mountain, termcolor.colored('^', 'grey', 'on_white')),
            NoiseRange('hugemountain', args.hugemountain, termcolor.colored('∆', 'grey', 'on_white'))
        ]
        
        print('file:\t\t%s\noctaves:\t%s\nwidth:\t\t%d\nheight:\t\t%d\nfrequency:\t%f (octaves * '
              'frequency)\nalgorithm:\t%s\n' % (file, octaves, width, height, frequency, algorithm))

        noise_map = NoiseMap(width, height, ranges)
        
        for y in range(height):
            row = []
            for x in range(width):
                noise_value = None
                if algorithm == 'perlin':
                    noise_value = pnoise2(x / frequency, y / frequency, octaves)
                elif algorithm == 'simplex':
                    noise_value = snoise2(x / frequency, y / frequency, octaves)
                row += [NoiseMapTile(x, y, noise_value)]
            noise_map.append(row)
    
        noise_map.display()
        
        if click.confirm('Save map?', default=True):
            noise_map.save(file)


if __name__ == "__main__":
    sys.exit(main())


import colorama
import json
import termcolor
import enum

from noise import pnoise2, snoise2
from noisemaptile import NoiseMapTile
from noiserange import NoiseRange


class NoiseMapBiome(enum.Enum):
    OCEAN = 1                       # ♒︎ on_blue
    SHALLOWS = 2                    # ~ on_cyan
    BEACH = 3                       # ⋯ on_yellow
    SCORCHED = 4                    # on_red
    BARE = 5                        # on_grey
    TUNDRA = 6                      # ⩊ on_grey
    TEMPERATE_DESERT = 7            #
    SHRUBLAND = 8                   # ⋎ on_green
    GRASSLAND = 9                   #   on_green
    TEMPERATE_DECIDUOUS_FOREST = 10 # ♣︎ on_green
    TEMPERATE_RAIN_FOREST = 11      # ♈︎ on_green
    SUBTROPICAL_DESERT = 12         #   on_yellow
    TROPICAL_SEASONAL_FOREST = 13   # ♠︎ on green
    TROPICAL_RAIN_FOREST = 14       # ♈︎ on_green
    SNOW = 15                       # ∷ on_white
    TAIGA = 16                      # ⨇ on_green

def get_character(value):
    character = None
    if value == NoiseMapBiome.OCEAN:
        character = termcolor.colored(' ', 'cyan', 'on_blue')
    elif value == NoiseMapBiome.SHALLOWS:
        character = termcolor.colored(' ', 'blue', 'on_cyan')
    elif value == NoiseMapBiome.BEACH:
        character = termcolor.colored('b', 'grey', 'on_yellow')
    elif value == NoiseMapBiome.SCORCHED:
        character = termcolor.colored(' ', 'grey', 'on_red')
    elif value == NoiseMapBiome.BARE:
        character = termcolor.colored(' ', 'grey', 'on_grey')
    elif value == NoiseMapBiome.TUNDRA:
        character = termcolor.colored('t', 'white', 'on_grey')
    elif value == NoiseMapBiome.TEMPERATE_DESERT:
        character = termcolor.colored('d', 'grey', 'on_yellow')
    elif value == NoiseMapBiome.SHRUBLAND:
        character = termcolor.colored('s', 'grey', 'on_green')
    elif value == NoiseMapBiome.GRASSLAND:
        character = termcolor.colored(' ', 'grey', 'on_green')
    elif value == NoiseMapBiome.TEMPERATE_DECIDUOUS_FOREST:
        character = termcolor.colored(chr(2263), 'white', 'on_green')#f'♧', 'white', 'on_green')
    elif value == NoiseMapBiome.TEMPERATE_RAIN_FOREST:
        character = termcolor.colored('r', 'white', 'on_green')
    elif value == NoiseMapBiome.SUBTROPICAL_DESERT:
        character = termcolor.colored(' ', 'white', 'on_yellow')
    elif value == NoiseMapBiome.TROPICAL_SEASONAL_FOREST:
        character = termcolor.colored('f', 'grey', 'on_green')
    elif value == NoiseMapBiome.TROPICAL_RAIN_FOREST:
        character = termcolor.colored('f', 'cyan', 'on_green')
    elif value == NoiseMapBiome.SNOW:
        character = termcolor.colored('s', 'grey', 'on_white')
    elif value == NoiseMapBiome.TAIGA:
        character = termcolor.colored('i', 'grey', 'on_green')
    return character


class NoiseMap:
    """
    A map of NoiseMapTiles.
    """

    def __init__(self, width, height, noise_ranges=[], tiles=[], moisture_map=None):
        """
        ranges = the number ranges for the different kinds of tiles
        eg. water 0.1, sand 0.25, etc as a dictionary
        """
        self.width = width
        self.height = height
        self.noise_ranges = noise_ranges
        self.tiles = tiles
        self.moisture_map = moisture_map
        self.algorithm = None
        self.frequency = None
        self.octaves = None

        # create a dictionary from the noise ranges list for quick lookups later
        self.noise_range_dict = {}
        for noise_range in noise_ranges:
            self.noise_range_dict[noise_range.name] = noise_range

    def generate(self, algorithm, frequency, octaves):
        """ Generate the noise map """
        self.algorithm = algorithm
        self.frequency = frequency
        self.octaves = octaves

        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                noise_value = None
                if algorithm == 'perlin':
                    noise_value = pnoise2(x / frequency, y / frequency, octaves)
                elif algorithm == 'simplex':
                    noise_value = snoise2(x / frequency, y / frequency, octaves)
                row += [NoiseMapTile(x, y, noise_value)]
            self.tiles += row

    def biome(self, elevation, moisture):
        """ From the elevation & the moisture, determine the biome of the tile. """
        # if elevation <= self.noise_range_dict['water'].threshold or elevation <= self.noise_range_dict['shallowwater'].threshold:
        #    return NoiseMapBiome.OCEAN
        # if elevation <= self.noise_range_dict['sand'].threshold:
        #    return NoiseMapBiome.BEACH
        #
        #if elevation > self.noise_range_dict['hugemountain'].threshold:
        #    if moisture < 0.1:
        #        return NoiseMapBiome.SCORCHED
        #    elif moisture < 0.2:
        #        return NoiseMapBiome.BARE
        #    elif moisture < 0.5:
        #        return NoiseMapBiome.TUNDRA
        #    return NoiseMapBiome.SNOW
        #
        #if elevation > self.noise_range_dict['mountain'].threshold:
        #    if moisture < 0.33:
        #        return NoiseMapBiome.TEMPERATE_DESERT
        #    elif moisture < 0.66:
        #        return NoiseMapBiome.SHRUBLAND
        #    return NoiseMapBiome.TAIGA

        if elevation >= self.noise_range_dict['mountain'].threshold:
            return None # don't handle it

        if elevation >= self.noise_range_dict['land'].threshold and elevation < self.noise_range_dict['mountain'].threshold:
            if moisture < 0.06:#0.16:
                return NoiseMapBiome.TEMPERATE_DESERT
            elif moisture < 0.2:
                return NoiseMapBiome.GRASSLAND
            elif moisture < 0.4:
                return NoiseMapBiome.TEMPERATE_DECIDUOUS_FOREST
            return NoiseMapBiome.TEMPERATE_RAIN_FOREST

        if elevation >= self.noise_range_dict['sand'].threshold:
            return NoiseMapBiome.BEACH

        if elevation >= self.noise_range_dict['shallowwater'].threshold:
            return NoiseMapBiome.SHALLOWS

        #if elevation < self.noise_range_dict['shallowwater'].threshold:
        return NoiseMapBiome.OCEAN

        #if moisture < 0.16:
        #    return NoiseMapBiome.SUBTROPICAL_DESERT
        #if moisture < 0.33:
        #    return NoiseMapBiome.GRASSLAND
        #if moisture < 0.66:
        #    return NoiseMapBiome.TROPICAL_SEASONAL_FOREST
        #return NoiseMapBiome.TROPICAL_RAIN_FOREST

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'width', self.width
        yield 'height', self.height
        yield 'algorithm', self.algorithm
        yield 'frequency', self.frequency
        yield 'octaves', self.octaves
        yield 'noise_ranges', [dict(noise_range) for noise_range in self.noise_ranges]
        yield 'tiles', [dict(tile) for tile in self.tiles]
        if self.moisture_map is not None:
            yield 'moisture_map', dict(self.moisture_map)

    def display(self):
        """ Print the map to the terminal. """

        def chunks(target_list, chunk_size):
            """
            Break a big list into smaller lists.
            """
            for i in range(0, len(target_list), chunk_size):
                yield target_list[i:i + chunk_size]

        colorama.init()

        # break the tiles into lines and print each tile with its range character
        tile_index = 0
        lines = chunks(self.tiles, self.width)
        for line in lines:
            for tile in line:
                range_found = False
                """
                for noise_range in self.noise_ranges:
                    if tile.noise_value <= noise_range.threshold:
                        noise_range.print()
                        range_found = True
                        break
                """
                for noise_range in self.noise_ranges:
                    if tile.noise_value >= noise_range.threshold:
                        moisture_tile = self.moisture_map.tiles[tile_index]
                        biome_character = get_character(self.biome(tile.noise_value, moisture_tile.noise_value))
                        if biome_character is None:
                            noise_range.print()
                        else:
                            print(biome_character, end='')
                        range_found = True
                        break

                # if no range was found, it's < 0 and should probably be water
                if not range_found:
                    self.noise_ranges[-1].print()

                # print uncolored black after the last character to stop color run off
                print('', end='')

                tile_index += 1

            print('')  # print new line to finish with

    def save(self, file_name):
        """ Save the map as JSON to a file. """
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
            tiles = [NoiseMapTile(tile['x'], tile['y'], tile['noise_value']) for tile in data['tiles']]

            # parse noise ranges
            noise_ranges = [NoiseRange(noise_range['name'], noise_range['threshold'], termcolor.colored(noise_range['character']))
                            for noise_range in data['noise_ranges']]

            file.close()

            return cls(width, height, noise_ranges, tiles)

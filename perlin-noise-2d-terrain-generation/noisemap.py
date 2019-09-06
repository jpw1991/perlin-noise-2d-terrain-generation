
import colorama
import json
import termcolor
import enum

from PIL import Image, ImageFont, ImageDraw
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
    SWAMP = 17                      # s on_grey

def get_character(value):
    character = None
    if value == NoiseMapBiome.OCEAN:
        character = termcolor.colored(' ', 'cyan', 'on_blue')
    elif value == NoiseMapBiome.SHALLOWS:
        character = termcolor.colored(' ', 'blue', 'on_cyan')
    elif value == NoiseMapBiome.BEACH:
        character = termcolor.colored('b', 'grey', 'on_yellow')
    elif value == NoiseMapBiome.SCORCHED:
        character = termcolor.colored('S', 'grey', 'on_red')
    elif value == NoiseMapBiome.BARE:
        character = termcolor.colored('B', 'grey', 'on_grey')
    elif value == NoiseMapBiome.TUNDRA:
        character = termcolor.colored('t', 'white', 'on_grey')
    elif value == NoiseMapBiome.TEMPERATE_DESERT:
        character = termcolor.colored('d', 'grey', 'on_yellow')
    elif value == NoiseMapBiome.SHRUBLAND:
        character = termcolor.colored('s', 'green', 'on_grey')
    elif value == NoiseMapBiome.GRASSLAND:
        character = termcolor.colored(' ', 'grey', 'on_green')
    elif value == NoiseMapBiome.TEMPERATE_DECIDUOUS_FOREST:
        character = termcolor.colored('f', 'grey', 'on_green')#f'♧', 'white', 'on_green')
    elif value == NoiseMapBiome.TEMPERATE_RAIN_FOREST:
        character = termcolor.colored('r', 'grey', 'on_green')
    elif value == NoiseMapBiome.SUBTROPICAL_DESERT:
        character = termcolor.colored('D', 'white', 'on_yellow')
    elif value == NoiseMapBiome.TROPICAL_SEASONAL_FOREST:
        character = termcolor.colored('F', 'grey', 'on_green')
    elif value == NoiseMapBiome.TROPICAL_RAIN_FOREST:
        character = termcolor.colored('R', 'grey', 'on_green')
    elif value == NoiseMapBiome.SNOW:
        character = termcolor.colored('s', 'grey', 'on_white')
    elif value == NoiseMapBiome.TAIGA:
        character = termcolor.colored('i', 'grey', 'on_green')
    elif value == NoiseMapBiome.SWAMP:
        character = termcolor.colored('s', 'white', 'on_grey')
    return character


def chunks(target_list, chunk_size):
    """
    Break a big list into smaller lists.
    """
    for i in range(0, len(target_list), chunk_size):
        yield target_list[i:i + chunk_size]


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
        self.scale = None
        self.octaves = None

        # create a dictionary from the noise ranges list for quick lookups later
        self.noise_range_dict = {}
        for noise_range in noise_ranges:
            self.noise_range_dict[noise_range.name] = noise_range

    def generate(self, algorithm, scale, octaves, persistence=0.5, lacunarity=2.0, sink_edges=False):
        """
        Generates the noise map.

        :param algorithm: use simplex or perlin algorithms
        :param scale: it's the scale of the map. Higher = zoomed in, lower = zoomed out.
        :param octaves: the level of detail. Lower = more peaks and valleys, higher = less peaks and valleys.
        :param persistence: how much an octave contributes to overall shape (adjusts amplitude).
        :param lacunarity: the level of detail on each octave (adjusts frequency).
        :param sink_edges: Sinks the edges and corners of the map into the ocean to create islands.
        :return: None
        """
        self.algorithm = algorithm
        self.scale = scale
        self.octaves = octaves

        self.tiles = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                noise_value = None
                if algorithm == 'perlin':
                    noise_value = pnoise2(x=x/scale, y=y/scale, octaves=octaves,
                                          persistence=persistence, lacunarity=lacunarity)
                elif algorithm == 'simplex':
                    noise_value = snoise2(x=x/scale, y=y/scale, octaves=octaves,
                                          persistence=persistence, lacunarity=lacunarity)
                row += [NoiseMapTile(x, y, noise_value)]
            self.tiles += row

        # If sink edges is true, we need to sink the corners & sides of the map into the ocean
        #
        # 1. Generate a box that fits inside the map with a small degree of margin.
        # 2. Generate a circle in its center
        # 3. Use this circle to cull all tiles that fall outside of it.
        #  _ _ _ _ _ _
        # |ooooKKKoooo|
        # |ooKKKKKKKoo|
        # |oKKKKKKKKKo|
        # |ooKKKKKKKoo|
        # |ooooKKKoooo|
        #
        # Something like above, where K is keep and O is ocean. Ok, awful ASCII art. I admit.
        #
        # http://mathcentral.uregina.ca/QQ/database/QQ.09.06/s/lori1.html
        # 1. Find the center tile

    def biome(self, elevation, moisture):
        if elevation <= self.noise_range_dict['water'].threshold:
           return NoiseMapBiome.OCEAN
        if elevation <= self.noise_range_dict['shallowwater'].threshold:
            return NoiseMapBiome.SHALLOWS
        if elevation <= self.noise_range_dict['sand'].threshold:
           return NoiseMapBiome.BEACH

        if elevation > self.noise_range_dict['hugemountain'].threshold:
            if moisture < 0.1:
                return NoiseMapBiome.SCORCHED
            elif moisture < 0.2:
                return NoiseMapBiome.BARE
            elif moisture < 0.5:
                return NoiseMapBiome.TUNDRA
            return NoiseMapBiome.SNOW

        if elevation > self.noise_range_dict['mountain'].threshold:
            if moisture < 0.33:
                return NoiseMapBiome.TEMPERATE_DESERT
            elif moisture < 0.66:
                return NoiseMapBiome.SHRUBLAND
            return NoiseMapBiome.TAIGA

        if moisture < 0.16:
           return NoiseMapBiome.SUBTROPICAL_DESERT
        if moisture < 0.33:
           return NoiseMapBiome.GRASSLAND
        if moisture < 0.66:
           return NoiseMapBiome.TROPICAL_SEASONAL_FOREST
        return NoiseMapBiome.TROPICAL_RAIN_FOREST

    def __iter__(self):
        """ Yields a dictionary when dict() is called for serializing to JSON """
        yield 'width', self.width
        yield 'height', self.height
        yield 'algorithm', self.algorithm
        yield 'scale', self.scale
        yield 'octaves', self.octaves
        yield 'noise_ranges', [dict(noise_range) for noise_range in self.noise_ranges]
        yield 'tiles', [dict(tile) for tile in self.tiles]
        if self.moisture_map is not None:
            yield 'moisture_map', dict(self.moisture_map)

    def display_as_image(self, tile_size):

        def get_biome_color(value):
            if value == NoiseMapBiome.OCEAN:
                return (54, 62, 150) # dark blue
            elif value == NoiseMapBiome.SHALLOWS:
                return (88, 205, 237) # cyan
            elif value == NoiseMapBiome.BEACH:
                return (247, 247, 119) # yellow
            elif value == NoiseMapBiome.SCORCHED:
                return (247, 149, 119) # peach
            elif value == NoiseMapBiome.BARE:
                return (168, 166, 165) # grey
            elif value == NoiseMapBiome.TUNDRA:
                return (132, 173, 158) # grey green
            elif value == NoiseMapBiome.TEMPERATE_DESERT:
                return (227, 155, 0) # orange
            elif value == NoiseMapBiome.SHRUBLAND:
                return (62, 110, 58) # olive
            elif value == NoiseMapBiome.GRASSLAND:
                return (55, 181, 43) # green
            elif value == NoiseMapBiome.TEMPERATE_DECIDUOUS_FOREST:
                return (62, 138, 55) # darker green
            elif value == NoiseMapBiome.TEMPERATE_RAIN_FOREST:
                return (161, 38, 255) # violet
            elif value == NoiseMapBiome.SUBTROPICAL_DESERT:
                return (255, 214, 153) # fleuro yellow
            elif value == NoiseMapBiome.TROPICAL_SEASONAL_FOREST:
                return (143, 80, 109) # musk
            elif value == NoiseMapBiome.TROPICAL_RAIN_FOREST:
                return (255, 0, 119) # rose
            elif value == NoiseMapBiome.SNOW:
                return (255, 255, 255) # white
            elif value == NoiseMapBiome.TAIGA:
                return (62, 87, 71) # dark olive
            elif value == NoiseMapBiome.SWAMP:
                return (92, 112, 104) # grey green
            else:
                return (0, 0, 0) # black

        # add some extra height to the image for the legend
        legend_height = 200
        legend_width = 1500
        image_width = self.width*tile_size
        if image_width < legend_width:
            image_width = legend_width
        image = Image.new('RGBA', size=(image_width, (self.height*tile_size)+legend_height), color=(0, 0, 0))

        d = ImageDraw.Draw(image)
        for tile_index in range(len(self.tiles)):
            tile = self.tiles[tile_index]
            moisture_tile = self.moisture_map.tiles[tile_index]
            biome_color = get_biome_color(self.biome(tile.noise_value, moisture_tile.noise_value))
            d.rectangle([tile.x*tile_size, tile.y*tile_size, tile.x*tile_size+tile_size, tile.y*tile_size+tile_size], fill=biome_color)

        # print the map legend so we know what we're looking at
        font_size = 14
        font = ImageFont.truetype('resources/fonts/JoshuaFont3.pfb', 14)
        keys = [str(key)[14:] for key in NoiseMapBiome]
        key_rows = chunks(keys, 5)
        text_x = 10
        text_y = (self.height*tile_size) + 10
        for key_row in key_rows:
            for key in key_row:
                # draw color key block
                d.rectangle([text_x, text_y, text_x + font_size, text_y + font_size], fill=get_biome_color(getattr(NoiseMapBiome, key)))
                # offset it by 2 char widths due to the color key and equals sign etc
                d.text((text_x+(font_size*2), text_y), ' = ' + key, font=font, fill=(255, 255, 255,))
                text_x += font_size * 20
            text_y += 50
            text_x = 10

        image.show()

    def display(self):
        """ Print the map to the terminal. """

        colorama.init()

        # print the map key/legend so we know what we're looking at
        keys = [str(key)[14:]+'='+get_character(key) for key in NoiseMapBiome]
        key_rows = chunks(keys, 5)
        for key_row in key_rows:
            line = ''
            for key in key_row:
                line += '{:<50}'.format(key)
            print(line)

        # break the tiles into lines and print each tile with its range character
        tile_index = 0
        lines = chunks(self.tiles, self.width)
        for line in lines:
            for tile in line:
                range_found = False
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
    def load(cls, data) -> 'NoiseMap':
        if data is not None:
            # parse map info
            width = data['width']
            height = data['height']

            # parse tiles
            tiles = [NoiseMapTile(tile['x'], tile['y'], tile['noise_value']) for tile in data['tiles']]

            # parse noise ranges
            noise_ranges = [
                NoiseRange(noise_range['name'], noise_range['threshold'], termcolor.colored(noise_range['character']))
                for noise_range in data['noise_ranges']]

            # parse moisture map
            moisture_map = None
            if 'moisture_map' in data:
                moisture_map = NoiseMap.load(data['moisture_map'])

            return cls(width, height, noise_ranges, tiles, moisture_map)

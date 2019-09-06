
import sys
import os
import argparse
import termcolor
import click
import json

from noisemap import NoiseMap
from noiserange import NoiseRange


def main():
    """
    python perlin-noise-2d-terrain-generator --algorithm simplex --water 0.00 --shallowwater 0.01 --mountain 0.5 --hugemountain 0.6 --land 0.4
    --algorithm simplex --hugemountain 0.5 --mountain 0.4 --land 0.0 --sand -0.1 --shallowwater -1.0 --water -2.0

    Nice island map: --algorithm perlin --octaves 8 --width 325 --height 64 --water 0.02 --shallowwater 0.05 --sand 0.1 --land 0.25 --mountain 0.3 --hugemountain 0.4

    Nice coastline: python perlin-noise-2d-terrain-generator --width 325 --height 85 --persistence 0.3
    Nicer coastline: python perlin-noise-2d-terrain-generator --width 325 --height 85 --persistence 0.4
    """
    parser = argparse.ArgumentParser(description='Generate or view a noise map')
    
    parser.add_argument('-v', '--view', help="Display an existing map.", type=str)
    parser.add_argument('-f', '--file', help="File name to generate", type=str)
    parser.add_argument('-o', '--octaves', help="Octaves used for generation.", type=int, default=8)
    parser.add_argument('--width', help="Map width to generate.", type=int, default=600)
    parser.add_argument('--height', help="Map height to generate.", type=int, default=200)
    parser.add_argument('--scale', help="Higher=zoomed in, Lower=zoomed out.", type=float, default=200)
    parser.add_argument('--algorithm', choices=['perlin', 'simplex'], help="Noise algorithm.", type=str, default='simplex')
    parser.add_argument('--persistence', help="how much an octave contributes to overall shape (adjusts amplitude).",
                        type=float, default=0.5)
    parser.add_argument('--lacunarity', help="The level of detail on each octave (adjusts frequency).", type=float,
                        default=3.0)
    parser.add_argument('--sinkedges', help="Sink the edges of the map into the sea.", type=str)

    parser.add_argument('--water', help="Height level of the water", type=float, default=0.0)
    parser.add_argument('--shallowwater', help="Height level of the shallow water", type=float, default=0.05)
    parser.add_argument('--sand', help="Height level of the sand", type=float, default=0.1)
    parser.add_argument('--land', help="Height of normal grass/land/forest", type=float, default=0.15)
    parser.add_argument('--mountain', help="Height of mountains", type=float, default=0.5)
    parser.add_argument('--hugemountain', help="Height of huge mountains", type=float, default=0.6)

    parser.add_argument('--moisturea', help="Moisture algorithm.", type=str, default='simplex')
    parser.add_argument('--moistureo', help="Moisture octaves.", type=int, default=8)
    parser.add_argument('--moistures', help="Moisture scale.", type=float, default=200)
    parser.add_argument('--moisturep', help="Moisture persistence.", type=float, default=0.5)
    parser.add_argument('--moisturel', help="Moisture lacunarity.", type=float, default=3.0)

    parser.add_argument('--tilesize', help="Size in pixels of tiles on the map.", type=int, default=4)

    args = parser.parse_args()

    if args.view is not None:
        # load existing
        with open(args.view, 'r', encoding='utf8') as file:
            data = json.load(file)
            noise_map = NoiseMap.load(data)
            file.close()

            print('file:\t\t%s' % args.view)

            noise_map.display_as_image(args.tilesize)

    else:

        # generate
        scale = args.scale
        moisture_scale = args.moistures

        noise_ranges = [
            NoiseRange('hugemountain', args.hugemountain, termcolor.colored('∆', 'grey', 'on_white')),
            NoiseRange('mountain', args.mountain, termcolor.colored('^', 'grey', 'on_white')),
            NoiseRange('land', args.land, termcolor.colored('.', 'white', 'on_green')),
            NoiseRange('sand', args.sand, termcolor.colored('.', 'white', 'on_yellow')),
            NoiseRange('shallowwater', args.shallowwater, termcolor.colored('~', 'blue', 'on_blue')),
            NoiseRange('water', args.water, termcolor.colored('≈', 'blue', 'on_blue', attrs=['dark'])),
        ]

        # generate terrain
        noise_map = NoiseMap(args.width, args.height, noise_ranges)
        noise_map.generate(args.algorithm, scale, args.octaves, args.persistence, args.lacunarity)

        # generate moisture
        moisture_map = NoiseMap(args.width, args.height)
        moisture_map.generate(args.moisturea, moisture_scale, args.moistureo, args.moisturep, args.moisturel)

        noise_map.moisture_map = moisture_map

        # display map
        noise_map.display_as_image(args.tilesize)
        
        if click.confirm('Save map?', default=False):
            # find a free file name
            i = 0
            while os.path.exists('noise_map_%03d.json' % i):
                i += 1
            file_name = 'noise_map_%03d.json' % i
            noise_map.save(file_name)
            print('Saved to: %s' % file_name)


if __name__ == '__main__':
    sys.exit(main())


import sys
import os
import argparse
import termcolor
import click

from noisemap import NoiseMap
from noiserange import NoiseRange


def main():
    """
    python perlin-noise-2d-terrain-generator --algorithm simplex --water 0.00 --shallowwater 0.01 --mountain 0.5 --hugemountain 0.6 --land 0.4
    --algorithm simplex --hugemountain 0.5 --mountain 0.4 --land 0.0 --sand -0.1 --shallowwater -1.0 --water -2.0
    """
    parser = argparse.ArgumentParser(description='Generate or view a noise map')
    
    parser.add_argument('-v', '--view', help="Display an existing map.", type=str)
    parser.add_argument('-f', '--file', help="File name to generate", type=str)
    parser.add_argument('-o', '--octaves', help="Octaves used for generation.", type=int, default=8)
    parser.add_argument('--width', help="Map width to generate.", type=int, default=164)
    parser.add_argument('--height', help="Map height to generate.", type=int, default=32)
    parser.add_argument('--frequency', help="Noise frequency.", type=float, default=4.0)
    parser.add_argument('--algorithm', choices=['perlin', 'simplex'], help="Noise algorithm.", type=str, default='simplex')
    
    parser.add_argument('--water', help="Height level of the water", type=float, default=-1.0)
    parser.add_argument('--shallowwater', help="Height level of the shallow water", type=float, default=-0.3)
    parser.add_argument('--sand', help="Height level of the sand", type=float, default=-0.1)
    parser.add_argument('--land', help="Height of normal grass/land/forest", type=float, default=0.0)
    parser.add_argument('--mountain', help="Height of mountains", type=float, default=0.4)
    parser.add_argument('--hugemountain', help="Height of huge mountains", type=float, default=0.5)

    parser.add_argument('--moisturea', help="Moisture algorithm for determining map moisture", type=str, default='simplex')
    parser.add_argument('--moistureo', help="Moisture octaves for determining map moisture", type=int, default=8)
    parser.add_argument('--moisturef', help="Moisture frequency for determining map moisture", type=float, default=4)

    args = parser.parse_args()

    if args.view is not None:
        # load existing
        noise_map = NoiseMap.load(args.view)

        print('file:\t\t%s' % args.view)

        noise_map.display()

    else:
        # generate
        frequency = args.frequency * args.octaves
        moisture_frequency = args.moisturef * args.moistureo

        noise_ranges = [
            NoiseRange('hugemountain', args.hugemountain, termcolor.colored('∆', 'grey', 'on_white')),
            NoiseRange('mountain', args.mountain, termcolor.colored('^', 'grey', 'on_white')),
            NoiseRange('land', args.land, termcolor.colored('.', 'white', 'on_green')),
            NoiseRange('sand', args.sand, termcolor.colored('.', 'white', 'on_yellow')),
            NoiseRange('shallowwater', args.shallowwater, termcolor.colored('~', 'blue', 'on_blue')),
            NoiseRange('water', args.water, termcolor.colored('≈', 'blue', 'on_blue', attrs=['dark'])),
        ]
        
        print('octaves:\t%s\n'
              'width:\t\t%d\n'
              'height:\t\t%d\n'
              'frequency:\t%f (%d * %f)\n'
              'algorithm:\t%s\n' % (args.octaves, args.width, args.height,
                                    frequency, args.octaves, args.frequency,
                                    args.algorithm))

        # generate terrain
        noise_map = NoiseMap(args.width, args.height, noise_ranges)
        noise_map.generate(args.algorithm, frequency, args.octaves)

        # generate moisture
        moisture_map = NoiseMap(args.width, args.height)
        moisture_map.generate(args.moisturea, moisture_frequency, args.moistureo)

        noise_map.moisture_map = moisture_map

        # display map
        noise_map.display()
        
        if click.confirm('Save map?', default=False):
            # find a free file name
            i = 0
            while os.path.exists('noise_map_%03d.json' % i):
                i += 1
            noise_map.save('noise_map_%03d.json' % i)


if __name__ == '__main__':
    sys.exit(main())

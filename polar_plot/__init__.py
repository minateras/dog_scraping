from os import listdir
from os.path import isfile, join
from pathlib import Path

from bph import BPH
from mh import MH

from polar_plot import PolarPlot


def validate_input(message, original, validate, error_message):
    while True:
        try:
            value = input(message)
            if len(value) > 0:
                if validate(value): return value
                raise Exception
            return original
        except KeyboardInterrupt:
            exit()
        except:
            print(f'{error_message} Please try again.')


if __name__ == '__main__':
    print("To configure your plot, you'll now be presented with a few options. The value inside the parentheses is the default. Press Enter to select the default value, otherwise input your preferred value and press Enter.")
    polar_plot_type = validate_input('Choose the type of plot you want to generate: (BPH) ', 'BPH', lambda value: value == 'BPH' or value == 'MH', 'Not a valid input.')
    path = Path(__file__).parent / 'input'
    file_names = [f[:-5] for f in listdir(path) if isfile(join(path, f))]
    file_name = validate_input('Enter the name of the JSON file you want to use, with the file extension (i.e., .json) excluded: (ideal) ', 'ideal', lambda value: value in file_names, 'No such file.')
    actual = PolarPlot.get_input_file(f'{file_name}.json')
    if polar_plot_type == 'BPH': BPH(actual)
    else: MH(actual)

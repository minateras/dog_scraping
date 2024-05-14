import json
from enum import Enum
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


class PolarPlot:
    PATH = Path(__file__).parent
    PATH_TO_INPUT = PATH / 'input'
    FONT_SIZE = 20
    FIGURE_SIZE = (10, 10)
    DPI = 300
    MIN = 0
    MAX = 5
    OFFSET = 8
    NONE = ()
    FIT = 'tight'


    class Colors(Enum):
        GREEN = 'g'
        RED = 'r'
        BLUE = 'b'


    class Labels(Enum):
        DOG = ('Hunden', .3)
        BREED = ('Rasen', .1)
        IDEAL = ('Vårt ideal', .1)


    @staticmethod
    def get_input_file(file_name):
        with open(PolarPlot.PATH_TO_INPUT / file_name) as f:
            return json.loads(f.read())


    def __init__(self, characteristics, expected, ideal, actual, object):
        expected = tuple(reversed(expected)) # Considering the order in which Matplotlib plots the values, they must be reversed.
        ideal = tuple(reversed(ideal)) # ^

        plt.rcParams.update({'font.size': self.FONT_SIZE})

        plt.figure(figsize=self.FIGURE_SIZE, dpi=self.DPI)
        plt.subplot(polar=True)

        theta = np.linspace(0, 2*np.pi, len(expected))
        lines, labels = plt.thetagrids(np.arange(0, 360, 360/len(characteristics)), self.__generate_x_labels(len(characteristics)))

        if len(actual) > 0:
            actual = tuple(reversed(actual)) # Considering the order in which Mathplotlib plots the values, they must be reversed.
            plt.plot(theta, actual, self.Colors.GREEN.value) # Plot actual.
        plt.plot(theta, expected, self.Colors.RED.value) # Plot expected.
        plt.plot(theta, ideal, self.Colors.BLUE.value) # Plot ideal.
        if len(actual) > 0: plt.fill(theta, actual, self.Colors.GREEN.value, alpha=self.Labels.DOG.value[1]) # Fill actual plot.
        plt.fill(theta, expected, self.Colors.RED.value, alpha=self.Labels.BREED.value[1]) # Fill expected plot.
        plt.fill(theta, ideal, self.Colors.BLUE.value, alpha=self.Labels.IDEAL.value[1]) # Fill ideal plot.

        axes = plt.gca() # Get the current axes.
        axes.set_ylim([self.MIN, self.MAX]) # Set limits.
        axes.set_theta_offset(self.OFFSET) # Adjust the plots rotation.
        axes.set_yticklabels(self.NONE) # Remove the y labels.

         # Insert a description of the plots:
        legend = plt.legend(
            labels=(self.Labels.DOG.value[0], self.Labels.BREED.value[0], self.Labels.IDEAL.value[0]) if len(actual) > 0 else (self.Labels.BREED.value[0], self.Labels.IDEAL.value[0]),
            loc=1,
            bbox_to_anchor=(0, 0),
        )

        # Insert explanations for the x labels:
        explanations = str()
        for index in range(0, len(characteristics)):
            characteristic = characteristics[index]
            explanations += f'{index + 1}.{''.join([' ']*6 if index + 1 < 10 else [' ']*4)}{characteristic}{'\n' if index < len(characteristics) - 1 else ''}' # Tabs doesn't render correctly in Matplotlib, thus the solution with spaces.
        text = plt.text(1.25, -.2, explanations, transform=axes.transAxes)

        self.__save_as_image_file(object, True)

        # Remove the x labels, the legend and the text:
        axes.set_xticklabels(self.NONE)
        legend.remove()
        text.remove()

        self.__save_as_image_file(object)


    def __generate_x_labels(self, length):
        x_labels = list(range(length, 0, -1))[:length-1]
        x_labels.insert(0, 1)
        return x_labels


    def __save_as_image_file(self, object, with_explanations=False):
        image_file = f'{type(object).__name__}{'_2' if with_explanations else ''}.png'
        plt.savefig(self.PATH / f'output/{image_file}', bbox_inches=self.FIT, transparent=True)

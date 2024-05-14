from polar_plot import PolarPlot


class MH(PolarPlot):
    CHARACTERISTICS = (
        'Nyfikenhet/Orädsla',
        'Aggressivitet',
        'Socialitet',
        'Jaktintresse',
        'Lekfullhet',
    )
    EXPECTED = (
        3.2,
        2,
        3.4,
        2.2,
        2.8,
        3.2,
    )
    IDEAL = 'ideal_mh.json'


    def __init__(self, dogs_with_actual):
        ideal = PolarPlot.get_input_file(self.IDEAL)
        super().__init__(self.CHARACTERISTICS, self.EXPECTED, ideal, dogs_with_actual, self)

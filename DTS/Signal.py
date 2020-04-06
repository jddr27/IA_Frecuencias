import numpy as np

SAMPLE_FRECUENCY = 10000

class Signal:
    y = []
    t = []

    def __init__(self):
        self.t = np.linspace(0, 1, SAMPLE_FRECUENCY, False)

    def generate(self, frecuency, amplitude, sinoidal):
        if sinoidal:
            self.y = amplitude*np.sin(2*np.pi*frecuency*self.t)
        else:
            self.y = amplitude*np.cos(2*np.pi*frecuency*self.t)

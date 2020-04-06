import scipy.signal as sig
from DTS.Signal import Signal

class Filter:

    values = []

    def __init__(self, constants):
        if len(constants) == 18:
            self.values = [constants[:6], constants[6:12], constants[12:18]]

    def filter(self, input):
        output = Signal()
        output.y = sig.sosfilt(self.values, input.y)
        return output

    def filterdatos(self, input):
        output = Signal()
        #print("filtro input.t",len(input.t)) 
        output.t = input.t
        #print("filtro output.t",len(input.t)) 
        output.y = sig.sosfilt(self.values, input.y)
        return output

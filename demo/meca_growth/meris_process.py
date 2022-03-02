from physiology import Physiology
from growth import Growth
from division import CellDivision
from cell_state import CellState

class PhysiologyNode(object):
    def __call__(self, *inputs):
        return Physiology(*inputs)

class GrowthNode(object):
    def __call__(self, *inputs):
        pos,algo,prop=inputs
        return Growth(pos,algo,[prop])

class CellDivisionNode(object):
    def __call__(self, *inputs):
        return CellDivision(*inputs)

class CellStateNode(object):
    def __call__(self, *inputs):
        return CellState(*inputs)


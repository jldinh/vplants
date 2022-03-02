import vplants.tutorial
from vplants.tutorial import meca
from openalea.deploy.shared_data import shared_data
import openalea.mtg
from openalea.mtg import *


dir = shared_data(openalea.mtg)
fn = dir/'boutdenoylum2.mtg'
drf = dir/'walnut.drf'
dressing_data = dresser.dressing_data_from_file(drf)

g = MTG(fn)
meca.apply_meca(g, dresser=dressing_data, epsilon=1.)

def test_meca():
    
    # shared_data(vplants.tutorial)
    path = shared_data(vplants.tutorial)/'Meca'/'noylum2.mtg'
    g = mtg.MTG(path)
    
    meca.apply_meca(g)

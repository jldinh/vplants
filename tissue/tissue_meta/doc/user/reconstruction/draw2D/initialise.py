from vplants.plantgl.math import Vector2
from openalea.container import Topomesh
from openalea.svgdraw import open_svg

mesh = Topomesh(2)

f = open_svg("coleochaete.svg",'r')
sc = f.read()
f.close()



# This file has been generated at Thu Jul 31 17:10:33 2008

from openalea.core import *


__name__ = 'vplants.fractalysis.engine'

__editable__ = True
__description__ = 'Fractalysis engine nodes.'
__license__ = 'CeCILL-C'
__url__ = 'http://openalea.gforge.inria.fr'
__alias__ = ['fractalysis.engine']
__version__ = '0.0.1'
__authors__ = 'OpenAlea consortium'
__institutes__ = 'INRIA/CIRAD'
__icon__ = 'engine_icon.png'
 


###### begin nodes definitions #############
__all__ = ['twosurfaces_TwoSurfaces', 'engine_nodes_BCM', 'engine_nodes_lactrix_fromPix', 'engine_nodes_lacunarity', 'engine_nodes_lactrix_fromScene', 'engine_nodes_voxelize', 'engine_nodes_MST', 'engine_nodes_MST_fromDict', 'engine_nodes_MST_toPix', 'engine_nodes_MST2Pgl']

engine_nodes_MST = Factory( name="MST",
              description="Generate a MultiScale Thing from the curdling and random trema generation",
              category="Fractal Analysis",
              nodemodule="engine_nodes",
              nodeclass="genMST",
              inputs=(dict(name="Dimension", interface=IInt(min=1), value=1),
                      dict(name="Depth", interface=IInt(min=1), value=3),
                      dict(name="Scale subdivision", interface=ISequence),
                      dict(name="Scale similarity", interface=IBool, value=False),
                      ),
              outputs=(dict(name="MST", interface = None),
                      ),
              widgetmodule=None,
              widgetclass=None,
              )

engine_nodes_MST_fromDict = Factory( name="MSTfromDict",
              description="Generate a MultiScale Thing from the curdling and random trema generation",
              category="Fractal Analysis",
              nodemodule="engine_nodes",
              nodeclass="MSTfromDict",
              inputs=(dict(name="Parameters", interface=IDict),
                      ),
              outputs=(dict(name="MST", interface = None),
                      ),
              widgetmodule=None,
              widgetclass=None,
              )

engine_nodes_MST_toPix = Factory( name="MST2Pix",
              description="Generate an image from a MST",
              category="Fractal Analysis,codec",
              nodemodule="engine_nodes",
              nodeclass="MST2Pix",
              inputs=(dict(name="MST", interface=None),
                      dict(name="Image name", interface=IStr, value="Mst"),
                      dict(name="Save directory", interface=IDirStr),
                      ),
              outputs=(dict(name="PIL image", interface = None),
                      ),
              widgetmodule=None,
              widgetclass=None,
              )

engine_nodes_MST2Pgl = Factory( name="MST2Pgl",
              description="Generate a PlantGL scene from a MST",
              category="Fractal Analysis,codec,scene",
              nodemodule="engine_nodes",
              nodeclass="MST2PglScene",
              inputs=(dict(name="MST", interface=None),
                      dict(name="Geometry", interface=None, value=None),
                      ),
              outputs=(dict(name="Pgl Scene", interface = None),
                      ),
              widgetmodule=None,
              widgetclass=None,
              )

engine_nodes_BCM = Factory( name="BCM",
              description="Apply box counting method on scene",
              category="Fractal Analysis",
              nodemodule="engine_nodes",
              nodeclass="BCM",
              inputs=(dict(name="Scene", interface=None,),
                      dict(name="Stop Factor", interface=IInt(min=3), value=10),
                      ),
              outputs=(dict(name="Scales", interface = ISequence),
                       dict(name="Intercepted Voxels", interface = ISequence),),
              widgetmodule=None,
              widgetclass=None,
              )


twosurfaces_TwoSurfaces = Factory(name='TwoSurfaces', 
                description='Computes two surfaces on a multiscale scenes', 
                category='Fractal Analysis', 
                nodemodule='engine_nodes',
                nodeclass='TwoSurfaces',
                inputs=({'interface': None, 'name': 'Leaves'}, {'interface': ISequence, 'name': 'Macrorep'}),
                outputs=({'interface': ISequence, 'name': 'Macrosurfaces'}, {'interface': ISequence, 'name': 'Microsurfaces'}),
                widgetmodule=None,
                widgetclass=None,
                )


engine_nodes_lactrix_fromPix = Factory( name="Pix2MatrixLac",
              description="Generate a MatrixLac from an Image",
              category="Fractal Analysis,codec",
              nodemodule="engine_nodes",
              nodeclass="lactrix_fromPix",
              inputs=(dict(name="Image", interface=None,),
                      dict(name="Pixel width", interface=IFloat),
                      dict(name="Save Directory", interface=IDirStr, value='/tmp'),
                      dict(name="Name", interface=IStr,)
                      ),
              outputs=(dict(name="MatrixLac", interface = None,),
                       dict(name="Thresholded image", interface = None,),
                      ),
              widgetmodule=None,
              widgetclass=None,
              )


engine_nodes_lacunarity = Factory(name='Lacunarity', 
                description='Compute lacunarity of n-dimensional matrix', 
                category='Fractal Analysis', 
                nodemodule='engine_nodes',
                nodeclass='lacunarity',
                inputs=None,
                outputs=None,
                widgetmodule=None,
                widgetclass=None,
                )




engine_nodes_lactrix_fromScene = Factory(name='Scene2MatrixLac', 
                description='Generate a MatrixLac from PlantGL scene', 
                category='Fractal Analysis,codec,scene', 
                nodemodule='engine_nodes',
                nodeclass='lactrix_fromScene',
                inputs=({'interface': None, 'name': 'Scene'}, {'interface': IStr, 'name': 'Name'}, {'interface': IFloat(min=2, max=16777216, step=1.000000), 'name': 'Grid Size'}, {'interface': IDirStr, 'name': 'Save Directory', 'value': '/tmp'}, {'interface': IBool, 'name': 'Density', 'value': False}),
                outputs=({'interface': None, 'name': 'MatrixLac'}, {'interface': None, 'name': 'Pgl scene'}),
                widgetmodule=None,
                widgetclass=None,
                )




engine_nodes_voxelize = Factory(name='Voxelize', 
                description='Generates an embedding grid for a scene', 
                category='Fractal Analysis,scene', 
                nodemodule='engine_nodes',
                nodeclass='voxelize',
                inputs=({'interface': None, 'name': 'Scene'}, {'interface': IInt, 'name': 'Division Factor', 'value': 10}, {'interface': IBool, 'name': 'Density', 'value': True}),
                outputs=({'interface': IInt, 'name': 'Voxels size'}, {'interface': ISequence, 'name': 'Centers'}, {'interface': ISequence, 'name': 'Densities'}, {'interface': None, 'name': 'VoxScene'}),
                widgetmodule=None,
                widgetclass=None,
                )





# -*- python -*-
#
#       OpenAlea.Asclepios
#
#       Copyright 2006-2009 INRIA - CIRAD - INRA
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################
"""Node declaration for image
"""

__license__ = "Cecill-C"
__revision__ = " $Id:  $ "

from openalea.core import *

__name__ = "vplants.asclepios"

__version__ = '0.8.0'
__license__ = 'CECILL-C'
__authors__ = 'OpenAlea Consortium'
__institutes__ = 'INRIA/CIRAD'
__description__ = 'Image manipulation'
__url__ = 'http://openalea.gforge.inria.fr'
__icon__ = 'asclepios.png'

__all__ = []

reech3d = Factory(name = "reech3d",
                category = "image processing",
                nodemodule = "vt_exec",
                nodeclass = "wra_reech3d",
                inputs = (dict(name="image", interface=None ),
                          dict(name="matrix", interface=None ),
                          dict(name="matrix_before", interface=None),
                          dict(name="deformation", interface=None ),
                          dict(name="gain", interface=IFloat, value=1.0 ),
                          dict(name="bias", interface=IFloat, value=0.0 ),
                          dict(name="interpolation", interface=IEnumStr(["linear","nearest","cspline"]), value="linear" ),
                          dict(name="iso", interface=IFloat, value=1.0),
                          dict(name="output_shape", interface=ITuple, value=None ),
                          dict(name="vin", interface=ITuple, value=None),
                          dict(name="vout", interface=ITuple, value=None),
                          dict(name="inv", interface=IBool, value=False),
                          dict(name="inv_before", interface=IBool, value=False),
                          dict(name="swap", interface=IBool, value=False),),
                outputs = (dict(name="result image", interface = None),),
                )

__all__.append("reech3d")

linear_block_matching = Factory(name='Baladin',
                                category='image',
                                nodemodule='vt_exec',
                                nodeclass='BlockMatching',
                                inputs=None,
                                outputs=None,
                                widgetmodule=None,
                                widgetclass=None,
                                lazy=True
                                )
__all__.append("linear_block_matching")

non_linear_block_matching = Factory(name='SuperBaloo',
                                    category='image',
                                    nodemodule='vt_exec',
                                    nodeclass='SuperBaloo',
                                    )
__all__.append("non_linear_block_matching")

watershed = Factory(name= "watershed",
              	   category = "vtissue",
 		   inputs=(dict(name="labeled markers image", interface=None),
 		           dict(name='gradient image', interface=None),),
		   outputs=(dict(name="segmented image", interface=None),),
              	   nodemodule = "vt_exec",
              	   nodeclass = "wra_watershed",
               	  )

__all__.append("watershed")


# -*- python -*-
#
#       tissueshape: tissue geometry and functions to use it
#
#       Copyright 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
"""
node definition for grid tissueshapes
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.core import ScriptLibrary
from openalea.celltissue import TissueDB
from openalea.tissueshape import regular_grid,hexagonal_grid

def create_regular_grid (shape) :
	db = regular_grid(shape)
	return db,

def create_regular_grid_script (inputs, outputs) :
	lib = ScriptLibrary()
	shape, = inputs
	db, = outputs
	db = lib.register(db,"db")
	
	script = "from openalea.tissueshape import regular_grid\n"
	script += "%s = regular_grid(%s)\n" % (db,shape)
	
	return script

def create_hexagonal_grid (shape, shape_geom) :
	db = hexagonal_grid(shape,shape_geom)
	return db,

def create_hexagonal_grid_script (inputs, outputs) :
	lib = ScriptLibrary()
	shape,shape_geom = inputs
	db, = outputs
	db = lib.register(db,"db")
	
	script = "from openalea.tissueshape import hexagonal_grid\n"
	script += "%s = hexagonal_grid(%s,%s)\n" % (db,shape,shape_geom)
	
	return script




# -*- python -*-
#
#       simpleplot: a simple widget to plot sequences
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

__doc__="""
This module defines a viewer for simple plot
"""

__license__= "Cecill-C"
__revision__=" $Id: plotter.py 7887 2010-02-09 07:49:59Z cokelaer $ "

from PyQt4.QtGui import QGraphicsView
from simpleplot import SimplePlot

class Plotter (QGraphicsView) :
	"""Simple viewer.
	"""
	def __init__ (self, seq, xres = 1., yres = 1., parent = None) :
		QGraphicsView.__init__(self,parent)
		self._sc = SimplePlot(seq)
		self._sc.set_xres(xres)
		self._sc.set_yres(yres)
		self.setScene(self._sc)
		

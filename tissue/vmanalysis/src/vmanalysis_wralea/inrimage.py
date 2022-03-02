# -*- python -*-
#
#       vmanalysis: algorithms to analyse images
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
node definition for vmanalysis package
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

from openalea.vmanalysis import InrImage,SlideViewer,compute_palette

def read (filename) :
	inr = InrImage()
	inr.read(filename)
	return inr,

def write (inr, filename) :
	inr.write(filename)
	return inr,

def split (inr) :
	return inr.header(),inr.data()

def merge (header, data) :
	inr = InrImage(header,data)
	return inr,

def display (inrimages, palette, color_index_max) :
	if isinstance(inrimages,InrImage) :
		inrimages = [inrimages]
	
	w_list = []
	for i,img in enumerate(inrimages) :
		w = SlideViewer()
		v = w.view()
		if color_index_max is None :
			cmax = img.data().max()
		else :
			cmax = color_index_max
		palette = compute_palette(palette,cmax)
		v.set_palette(palette)
		v.set_image(img)
		
		w.setWindowTitle("inrimage%d" % i)
		w.show()
		w_list.append(w)
	
	return w_list,



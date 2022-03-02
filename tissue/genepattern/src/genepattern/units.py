# -*- python -*-
#
#       genepattern: abstract geometry and functions to use them
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
This module defines a function to deal with differents units
"""

__license__= "Cecill-C"
__revision__=" $Id: $ "

unit_mult = {"m":1.,
			 "dm":1e-1,
			 "cm":1e-2,
			 "mm":1e-3,
			 "mum":1e-6,
			 "nm":1e-9,
			 "km":1e3}

def convert_to_meters (value, unit) :
	try :
		return value*unit_mult[unit]
	except KeyError :
		raise UserWarning("%s is not a recognized unit" % unit)

def change_unit (value, unit, wanted_unit) :
	try :
		ui_value = value*unit_mult[unit]
	except KeyError :
		raise UserWarning("%s is not recognized unit for your value" % unit)
	try :
		return ui_value/unit_mult[wanted_unit]
	except KeyError :
		raise UserWarning("%s is not recognized unit" % wanted_unit)
	

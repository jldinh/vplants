#!/usr/bin/env python
"""Convert all meristems from Pierre with options files taken from their subfolders.

:todo:
    Nothing.

:bug:
    None known.
    
:organization:
    INRIA

"""
# Module documentation variables:
__authors__="""Szymon Stoma    
"""
__contact__=""
__license__="Cecill-C"
__date__="<Timestamp>"
__version__="0.1"
__docformat__= "restructuredtext en"
__revision__="$Id: 08-05-28-convertPierresMeristems.py 7875 2010-02-08 18:24:36Z cokelaer $"


from openalea.mersim.serial.convertFromMerrysim import convert

path="/home/stymek/mdata/"
for i in ["08-06-02-discretizedWallAndCell1D","08-05-21-marianne01", "m101"]:
    convert(path+i+"/convert_options.py")
    
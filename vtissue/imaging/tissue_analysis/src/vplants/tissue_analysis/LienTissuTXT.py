#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
#
#       Vplants.tissue_analysis
#
#       Copyright 2006-2011 INRIA - CIRAD - ENS 
#
#       File author(s): Vincent Mirabet <vincent.mirabet@ens-lyon.fr>
#                       Jonathan LEGRAND <jonathan.legrand@ens-lyon.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
###############################################################################

__license__ = "CeCILL v2"
__revision__ = " $Id$ "

from string import *
import numpy as np
import warnings
import sys

class LienTissuTXT(object):
    """
    Class allowing to import lineage '.txt' files, saved from ALT or handmade.
    
    :Example:
        435 2658 165
        Mother cell: 435
        Daugthers cells: 2658, 165
    
    Previous Version : 8th April 2011
    Current Version : 24th September 2012
    """
    def __init__(self, suiviTXT):
        self.filename=suiviTXT
        self.cellT1_cellT2={}
        try:
            self.cellT1_cellT2=self.OpenLineage(suiviTXT)
        except IOError:
             print "Oops! Wrong input file specified, try again"
             sys.exit(1)
             
        self.cellT2_cellT1={}
        self.cellT2_cellT1=self.LineageInversion()


    def OpenLineage(self, filename):
        """
        Function creating mother - daughter dictionary.
        """
        f = open(filename,'r')
        lines = f.readlines()
        t1t2 = {}
        for line in lines:
            numbers = line.split()
            # - We make sure of the unicity of the lineage: each mother has been associated ONCE!
            if t1t2.has_key(int(numbers[0])):
                warnings.warn( "Apparently the mother cell #"+numbers[0]+" has already been associated with cell(s) "+str(t1t2[int(numbers[0])]) )
                warnings.warn( "You are trying to associate it again with: "+str(numbers[1:]) )
            t1t2[int(numbers[0])]=[]
            for i3 in numbers[1:]:
                t1t2[int(numbers[0])].append(int(i3))
        f.close()
        return t1t2


    def LineageInversion(self):
        """
        Function creating daughter - mother dictionary.
        """
        t2t1={}
        for c in self.cellT1_cellT2.keys():
            for c1 in self.cellT1_cellT2[c]:
                # - We make sure of the unicity of the lineage: each daughter has been associated ONCE!
                if t2t1.has_key(c1):
                    warnings.warn( "Apparently the daughter cell #"+str(c1)+" has already been associated with cell #"+str(t2t1[c1]) )
                    warnings.warn( "You are trying to associate it again with: #"+str(c) )
                t2t1[c1]=c      
        return t2t1


def main():
    l=LienTissu(sys.argv[1:])


if __name__ == '__main__':
    main()

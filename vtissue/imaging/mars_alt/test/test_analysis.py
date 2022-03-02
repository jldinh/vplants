# -*- python -*-
# -*- coding: latin-1 -*-
#
#       test_analysis
#
#       Copyright 2006 - 2010 INRIA - CIRAD - INRA
#
#       File author(s): Eric MOSCARDI <eric.moscardi@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
#
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

from openalea.image.all import imread
from vplants.mars_alt.all import VTissueAnalysis, extract_L1
import numpy as np

########################
# Tests in dimension 2 #
########################

a = np.array([[1, 2, 7, 7, 1, 1],
              [1, 6, 5, 7, 3, 3],
              [2, 2, 1, 7, 3, 3],
              [1, 1, 1, 4, 1, 1]])

def test_nlabels2d():
    """ Test of VTissuAnalysis.nlabels() method """

    analysis = VTissueAnalysis(a)
    assert analysis.nlabels() == 7

def test_center_of_mass2d():
    """ Test of VTissuAnalysis.center_of_mass() method """

    analysis = VTissueAnalysis(a)
    assert analysis.center_of_mass(7) == [0.75, 2.75]
    assert analysis.center_of_mass([7,2]) == [[0.75, 2.75], [1.3333333333333333, 0.66666666666666663]]
    assert analysis.center_of_mass() == [[1.8, 2.2999999999999998],
                                        [1.3333333333333333, 0.66666666666666663],
                                        [1.5, 4.5],
                                        [3.0, 3.0],
                                        [1.0, 2.0],
                                        [1.0, 1.0],
                                        [0.75, 2.75]]

def test_volume2d():
    """ Test of VTissuAnalysis.volume() method """

    analysis = VTissueAnalysis(a)
    assert analysis.volume(7) == 4.0
    assert analysis.volume([7,2]) == [4.0, 3.0]
    assert analysis.volume() == [10.0, 3.0, 4.0, 1.0, 1.0, 1.0, 4.0]


def test_neighbors2d():
    """ Test of VTissuAnalysis.neighbors() method """

    analysis = VTissueAnalysis(a)
    assert analysis.neighbors(7) == [(5, [1, 2, 3, 4, 5])]
    assert analysis.neighbors([7,2]) == [(5, [1, 2, 3, 4, 5]), (3, [1, 6, 7])]
    assert analysis.neighbors() == [None,
                                    (3, [1, 6, 7]),
                                    (2, [1, 7]),
                                    (2, [1, 7]),
                                    (3, [1, 6, 7]),
                                    (3, [1, 2, 5]),
                                    (5, [1, 2, 3, 4, 5])]

def test_surface_area2d():
    """ Test of VTissuAnalysis.surface_area() method """

    analysis = VTissueAnalysis(a)
    assert analysis.surface_area(7,2) == 1
    assert analysis.surface_area(2,7) == 1

########################
# Tests in dimension 3 #
########################

a = np.array([[1, 2, 7, 7, 1, 1],
              [1, 6, 5, 7, 3, 3],
              [2, 2, 1, 7, 3, 3],
              [1, 1, 1, 4, 1, 1]])

b = np.zeros((2,4,6),np.uint)
b[0] = np.arange(1,25).reshape(4,6)
b[1] = a


def test_nlabels3d():
    """ Test of VTissuAnalysis.nlabels() method """

    analysis = VTissueAnalysis(b)
    assert analysis.nlabels() == 24

def test_center_of_mass3d():
    """ Test of VTissuAnalysis.center_of_mass() method """

    analysis = VTissueAnalysis(b)
    assert analysis.center_of_mass(7) == [0.80000000000000004, 0.80000000000000004, 2.2000000000000002]
    assert analysis.center_of_mass([7,2]) == [[0.80000000000000004, 0.80000000000000004, 2.2000000000000002],
                                             [0.75, 1.0, 0.75]]
    assert analysis.center_of_mass() == [[0.90909090909090906, 1.6363636363636365, 2.0909090909090908],
                                         [0.75, 1.0, 0.75],
                                         [0.80000000000000004, 1.2, 4.0],
                                         [0.5, 1.5, 3.0],
                                         [0.5, 0.5, 3.0],
                                         [0.5, 0.5, 3.0],
                                         [0.80000000000000004, 0.80000000000000004, 2.2000000000000002],
                                         [0.0, 1.0, 1.0],
                                         [0.0, 1.0, 2.0],
                                         [0.0, 1.0, 3.0],
                                         [0.0, 1.0, 4.0],
                                         [0.0, 1.0, 5.0],
                                         [0.0, 2.0, 0.0],
                                         [0.0, 2.0, 1.0],
                                         [0.0, 2.0, 2.0],
                                         [0.0, 2.0, 3.0],
                                         [0.0, 2.0, 4.0],
                                         [0.0, 2.0, 5.0],
                                         [0.0, 3.0, 0.0],
                                         [0.0, 3.0, 1.0],
                                         [0.0, 3.0, 2.0],
                                         [0.0, 3.0, 3.0],
                                         [0.0, 3.0, 4.0],
                                         [0.0, 3.0, 5.0]]

def test_volume3d():
    """ Test of VTissuAnalysis.volume() method """

    analysis = VTissueAnalysis(b)
    assert analysis.volume(7) == 5.0
    assert analysis.volume([7,2]) == [5.0, 4.0]
    assert analysis.volume() == [11.0,
                                 4.0,
                                 5.0,
                                 2.0,
                                 2.0,
                                 2.0,
                                 5.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0,
                                 1.0]

def test_neighbors3d():
    """ Test of VTissuAnalysis.neighbors() method """

    analysis = VTissueAnalysis(b)
    assert analysis.neighbors(7) == [(9, [1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 10.0, 13.0, 16.0])]
    assert analysis.neighbors([7,2]) == [(9, [1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 10.0, 13.0, 16.0]),
                                         (7, [1.0, 3.0, 6.0, 7.0, 8.0, 13.0, 14.0])]
    assert analysis.neighbors() == [ None,
                                     (7, [1.0, 3.0, 6.0, 7.0, 8.0, 13.0, 14.0]),
                                     (9, [1.0, 2.0, 4.0, 7.0, 9.0, 11.0, 12.0, 17.0, 18.0]),
                                     (6, [1.0, 3.0, 5.0, 7.0, 10.0, 22.0]),
                                     (6, [1.0, 4.0, 6.0, 7.0, 9.0, 11.0]),
                                     (5, [8.0, 1.0, 2.0, 12.0, 5.0]),
                                     (9, [1.0, 2.0, 3.0, 4.0, 5.0, 8.0, 10.0, 13.0, 16.0]),
                                     (5, [9.0, 2.0, 14.0, 6.0, 7.0]),
                                     (5, [8.0, 10.0, 3.0, 5.0, 15.0]),
                                     (5, [16.0, 9.0, 11.0, 4.0, 7.0]),
                                     (5, [17.0, 10.0, 3.0, 12.0, 5.0]),
                                     (4, [11.0, 18.0, 3.0, 6.0]),
                                     (4, [2.0, 19.0, 14.0, 7.0]),
                                     (5, [8.0, 2.0, 20.0, 13.0, 15.0]),
                                     (5, [16.0, 1.0, 21.0, 14.0, 9.0]),
                                     (5, [17.0, 10.0, 15.0, 22.0, 7.0]),
                                     (5, [11.0, 16.0, 18.0, 3.0, 23.0]),
                                     (4, [24.0, 17.0, 3.0, 12.0]),
                                     (3, [1.0, 20.0, 13.0]),
                                     (4, [1.0, 19.0, 21.0, 14.0]),
                                     (4, [1.0, 20.0, 22.0, 15.0]),
                                     (4, [16.0, 4.0, 21.0, 23.0]),
                                     (4, [24.0, 1.0, 22.0, 17.0]),
                                     (3, [1.0, 18.0, 23.0])]

def test_surface_area3d():
    """ Test of VTissuAnalysis.surface_area() method """

    analysis = VTissueAnalysis(a)
    assert analysis.surface_area(7,2) == 1
    assert analysis.surface_area(2,7) == 1


def test_extract_L1():
    """ Test of extract_L1 function"""
    L1 = extract_L1(a)
    assert L1 == [2, 3, 4, 5, 6, 7]

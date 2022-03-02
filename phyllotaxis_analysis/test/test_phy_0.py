#       
#
#       Copyright 2006 - 2010 INRIA - CIRAD - INRA  
#
#       File author(s): Yassin REFAHI <yassin.refahi@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################
__license__ = "Cecill-C"

from vplants.phyllotaxis_analysis.analysis_functions import *

def test1():
    seq = [120, 145, 280, 220, 270, 150, 145, 115, 135, 280, 225, 70, 240, 260, 145, 125, 285, 225, 260, 285, 235, 260, 145]
    intervalsDict = {}
    intervalsDict[137.5] = [104, 170]
    intervalsDict = {137.5: [104, 170], 222.5: [195, 255], 52.5: [5, 79], 275: [241, 308], 85: [57, 118], 190: [156, 217], 327.5: [294, 14]}
    tree_indices = codeSequence(seq, 3, 137.5, intervalsDict, kappa = 10.4, threshold =0.05 )
    prediction, notExplained, newInversion, invalides = extractSequences(tree_indices, seq, 3, 137.5, True)
    assert prediction == [137.5, 137.5, 275, 222.5, 275, 137.5, 137.5, 137.5, 137.5, 275, 222.5, 52.5, 222.5, 275, 137.5, 137.5, 275, 222.5, 275, 275, 222.5, 275, 137.5]


def test_doc():
    # Copy the tutorial in this test and test the results.
    permutationBlockMaxSize, canonicalAngle = 3, 137.5
    assert theoretical_divergence_angles(permutationBlockMaxSize, canonicalAngle) == ([85.0, 222.5, 137.5, 275.0, 52.5, 190.0, 327.5], [-2, -1, 1, 2, 3, 4, 5])
    theoreticalAnglesIntervals = {137.5: [104, 170],
                                      222.5: [195, 255],
                                      52.5: [5, 79],
                                      275: [241, 308],
                                      85: [57, 118],
                                      190: [156, 217],
                                      327.5: [294, 14]}
    
    seqTA = [137.5, 137.5, 275, 222.5, 275, 137.5]
    assert isNadmissible(seqTA, 137.5) == (2, ([[4, 3]], [0, 1, 2, 4, 3, 5, 6]))
    assert isNadmissible(seqTA, 137.5, 2) == (2, ([[4, 3]], [0, 1, 2, 4, 3, 5, 6]))
    
    orderIndexSeries = [0, 1, 2, 4, 3, 5, 6]
    assert isNAdmissibleIntegers(orderIndexSeries, 2) == (True, [[4, 3]])
    
    measuredSeq = [120, 145, 280, 220, 270, 150, 145, 115, 135, 280, 225, 70, 240, 260, 145, 125, 285, 225, 260, 285, 235, 260, 145]
    ListOfTreesIndex = codeSequence(measuredSeq, 3, 137.5, theoreticalAnglesIntervals, kappa = 10.4, threshold = 0.05 )
    
    bestSequence, notExpalinedAngles, validPermutations, invalids = extractSequences(ListOfTreesIndex, measuredSeq, 3, 137.5)
    
    assert bestSequence == [137.5, 137.5, 275, 222.5, 275, 137.5, 137.5, 137.5, 137.5, 275, 222.5, 52.5, 222.5, 275, 137.5, 137.5, 275, 222.5, 275, 275, 222.5, 275, 137.5]


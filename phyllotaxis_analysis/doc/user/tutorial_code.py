from vplants.phyllotaxis_analysis.analysis_functions import *

measuredSeq = [120, 145, 280, 220, 270, 150, 145, 115, 135, 280, 225, 70, 240, 260, 145, 125, 285, 225, 260, 285, 235, 260, 145]

permutationBlockMaxSize, canonicalAngle = 3, 137.5

theoretical_divergence_angles(permutationBlockMaxSize, canonicalAngle)

theoreticalAnglesIntervals = {137.5: [104, 170],
                                      222.5: [195, 255],
                                      52.5: [5, 79],
                                      275: [241, 308],
                                      85: [57, 118],
                                      190: [156, 217],
                                      327.5: [294, 14]}
    
seqTA = [137.5, 137.5, 275, 222.5, 275, 137.5]

isNadmissible(seqTA, 137.5) 

isNadmissible(seqTA, 137.5, 2) 
    
orderIndexSeries = [0, 1, 2, 4, 3, 5, 6]

isNAdmissibleIntegers(orderIndexSeries, 2) 
    
ListOfTreesIndex = codeSequence(measuredSeq, 3, 137.5, theoreticalAnglesIntervals, kappa = 10.4, threshold = 0.05 )
    
bestSequence, notExpalinedAngles, validPermutations, invalids = extractSequences(ListOfTreesIndex, measuredSeq, 3, 137.5)
    


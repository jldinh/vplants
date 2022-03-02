#       
#
#       Copyright 2006 - 2011 INRIA - CIRAD - INRA  
#
#       File author(s): Yassin REFAHI <yassin.refahi@inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
################################################################################

"""
This module contains the functions used to detect permutations in sequences of divergence angles.
"""

import copy
from itertools import product, izip
import numpy as np
from scipy.special import i1, i0
from nAdmissibleTree_implementation import nAdmissibleTree 


def counterClockWise(angles):
    """
    `` change the orientation of a sequence of divergence angles
    
    :Parameters:
    -   `angleList`    -    sequence of divergence angles
    
    :Returns:
    -    If  `angleList` is in clockwise (or counterclockwise) orientation `` returns the sequence of divergence angles in counterclockwise orientation (or clockwise orientation respectively) 
    """
    return [360 - i for i in angles]    

class EqualTheorAngles(Exception):
    """
    Raised when different multiples of canonical angles modulo 360 leads to the same value   
    """
    def __str__(self):
        s= """There are equal theoretical divergence angles!
A slight change in the value of the canonical angle can solve this problem. """
        return s

def theoretical_divergence_angles(permutationBlockMaxSize, alpha):
    """ 
    calculate all possible theoretical angles both in degrees and integers representing coefficients of canonical angles.
    
    :Parameters:
    -    `permutationBlockMaxSize`    -    maximum number of organs involved in permutations 
    -    `alpha`    -    canonical divergence angle (examples: 137.5, 99.5, ...)
    
    :Returns:
    -   `D_n`    -     list of theoretical divergence angles
    -   `D_n_coefficients`    -    list of theoretical divergence angles as list of integers representing coefficients of canonical angles.
    """
    D_n_coefficients = [ i for i in xrange(1 - permutationBlockMaxSize , 2 * permutationBlockMaxSize) if i != 0 ]
    D_n = [(coef * alpha) % 360 for coef in D_n_coefficients]
    for i in xrange(3 * permutationBlockMaxSize - 3):
        for j in xrange(i + 1, 3 * permutationBlockMaxSize - 3):
            if D_n[i] == D_n[j]:
                raise EqualTheorAngles(D_n)
    return D_n, D_n_coefficients

def circularStdDev(kappa):
    """
    calculate circular standard deviation from a concentration parameter
    
    :Parameters:
    -    `kappa`    -    concentration parameter
    
    :Returns:
    -    circular standard deviation
    """
    return 180.0/np.pi * (np.sqrt(-2 * np.log(i1(kappa)/i0(kappa))))

def myVMpdf(x, mu, kappa):
    """
    calculate circular probability density function
    
    :Parameters:
    -    `x`    -    measured angle
    -   `mu`    -    theoretical angle
    -   `kappa`    -    concentration parameter
    
    :Returns:
    -    circular probability 
    """
    return 1.0 / (360 * i0(kappa)) * np.exp( kappa * np.cos(np.radians(x) - np.radians(mu)) * (np.pi /180) )

def probOfAngle(x, mu, kappa, tAngles):
    """
    calculate probability of assigning a theoretical angle to a measured angle
    
    :Parameters:
    -    `x`    -    measured angle
    -   `mu`    -    theoretical angle
    -   `kappa`    -    concentration parameter
    -   `tAngles`    -    list of theoretical angles
    
    :Returns:
    -    probability of assigning of `mu` to `x`
    """
    Sum = sum(myVMpdf(y, mu, kappa) for y in tAngles)
    return myVMpdf(x, mu, kappa) / Sum

def logOfProbOfAngle(x, mu, kappa, tAngles):
    """
    calculate logarithmic value of probability of assigning a theoretical angle to a measured angle
    
    :Parameters:
    -    `x`    -    measured angle
    -   `mu`    -    theoretical angle
    -   `kappa`    -    concentration parameter
    -   `tAngles`    -    list of theoretical angles
    
    :Returns:
    -    logarithmic value of probability of assigning of `mu`, to `x`
    """
    Sum = sum(myVMpdf(y, mu, kappa) for y in tAngles)
    return np.log(myVMpdf(x, mu, kappa)) - np.log(Sum)


def maxProbAngle(x, kappa, theoreticalAngles):
    """
    calculate the list of most probable theoretical angles 
    
    :Parameters:
    -    `x`    -    measured angle
    -   `mu`    -    theoretical angle
    -   `theoreticalAngles`    -    list of theoretical angles
    
    :Returns:
    -    list of most probable theoretical angles that can be assigned to `x`   
    """
    probList = [probOfAngle(x, tAngle, kappa, theoreticalAngles) for tAngle in theoreticalAngles ]
    maxProb = max(probList)
    # Use ienumerate rather than xrange
    maxProbAngleList = [theoreticalAngles[i] for i in xrange(len(probList)) if probList[i] == maxProb]
    return maxProbAngleList

def candidateAngles(angle, bordersDict):
    """ 
    find the theoretical angles that may correspond to a measured angle
    
    :Parameters:
    -   `angle`    -    measured angle
    -    `bordersDict`    -    dictionary of theoretical angles and corresponding intervals
    
    :Returns:
    -    possible theoretical angles for `angle`

    """
    candidates = list()
    for tAngle in bordersDict:
        B = bordersDict[tAngle]
        if B[0] < tAngle < B[1] and B[0] < angle < B[1]:
            candidates.append(tAngle)
        if (tAngle < B[0]) and (tAngle < B[1]):
            if (0 <= angle < B[1]) or (B[0] < angle < 360):
                candidates.append(tAngle)
        if (tAngle > B[0]) and (tAngle > B[1]):
            if (B[0] <= angle < 360) or (0 < angle < B[1]):
                candidates.append(tAngle)
    return candidates

def candidateAnglesList(angles, bordersDict):
    """
    calculate list of possible theoretical angles for a list of measured angle
     
    Returns list of possible theoretical angles for a list of measured angle 
    
    :Parameters:
    -   `angles`    -    measured angle
    -    `bordersDict`    -    dictionary of theoretical angles and corresponding intervals
    
    :Returns:
    -    list of possible theoretical angles for `itemList`
    """
    candidatesList = (candidateAngles(angle, bordersDict) for angle in angles)
    return product(* candidatesList)


def isSubSequence(seq1, seq2):
    """
    check whether one sequence is subsequence of the other.
    
    :Parameters:
    -    seq1    -    a sequence of angles
    -    seq2    -    a sequence of angles
    
    :Returns:
    -    True if `seq1` is a subsequence of `seq2`, otherwise returns False. 
    """
    if len(seq1) > len(seq2):
        return False
    for i, j in izip(seq1, seq2):
        if i != j:
            return False
    return True

def isPermutation(seq, minElement, n):
    """
    check whether the entered list is a permutation of  successive integers.
    
    :Parameters:
    -   `seq` -    a sequence of integers
    -   `n`    -    an integer
    -   `minElement`    -    an integer
    
    :Returns:
    -    True if `seq` is a permutation of  `[minElement, ...., minElement + n - 1]`
    """
    Psi = [0 for i in xrange(n)]
    for i in seq:
        if minElement <= i <= minElement + n - 1:
            Psi[i - minElement] += 1
        else:
            return False
    for i in Psi:
        if i != 1:
            return False
    return True

def isN_admissible2(seq, n, canonicalAngle, D_n_coeffDict):
    """
    check whether an entered sequence is an `n`-admissible sequence.
    
    :Parameters:
    -    `seq`    -    a sequence of theoretical angles
    -   `n`    -    maximum number of organs involved in permutations
    -    `canonicalAngle`    -    canonical divergence angle
    -    `D_n_coeffDict`    -    dictionary of theoretical angles and their coefficients
    
    :Returns:
    -    True if the `seq` is `n`-admissible, otherwise it returns False. Also list of permutations
    """
    sequenceLength = len(seq)
    coeffSeq = [D_n_coeffDict[angle] for angle in seq]
    absoluteAngles = [sum(coeffSeq[:i]) for i in xrange(sequenceLength + 1)]
    Min = min(absoluteAngles)
    if Min != 0:
        newAbsAngles = [i - Min for i in absoluteAngles]
        absoluteAngles = newAbsAngles
    index = 0
    permutations = list()
    notExplained = list()
    while index <= sequenceLength :
        if absoluteAngles[index] != index:
            k = sequenceLength - index + 1
            maxDepth = n if n < k else k # Attention: if maxDepth == k it means that we are in the end of string! 
            for depth in xrange(2, maxDepth + 1):
                if isPermutation(absoluteAngles[index: index + depth], index, depth):
                    permutations.append(absoluteAngles[index: index + depth])
                    index += depth 
                    break                
            else:
                notExplained.append(absoluteAngles[index])
                index += 1
        else:
            index += 1
    return len(notExplained) == 0, permutations

def isN_admissible_firstAngles(seq, n, canonicalAngle, D_n_coeffDict):
    """
    check whether an entered sequence is an `n`-admissible sequence by taking into account a possible permutation at the beginning of the sequence.
    
    :Parameters:
    -    `seq`    -    a sequence of theoretical angles
    -   `n`    -    maximum number of organs involved in permutations
    -    `canonicalAngle`    -    canonical divergence angle
    -    `D_n_coeffDict`    -    dictionary of theoretical angles and their coefficients
    
    :Returns:
    -    True if the `seq` is `n`-admissible, otherwise False  
    -    `permutations`    -    list of permutations
    -   `U`    -    order index series
    """
    sequenceLength = len(seq)
    coeffSeq = [D_n_coeffDict[angle] for angle in seq]
    absoluteAngles = [sum(coeffSeq[:i]) for i in xrange(sequenceLength + 1)]
    Min = min(absoluteAngles)
    if Min != 0:
        U = [i - Min for i in absoluteAngles]
    else:
        U = absoluteAngles
    pMap = [0 for i in xrange(sequenceLength + 1)]
    for i in U:
        if i > sequenceLength :
            return False, [], U
        else:
            pMap[i] += 1
    for i in pMap:
        if i <> 1 :
            return False, [], U
    permutations = []
    i = 0
    while i <= sequenceLength :
        if U[i] != i:
            lower = U[i]
            upper = U[i]
            j = i + 1
            while True:
                if j > sequenceLength:
                    i = sequenceLength + 1
                    break
                if U[j] < lower:
                    lower = U[j]
                if U[j] > upper:
                    upper = U[j]
                if j - i > n - 1:
                    return False, permutations, U
                if lower == i and upper == j:
                    permutations.append(U[i: j + 1])
                    i = j + 1
                    break
                j += 1
        else:
            i += 1
    return True, permutations, U

def isNAdmissibleIntegers(U, n):
    """
    check whether an entered sequence of integers is an order index series of any `n`-admissible sequence.
    
    :Parameters:
    -    `U`    -    a sequence of integers
    -   `n`    -    maximum number of organs involved in permutations
    
    :Returns:
    -    True if the `seq` is `n`-admissible, otherwise False  
    -    `permutations`    -    list of permutations
    """
    sequenceLength = len(U)
    pMap = [0 for i in xrange(sequenceLength)]
    for i in U:
        if i > sequenceLength :
            return False, []
        else:
            pMap[i] += 1
    for i in pMap:
        if i <> 1 :
            return False, []
    permutations = []
    i = 0
    while i < sequenceLength :
        if U[i] != i:
            lower = U[i]
            upper = U[i]
            j = i + 1
            while True:
                if j > sequenceLength:
                    i = sequenceLength + 1
                    break
                if U[j] < lower:
                    lower = U[j]
                if U[j] > upper:
                    upper = U[j]
                if j - i > n - 1:
                    return False, permutations, U
                if lower == i and upper == j:
                    permutations.append(U[i: j + 1])
                    i = j + 1
                    break
                j += 1
        else:
            i += 1
    return True, permutations

def isNadmissible(seq, canonicalAngle, permutationBlockMaxSize = None):
    """
    check whether an entered sequence is an `n`-admissible sequence 
    
    :Parameters:
    -    `seq`    -    a sequence of theoretical angles
    -    `canonicalAngle`    -    canonical divergence angle
    -    `permutationBlockMaxSize`    -    maximum number of organs involved in a permutation 
    
    :Returns:
    -    True if the `seq` is `n`-admissible, otherwise False
    -    `permutations`    -    list of permutations
    -   `U`    -    order index series
    """
    if permutationBlockMaxSize == None:
        for n in xrange(1, len(seq) + 1):
            theoreticalAngles, theoreticalCoeffAngles = theoretical_divergence_angles(n, canonicalAngle)
            D_n_coeffDict = dict( (theoreticalAngles[i], theoreticalCoeffAngles[i]) for i in xrange(3 * n - 2) )
            try:
                res = isN_admissible_firstAngles(seq, n, canonicalAngle, D_n_coeffDict)
            except KeyError:
                continue
            if res[0]:
                return n, res[1:]
        return 0, [], []
    else:
        theoreticalAngles, theoreticalCoeffAngles = theoretical_divergence_angles(permutationBlockMaxSize, canonicalAngle)
        D_n_coeffDict = dict( (theoreticalAngles[i], theoreticalCoeffAngles[i]) for i in xrange(3 * permutationBlockMaxSize - 2) )
        res = isN_admissible_firstAngles(seq, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
        if res[0]:
            return permutationBlockMaxSize, res[1:]
        else:
            return 0, [], []

def isN_admissible_notFirstAngles(seq, n, canonicalAngle, D_n_coeffDict):
    """
    check whether an entered sequence is an `n`-admissible sequence without taking into account a possible permutation at the beginning of the sequence.
    
    :Parameters:
    -    `seq`    -    a sequence of theoretical angles
    -   `n`    -    maximum number of organs involved in permutations
    -    `canonicalAngle`    -    canonical angle
    -    `D_n_coeffDict`    -    dictionary of theoretical angles and their coefficients
    
    :Returns:
    -    True if the `seq` is `n`-admissible, otherwise False  
    -    `permutations`    -    list of permutations
    -   `U`    -    order index series
    """
    sequenceLength = len(seq)
    if seq[0] not in D_n_coeffDict:
        return False, [], []
    coeffSeq = [D_n_coeffDict[angle] for angle in seq]
    U = [sum(coeffSeq[:i]) for i in xrange(sequenceLength + 1)]
    pMap = [0 for i in xrange(sequenceLength + 1)]
    for i in U:
        if i > sequenceLength or i < 0:
            return False, [], U
        else:
            pMap[i] += 1
    for i in pMap:
        if i <> 1 :
            return False, [], U
    permutations = []
    i = 0
    while i <= sequenceLength :
        if U[i] != i:
            lower = U[i]
            upper = U[i]
            j = i + 1
            while True:
                if j > sequenceLength:
                    i = sequenceLength + 1
                    break
                if U[j] < lower:
                    lower = U[j]
                if U[j] > upper:
                    upper = U[j]
                if j - i > n - 1:
                    return False, permutations, U
                if lower == i and upper == j:
                    permutations.append(U[i: j + 1])
                    i = j + 1
                    break
                j += 1
        else:
            i += 1
    return True, permutations, U

def isN_admissibleU(seqU, n):
    """
    check whether an entered order index series corresponds to an `n`-admissible sequence
    
    :Parameters:
    -    `seqU`    -    order index series
    -   `n`    -    an integer

    :Returns:
    -    True if the `seq` is `n`-admissible, otherwise False  
    -    `inversionList`    -    list of permutations
    """
    sequenceLength = len(seqU) - 1
    absoluteAngles = seqU
    index = 0
    inversionList = list()
    notExplained = list()
    while index <= sequenceLength :
        if absoluteAngles[index] != index:
            k = sequenceLength - index + 1
            maxDepth = n if n < k else k # Attention: if maxDepth == k it means that we are in the end of string! 
            for depth in xrange(2, maxDepth + 1):
                if isPermutation(absoluteAngles[index: index + depth], index, depth):
                    inversionList.append(absoluteAngles[index: index + depth])
                    index += depth 
                    break                
            else:
                notExplained.append(absoluteAngles[index])
                index += 1
        else:
            index += 1
    return len(notExplained) == 0, inversionList   

def listsComplementAsSet(LOfL1, removeList):
    """
    return relative complement, given two lists of list (that should be considered as a list).
    
    :Parameters:
    -    `LOfL1`    - a list of lists
    -   `removeList`    -    a list of list
     
    :Returns:
    `complements`    -    relative complement of `removeList` to `LOfL1`  
       
    """
    complements = []
    for lm in LOfL1:
        flag = False
        for lr in removeList:
            if ( set(lr) == set(lm) ):
                flag = True
        if not flag:
            complements.append(lm)
    return complements


def invalidateSeq(S, notExplained, permutationBlockMaxSize):
    """
    invalidate permutations preceding a not explained angles down to a splitting point
    
    :Parameters:
    -    `S`    - sequence of divergence angles
    -   `notExplained`    -    list of not explained angles
    -    `permutationBlockMaxSize`    -    maximum number of organs involved in permutations
     
    :Returns:
    `invalid`    -    list of invalidated angles  
    """
    invalide = []
    if len(notExplained) == 0:
        return invalide
    notExplained.sort()
    subSeq = []
    first = -1
    for i in notExplained: 
        subSeq.append(S[first + 1 : i + 1])
        first = i
    if len(S[notExplained[-1] + 1:]) != 0: 
        subSeq.append(S[notExplained[-1] + 1:])
    UsubSeq = []
    for s in subSeq:
        u = [sum(s[:i]) for i in xrange(len(s))]
        Min = min(u)
        if Min != 0:
            u = [i - Min for i in u]
        UsubSeq.append(u)
    LenUsubSeq = [len(u) for u in UsubSeq]
    LenSsubSeq = [len(s) for s in subSeq]
    counter = 0
    ind = 0
    if notExplained[-1] == len(S) - 1:
        newUSubSeq = list(UsubSeq)
    else:
        newUSubSeq = list(UsubSeq[:-1])
    for U in newUSubSeq:
        i = len(U) 
        result, inversions = isN_admissibleU(U, permutationBlockMaxSize)
        if  len(subSeq[counter]) > 1:
            marked = False
            for j in xrange(i - 1, -1, -1):
                if U[j] == j:
                    isInInverions = False
                    for l1 in inversions:
                        if j in l1:
                            isInInverions = True
                            break
                    if not isInInverions:
                        if j + 1 != i: # if j + 1 == i this means that there is no inversion before the not explained angle
                            invalide.append([j  + ind, i  + ind - 2]) #([j + 1 + ind,i - 1 + ind])
                        marked = True
                        break
            if not marked:
                invalide.append([0 + ind, i + ind - 2])
        ind += len(subSeq[counter])
        counter += 1
    return invalide


def codeSequence(seq, permutationBlockMaxSize, canonicalAngle, bordersDict, kappa, threshold):
    """
    make list of `n`-admissible trees coding sequence of measured angles
    
    :Parameters:
    -   `seq`    -    sequence of measured angles
    -   `permutationBlockMaxSize` -     maximum number of organs involved in permutations
    -    `canonicalAngle`    -    canonical divergence angle
    -   `bordersDict`    -    dictionary of theoretical angles and the corresponding intervals
    -   `kappa`    -    concentration parameter
    -    `threshold`    -    a statistical threshold to prune the `n`-admissible trees
    
    :Returns:
    -    `treesIndexes`    -    a list of `[n-admissible tree, index]` such that each tree in the list is an n-admissible tree coding to `seq[(index - 1): index]`
    """
    D_n, D_n_Coeff = theoretical_divergence_angles(permutationBlockMaxSize, canonicalAngle)
    D_n_coeffDict = dict( (D_n[i], D_n_Coeff[i]) for i in xrange(3 * permutationBlockMaxSize - 2) )
#    weights = weightsFunc(theoreticalAngles)
    sequenceLength = len(seq)
    treesIndexes = list()
    index = 0
    while index <= sequenceLength - 1:
        if index == 0:
            tree = makeNAdmissibleTree(seq[index: ], permutationBlockMaxSize, canonicalAngle, bordersDict, threshold, D_n, D_n_Coeff, D_n_coeffDict, kappa, seqBegin = True)
        else:
            tree = makeNAdmissibleTree(seq[index: ], permutationBlockMaxSize, canonicalAngle, bordersDict, threshold, D_n, D_n_Coeff, D_n_coeffDict, kappa, D_n_coeffDict)
        index += tree.getMaxLevel() + 1
        treesIndexes.append([tree,index - 1])
    return treesIndexes
  
def makeNAdmissibleTree(seq, permutationBlockMaxSize, canonicalAngle, bordersDict, threshold, D_n, theoreticalCoeffAngles, D_n_coeffDict, kappa, seqBegin = False):
    """
    make `n`-admissible tree coding sequence of measured angles. It stops when it can not code an angle, i.e. at a not explained angle
    
    :Parameters:
    -   `seq`    -    sequence of measured angles
    -   `permutationBlockMaxSize` -     maximum number of organs involved in permutations
    -    `canonicalAngle`    -    canonical divergence angle
    -   `bordersDict`    -    dictionary of theoretical angles and the corresponding intervals
    -   `kappa`    -    concentration parameter
    -    `threshold`    -    a statistical threshold to prune the `n`-admissible trees
    -    `D_n`    -    list of theoretical angles
    -    `theoreticalCoeffAngles`    -    list of coefficients of theoretical angles 
    -    `D_n_coeffDict`    -    dictionary of theoretical angles and their coefficients
    -    `kappa`    -    concentration parameter
    -    `seqBegin` - indicates whether permutations at the beginning of the sequence should be taken into account 
    
    :Returns:
    -   `n`-admissible tree
    """
    sequenceLength = len(seq)
    nAdmTree = nAdmissibleTree()
    index = 0 # the index of seq
    # Initializing tree
    possible = list()
    candidates = list()
    horizon = min(sequenceLength - index, permutationBlockMaxSize)
    for i in xrange(0, horizon):
        possible = candidateAnglesList(seq[index: index + i + 1], bordersDict)
        if seqBegin:
            for pos in possible:
                nadmList = isN_admissible_firstAngles(pos, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
                if nadmList[0]:
                    candidates.append([pos, nadmList[2]])
        else:
            for pos in possible:
                nadmList = isN_admissible_notFirstAngles(pos, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
                if nadmList[0]:
                    candidates.append([pos, nadmList[2]])
            
    candLen = len(candidates)
    notSubseq = np.ones(candLen)
    for j in xrange(candLen):
        for i in xrange(j + 1, candLen):
            if isSubSequence(candidates[j][0], candidates[i][0]):
                notSubseq[i] = 0
    newCandidates = [candidates[i] for i in xrange(candLen) if notSubseq[i]]
    candidatesProb = list()
    for pos in newCandidates:
        for i in xrange(len(pos[0])):
            if probOfAngle(seq[index + i], pos[0][i], kappa, D_n) <= threshold:
                break
        else:
            candidatesProb.append(pos)

    if candidatesProb == []:
        for affectedAngle in maxProbAngle(seq[index], kappa, D_n):
            pbAngle = probOfAngle(seq[index], affectedAngle, kappa, D_n)
            logPbAngle = logOfProbOfAngle(seq[index ], affectedAngle, kappa, D_n)
#            tree.addMarkedNodeProb(tree.treeRoot().id ,[ affectedAngle, index, pbAngle, logPbAngle, "null"])
            nAdmTree.addChild(parent = nAdmTree.root, value = affectedAngle, level = index, pbAngle = pbAngle, logPbAngle = logPbAngle, questionMark = True, orderIndex = "null")
            
        return nAdmTree
    else:
        for pos in candidatesProb:
            treePos = list() # treePos is a list of affected values and their level in the tree.
            currentID = nAdmTree.root
            for i in xrange(len(pos[0])):
                pbAngle = probOfAngle(seq[index + i], pos[0][i], kappa, D_n )
                logPbAngle = logOfProbOfAngle(seq[index + i], pos[0][i], kappa, D_n)
                orderIndex = pos[1][i + 1]
                treePos.append([pos[0][i], index + i, pbAngle, logPbAngle, orderIndex])
            nAdmTree.addListValueLevelProb(nAdmTree.root, treePos)
    # Initializing tree finished
    while True:
        leavesNotLast = nAdmTree.leavesNotLast(sequenceLength - 1) #The leaves whose level are less than sequenceLength - 1
        if len(leavesNotLast) == 0:
            return nAdmTree
        leavesNotLastNotQuestion = [vertex for vertex in leavesNotLast if (not nAdmTree.get_vertex_property(vertex)["questionMark"]    )]
        if leavesNotLastNotQuestion == []: # all leaves whose levels are less than sequenceLength - 1 have question marks
            leaves = nAdmTree.leaves()
            if nAdmTree.leavesLast(sequenceLength - 1) == []:
                
                maxLevel = nAdmTree.getMaxLevel()
                for feuille in leaves:
                    
                    if nAdmTree.get_vertex_property(feuille)["level"] != maxLevel:
                        ver = feuille
                        while nAdmTree.is_leaf(ver):
                            pid = nAdmTree.parent(ver)
                            nAdmTree.remove_vertex(ver)
                            ver = pid
                return nAdmTree
            else:
                for vertex in leavesNotLast:
                    ver = copy.deepcopy(vertex)
                    while nAdmTree.is_leaf(ver):
                        pid = nAdmTree.parent(ver)
                        nAdmTree.remove_vertex(ver)
                        ver = pid
                return nAdmTree
        for leaf in leavesNotLastNotQuestion:
            index = nAdmTree.get_vertex_property(leaf)["level"] + 1
            pid = leaf
            possible = list()
            candidates = list()
            horizon = min(sequenceLength - index, permutationBlockMaxSize)        
            for i in xrange(0, horizon):
                possible = candidateAnglesList(seq[index: index + i + 1], bordersDict)
                if index <= permutationBlockMaxSize:
                    for pos in possible:
                        pathRoot = nAdmTree.pathToRoot(leaf)
                        newPos = list(pathRoot)
                        newPos.extend(pos)
                        if seqBegin:  # here a voir
                            nadmList = isN_admissible_firstAngles(newPos, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
                        else:
                            nadmList = isN_admissible_notFirstAngles(newPos, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
                        if nadmList[0]:
                            candidates.append([pos, nadmList[2][len(pathRoot): ]])
                else:
                    for pos in possible:
                        newPos = list(pos)
                        newPos[0] = (newPos[0] + (nAdmTree.get_vertex_property(leaf)["orderIndex"] - index)* canonicalAngle) % 360
                        nadmList = isN_admissible_notFirstAngles(newPos, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
                        if nadmList[0]:
                            candidates.append([pos, [index + i for i in nadmList[2]]])
            candLen = len(candidates)
            notSubseq = np.ones(candLen)
            for j in xrange(candLen):
                for i in xrange(j + 1, candLen):
                    if isSubSequence(candidates[j][0], candidates[i][0]):
                        notSubseq[i] = 0
            newCandidates = [candidates[i] for i in xrange(candLen) if notSubseq[i]]
            candidatesProb = list()
            for pos in newCandidates:
                for i in xrange(len(pos[0])):
                    if probOfAngle(seq[index + i], pos[0][i], kappa, D_n) <= threshold:
                        break
                else:
                    candidatesProb.append(pos)
            if candidatesProb == []:
                for affectedAngle in maxProbAngle(seq[index], kappa, D_n):
                    pbAngle = probOfAngle(seq[index], affectedAngle, kappa, D_n)
                    logPbAngle = logOfProbOfAngle(seq[index ], affectedAngle, kappa, D_n)
                    nAdmTree.addChild(parent = pid, value = affectedAngle, level = index, pbAngle = pbAngle, logPbAngle = logPbAngle, questionMark = True, orderIndex = "null")
            else:
                for pos in candidatesProb:
                    treePos = list() # treePos is a list of affected values and their level in the tree.
                    for i in xrange(len(pos[0])):
                        pbAngle = probOfAngle(seq[index + i], pos[0][i], kappa, D_n)
                        logPbAngle = logOfProbOfAngle(seq[index + i], pos[0][i], kappa, D_n)
                        orderIndex = pos[1][i + 1]
                        treePos.append([pos[0][i], index + i, pbAngle, logPbAngle, orderIndex])
                    nAdmTree.addListValueLevelProb(pid, treePos)

def subInvalidateLast(inversions, last):
    """
    identify from a list of permutations, those that should be invalidated given an element of an invalid permutation
    
    :Parameters:
    -    `inversions`    -    list of permutations
    -    `last`    -    an element of an invalid permutation
    
    :Returns:
    `invalidate`    -    list of invalid permutations
    """
    if inversions == [] or last not in inversions[-1]:
        return []
    invalidate = [inversions[-1]]
    m = min(inversions[-1])
    for i in xrange(len(inversions) - 2, -1, -1):
        if m - 1 == max(inversions[i]):
            invalidate.append(inversions[i])
            m = min(inversions[i])
        else:
            break
    return invalidate

def extractSequences(treesIndexes, seq, permutationBlockMaxSize, canonicalAngle, probCheck = True):
    """
    extract `n`-admissible sequences from a list of n-admissible trees
    
    :Parameters:
    -   `treesIndexes`    -    a list of `[n-admissible tree, index]` such that each tree in the list is the n-admissible tree coding `seq[(index - 1): index]`
    -   `seq`    -    sequence of measured angles
    -   `permutationBlockMaxSize` -     maximum number of organs involved in permutations
    -    `canonicalAngle`    -    canonical divergence angle
     
    
    :Returns:
    -   `prediction`    -    prediction, i.e. list of theoretical angles coding `seq`
    -   `notExplainedList`    -    list of not explained angles
    -   `validPermutations`    -    list of valid permutations
    -   `invalids`    -    list of invalidated permutations
    """
    theoreticalAngles, theoreticalCoeffAngles = theoretical_divergence_angles(permutationBlockMaxSize, canonicalAngle)
    D_n_coeffDict = dict( (theoreticalAngles[i], theoreticalCoeffAngles[i]) for i in xrange(3 * permutationBlockMaxSize - 2) )
    index = 0
    bestSeq = []
    bestProb = 0
    for treeIndex in treesIndexes:
        bestPath = []
        seqList = []
        maxProb = None
        for pathAll in treeIndex[0].allPathsAll():
            result, inversionList = isN_admissible2(pathAll[0], permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
            if not result: 
                result, inversionList = isN_admissible2(pathAll[0][:-1], permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
            newInversionList = list()
            for inversion in inversionList:
                newInversion = [j + index for j in inversion]
                newInversionList.append(newInversion)
            seqList.append(pathAll)
            if maxProb == None:
                maxProb = pathAll[3]
            elif maxProb < pathAll[3]:
                maxProb = pathAll[3]
        for pathAll in seqList:
            if pathAll[3] == maxProb:
                bestPath.append(pathAll)
                break #???
        bestProb += maxProb
        bestSeq.append(bestPath)
        index = treeIndex[1] + 1
    ind = 0
    notExplainedList = []
    prediction = [] 
    inversions = []
    allProb = []
    for sList in bestSeq:
        for pathAll in sList:
            prediction.extend(pathAll[0])
            if probCheck:
                allProb.extend(pathAll[1])
            notExplainedList.extend([j[1] + ind for j in pathAll[2]])
            result, inversionList = isN_admissible2(pathAll[0], permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
            if not result: 
                result, inversionList = isN_admissible2(pathAll[0][:-1], permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
            newInversionList = list()
            for inversion in inversionList:
                newInversion = [j + ind for j in inversion]
                newInversionList.append(newInversion)
            inversions.extend(newInversionList)
            ind += len(pathAll[0])
    notExplainedAngles = [seq[j] for j in notExplainedList]
    D_n , D_n_com = theoretical_divergence_angles(permutationBlockMaxSize, canonicalAngle)
    code = dict((D_n[j], D_n_com[j]) for j in xrange(len(D_n)) )
    codedSeqNow = [code[j] for j in prediction]
    
    ssList = []
    ends = []
    for l in treesIndexes:
        ends.append(l[1])
    if prediction[0 : ends[0] + 1] != []:
        subSeqs = [prediction[0 : ends[0] + 1]]
    else:
        subSeqs = []
    for i in xrange(len(ends) - 1):
        subSeqs.append(prediction[ends[i] + 1: ends[i + 1] + 1])
    if prediction[ends[-1] + 1: len(prediction)] != []:    
        subSeqs.append(prediction[ends[-1] + 1: len(seq)])
        
    invalideCounter = 0
    ind = 0
    for ss in subSeqs:
        res = isN_admissible_firstAngles(ss, permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
        if res[0]:
            ssList.append([ss, res[1], []])    
        elif len(ss) > 1:
            res = isN_admissible_firstAngles(ss[:-1], permutationBlockMaxSize, canonicalAngle, D_n_coeffDict)
            invalides = subInvalidateLast(res[1], len(ss) - 1)
            for inv in invalides:
                invalideCounter += len(inv)
            ssList.append([ss, res[1], invalides])
        else:
            ssList.append([ss, res[1], []])
        
        ind += len(ss)
    invalideCounter += len(notExplainedList)
    invalids = invalidateSeq(codedSeqNow, notExplainedList, permutationBlockMaxSize)
    validPermutations = listsComplementAsSet(newInversionList, invalids)
    return prediction, notExplainedList, validPermutations, invalids






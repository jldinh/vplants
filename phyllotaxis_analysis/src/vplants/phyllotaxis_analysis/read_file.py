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

__doc__ = """
This module contains a class and some functions to read and extract data from a csv file.
We suppose that the data for each plant is stored in a column. 
"""

import csv

def readCSVFile(filename):
    """
    Read and extract data from a csv file, supposed that the data for each plant is stored in a column.
    
    :Parameters:
    -    `filename`    - file name to read
     
    :Returns:
    `angles`    -    list of sequences of divergence angles 
    """
    fobj = file(filename, 'r')
    readerObj = csv.reader(fobj, delimiter = '\t')
    mainList = [list(row) for row in readerObj]
    angles = [[int(angle) for angle in row if angle != "" ] for row in mainList]
    fobj.close()
    return angles

def withOutExtension(filename):
    """
    Return the filename without the extension.
    
    :Parameters:
    -    `filename`    - file name 
     
    :Returns:
    
    file name without extension 
    """
    for i in xrange(len(filename) - 1, -1 , - 1):
        if filename[i] == '.':
            return filename[:i]
    return filename

def extension(filename):
    """
    Returns the extension of the filename.
    
    :Parameters:
    -    `filename`    - file name 
     
    :Returns:
    
    file extension 
    """
    for i in xrange(len(filename) - 1, -1 , - 1):
        if filename[i] == '.':
            return filename[i+1:]
    return filename

def readTxtDataFile(filename):
    """
    Read and extract data from a text file
    
    :Parameters:
    -    `filename`    - file name to read
     
    :Returns:
    `anglesList`    -    list of sequences of divergence angles 
    """
    
    fobj = file(filename, 'r')
    anglesList = []
    for line in fobj:
        print line
        print "text line"
        lineList = line[:-1].split(' ')
        l = [int(i) for i in lineList]
        anglesList.append(l)
    return anglesList


def readSeqFile(filename):
    """
    Read and extract data from a .seq file
    
    :Parameters:
    -    `filename`    - file name to read
     
    :Returns:
    `anglesList`    -    list of sequences of divergence angles 
    """
    anglesList = []
    fobj = file(filename, 'r')
    counter = 0
    seq = []
    seqCounter = 0
    dataNo = 0
    for line in fobj:
        if counter >= 12 and len(line) > 3:
            if '\\' in line[-4:]:
                splittedLine = line[:-3].split()
                seq.extend([int(i) for i in splittedLine])
            elif ')' in line[-4:] :
                splittedLine = line[:-8].split()
                seqRest = [int(i) for i in splittedLine]
                seq.extend(seqRest)
                anglesList.append(seq)
                dataNo += len(seq)
                seqCounter += 1

                seq = []
        
        counter += 1
    return anglesList


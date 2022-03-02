from vplants.phyllotaxis_analysis.read_file import readCSVFile
def sequence_reader(file):
    '''    Read a file of sequences measured angles
    '''
    listofseqs = readCSVFile(file); 
    # write the node code here.

    # return outputs
    return listofseqs,

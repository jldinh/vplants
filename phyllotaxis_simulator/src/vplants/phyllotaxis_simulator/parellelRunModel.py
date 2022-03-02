from itertools import product
from openalea.lpy import *
import multiprocessing
import numpy as np
import pickle
import time

lsys = Lsystem("phyllotaxis_simulator.lpy")

def runHofmeister(params):
    """
    Run the Hofmesiter model
    """
    print "started"
    global lsys
    lsys.m.V_0, lsys.m.intialDivAngle = params
    lsys.m.initialDivAngleNumber = 150
    if lsys.m.V_0 < 0.2:
        lsys.m.maxDistance = 20
    elif lsys.m.V_0 < 0.3:
        lsys.m.maxDistance = 50
    elif lsys.m.V_0 < 0.4:
        lsys.m.maxDistance = 150
    elif lsys.m.V_0 < 0.5:
        lsys.m.maxDistance = 250
    else:
        lsys.m.maxDistance = 500
    lstring = lsys.derive()
    return lsys.m.divergenceAngles

class MyParallel(object):
    def __init__(self, func2Parallelize, dumpFileName, parameterRanges):
        self.dumpFileName = dumpFileName
        self.parameterRanges = parameterRanges
        self.func2Parallelize = func2Parallelize
    
    def run(self):
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        parametersList = [ params for params in product( * [ parRange for parRange in self.parameterRanges] )]
        self.result = pool.map(self.func2Parallelize, parametersList)
        pool.close()
        pool.join()
    
    def save(self):
        fobj = file(self.dumpFileName, "wb")
        pickle.dump(self.result, fobj)
        fobj.close()

if __name__ == "__main__":
    startTime = time.time()    
    obj = MyParallel(func2Parallelize = runHofmeister, dumpFileName = "resultHofmeister.txt", parameterRanges = [np.linspace(0.01, 1.2, 10), np.linspace(60, 170, 10)])
    obj.run()
    obj.save()
    print "Elapsed time: ", time.time() - startTime


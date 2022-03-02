import numpy as np
from vplants.mars_alt.alt import optimal_lineage as opt_lin
import scipy as sp

def maxLabels(graph):
    """ Given a bipartite graph, return the two max labels
    
    :Parameters:
    - `graph` (dictionnary) - the dictionnary mapping mothers to children

    :Returns:
    Max label for mothers and max label for children
    """
    maxLabel0=0
    maxLabel1=0
    for m in graph.iterkeys():
        if m>maxLabel0 : maxLabel0=m
        for k in graph[m][:]:
            if k[0]>maxLabel1 : maxLabel1=k[0]
    return maxLabel0, maxLabel1

def degreeStats(graph):
    """ Given an graph oriented graph, return some stats about out degrees
    
    :Parameters:
    - `graph` (dictionnary) - the dictionnary mapping mothers to children

    :Returns:
    Max of out degrees, min of out degrees and mean of out degrees
    """
    degrees=[]
    i=0
    for m in graph.iterkeys():
        degrees.append(0)
        i+=1
        for k in graph[m][:]:
            degrees[i-1]+=1
    return max(degrees), min(degrees), sp.mean(degrees)

def nbCommonEdges(graph1, graph2):
    """ Given two oriented graphs, return the number of common edges
    (two edges are the same if they have the two same labels)
    
    :Parameters:
    - `graph1` (dictionnary) - the dictionnary mapping mothers to children for the first graph
    - `graph2` (dictionnary) - the dictionnary mapping mothers to children for the second graph

    :Returns:
    Number of common edges
    """

    nbCommon=0
    degreesG1=[]
    degreesG2=[]
    i=0
    for m in graph1.iterkeys():
        if graph2.has_key(m):
            isThereCommonEdges=False
            for k in graph2[m][:]:
                if not graph1[m].count(k)==0:
                    isThereCommonEdges=True
                nbCommon+=graph1[m].count(k)
            if isThereCommonEdges:
                degreesG1.append(0)
                degreesG2.append(0)
                i+=1
                for k in graph1[m][:]:
                    degreesG1[i-1]+=1
                for k in graph2[m][:]:
                    degreesG2[i-1]+=1
                
    return nbCommon, max(degreesG1), min(degreesG1), sp.mean(degreesG1), max(degreesG2), min(degreesG2), sp.mean(degreesG2)

def nbEdges(graph):
    nbEdges=0
    for m in graph.iterkeys():
        nbEdges+=len(graph[m])
    return nbEdges
"""    
nbEdges=0
    for m in graph.iterkeys():
        for k in graph[m][:]:
            nbEdges+=1
    return nbEdges
"""

def nbVertexes(graph):
    nbVertexes=len(graph)
    inv_graph={}
    for m in graph.iterkeys():
        for k in graph[m][:]:
            inv_graph.setdefault(k[0], []).append((k[1], m))
    nbVertexes+=len(inv_graph)

    

def build_random_graph(NBMOTHERS, NBCHILDRENMAX):
    graph={}
    tmp=np.random.normal(3, 2, NBMOTHERS+2)
    nbEdgesForM=[]
    nChildren=2
    for i in tmp:
        nbEdgesForM.append(round(abs(i)))
    mothersJumped=0
    print tmp
    print nbEdgesForM
    present=[]
    for i in range(0, NBCHILDRENMAX+2) : present.append(0)
    for i in range(2, NBMOTHERS+2):
        if int(nbEdgesForM[i])==0 : mothersJumped+=1
        while present.count(1)>0 : present[present.index(1)]=0
        for j in range(int(nbEdgesForM[i])):
            child=np.random.randint(2, NBCHILDRENMAX+2)
            if child > nChildren : 
                child=nChildren
                nChildren+=1
            if present[child]==0:
                graph.setdefault(i-mothersJumped, []).append((child, abs(np.random.normal(0.2, 0.5))))
            present[child]=1
    maxLabel1=0
    degreeKids=[]
    for i in range(NBCHILDRENMAX+2):
        degreeKids.append(0)
    
    for i in graph.iterkeys():
        for j in graph[i][:]:
            degreeKids[int(j[0])]+=1
            if maxLabel1<j[0]:
                maxLabel1=j[0]
    
    nChildren=0
    for i in degreeKids:
        if not i==0 : nChildren+=1
    
    degreeSum=sum(degreeKids) #actually same as nbEdges
    maxLabel0=NBMOTHERS+1-mothersJumped
    return graph, nChildren, degreeSum, maxLabel0, maxLabel1
    

def test_basic_optimal_lineage():
    
    

    gRfVsgSimplex=[]
    gRfVsgBasic=[]
    gBasicVsgSimplex=[]
    nbRfEdges=[]
    nbSimplexEdges=[]
    nbBasicEdges=[]
    for i in range(0,1):
    #g, nChildren, degreeSum, maxLabel0, maxLabel1=build_random_graph(500, 1000)
        g, nChildren, degreeSum, maxLabel0, maxLabel1=build_random_graph(50, 100)
        gRf=opt_lin.optimal_lineage(maxLabel0, maxLabel1, candidates=g, ndiv=8, optimization_method="rf_flow")
        gSimplex=opt_lin.optimal_lineage(maxLabel0, maxLabel1, candidates=g, ndiv=8, optimization_method="nx_simplex")
        gBasic=opt_lin.optimal_lineage(maxLabel0, maxLabel1, candidates=g, ndiv=8, optimization_method="basic_solve")
        
        gRfVsgSimplex.append(nbCommonEdges(gRf, gSimplex))
        gRfVsgBasic.append(nbCommonEdges(gRf, gBasic))
        gBasicVsgSimplex.append(nbCommonEdges(gBasic, gSimplex))
        nbRfEdges.append(nbEdges(gRf))
        nbSimplexEdges.append(nbEdges(gSimplex))
        nbBasicEdges.append(nbEdges(gBasic))

    print "nb of Rf edges                   average :", np.average(nbRfEdges)
    print "nb of Rf edges                   std :", np.std(nbRfEdges)
    print "nb of Simplex edges              average :", np.average(nbSimplexEdges)
    print "nb of Simplex edges              std :", np.std(nbSimplexEdges)
    print "nb of Basic edges                average :", np.average(nbBasicEdges)
    print "nb of Basic edges                std :", np.std(nbBasicEdges)
    print "nb of common edges Rf/Simplex    average :", np.average(gRfVsgSimplex)
    print "nb of common edges Rf/Simplex    std :", np.std(gRfVsgSimplex)
    print "nb of common edges Rf/Basic      average :", np.average(gRfVsgBasic)
    print "nb of common edges Rf/Basic      std :", np.std(gRfVsgBasic)
    print "nb of common edges Basic/Simplex average :", np.average(gBasicVsgSimplex)
    print "nb of common edges Basic/Simplex std :", np.std(gBasicVsgSimplex)

    return gRf, gBasic, gSimplex, gRfVsgSimplex, gRfVsgBasic, gBasicVsgSimplex

from vplants.mars_alt.alt.mapping import lineage_from_file

def recup_lineages_and_sets():
    lin=lineage_from_file("/home/leo/Downloads/alt_loop_2011-10-27-16-29-23_0_candidate.clin")
    linExp=lineage_from_file("/home/leo/Downloads/lineage_t0_t1_v3.txt")
    linDist={}
    linDistM={}
    linM={}

    for m in lin.iterkeys():
        for k in lin[m][:]:
            if m in linExp:
                linDistM.setdefault(m, []).append((k[0], 1-k[1]))
                linM[m]=lin[m]
            linDist.setdefault(m, []).append((k[0], 1-k[1]))

    maxLabel0, maxLabel1=maxLabels(linDist)
    maxLabel0M, maxLabel1M=maxLabels(linDistM)
    
    linB=opt_lin.optimal_lineage(maxLabel0, maxLabel1, candidates=linDist,
                                 optimization_method="basic_solve", ndiv=8)

    linBM=opt_lin.optimal_lineage(maxLabel0M, maxLabel1M, candidates=linDistM,
                                  optimization_method="basic_solve", ndiv=4)

    linRf=opt_lin.optimal_lineage(maxLabel0, maxLabel1, candidates=lin, ndiv=4)
    
    linRfM=opt_lin.optimal_lineage(maxLabel0, maxLabel1, candidates=linM, ndiv=8)
    
    linRf.pop(0)
    linRfM.pop(0)

    setL=set()
    setLM=set()
    setExp=set()
    setRf=set()
    setRfM=set()
    setB=set()
    setBM=set()
    
    for m in linDist.iterkeys():
        for k in linDist[m][:]:
            setL.add((m, k))

    for m in linDistM.iterkeys():
        for k in linDistM[m][:]:
            setLM.add((m, k))

    for m in linExp.iterkeys():
        for k in linExp[m][:]:
            setExp.add((m, k))

    for m in linB.iterkeys():
        for k in linB[m][:]:
            setB.add((m, k))

    for m in linBM.iterkeys():
        for k in linBM[m][:]:
            setBM.add((m, k))

    for m in linRf.iterkeys():
        for k in linRf[m][:]:
            setRf.add((m, k))

    for m in linRfM.iterkeys():
        for k in linRfM[m][:]:
            setRfM.add((m, k))

    return lin, linDist, linDistM, linExp, linB, linBM, linRf, linRfM, setL, setLM, setExp, setB, setBM, setRf, setRfM

def test_on_pradip_data():
    lin, linDist, linDistM, linExp, linB, linBM, linRf, linRfM, setL, setLM, setExp, setB, setBM, setRf, setRfM=recup_lineages_and_sets()
    print "linPradip, Ge=(Ve, Ee):: #Edges   :", len(setExp)
    print "                        #Mothers :", len(linExp)
    d=degreeStats(linExp)
    print "                        d Max   :", d[0]
    print "                        d Min   :", d[1]
    print "                        d Moyen :", d[2]
    print
    print "Graph des possibles, Gp=(Vp, Ep):: #Edges   :", len(setL)
    print "                                  #Mothers :", len(linDist)
    d=degreeStats(linDist)
    print "                                  d Max   :", d[0]
    print "                                  d Min   :", d[1]
    print "                                  d Moyen :", d[2]
    print
    print "Reduct Graphe des possibles, Gpr=(Vrp, Erp):: #Edges   :", len(setLM)
    print "                                           #Mothers :", len(linDist)
    d=degreeStats(linDistM)
    print "                                           d Max   :", d[0]
    print "                                           d Min   :", d[1]
    print "                                           d Moyen :", d[2]
    print
    print "Romain from Gp, Gr=(Vr, Er):: #Edges   :", len(setRf)
    print "                                 #Mothers :", len(linRf)
    d=degreeStats(linRf)
    print "                                 d Max   :", d[0]
    print "                                 d Min   :", d[1]
    print "                                 d Moyen :", d[2]
    print "                        nbCommon:", nbCommonEdges(linExp, linRf)
    print
    print "Romain from Gpr, Grr=(Vrr, Err):: #Edges   :", len(setRfM)
    print "                                 #Mothers :", len(linRfM)
    d=degreeStats(linRfM)
    print "                                 d Max   :", d[0]
    print "                                 d Min   :", d[1]
    print "                                 d Moyen :", d[2]
    print "                        nbCommon:", nbCommonEdges(linExp, linRfM)
    print 
    print "Basic from Gp, Gb=(Vb, Eb):: #Edges   :", len(setB)
    print "                             #Mothers :", len(linB)
    d=degreeStats(linB)
    print "                             d Max   :", d[0]
    print "                             d Min   :", d[1]
    print "                             d Moyen :", d[2]
    print "                        nbCommon:", nbCommonEdges(linExp, linB)
    print
    print "Basic from Gpr, Gbr=(Vbr, Ebr):: #Edges   :", len(setBM)
    print "                             #Mothers :", len(linBM)
    d=degreeStats(linBM)
    print "                             d Max   :", d[0]
    print "                             d Min   :", d[1]
    print "                             d Moyen :", d[2]
    print "                        nbCommon:", nbCommonEdges(linExp, linBM)

    

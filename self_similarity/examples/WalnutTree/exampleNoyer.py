# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.self_similarity
#
#       Copyright 2010 LaBRI
#
#       File author(s): Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

__doc__= "Example to use clustering from self_similarity package"
__docformat__ = "restructuredtext"
__license__= "Cecill-C"
__revision__= "$Id: $"


from openalea.aml import *
from self_similarity.clustering import *

from self_similarity.graph import *
from self_similarity.cst import *
from self_similarity.mtg2graph import *
from geometry import *

valeursmatrices=['long-diam.95.05_indel55','long.5.5_indel','noDiam','noLong','paramEquiprob','orientationOnly']
for valmatrice in valeursmatrices:
    ##
    mtg_filename = './walnut.mtg'
    ##
    g = MTG(mtg_filename)
    ##
    ##
    ##
    ###match=TreeMatching(roots,MatchingType->test)
    ##
    ##
    print 'Compute an AML PlantFrame'
    # to have complete geometrical information
    def diam(x) :
        r = Feature(x,'TopDia')
        if r: return r/10
           
    pf = PlantFrame(1,Scale=3,TopDiameter=diam)
    #Viewer.camera.set(Vector3(0,0,0),-60,-20)
    #Viewer.frameGL.setSize(300,850)
    Viewer.frameGL.maximize()
    Viewer.grids.setAxis(False)
    Plot(pf)
    Viewer.frameGL.saveImage('walnut.png')

    ##
    ##
    ##
    ##
    ##from openalea.mtg.mtg import *
    ##import openalea.mtg.aml as aml
    ##import openalea.mtg.plantframe as plantframe
    ##from openalea.mtg import dresser
    ##from openalea.plantgl.all import Viewer
    ##
    ##fn = './plant2.mtg'
    ##g3= aml.MTG(fn)
    ##
    ##def plant3d(g):
    ##        topdia = lambda x: g.property('TopDia').get(x)
    ##
    ##        #dressing_data = dresser.dressing_data_from_file(drf_fn)
    ##        
    ##        pf = plantframe.PlantFrame(g3,TopDiameter=topdia)
    ##        pf.propagate_constraints()
    ##        diameters = pf.algo_diameter()
    ##        axes = plantframe.compute_axes(g,3, pf.points, pf.origin)
    ##        scene=plantframe.build_scene(pf.g, pf.origin, axes, pf.points, diameters, 10000)
    ##        return scene
    ##sc= plant3d(g3)       
    ##Viewer.display(sc)
    ##sc.save('initLiltest2.bgeom')



        
    # retrieve geometrical info from plantframe. For this convert orientation into relative orientation
    parameters = compute_geom_parameters(pf,VtxList(Scale=3),True, Father)




    #print 'tree <=> MTG'
    tree = mtg2graph(3, 3, parameters)


    #print 'Write the distance matrix in matrix_filename'
    matrix_params_filename = 'WalnutParams.txt'
    #print_matrix_params(tree, matrix_params_filename,0)

    # output distances by number of class
    treeMat = []
    treeMatParam = []
    linear = []



    # NEST method
    dag_tmp = tree_reduction(tree)
    tree_colored = tree_reconstruction(dag_tmp)
    print(str(nb_nodes(tree_colored))+' nb nodes tree')
    print(str(nb_nodes(dag_tmp))+' nb nodes dag')
    print 'nb Edge '+ str(edge_nb(dag_tmp))
    print 'nb sign '+str(max_signature_edge(tree_colored))
    #inputSize=nb_nodes(tree_colored)*ceil(log(nb_nodes(tree_colored))/log(2))
    inputSize=nb_nodes(tree_colored)*(4+8+16)
    print 'inputsize '+str(inputSize)


    #graph2mtg(tree,'LilInit.mtg',0)
    g2 = MTG('LilInit.mtg')
    print VtxList(Scale=2)
    print 'Write the distance matrix in matrix_filename'
    matrix_filename = str(valmatrice)+'.txt'
    #matrix_construct(matrix_filename, 2)


    # Compute reduction with c classes
    # 2 classes to exact reduction
    max_class = 2601#nb_nodes(tree_colored)
    #max_class = 9
    min_class = 2600#3701
    nb_geo=1

    (params,val) = matrix_params_clustering(matrix_params_filename, 1)
    rect1 = matrix_clustering(matrix_filename,nb_nodes(tree_colored))

    # construct the dag
    #dag_parent = cluster_fast(tree,rect1)
    print 'compute dag parent'
    dag_parent = cluster_fast2(tree,rect1,params,val,nb_geo)

    print 'compute treerec'
    tree_nest_coCom = tree_reconstruction(dag_parent)

    for i in range(min_class, max_class,1):
        # cluster
        
        print 'compute clusparam'+str(i)
        #(params,val) = matrix_params_clustering(matrix_params_filename, 6200)
        #for i in range(nb_nodes(tree_colored)):
        #    params[i]=1
        #val={}
        print 'compute clustering'+str(i)
        rect1 = matrix_clustering(matrix_filename, i)
        #rect1 = matrix_clustering(matrix_filename, 6427)

        # construct the dag
        #dag_parent = cluster_fast(tree,rect1)
        print 'compute cluster fast'+str(i)
        dag_parent = cluster_fast2(tree,rect1,params,val,nb_geo)
        
        if is_linear(dag_parent):
            linear.append(i)


        
        # final tree
        print 'compute rec'+str(i)
        tree_nest_parent = tree_reconstruction(dag_parent)
        ##    
        ##    print(str(nb_nodes(tree_colored))+' nb nodes tree')
        ##    print(str(nb_nodes(dag_tmp))+' nb nodes dag')
        ##    print 'nb Edge '+ str(edge_nb(dag_tmp))+'\n'
        ##    print 'nb sign '+str(max_signature_edge(tree_colored))+'\n'
        ##    print(str(nb_nodes(dag_parent))+' nb nodes dag')
        ##    print 'nb Edge '+ str(edge_nb(dag_parent))+'\n'
        ##    print 'nb sign '+str(max_signature_edge(tree_nest_parent))+'\n'

        #output=edge_nb(dag_parent)*(ceil(log(nb_nodes(dag_parent))/log(2))+ceil(log(max_signature_edge(tree_nest_parent)+1)/log(2)))
        output=max_signature_edge(tree_nest_parent)*16+nb_nodes(dag_parent)*(4+8)+16.0
        print 'input:::: '+str(inputSize)
        print 'output:::: '+str(output)
        # real save
        #graph2mtg(tree,'LilInit.mtg',0)
        maxSize=height_of_graph(tree_nest_coCom)
        if height_of_graph(tree_nest_parent)>maxSize:
            maxSize=height_of_graph(tree_nest_parent)
        graph2mtg(tree_nest_coCom,'resMTG1/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.mtg',0,maxSize)
        graph2mtg(tree_nest_parent,'resMTG1/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.mtg',1,maxSize)
        
        # compute distance with tree_matching
        #g = MTG('resMTG/'+str(output/inputSize)+'nbno'+str(i)+'.mtg')
        #matching = TreeMatching(roots_to_compare,MatchingType='Edition',OrderType='Unordered',MappingType='Global',ScaleType='SingleScale')
        #mappedVertexList = MatchingExtract(matching,ViewPoint = 'List',InputTree=1,ReferenceTree=2)

        #treeMat.append(MatchingExtract(matching,ViewPoint = 'Distance',InputTree=1,ReferenceTree=2))





        g5 = MTG('resMTG1/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.mtg')
        roots_to_compare = [v+1 for v in VtxList(Scale=1)]

        VectoDist=VectorDistance(.30,'NUMERIC',.30,'NUMERIC',0.1,'NUMERIC',0.1,'NUMERIC',0.1,'NUMERIC',0.1,'NUMERIC',Distance='QUADRATIC')

        def diam(x):
            return Feature(x,"Diameter")
        def long(x):
            return Feature(x,"Length")
        def Q1(x):
            return Feature(x,"Q1")
        def Q2(x):
            return Feature(x,"Q2")
        def Q3(x):
            return Feature(x,"Q3")
        def Q4(x):
            return Feature(x,"Q4")


        func = [diam,long,Q1,Q2,Q3,Q4]

        match=0
        #match=TreeMatching([2,302],MatchingType='Edition',FuncList = func,VectorDistance=VectoDist,MappingType='Global')
        
        #mappedVertexList = MatchingExtract(match,ViewPoint = 'List',InputTree=1,ReferenceTree=2)

        #res=MatchingExtract(match,ViewPoint = 'Distance',InputTree=1,ReferenceTree=2)/(nb_nodes(tree_nest_coCom)+nb_nodes(tree_nest_parent))
     

        #treeMatParam.append(res)
        treeMat.append(inputSize/output)

        graph2mtg(tree_nest_parent,'resMTG1only/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.mtg',0,maxSize)

        print 'Compute representation'
        g2 = MTG('resMTG1only/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.mtg')
        # retrieve geometrical info from plantframe. For this convert orientation into relative orientation
        vtxlist = VtxList(Scale=2)

        parameters2 = {}
        parameters2['AnchorT'] ={}
        parameters2['Length'] ={}
        parameters2['Diameter'] ={}
        parameters2['QtOrientation'] = {}
        for v in VtxList(Scale=2):
            parameters2['Diameter'][v]=Feature(v,'Diameter')
            parameters2['Length'][v]=Feature(v,'Length')
            parameters2['AnchorT'][v]=Feature(v,'AnchorT')
            val_quater = Quaternion(Feature(v,'Q1'),Feature(v,'Q2'),Feature(v,'Q3'),Feature(v,'Q4'))
            parameters2['QtOrientation'][v]=val_quater
        
        
        def get_param2(v,paramname): return parameters2[paramname][v]


        sc = compute_representation(Root(vtxlist[0]),get_param2)
        sc.save('resBGEOM1/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.bgeom')

        #Plot(pf)
        #Viewer.camera.lookAt(Vector3(-0,-0,-80 ) )
        
        #Viewer.dialog.question('InitialLil rep')
        #Viewer.frameGL.saveImage('InitialLil.png')
        Viewer.display(sc)
        #Viewer.camera.lookAt(Vector3(10,-10,-10) )

        #Viewer.dialog.question('Final rep')
        Viewer.frameGL.saveImage('resPNG1/'+str(valmatrice)+'mat'+str(inputSize/output)+'nbno'+str(i)+'.png')
        
     
    # print the distance between tree and pseudo nest
    print 'TREE MATCHING FINAL'


    logfile = open('CompressionFactor', 'w+') 
    comp = min_class
    for i in treeMat:
        logfile.write(str(comp) + '\t'+ str(i)+'\n')
        comp += 1 
    logfile.close()


    logfile2 = open('Distance', 'w+') 
    comp = min_class
    for i in treeMatParam:
        logfile2.write(str(comp) + '\t'+ str(i)+'\n')
        comp += 1 
    logfile2.close()


    comp = min_class
    for i in linear: 
        print "Class "+str(comp)+ " linear? "+str(i)
        comp += 1 
        

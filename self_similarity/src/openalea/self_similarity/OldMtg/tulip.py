# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.Self_similarity: Self_similarity tools package
#
#       Copyright 2010 LaBRI
#
#       File author(s): Pascal Ferraro <pascal.ferraro@labri.fr>
#                       Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

'''
Graph output tulip format tools.
Updated with the new tulip format.
'''

__license__= "Cecill-C"
__revision__=" $Id: tulip.py 17111 2014-07-09 15:42:49Z azais $ "
__docformat__ = "restructuredtext en"

# to work with the new configuration of Mac
import sys
sys.path.append('../src/self_similarity')

from graph import *


def save_tulip(graph, name):
    """ Save the graph in a tulip file.
    
    Save the graph a c_graph object in tulip file format.
    If name file exists the old file will be delete.

    Usage
    -----
      save_tulip(graph, name)

    :Parameters:
      - `graph` (c_graph): the graph to save in tulip format
      - `name` (str): name and path of the file to save
        
    :Returns:
      None
        
    :Examples:
      save_tulip(graph,'graph.tlp')
      
    .. warning:: You must have writing permission in name path.
    ------------
    
    .. todo:: tests, empty graph
    ---------
        
    """
    # delete the old file if exists
    try:
        source = open(name,'w')
    except IOError:
        sys.exit('Could not create '+ name)    
    
    # vertices       
    nb_vertex = nb_nodes(graph)

    source.write('(nodes ')
    for i in xrange(nb_vertex):
        source.write(' %d ' %i)
    source.write(')\n')

    # edges
    edge_nb = 0
    for i in xrange(nb_vertex):
        # for all nodes
        n = node(graph, i)
        for e in graph.edges:
            # if out edge
            if e.start ==n:
                source.write('(edge %d '% (edge_nb))
                source.write('%s ' % (i))
                source.write(' %s )\n'% (graph.nodes.index(e.end)))
                edge_nb += 1

    # color property
    source.write('(property  0 color \"viewColor\"\n')
    source.write('(default \"(255,0,0,255)\" \"(0,0,0,255)\" )\n')
    # if signatures in graph put the right color
    nb_signature = graph.nb_signature
    if nb_signature!=0:
        for i in xrange(nb_vertex):
            signature = node(graph,i).signature
            source.write('(node %d \"(' %(i))
            source.write('%d ,'%red_color_vertex(signature,nb_signature))
            source.write('%d ,'%green_color_vertex(signature,nb_signature))
            source.write('%d ,'%blue_color_vertex(signature,nb_signature))
            source.write(' 255)\")\n')
    source.write(')\n')
    source.write('(property  0 size \"viewSize\"\n')
    source.write('(default \"(10,10,0)\" \"(0.125,0.125,10)\" )\n')
    source.write(') \n')
    source.write(') \n')
    source.close()


def blue_color_vertex(signature, nb_pattern):
    """ Return the level of blue in tulip for a signature.
    
    Return a number between 0 and 255 that correspond to the blue level with
    signature on nb_pattern.

    Usage
    -----
      blue_color_vertex(signature, nb_pattern)

    :Parameters:
      - `signature` (int): the id of the signature.
      - `nb_pattern` (int): the number of different signatures in the graph.
        
    :Returns:
      A number between 0 and 255.
        
    :Examples:
      blue_color_vertex(2, 5)
        
    """  
    if signature == -1:
        return 0
    else :
        step = nb_pattern/6.
        v = signature % nb_pattern
        if v < nb_pattern/3. :
            return 0
        else :
            if v < nb_pattern/2. :
                return int(v * 255 /step)%255
            else :
                if v < 5*nb_pattern/6. :
                    return 255
                else :
                    return 255 - int(v * 255 /step)%255


def green_color_vertex(signature, nb_pattern):
    """ Return the level of green in tulip for a signature.
    
    Return a number between 0 and 255 that correspond to the green level with
    signature on nb_pattern.

    Usage
    -----
      green_color_vertex(signature, nb_pattern)

    :Parameters:
      - `signature` (int): the id of the signature.
      - `nb_pattern` (int): the number of different signatures in the graph.
        
    :Returns:
      A number between 0 and 255.
        
    :Examples:
      green_color_vertex(2, 5)
        
    """    
    if signature == -1:
        return 0
    else :
        step = nb_pattern/6.
        v = signature % nb_pattern
        if v < nb_pattern/6. :
            return int(v * 255 /step)%255
        else :
            if v < nb_pattern/2. :
                return 255
            else :
                if v < 2*nb_pattern/3. :
                    return 255 - int(v * 255 /step)%255
                else :
                    return 0


def red_color_vertex(signature, nb_pattern):
    """ Return the level of red in tulip for a signature.
    
    Return a number between 0 and 255 that correspond to the red level with
    signature on nb_pattern.

    Usage
    -----
      red_color_vertex(signature, nb_pattern)

    :Parameters:
      - `signature` (int): the id of the signature.
      - `nb_pattern` (int): the number of different signatures in the graph.
        
    :Returns:
      A number between 0 and 255.
        
    :Examples:
      red_color_vertex(2, 5)
        
    """      
    if signature == -1:
        return 0
    else :
        step = nb_pattern/6.
        v = signature % nb_pattern
        if v < nb_pattern/6. :
            return 255
        else :
            if v < nb_pattern/3. :
                return 255-int(v * 255 /step)%255
            else :
                if v < 2*nb_pattern/3. :
                    return 0
                else :
                    if v<5*nb_pattern/6. :
                        return int(v * 255 /step)%255
                    else :
                        return 255

# end of file

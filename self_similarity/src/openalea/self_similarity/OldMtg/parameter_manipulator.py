# -*- python -*-
# -*- coding: utf-8 -*-
#
#       Vplants.Self_similarity: Self_similarity tools package
#
#       Copyright 2010 LaBRI
#
#       File author: Anne-Laure Gaillard <anne-laure.gaillard@labri.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#
################################################################################

'''
Clustering tools for the approximation self_similarity method with geometry.
'''

__docformat__ = "restructuredtext"
__license__= "Cecill-C"
__revision__=" $Id: parameter_manipulator.py 17111 2014-07-09 15:42:49Z azais $ "


# quaternion param
from PyQGLViewer import Quaternion, Vec

# datastruct
from UserDict import UserDict

class parameter_manipulator2(UserDict):  
                              
    """
        Class for parameters manipulation
    """ 

    # redefine UserDict methods
    def __init__(self, dict=None):           
        self.data = {}                         
        if dict is not None: self.update(dict)
        
    def clear(self): self.data.clear()  
            
    def copy(self):                             
        if self.__class__ is UserDict:          
            return UserDict(self.data)         
        import copy                             
        return copy.copy(self)     
                    
    def keys(self): return self.data.keys()    
     
    def __getitem__(self, key): return self.data[key]
    
    def __setitem__(self, key, item): self.data[key] = item  
     
    def items(self): return self.data.items()  
    
    def values(self): return self.data.values()
    
    def __repr__(self):
        return "<Parameter_manipulator " + str(self.data) +">"

    def __str__(self):
        return str(self.data)
        
    # new methods
    def init_parameter(self, dict, vid):
        """ Initialisation of nodes parameters.
    
        Initialisation of the dictionary associated with vid node.

        Usage
        -----
          init_parameter(dict, vid)

        :Parameters:
          - `dict` (dict): the dictonary to put in the node.
          - `vid` (int): the vertex identifier.
        
        :Returns:
          None
        
        :Examples:
          TO DO
        ------------
    
        .. todo:: Examples in this doc.
        ---------
        
        """
        for k in dict.keys():
            self[k] = dict[k][vid]
        


    def merge(self):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        dicto = {}
        for k in self.keys():
            # float merging
            if not k == 'QtOrientation':
                somme = 0
                for val in self[k]:
                    somme += val
                somme /= len(self[k])
                dicto[k] = somme
            # quaternion merging
            else:
                comp = 1
                dicto[k] = self[k][0]
                for val in self[k]:
                    if not comp == 1:
                        dicto[k] = Quaternion.slerp(dicto[k], val, comp)
                    comp /= 2
        return dicto    
    


    def merge_edge_moy(self):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        dicto = {}
        nb=0
        dicto[nb]={}
        for k in self.keys():
            # float merging
            if k == 'QtOrientation':
                comp = 1
                dicto[nb] = self[k][0]
                for val in self[k]:
                    if not comp == 1:
                        dicto[nb] = Quaternion.slerp(dicto[nb], val, comp)
                    comp /= 2
        return dicto

    

    def merge_edge_moy_para(self,rect):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        dicto = {}
        for k in rect.keys():
            dicto[k-1]={}
            comp = 1
            dicto[k-1] = self.data['QtOrientation'][rect[k][0]]
            for val in rect[k]:
                if val<len(self.data['QtOrientation']):
                    if not comp == 1:
                        dicto[k-1] = Quaternion.slerp(dicto[k-1], self.data['QtOrientation'][val], comp)
                    comp /= 2

        return dicto          

    def merge_vertex(self):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        dicto = {}
        for k in self.keys():
            # float merging
            if not k == 'QtOrientation':
                somme = 0
                for val in self[k]:
                    somme += val
                somme /= len(self[k])
                dicto[k] = somme
            # quaternion merging
        return dicto    
    
      

    def merge_edge(self,rect2):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        dicto = {}
        nb=0
        for k in rect2:
            dicto[nb]={}
            for i in range(4):
                dicto[nb][i] = k[i]
            nb+=1
        return dicto    
    
      
                
    def parameters2mtg_feature(self):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        all_str = ''
        if len(self.keys())>0:
            all_str += 'Diameter\tREAL\n'
            all_str += 'AnchorT\tREAL\n'
            all_str += 'Length\tINT\n'
            all_str += 'Q1\tREAL\n'
            all_str += 'Q2\tREAL\n'
            all_str += 'Q3\tREAL\n'
            all_str += 'Q4\tREAL\n'

        return all_str
        
            
    def parameters2mtg_entity_code(self, size):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        all_str = ''
        if len(self.keys())>0:
            all_str += "ENTITY-CODE"
            for t in xrange(size+1):
                all_str += '\t'
            all_str += "Diameter\tAnchorT\tLength\tQ1\tQ2\tQ3\tQ4\n"
        return all_str
                
                        
    def parameters2mtg(self, size):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        all_str = ''
        if len(self)>0:
            for t in xrange(size):
                all_str+="\t"

            for k in self.keys():
                if k == 'Length':
                    all_str+=str(int(self['Length']))+'\t'
                elif k == 'QtOrientation':
                    for i in xrange (4):
                        all_str+=str(round(self['QtOrientation'][i],7))+'\t'
                else:
                    all_str+=str(round(self[k],10))+'\t'
            all_str+='\n'
        return all_str



    def print_params(self,orientation=1):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        all_str = ''
        for k in self.keys():
            if k == 'QtOrientation' and orientation>0:
                for i in xrange (4):
                    all_str+=str(round(self['QtOrientation'][i],7))+'\t'
            elif k == 'QtOrientation' and not orientation:
                all_str = all_str
            elif orientation <> 2:
                all_str+=str(self[k])
                all_str+= '\t'
        all_str+= "\n"
        return all_str
    
    def print_params_orient(self):
        """ .

        Usage
        -----
         

        :Parameters:
        
        :Returns:
        
        :Examples:
          TO DO
        ------------
    
        .. todo::
        ---------
        
        """
        all_str = ''
        for k in self.keys():
            if k == 'QtOrientation':
                for c in self['QtOrientation']:
                    all_str+=str(round(c,7))+'\t'
                all_str+= "\n"
        for k in self.keys():
            if k == 'QtOrientation':
                for c in self['QtOrientation']:
                    all_str+=str(round(c,7))+'\t'
                all_str+= "\n"
        return all_str
    
# end file

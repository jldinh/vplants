from openalea.container.tree import PropertyTree

class nAdmissibleTree(PropertyTree):
    """
    A class that adds some methods to PropertyTree to construct and explore an n-admissible tree.
    """
    def __init__(self):
        self.maxLevel = -1
        PropertyTree.__init__(self)
    
    def addChild(self, parent, value, level, pbAngle = None, logPbAngle = None, questionMark = False, orderIndex = None):
        """
        Add child with properties to the tree.
        """
        for childId in self.children(parent):
            prop = self.get_vertex_property(childId)
            if ( prop["value"] == value) and  (prop["level"] == level) :
#                print "Already in the tree"
                return childId
                break
        else:
            if level > self.maxLevel:
                self.maxLevel = level
            return self.add_child(parent, value = value, level = level, nodePrb = pbAngle, nodeLogProb = logPbAngle, questionMark = questionMark, orderIndex = orderIndex)
            
    def addListValueLevelProb(self, currentId, ListValueLevel):
        """
        add vertexes given their ids and values to a vertex and updates the probability and order index of the vetex
        
        :Parameters:
        -    currentID    -    vertex id to which new vertexes should be added 
        -    ListValueLevel    -    list of values, levels, probabilities, log of probabilities, and order indexes of children  
        """
        for node in ListValueLevel:            
            currentId = self.addChild(parent = currentId, value = node[0], level = node[1], pbAngle = node[2], logPbAngle = node[3], orderIndex = node[4])
        
    def leaves(self):
        """
        return the list of leaves of the n-admisisble tree.
        """
        return [vid for vid in self.vertices() if self.is_leaf(vid)]
    
    def leavesNotLast(self, seqLen):
        """
        return the leaves of the tree whose level is different from a given value.
        
        :Parameters:
        -    `seqlen`    -    an integer
        
        :Returns:
        -    list of leaves whose level is not equal to `seqLen`
        """
        return [vid for vid in self.vertices() if (  self.is_leaf(vid)  and (self.get_vertex_property(vid)["level"] != seqLen  )) ]
    
    def leavesLast(self, seqLen):
        """
        return the leaves of the tree whose level is equal to a given value.
        
        :Parameters:
        -    `seqlen`    -    an integer
        
        :Returns:
        -    list of leaves whose level is equal to `seqLen`
        """
        return [vid for vid in self.vertices() if (vid != self.root) and ( self.get_vertex_property(vid)["level"] == seqLen  ) ]
    
    def getMaxLevel(self):
        """
        get the maximum level of leaves.
        """
        return self.maxLevel     
    
    def pathToRoot(self, vid):
        """
        return list of values of vertexes on the path from a given vertex to the root.
        
        :Parameters:
        -   `vid`    -    a vertex id 
        
        :Returns:
        `valueList`    -    list of values of vertexes on the path from the `vertex` to the root.
        """
        
        valueList = list()
        while not (vid == self.root):
            valueList.append(self.get_vertex_property(vid)["value"]) 
            vid = self.parent(vid)
        valueList.reverse()
        return valueList

    def allPathsAll(self):
        """
        `allPathsAll` returns a list of values, probabilities , question marks, as well as the total logarithmic probability of all the vertexes on the paths from leaves to the root.
        
        :Returns:
        -    `[valueList, probList ,questionList, logProb]`    -    list of lists of values, probability , question marks, as well as the total logarithmic probability of all the vertexes on the paths from leaves to the root
        """
        for vid in self.vertices():
            if self.is_leaf(vid):
                valueList = list()
                probList = list()
                questionList = list()
                logProb = 0.0
                while not (vid == self.root):
                    valueList.append(self.get_vertex_property(vid)["value"])
                    probList.append(self.get_vertex_property(vid)["nodePrb"])
                    logProb += self.get_vertex_property(vid)["nodeLogProb"]
                    if self.get_vertex_property(vid)["questionMark"]:
                        questionList.append([self.get_vertex_property(vid)["value"], self.get_vertex_property(vid)["level"] ])
                    vid = self.parent(vid)
                valueList.reverse()
                probList.reverse()
                questionList.reverse()
                yield [valueList, probList ,questionList, logProb]
       

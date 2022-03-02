import openalea.tissueshape.grid_tissue as gt
from openalea.celltissue.tissuedb import TissueDB
from openalea.tissueshape.mesh_edition import divide_face
from openalea.tissueshape.mesh_geometry import centroid
from copy import deepcopy,copy
from openalea.plantgl.all import Vector2

class ProxyNode:
    def __init__(self,id,degree,tissuedb,ro = False):
        self.__dict__['__tissuedb__'] = tissuedb
        self.__dict__['id'] = id
        self.__dict__['degree'] = degree
        self.__dict__['__ro__'] = ro
    def __repr__(self):
        return 'ProxyNode('+self.__repr_args__()+')'
    def __str__(self):
        return 'ProxyNode('+self.__repr_args__()+')'
    def __repr_args__(self):
        props = [(p,self.__getattr__(p)) for p in self.__tissuedb__.properties() if hasattr(self,p)]
        return 'id='+str(self.id)+',degree='+str(self.degree)+ ','+','.join([n+'='+repr(v) for n,v in props if not v is None])
    def __eq__(self, other):
        return self.id == other.id
    def __hash__(self):
        return hash(self.id)
    def __getattr__(self,name):
        try:
            prop = self.__tissuedb__.get_property(name)
            try:
                return prop[self.id]
            except KeyError:
                raise AttributeError(name)
        except KeyError :
            raise AttributeError(name)
    def __setattr__(self,name,value):
        assert self.__ro__ == False and 'ReadOnly Node'
        try:
            prop = self.__tissuedb__.get_property(name)
        except:
            prop = {}
            self.__tissuedb__.set_property(name, prop)
        prop[self.id] = value
    def set(self,**args):
        for k,v in args.iteritems():
            self.__setattr__(k,v)
    def neighbors(self):
        mesh = self.__tissuedb__.get_topology("mesh_id")
        for cid in mesh.border_neighbors(self.degree,self.id) :
            yield ProxyNode(cid,self.degree,self.__tissuedb__,True)
    def borders(self):
        mesh = self.__tissuedb__.get_topology("mesh_id")
        for cid in mesh.borders(self.degree,self.id) :
            yield ProxyNode(cid,self.degree-1,self.__tissuedb__,True)
    def regions(self):
        mesh = self.__tissuedb__.get_topology("mesh_id")
        for cid in mesh.regions(self.degree,self.id) :
            yield ProxyNode(cid,self.degree+1,self.__tissuedb__,True)
    def centroid(self):
        mesh = self.__tissuedb__.get_topology("mesh_id")
        return centroid(mesh, self.__tissuedb__.get_property('position'),self.degree,self.id)
            
            
class BufferedProxyNode (ProxyNode):
    def __init__(self,id,degree,tissuedb,futuretissuedb):
        ProxyNode.__init__(self,id,degree,tissuedb)
        self.__dict__['__futuretissuedb__'] = futuretissuedb
        self.__dict__['__futurevalue__'] = False
    def __repr__(self):
        return 'BufferedProxyNode('+str(self.id)+','+','.join([p+'='+str(self.__getattr__(p) for p in self.__tissuedb__.properties())])+')'
    def __getattr__(self,name):
        tissuedb = self.__tissuedb__ if self.__futurevalue__ == False else self.__futuretissuedb__
        try:
            prop = tissuedb.get_property(name)
            try:
                return prop[self.id]
            except KeyError, e:
                raise AttributeError(name)
        except IndexError,e :
            raise AttributeError(name)
    def __setattr__(self,name,value):
        if self.__futuretissuedb__ is None:
            raise ValueError('ReadOnly Node : Cannot edit parameter '+repr(name)+' of node '+repr(self.id))
        try:
            prop = self.__futuretissuedb__.get_property(name)
        except KeyError, e:
            prop = {}
            self.__futuretissuedb__.set_property(name, prop)
        prop[self.id] = value
        self.__futurevalue__ == True
    def future_neighbors(self):
        mesh = self.__futuretissuedb__.get_topology("mesh_id")
        degree = mesh.degree()
        for cid in mesh.border_neighbors(degree,self.id) :
            yield ProxyNode(cid,degree,self.__futuretissuedb__,True)
    def future_borders(self):
        mesh = self.__futuretissuedb__.get_topology("mesh_id")
        for cid in mesh.borders(self.degree,self.id) :
            yield ProxyNode(cid,self.degree-1,self.__futuretissuedb__,True)
    def future_regions(self):
        mesh = self.__futuretissuedb__.get_topology("mesh_id")
        for cid in mesh.regions(self.degree,self.id) :
            yield ProxyNode(cid,self.degree+1,self.__futuretissuedb__,True)
    def divide(self,point,normal, default_labels = {}):
        mesh = self.__futuretissuedb__.get_topology("mesh_id")
        if self.degree == 2:
            normal = Vector2(normal).normed()
            lineages = divide_face(mesh,self.__futuretissuedb__.get_property('position'),self.id,Vector2(point),normal)
            print lineages
            result = {}
            for degree, lineage in enumerate(lineages):
                for olditem, newitems in lineage.iteritems():
                    if not olditem is None:
                        for prop in self.__futuretissuedb__.properties():
                            try:
                                self.__futuretissuedb__.get_property(prop).pop(olditem)
                            except KeyError:
                                pass
                    oldnode = None if olditem is None else ProxyNode(olditem,degree,self.__tissuedb__,True)
                    newnodes = [ProxyNode(n,degree,self.__futuretissuedb__) for n in newitems]
                    if len(default_labels) > 0:
                        for nn in newnodes:
                            if default_labels.has_key(nn.degree):
                                nn.label = default_labels[nn.degree]
                    if not result.has_key(oldnode):
                        result[oldnode] = newnodes
                    else: result[oldnode] += newnodes
            self.__dict__['__futuretissuedb__'] = None
            return result
        elif self.degree == 1:
            pass
        else:
            raise ValueError("Cannot divide point")

Cell, Wall, Point = range(3)
TypeDegree = { Cell : 2, Wall : 1, Point : 0 }
TypeLabel  = { Cell : 'CELL', Wall : 'WALL', Point : 'POINT' }
TypeId     = { 'CELL' : Cell, 'WALL' : Wall, 'POINT' : Point}

def get_nodes_of_type(tissuedb, type):    
    cfg = tissuedb.get_config('config')
    mid = cfg['mesh_id']
    degree = TypeDegree[type]
    for elem in tissuedb.tissue().elements(cfg[TypeLabel[type]]):
        yield ProxyNode(elem,degree,tissuedb)

def get_nodes(tissuedb):
    t = tissuedb.tissue()
    for elem in t.elements():
        yield ProxyNode(elem,TypeDegree[TypeId[t.type_name(t.type(elem))]],tissuedb)

def get_buffered_nodes_of_type(tissuedb,futuretissuedb,type):
    cfg = tissuedb.get_config('config')
    mid = cfg['mesh_id']
    degree = TypeDegree[type]
    for elem in tissuedb.tissue().elements(TypeLabel[type]):
        yield BufferedProxyNode(elem,degree,tissuedb,futuretissuedb)

def get_buffered_nodes(tissuedb,futuretissuedb):
    t = tissuedb.tissue()
    for elem in t.elements():
        yield BufferedProxyNode(elem,TypeDegree[TypeId[t.type_name(t.type(elem))]],tissuedb,futuretissuedb)

get_cell_nodes = lambda tissuedb : get_nodes_of_type(tissuedb,Cell)
get_wall_nodes = lambda tissuedb : get_nodes_of_type(tissuedb,Wall)
get_point_nodes = lambda tissuedb : get_nodes_of_type(tissuedb,Point)

get_buffered_cell_nodes = lambda tissuedb,futuretissuedb : get_buffered_nodes_of_type(tissuedb,futuretissuedb,Cell)
get_buffered_wall_nodes = lambda tissuedb,futuretissuedb : get_buffered_nodes_of_type(tissuedb,futuretissuedb,Wall)
get_buffered_point_nodes = lambda tissuedb,futuretissuedb : get_buffered_nodes_of_type(tissuedb,futuretissuedb,Point)


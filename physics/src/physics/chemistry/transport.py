from interface.chemistry import IChemistry

class GraphTransport (IChemistry) :
    """
    perform active transport of substance on a graph
    pumps are located on oriented edges

    C(t+dt) = C(t) + sum(in edges i) Fi,s->t*dt
                     - sum(out edges i) Fi,s->t*dt
    ou :
        Fi,s->t = Pi,s->t Cs
    Pi,s->t pump number on edge i oriented from source to target
    """
    def __init__ (self, graph, vertex_volume, edge_pumps) :
        self._graph=graph # transport will occur along edges of this graph
        self._vertex_volume=vertex_volume # volume of vertices
        self._edge_pumps=edge_pumps # pumping from source to target
    
    def react (self, substance, dt) :
        graph=self._graph
        vV=self._vertex_volume
        fluxes=self.fluxes(substance)
        for eid,flux in fluxes.iteritems() :
            substance[graph.source(eid)]-=flux*dt/vV[graph.source(eid)]
            substance[graph.target(eid)]+=flux*dt/vV[graph.target(eid)]
        return fluxes
    
    def fluxes (self, substance) :
        """
        return the flux along a given edge
        """
        graph=self._graph
        return dict( (eid,pump*substance[graph.source(eid)]) for eid,pump in self._edge_pumps.iteritems() )

class GraphReverseTransport (IChemistry) :
    """
    perform active transport of substance on a graph
    pumps are located on oriented edges

    C(t+dt) = C(t) + sum(in edges i) Fi,s->t*dt
                     - sum(out edges i) Fi,s->t*dt
    ou :
        Fi,s->t = Pi,s->t Cs
    Pi,s->t pump number on edge i oriented from target to source
    """
    def __init__ (self, graph, vertex_volume, edge_pumps) :
        self._graph=graph # transport will occur along edges of this graph
        self._vertex_volume=vertex_volume # volume of vertices
        self._edge_pumps=edge_pumps # pumping from source to target
    
    def react (self, substance, dt) :
        graph=self._graph
        vV=self._vertex_volume
        fluxes=self.fluxes(substance)
        for eid,flux in fluxes.iteritems() :
            substance[graph.source(eid)]+=flux*dt/vV[graph.source(eid)]
            substance[graph.target(eid)]-=flux*dt/vV[graph.target(eid)]
        return fluxes
    
    def fluxes (self, substance) :
        """
        return the flux along a given edge
        """
        graph=self._graph
        return dict( (eid,pump*substance[graph.target(eid)]) for eid,pump in self._edge_pumps.iteritems() )

class RelationTransport (IChemistry) :
    """
    perform active transport of substance left elements to right elements
    pumps are located on oriented links between elements

    Cl(t+dt) = Cl(t) - sum(links i) Fi*dt
    Cr(t+dt) = Cr(t) + sum(links i) Fi*dt
    where :
        Fi = Pi Cl
    Pi pump number on link i
    """
    def __init__ (self, relation, elm_volume, link_pumps) :
        self._relation=relation # transport will occur along links of this relation
        self._elm_volume=elm_volume # volume of left and right elements
        self._link_pumps=link_pumps # pumping from left to right
    
    def react (self, substance, dt) :
        rel=self._relation
        V=self._elm_volume
        fluxes=self.fluxes(substance)
        for lid,flux in fluxes.iteritems() :
            substance[rel.left(lid)]-=flux*dt/V[rel.left(lid)]
            substance[rel.right(lid)]+=flux*dt/V[rel.right(lid)]
        return fluxes
    
    def fluxes (self, substance) :
        """
        return the flux along a given edge
        """
        rel=self._relation
        return dict( (lid,pump*substance[rel.left(lid)]) for lid,pump in self._link_pumps.iteritems() )

class RelationReverseTransport (IChemistry) :
    """
    perform active transport of substance right elements to left elements
    Orientation of flux is opposite to RelationTransport
    pumps are located on oriented links between elements

    Cl(t+dt) = Cl(t) + sum(links i) Fi*dt
    Cr(t+dt) = Cr(t) - sum(links i) Fi*dt
    where :
        Fi = Pi Cr
    Pi pump number on link i
    """
    def __init__ (self, relation, elm_volume, link_pumps) :
        self._relation=relation # transport will occur along links of this relation
                                # oriented in a reverse way
        self._elm_volume=elm_volume # volume of left and right elements
        self._link_pumps=link_pumps # pumping from right to left
    
    def react (self, substance, dt) :
        rel=self._relation
        V=self._elm_volume
        fluxes=self.fluxes(substance)
        for lid,flux in fluxes.iteritems() :
            substance[rel.left(lid)]+=flux*dt/V[rel.left(lid)]
            substance[rel.right(lid)]-=flux*dt/V[rel.right(lid)]
        return fluxes
    
    def fluxes (self, substance) :
        """
        return the flux along a given edge
        """
        rel=self._relation
        return dict( (lid,pump*substance[rel.right(lid)]) for lid,pump in self._link_pumps.iteritems() )


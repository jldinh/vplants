#Adapted from diffusion.py 25/06/2009
#by Vincent Mirabet
#during the 2009 VPlants coding sprint
#
# Save this file in vplants/trunk/physics/chemistry/MultipleDiffusion.py
#
# Modified to include uni-directional active transport 08/07/2009 by Michael Walker

from interface.chemistry import IChemistry

class MultipleDiffusion (IChemistry) :
        """
        implementation of diffusion between vertices of lists
        of directed/undirected graphs.
        Ci(t+dt)=Ci(t) + sum(neighbors j) (diffusivity(Eij)*dt/V(Ci)*(Cj(t+dt)-Ci(t+dt)))
        Eij, link between i and j
        """
        def __init__ (self, relations, vertex_volumes, edge_diffusion_coefficients,active_transport,nbelements) :
                self._nbelements = nbelements
                if (len(relations)!=self._nbelements) or (len(vertex_volumes)!=self._nbelements) or (len(edge_diffusion_coefficients)!=self._nbelements):
                        print "lists of different sizes"
                        sys.exit()
                self._relations=relations # diffusion will occur between vertices
                                                  # in these graphs
                self._vertex_volumes=vertex_volumes # volume of vertices
                self._edge_diffusion_coefficients=edge_diffusion_coefficients # diffusivity of edges
                self._active_transport=active_transport	#whether active transport is involved

        def react (self, substance, dt, nb_steps = 1) :
                if (len(substance)!=self._nbelements):
                        print "in react, number of substances in list different that number of relations"
                        sys.exit()
                relations=self._relations
                vV=self._vertex_volumes
                fluxes = None
                for i in xrange(nb_steps) :
                        for j in range(self._nbelements):
                            if relations[j].name=="relation":
                                fluxes=self.fluxes(substance,j)
                                for eid,flux in fluxes.iteritems() :
                                    #print "vol ", vV[j][0][relations[j].left(eid)], vV[j][1][relations[j].right(eid)]
                                    substance[j][0][relations[j].left(eid)] -= flux * dt / vV[j][0][relations[j].left(eid)]
                                    substance[j][1][relations[j].right(eid)] += flux * dt / vV[j][1][relations[j].right(eid)]
                            else:
                                fluxes=self.fluxes(substance,j)
                                #print substance[j]
                                for eid,flux in fluxes.iteritems() :
                                    #print "j, eid, flux", j, eid, flux
                                    substance[j][relations[j].source(eid)] -= flux * dt / vV[j][relations[j].source(eid)]
                                    substance[j][relations[j].target(eid)] += flux * dt / vV[j][relations[j].target(eid)]


                return fluxes
        
        def fluxes (self, substance, j) :
                """
                compute oriented fluxed along edges
                efflux = True corresponds to PIN transport
                TODO: generalise to include active influx transport
                """
                relations=self._relations
                efflux = self._active_transport[j]
                if relations[j].name=="relation":
                        if efflux:
                            _direction = dict((eid,0) for eid,D in self._edge_diffusion_coefficients[j].iteritems() )
                            for eid,D in self._edge_diffusion_coefficients[j].iteritems():
                                if substance[j][0][relations[j].left(eid)]>substance[j][1][relations[j].right(eid)]:	#transport only in one direction through PIN
                                    _direction[eid] = D*(substance[j][0][relations[j].left(eid)]-substance[j][1][relations[j].right(eid)])
                            return _direction
                        return dict( (eid,D*(substance[j][0][relations[j].left(eid)]-substance[j][1][relations[j].right(eid)])) for eid,D in self._edge_diffusion_coefficients[j].iteritems() )
                if relations[j].name=="graph":
                        #print "coucou graphe", j
                        return dict( (eid,D*(substance[j][relations[j].source(eid)]-substance[j][relations[j].target(eid)])) for eid,D in self._edge_diffusion_coefficients[j].iteritems() )


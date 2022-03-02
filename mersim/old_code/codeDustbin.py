#!/usr/bin/env python
"""filename.py

Desc.

:version: 
:author:  szymon stoma
"""

    def discover_curvature( self, tolerance=None ):
        cell_norm = {}
        stained=[]
        if not tolerance:
            tolerance = 0.78
        for e in self.tissue._cells.edges():
            c, n = e
            if c not in cell_norm:
                cn = self.tissue.get_cell_normal( c )
                cell_norm[ c ] = cn
            else:
                cn = cell_norm[ c ]
            if n not in cell_norm:
                nn = self.tissue.get_cell_normal( n )
                cell_norm[ n ] = nn
            else:
                nn = cell_norm[ n ]  
            #print cn, nn, visual.dot( cn, nn )
            if visual.dot( cn, nn ) < tolerance:
                #print cn, nn
                stained.append(c)
                stained.append(n)
        
        for c in stained:
            self.tissue.cell_property( cell=c, property="was_under_angular_stress", value=True )
        #print stained
        b = self.tissue.cell_centers()
        for i in b.keys():
            if i in stained:
                color = (1,0,0)
            else:
                color = (1,1,1)
            visual.arrow( pos= b[i], axis=5*self.tissue.get_cell_normal( i ), color=color )

    def change_k_of_springs( self ):

        for i in self.forces[ "spring_force" ].springs:
            axis = i.m1.pos - i.m0.pos
            stress = (visual.mag( axis ) - i.l0)/i.l0

            if stress < 0.2:
                # small smaller tension
                if stress  < 0:
                    print "! stress:" ,stress
                    stress = 0.000000000000001
            else:
                # biger tension
                if stress > 0.4:
                    print "! stress:" ,stress
                    stress = 0.4
            print "old_k", i.k           
            i.k = self.const.spring_standart_k+20*stress
            print "new_k", i.k
            
    def mark_cell_velocity_field( self ):
        self._cell_velocity_field = {}
        for c in self.tissue.cells():
            self._cell_velocity_field[ c ] = self.tissue.cell_center( cell=c )
            
    def harvest_cell_velocity_field( self ):
        z  = {}
        for c in self._cell_velocity_field:
            if self.tissue._cells.has_node( c ):
                z[ c ] = (self._cell_velocity_field[ c ], self.tissue.cell_center( cell=c ) - self._cell_velocity_field[ c ])
                
        return z
        
    def display_cell_velocity_field( self ):
        d = visual.display()
        d.select()
        for i in self.harvest_cell_velocity_field().values():
            visual.arrow( pos=i[0], axis=i[1])
        return d
    
    def display_cell_velocity_field_projection_to_z( self ):
        d = visual.display()
        d.select()
        for i in self.harvest_cell_velocity_field().values():
            p = i[0]
            p.z=0
            v = i[1]
            v.z=0
            v = v*10
            visual.arrow( pos=p, axis=v)
        return d
    
    def primodium_influence_growth( self, step = None ):
        if not self.frame_nbr  >= step:
            return
        for c in self.tissue.cells():
            if  self.tissue.cell_property( cell = c, property="PrC") > 0:
                for w in self.tissue.cell2wvs_edges( c ):
                    self.id2spring( self.tissue.wv_edge_id( w ) ).spring_growth_if_under_tension( factor = self.const.auxin_spring_growth_rate)


    ##def plane(self, t):
    ##    b = 10000
    ##    s = -b
    ##    c = visual.convex(pos = [visual.vector(b,t,s), visual.vector(b,t,b),
    ##    visual.vector(s,t,b), visual.vector(s,t,s)], color= (0,0,0))
    
    ##def advance(self):
    ##    """Perform one Iteration of the system by advancing one timestep.
    ##    """
    ##    microstep = self.timestep / self.oversample
    ##    
    ##    self.time += self.timestep
    ##    
    ##    for i in range(self.oversample):
    ##        for f in self.forces.values():
    ##            f.apply()
    ##    
    ##    for mass in self.masses:
    ##        if not mass.fixed:
    ##            mass.calc_new_location(microstep)
    ##
    ##   #moved to cleaning step. visualisation is using this values
    ##   #mass.clear_force()



    ##def update_springs_acording_to_direction( self ):
    ##    """experimental
    ##    """
    ##    springs = self.forces["spring_force"].springs
    ##    for s in springs:
    ##        d = s.m0.sphere.pos - s.m1.sphere.pos
    ##        # projection on 'horizontal plane'
    ##        d.z = 0.
    ##        if visual.mag( d ) < 1:
    ##            #s.k = self.const.spring_standart_k
    ##            #s.cylinder.color = Color.spring
    ##            s.l0_dir = s.l0
    ##            s.k0 = self.const.spring_standart_k
    ##            continue
    ##        diff = visual.dot(d.norm(), self.direction)/3. 
    ##        #print diff
    ##        s.l0_dir = s.l0 - math.fabs( diff*2 )*s.l0  #math.fabs( visual.dot(d.norm(), self.direction) )
    ##        s.k0 = self.const.spring_standart_k - diff*self.const.spring_standart_k 
    ##        print "argh!!"
    ##        #c = Color.spring
    ##        #r = (1-diff)*5 - 4.3
    ##        #print r
    ##        #s.cylinder.color = (r, c[1], r) 
    ##
    #
    ##def associated_springs( self, mass ):
    ##    """Returns springs associated with mass.
    ##    """
    ##    return self._mass2springs 

    ##def update_springs_acording_to_global_direction( self ):
    ##    """experimental
    ##    """
    ##    springs = self.forces["spring_force"].springs
    ##    for s in springs:
    ##        d = s.m0.pos - s.m1.pos
    ##        s.k = math.fabs( visual.dot(d.norm(), self.const.division_symetry_direction) ) 

    

    ##def _associate_mass2spring(self, mass, spring):
    ##    """Associates mass with spring in self._mass2springs, self._spring2masses taking
    ##    care for updating and finding duplicates. it *must* be run after inserting the spring
    ##    into the system, when the _spring2mass_tag is set.
    ##    #"""
    ##    if not self._mass2springs.has_key( mass ):
    ##        self._mass2springs[ mass ] = [ spring ]
    ##    else:
    ##        springs = self._mass2springs[ mass ]
    ##        if spring not in springs:
    ##            springs.append( spring )
    ##            self._mass2springs[ mass ] = springs
    ##
    ##    if not self._spring2masses.has_key( spring ):
    ##        self._spring2masses[ spring ] = [ mass ]
    ##    else:    
    ##        masses = self._spring2masses[ spring ]
    ##        if mass not in masses:
    ##            masses.append( mass )
    ##            self._spring2masses[ spring ] = masses
    ##        
    ##def _deassociate_mass2spring( self, spring ):
    ##    """Remove association of mass with the spring. It *must* be run only while spring is delated. 
    ##    it *must* be run after removing the spring from the system, when the _spring2mass_tag is set.
    ##     
    ##    """
    ##    for m in self._spring2masses[ spring ]:
    ##        self._mass2springs[ m ] = self._mass2springs[ m ].remove( spring )
    ##        if self._mass2springs[ m ] == []:
    ##            self._mass2springs.pop( m )
    ##
    ##    self._spring2masses.pop( spring )

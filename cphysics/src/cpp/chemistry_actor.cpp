/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.container: utils package                                     
 *                                                                              
 *        Copyright 2006 INRIA - CIRAD - INRA                      
 *                                                                              
 *        File author(s): Jerome Chopard <jerome.chopard@sophia.inria.fr>         
 *                                                                              
 *        Distributed under the Cecill-C License.                               
 *        See accompanying file LICENSE.txt or copy at                          
 *            http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html       
 *                                                                              
 *        OpenAlea WebSite : http://openalea.gforge.inria.fr                    
 *       
 *                                                                       
 *-----------------------------------------------------------------------------*/

#include <iostream>

#include <math.h>
#include "cphysics/chemistry_actor.h"

namespace physics {
namespace chemistry {
	void Reaction::react (tank_list& tanks, double dt) {
		for (rmap::iterator it=creation.begin();
				it!=creation.end();
				++it) {
			tanks[it->first]->level += it->second*dt;
		}
		for (rmap::iterator it=decay.begin();
				it!=decay.end();
				++it) {
			tanks[it->first]->level /= (1. + it->second*dt);
		}
	}

	void ForwardTransport::react (tank_list& tanks, double dt) {
		for (pipe_list::iterator it=_pipe_list.begin();
				it!=_pipe_list.end();
				++it) {
			it->flux = it->strength * tanks[it->source]->level;
		}
		for (pipe_list::iterator it=_pipe_list.begin();
				it!=_pipe_list.end();
				++it) {
			tanks[it->source]->level -= it->flux * dt / tanks[it->source]->volume;
			tanks[it->target]->level += it->flux * dt / tanks[it->target]->volume;
		}
	}

};//chemistry
};//physics

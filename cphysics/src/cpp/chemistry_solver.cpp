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

#include "cphysics/chemistry_solver.h"

namespace physics {
namespace chemistry {
	ForwardEuler::~ForwardEuler () {
		for (actor_list::iterator it=_actor_list.begin();it!=_actor_list.end();++it) {
			delete *it;
		}
		for (tank_list::iterator it=_tank_list.begin();it!=_tank_list.end();++it) {
			delete *it;
		}
	}

	int ForwardEuler::add_tank (double volume, double level) {
		_tank_list.push_back(new Tank(volume,level));
		return _tank_list.size() - 1;
	}
	
	void ForwardEuler::step_react (double dt) {
		//int i = 0;
		for (actor_list::iterator it=_actor_list.begin();it!=_actor_list.end();++it) {
			//std::cout << i << std::endl;
			//i += 1;
			(*it)->react(_tank_list,dt);
		}
		boundary();
	}

};//chemistry
};//physics

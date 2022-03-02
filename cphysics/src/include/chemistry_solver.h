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

#ifndef __CPHYSICS_CHEMISTRY_SOLVER_H__
#define __CPHYSICS_CHEMISTRY_SOLVER_H__

#include <vector>

#include <boost/python.hpp>
using namespace boost::python;

#include "chemistry_utils.h"
#include "chemistry_actor.h"

namespace physics {
namespace chemistry {

	class CPHYSICS_EXPORT ForwardEuler {
	private:
		typedef std::vector<ChemistryActor*> actor_list;
	private:
		actor_list _actor_list;
		object _boundary_function;
		tank_list _tank_list;
	public:
		ForwardEuler () {}

		~ForwardEuler ();

		void set_volume (int tid, double v) {
			_tank_list[tid]->volume = v;
		}
		double volume (int tid) {
			return _tank_list[tid]->volume;
		}
		void set_level (int tid, double l) {
			_tank_list[tid]->level = l;
		}
		double level (int tid) {
			return _tank_list[tid]->level;
		}
		void set_boundary_function (object func) {
			_boundary_function=func;
		}
		void boundary () {
			_boundary_function();
		}

		int add_tank (double volume, double level=0);

		void add_actor (ChemistryActor* actor) {
			_actor_list.push_back(actor);
		}

		void step_react (double dt);

		void react (double dt, int nb_steps=1) {
			for (int i=0;i<nb_steps;++i) {
				step_react(dt);
			}
		}
	};

};//chemistry
};//physics
#endif //__CPHYSICS_CHEMISTRY_SOLVER_H__

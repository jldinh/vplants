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

#ifndef __CPHYSICS_CHEMISTY_ACTOR_H__
#define __CPHYSICS_CHEMISTY_ACTOR_H__

#include "chemistry_utils.h"

#include <vector>
#include <map>

namespace physics {
namespace chemistry {
	class CPHYSICS_EXPORT ChemistryActor {
	public:
		ChemistryActor () {}

		virtual void react (tank_list& tanks, double dt) {}
	};

	class CPHYSICS_EXPORT Reaction : public ChemistryActor {
	private:
		typedef std::map<int,double> rmap;
	private:
		rmap creation;
		rmap decay;
	public:
		Reaction ()
			: ChemistryActor() {}

		void set_creation (int tid, double val) {
			creation[tid]=val;
		}

		void set_decay (int tid, double val) {
			decay[tid]=val;
		}

		void react (tank_list& tanks, double dt);
	};

	struct CPHYSICS_EXPORT Pipe {
	public:
		int source;
		int target;
		double strength;
		double flux;
	
		Pipe ()
			: source(0),
			  target(0),
			  strength(0.),
			  flux(0.) {}

		Pipe (int source, int target, double strength)
			: source(source),
			  target(target),
			  strength(strength),
			  flux(0.) {}
	};

	class CPHYSICS_EXPORT ForwardTransport : public ChemistryActor {
	private:
		typedef std::vector<Pipe> pipe_list;
	private:
		pipe_list _pipe_list;
	public:
		ForwardTransport ()
			: ChemistryActor() {}

		void add_pipe (int source, int target, double strength) {
			_pipe_list.push_back(Pipe(source,target,strength));
		}

		void react (tank_list& tanks, double dt);
	};

};//chemistry
};//physics
#endif //__CPHYSICS_CHEMISTY_ACTOR_H__


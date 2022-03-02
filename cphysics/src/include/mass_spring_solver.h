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

#ifndef __CPHYSICS_MSSOLVER_H__
#define __CPHYSICS_MSSOLVER_H__

#include <vector>

#include <boost/python.hpp>
using namespace boost::python;

#include "mechanics_utils.h"
#include "spring.h"

namespace physics {
namespace mechanics {
	double LARGE = 1e9;
	
	class CPHYSICS_EXPORT DivergenceError {
	public:
		DivergenceError () {}
		~DivergenceError () {}
	};
	/* **************************************************
	*
	*	MSSolver
	*
	************************************************** */
	class CPHYSICS_EXPORT MSSolver2D {
	private:
		typedef std::vector<Spring2D*> spring_list;
	public:
		typedef Vector2 Vector;
	private:
		spring_list _spring_list;
		object _boundary_function;
		P2D_list _particules;
	public:
		MSSolver2D () {}

		~MSSolver2D ();

		/* *****************************************
		*
		*	accessors
		*
		***************************************** */
		double weight (int pid) {
			return _particules[pid].weight;
		}
		
		void set_weight (int pid, double w) {
			_particules[pid].weight = w;
		}
		
		void boundary () {
			_boundary_function();
		}
		
		void set_boundary_function (object func) {
			_boundary_function = func;
		}

		int add_particule ();

		Vector position (int pid) {
			return _particules[pid].pos;
		}
		
		void set_position (int pid, const Vector& pos) {
			_particules[pid].pos = pos;
		}

		Vector force (int pid) {
			return _particules[pid].force;
		}

		void set_force (int pid, const Vector& F) {
			_particules[pid].force = F;
		}
		
		void add_spring (Spring2D* spring) {
			_spring_list.push_back(spring);
		}

		/* *****************************************
		*
		*	deform
		*
		***************************************** */
		void compute_forces (P2D_list& particules);
		void update_positions (P2D_list& particules, double dt);
		
		double force_max (const P2D_list& particules);
		
		double deform (P2D_list& particules, double dt);
		
		void deform_to_equilibrium (double dt, double force_threshold);
	};

	class CPHYSICS_EXPORT MSSolver3D {
	private:
		typedef std::vector<Spring3D*> spring_list;
	public:
		typedef Vector3 Vector;
	private:
		spring_list _spring_list;
		object _boundary_function;
		P3D_list _particules;
		P3D_list* cur_part;
	public:
		MSSolver3D () {
			cur_part = &_particules;
		}

		~MSSolver3D ();

		/* *****************************************
		*
		*	accessors
		*
		***************************************** */
		void set_weight (int pid, double w) {
			(*cur_part)[pid].weight = w;
		}
		double weight (int pid) {
			return (*cur_part)[pid].weight;
		}
				
		void boundary () {
			_boundary_function();
		}
		
		void set_boundary_function (object func) {
			_boundary_function = func;
		}

		int add_particule ();
		
		P3D_list& particules () {
			return _particules;
		}

		Vector position (int pid) {
			return (*cur_part)[pid].pos;
		}
		
		void set_position (int pid, const Vector& pos) {
			(*cur_part)[pid].pos = pos;
		}

		Vector force (int pid) {
			return (*cur_part)[pid].force;
		}

		void set_force (int pid, const Vector& F) {
			(*cur_part)[pid].force = F;
		}
		
		void add_spring (Spring3D* spring) {
			_spring_list.push_back(spring);
		}

		/* *****************************************
		*
		*	deform
		*
		***************************************** */
		void compute_forces (P3D_list& particules);
		void update_positions (P3D_list& particules, double dt);
		
		double force_max (const P3D_list& particules);
		
		virtual double deform (P3D_list& particules, double dt);

		void deform_to_equilibrium (double dt, double force_threshold);
	};

	/* **************************************************
	*
	*	ForwardEuler
	*
	************************************************** */
	class CPHYSICS_EXPORT ForwardEuler2D : public MSSolver2D {
	public :
		ForwardEuler2D ()
		      : MSSolver2D() {}
		double deform (P2D_list& particules, double dt);
	};

	class CPHYSICS_EXPORT ForwardEuler3D : public MSSolver3D {
	private :
		int nb_iterations;
	public :
		ForwardEuler3D ()
		      : MSSolver3D(),
		        nb_iterations(100) {}
		double deform (P3D_list& particules, double dt);
	};

	/* **************************************************
	*
	*	ForwardMarching
	*
	************************************************** */
	class CPHYSICS_EXPORT ForwardMarching2D : public MSSolver2D {
	public :
		double DT_MAX;
		int NB_SUBDI;
		double ERR_MAX_THRESHOLD;
		double ERR_MIN_THRESHOLD;
	public :
		ForwardMarching2D ()
		      : MSSolver2D(),
		        DT_MAX(10.),
		        NB_SUBDI(10),
		        ERR_MAX_THRESHOLD(1e-3),
		        ERR_MIN_THRESHOLD(1e-4) {}
		double deform (P2D_list& particules, double dt);
		double _deform (P2D_list& particules, double dt);
	};

	class CPHYSICS_EXPORT ForwardMarching3D : public MSSolver3D {
	public :
		double DT_MAX;
		int NB_SUBDI;
		double ERR_MAX_THRESHOLD;
		double ERR_MIN_THRESHOLD;
		double prev_error;
		int nb_fine_iter;
	public :
		ForwardMarching3D ()
		      : MSSolver3D(),
		        DT_MAX(10.),
		        NB_SUBDI(10),
		        ERR_MAX_THRESHOLD(1e-3),
		        ERR_MIN_THRESHOLD(1e-4),
		        prev_error(-1.),
		        nb_fine_iter(0) {}
		double deform (P3D_list& particules, double dt);
		double _deform (P3D_list& particules, double dt);
	};

};//mechanics
};//physics
#endif //__CPHYSICS_MSSOLVER_H__

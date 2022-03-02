/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.cmechanics: mass spring solver package                       
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

#ifndef __CMECHANICS_MSSOLVER_H__
#define __CMECHANICS_MSSOLVER_H__

#include <vector>

#include <boost/python.hpp>
using namespace boost::python;

#include "mechanics_utils.h"
#include "spring.h"

namespace mechanics {
	double LARGE = 1e9;
	
	class CMECHANICS_EXPORT DivergenceError {
	public:
		DivergenceError () {}
		~DivergenceError () {}
	};
	/* **************************************************
	*
	*	MSSolver
	*
	************************************************** */
	class CMECHANICS_EXPORT MSSolver2D {
	private:
		typedef std::vector<Spring2D*> spring_list;
	public:
		typedef Vector2 Vector;
		typedef Particule2D Particule;
		typedef P2D_list P_list;
	private:
		spring_list _spring_list;
		object _boundary_function;
		P_list _particules;
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
			_particules[pid].pos = Vector(pos);
		}

		Vector force (int pid) {
			return _particules[pid].force;
		}

		void set_force (int pid, const Vector& F) {
			_particules[pid].force = Vector(F);
		}
		
		void add_spring (Spring2D* spring) {
			_spring_list.push_back(spring);
		}

		/* *****************************************
		*
		*	deform
		*
		***************************************** */
		void compute_forces ();
		void update_positions (double dt);
		
		double force_max ();
		
		virtual double deform (double dt);
		virtual void deform_to_equilibrium (double dt, double force_threshold);
	};

	class CMECHANICS_EXPORT MSSolver3D {
	private:
		typedef std::vector<Spring3D*> spring_list;
	public:
		typedef Vector3 Vector;
		typedef Particule3D Particule;
		typedef P3D_list P_list;
	protected:
		spring_list _spring_list;
		object _boundary_function;
		P_list _particules;
	public:
		MSSolver3D () {}

		~MSSolver3D ();

		/* *****************************************
		*
		*	accessors
		*
		***************************************** */
		void set_weight (int pid, double w) {
			_particules[pid].weight = w;
		}
		double weight (int pid) {
			return _particules[pid].weight;
		}
				
		void boundary () {
			_boundary_function();
		}
		
		void set_boundary_function (object func) {
			_boundary_function = func;
		}

		int add_particule ();
		
		P_list& particules () {
			return _particules;
		}

		Vector position (int pid) {
			return _particules[pid].pos;
		}
		
		void set_position (int pid, const Vector& pos) {
			_particules[pid].pos = Vector(pos);
		}

		Vector force (int pid) {
			return _particules[pid].force;
		}

		void set_force (int pid, const Vector& F) {
			_particules[pid].force = Vector(F);
		}
		
		void add_spring (Spring3D* spring) {
			_spring_list.push_back(spring);
		}

		/* *****************************************
		*
		*	deform
		*
		***************************************** */
		void compute_forces ();
		void update_positions (double dt);
		
		double force_max ();
		
		virtual double deform (double dt);
		virtual void deform_to_equilibrium (double dt, double force_threshold);
	};

	/* **************************************************
	*
	*	ForwardEuler
	*
	************************************************** */
	class CMECHANICS_EXPORT ForwardEuler2D : public MSSolver2D {
	private :
		int _nb_steps;
	public :
		ForwardEuler2D ()
		      : MSSolver2D(),
		       _nb_steps(1) {}
		double deform (double dt);
	};

	class CMECHANICS_EXPORT ForwardEuler3D : public MSSolver3D {
	private :
		int _nb_steps;
	public :
		ForwardEuler3D ()
		      : MSSolver3D(),
		       _nb_steps(1) {}
		double deform (double dt);
	};

	/* **************************************************
	*
	*	ForwardMarching
	*
	************************************************** */
	class CMECHANICS_EXPORT ForwardMarching2D : public MSSolver2D {
	private :
		int _nb_good_iter;
	public :
		ForwardMarching2D ()
		      : MSSolver2D(),
		        _nb_good_iter(0) {}
		double deform (double dt);
	};

	class CMECHANICS_EXPORT ForwardMarching3D : public MSSolver3D {
	private :
		int _nb_good_iter;
	public :
		ForwardMarching3D ()
		      : MSSolver3D(),
		        _nb_good_iter(0) {}
		double safe_apply_forces (double dt);
		double deform (double dt);
		void deform_to_equilibrium (double dt, double force_threshold);
	};

//	class CMECHANICS_EXPORT ForwardMarching2D : public MSSolver2D {
//	public :
//		double DT_MAX;
//		int NB_SUBDI;
//		double ERR_MAX_THRESHOLD;
//		double ERR_MIN_THRESHOLD;
//	public :
//		ForwardMarching2D ()
//		      : MSSolver2D(),
//		        DT_MAX(10.),
//		        NB_SUBDI(10),
//		        ERR_MAX_THRESHOLD(1e-3),
//		        ERR_MIN_THRESHOLD(1e-4) {}
//		double deform (double dt);
//	};

//	class CMECHANICS_EXPORT ForwardMarching3D : public MSSolver3D {
//	public :
//		int nb_fine_iter;
//	public :
//		ForwardMarching3D ()
//		      : MSSolver3D(),
//		        nb_fine_iter(0) {}
//		double deform (double dt);
//	};

};//mechanics

#endif //__CMECHANICS_MSSOLVER_H__

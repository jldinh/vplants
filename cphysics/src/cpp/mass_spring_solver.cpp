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

#include <algorithm>
#include "cphysics/mass_spring_solver.h"

namespace physics {
namespace mechanics {
	/* *******************************************************
	*
	*	MSSolver2D
	*
	*********************************************************/
	MSSolver2D::~MSSolver2D () {
		/*for (spring_list::iterator it=_spring_list.begin();it!=_spring_list.end();++it) {
			delete *it;
		}*/
		/*for (P2D_list::iterator it=_particules.begin();it!=_particules.end();++it) {
			delete *it;
		}*/
	}

	int MSSolver2D::add_particule () {
		_particules.push_back(Particule2D());
		return _particules.size() - 1;
	}
	
	void MSSolver2D::compute_forces (P2D_list& particules) {
		//set forces to zero
		for (P2D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			it->force = MSSolver2D::Vector();
		}
		
		//assign forces
		for (spring_list::iterator it = _spring_list.begin();
		                           it != _spring_list.end();
		                           ++it) {
			(*it)->assign_forces(particules);
		}
		
		//boundary condition
		boundary();
	}
	
	void MSSolver2D::update_positions (P2D_list& particules, double dt) {
		for (P2D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			it->pos += it->force * (dt / it->weight);
			if (it->pos.x() > LARGE or it->pos.y() > LARGE) {
				throw DivergenceError();
			}
		}		
	}
	
	double MSSolver2D::force_max (const P2D_list& particules) {
		double Fmax = 0;
		for (P2D_list::const_iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			Fmax = std::max(Fmax,norm( it->force ) );
		}		
		return Fmax;
	}
	
	double MSSolver2D::deform (P2D_list& particules, double dt) {
		compute_forces(particules);
		update_positions(particules,dt);
		return dt;
	}
	
	void MSSolver2D::deform_to_equilibrium (double dt, double force_threshold) {
		double Fmax = 2 * force_threshold;
		while ( Fmax > force_threshold ) {
			dt = deform(_particules,dt);
			Fmax = force_max(_particules);
			std::cout << "Fmax " << Fmax << std::endl;
		}
	}

	/* *******************************************************
	*
	*	MSSolver3D
	*
	*********************************************************/
	MSSolver3D::~MSSolver3D () {
		/*for (spring_list::iterator it=_spring_list.begin();it!=_spring_list.end();++it) {
			delete *it;
		}*/
		/*for (P3D_list::iterator it=_particules.begin();it!=_particules.end();++it) {
			delete *it;
		}*/
	}

	int MSSolver3D::add_particule () {
		_particules.push_back(Particule3D() );
		return _particules.size() - 1;
	}
	
	void MSSolver3D::compute_forces (P3D_list& particules) {
		//std::cout << "compute" << std::endl;
		//set forces to zero
		for (P3D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			it->force = MSSolver3D::Vector();
		}
		int i;
		/*PRINT
		i = 0;
		for (P3D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			std::cout << "F0" << i << " " << it->force << std::endl;
			++i;
		}*/
		
		//assign forces
		for (spring_list::iterator it = _spring_list.begin();
		                           it != _spring_list.end();
		                           ++it) {
			(*it)->assign_forces(particules);
		}
		/*PRINT
		i = 0;
		for (P3D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			std::cout << "F" << i << " " << it->force << std::endl;
			++i;
		}*/
		
		
		//boundary condition
		cur_part = &particules;
		boundary();
		/*PRINT
		i = 0;
		for (P3D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			std::cout << "Fb" << i << " " << it->force << std::endl;
			++i;
		}*/
		
	}
	
	void MSSolver3D::update_positions (P3D_list& particules, double dt) {
		for (P3D_list::iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			it->pos += it->force * (dt / it->weight);
			if (it->pos.x() > LARGE or it->pos.y() > LARGE or it->pos.z() > LARGE) {
				throw DivergenceError();
			}
		}		
	}
	
	double MSSolver3D::force_max (const P3D_list& particules) {
		double Fmax = 0;
		for (P3D_list::const_iterator it = particules.begin();
		                        it != particules.end();
		                        ++it) {
			Fmax = std::max(Fmax,norm( it->force ) );
		}		
		return Fmax;
	}
	
	double MSSolver3D::deform (P3D_list& particules, double dt) {
		//std::cout << "MSSolver" << std::endl;
		compute_forces(particules);
		update_positions(particules,dt);
		return dt;
	}
	
	void MSSolver3D::deform_to_equilibrium (double dt, double force_threshold) {
		double Fmax = 2 * force_threshold;
		while ( Fmax > force_threshold ) {
			dt = deform(_particules,dt);
			Fmax = force_max(_particules);
			std::cout << "Fmax " << Fmax << std::endl;
		}
		cur_part = &_particules;
	}

	/* *******************************************************
	*
	*	ForwardEuler
	*
	*********************************************************/
	double ForwardEuler2D::deform (P2D_list& particules, double dt) {
		for (int i = 0; i < 100; ++i) {
			compute_forces(particules);
			update_positions(particules,dt);
		}
		return dt;
	}

	double ForwardEuler3D::deform (P3D_list& particules, double dt) {
		std::cout << "Euler " << dt << std::endl;
		for (int i = 0; i < nb_iterations; ++i) {
			compute_forces(particules);
			update_positions(particules,dt);
			//std::cout << "Fmax " << force_max(particules) << std::endl;
		}
		return dt;
	}

	/* *******************************************************
	*
	*	ForwardMarching
	*
	*********************************************************/
	double ForwardMarching2D::deform (P2D_list& particules, double dt) {
		compute_forces(particules);
		return _deform(particules,dt);
	}
	
	double ForwardMarching2D::_deform (P2D_list& particules, double dt) {
		//compute ref
		P2D_list p_ref(particules);
		update_positions(p_ref,dt);
		
		//compute test
		double dt_test = dt / NB_SUBDI;
		P2D_list p_test(particules);
		update_positions(p_test,dt_test);
		
		for (int i = 0; i < NB_SUBDI; ++i) {
			compute_forces(p_test);
			update_positions(p_test,dt_test);
		}
		
		//put forces in particules
		P2D_list::iterator it = particules.begin();
		P2D_list::iterator it_test = p_test.begin();
		while (it != particules.end() and it_test != p_test.end() ) {
			it->force = it_test->force;
			++ it;
			++ it_test;
		}
		
		//compare
		double err = 0.;
		P2D_list::iterator it_ref = p_ref.begin();
		it_test = p_test.begin();
		while (it_ref != p_ref.end() and it_test != p_test.end() ) {
			err = std::max(err,norm( it_ref->pos - it_test->pos ) );
			++ it_ref;
			++ it_test;
		}
		std::cout << "err" << err << "," << dt << std::endl;
		if (err > ERR_MAX_THRESHOLD) {
			return _deform(particules,dt / 2.);
		}
		else {
		if (err < ERR_MIN_THRESHOLD) {
			return std::min(DT_MAX,dt * 1.3);
		}
		else {
			return dt;
		} }
	}

	double ForwardMarching3D::deform (P3D_list& particules, double dt) {
		//std::cout << "deform" << std::endl;
		compute_forces(particules);
		return _deform(particules,dt);
	}
	
	double ForwardMarching3D::_deform (P3D_list& particules, double dt) {
		//std::cout << "_deform" << std::endl;
		//compute ref
		//std::cout << "ref" << std::endl;
		try {
			P3D_list p_ref(particules);
			update_positions(p_ref,dt);
			
			//compute test
			//std::cout << "test" << std::endl;
			double dt_test = dt / NB_SUBDI;
			P3D_list p_test(particules);
			update_positions(p_test,dt_test);
			
			for (int i = 0; i < NB_SUBDI; ++i) {
				//std::cout << "test" << i << std::endl;
				compute_forces(p_test);
				update_positions(p_test,dt_test);
			}
			/*PRINT
			int i = 0;
			std::cout << "pos";
			for (P3D_list::iterator it = p_test.begin();
			                        it != p_test.end();
			                        ++it) {
				std::cout << " " << it->pos;
				++i;
			}
			std::cout << std::endl;*/
		
			//put forces in particules
			P3D_list::iterator it = particules.begin();
			P3D_list::iterator it_test = p_test.begin();
			while (it != particules.end() and it_test != p_test.end() ) {
				it->force = it_test->force;
				++ it;
				++ it_test;
			}
			
			//compare
			double err = 0.;
			P3D_list::iterator it_ref = p_ref.begin();
			it_test = p_test.begin();
			while (it_ref != p_ref.end() and it_test != p_test.end() ) {
				err = std::max(err,norm( it_ref->pos - it_test->pos ) );
				++ it_ref;
				++ it_test;
			}
			std::cout << "                     err " << err << "," << prev_error << "," << dt << "," << nb_fine_iter << std::endl;
			if (prev_error > 0) {
				//previous step dt *= 1.5
				if (err > (prev_error * 1.4) and err > ERR_MIN_THRESHOLD) {
					std::cout << "                     go back" << std::endl;
					//go back
					nb_fine_iter = 0;
					return _deform(particules,dt / 1.5);
				}
			}
			if (err > ERR_MAX_THRESHOLD) {
				//std::cout << "MAX" << std::endl;
				prev_error = -1.;
				nb_fine_iter = 0;
				return _deform(particules,dt / 2.);
			}
			else {
				//put positions in particules
				it = particules.begin();
				it_test = p_test.begin();
				while (it != particules.end() and it_test != p_test.end() ) {
					it->pos = it_test->pos;
					++ it;
					++ it_test;
				}
				if (err < ERR_MIN_THRESHOLD and nb_fine_iter > 10) {
					prev_error = err;
					nb_fine_iter = 0;
					return std::min(DT_MAX,dt * 1.5);
				}
				else {
					prev_error = -1.;
					nb_fine_iter += 1;
					return dt;
				}
			}
		}
		catch (DivergenceError e) {
			std::cout << "nan " << dt << std::endl;
			nb_fine_iter = 0;
			return _deform(particules,dt / 2.);
		}
	}

};//mechanics
};//physics

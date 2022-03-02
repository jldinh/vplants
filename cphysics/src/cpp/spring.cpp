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
#include "cphysics/spring.h"

namespace physics {
namespace mechanics {
	/* *******************************************************
	*
	*	LinearSpring2D
	*
	*********************************************************/
	double LinearSpring2D::strain (P2D_list& particules) {
		Particule2D& p1 = particules[_pid1];
		Particule2D& p2 = particules[_pid2];
		Vector2 dir = p2.pos - p1.pos;
		double l = sqrt( dir * dir );
		return (l - _ref_length) / _ref_length;
	}

	double LinearSpring2D::stress (P2D_list& particules) {
		return _stiffness * strain(particules);
	}

	void LinearSpring2D::assign_forces (P2D_list& particules) {
		//compute force
		Particule2D& p1 = particules[_pid1];
		Particule2D& p2 = particules[_pid2];
		Vector2 dir = p2.pos - p1.pos;
		dir.normalize();
		Vector2 F = dir * stress(particules);
		//std::cout << _point1 << "," << _point2 << "," << l << "\t" << st << std::endl;
		//assign forces
		p1.force += F;
		p2.force -= F;
	}

	/* *******************************************************
	*
	*	LinearSpring3D
	*
	*********************************************************/
	double LinearSpring3D::strain (P3D_list& particules) {
		Particule3D& p1 = particules[_pid1];
		Particule3D& p2 = particules[_pid2];
		Vector3 dir = p2.pos - p1.pos;
		double l = sqrt( dir * dir );
		return (l - _ref_length) / _ref_length;
	}

	double LinearSpring3D::stress (P3D_list& particules) {
		return _stiffness * strain(particules);
	}

	void LinearSpring3D::assign_forces (P3D_list& particules) {
		//compute force
		Particule3D& p1 = particules[_pid1];
		Particule3D& p2 = particules[_pid2];
		Vector3 dir = p2.pos - p1.pos;
		dir = dir / sqrt( dir * dir );
		Vector3 F = dir * stress(particules);
		//std::cout << _point1 << "," << _point2 << "," << l << "\t" << st << std::endl;
		//assgin forces
		p1.force += F;
		p2.force -= F;
	}

};//mechanics
};//physics

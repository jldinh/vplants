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

#ifndef __CPHYSICS_SPRING_FEM_H__
#define __CPHYSICS_SPRING_FEM_H__

#include <iostream>

#include "geometry_utils.h"
#include "mechanics_utils.h"
#include "spring.h"

namespace physics {
namespace mechanics {
	Frame3 triangle_frame (const Vector3& pt1, const Vector3& pt2, const Vector3& pt3);
	
	//kronecker function
	int kron (int i, int j) {
		if ( i == j ) {
			return 1;
		}
		else {
			return 0;
		}
	};
	
	Tensor2222 CPHYSICS_EXPORT isotropic_material2D (double E, double nu);
	
	class CPHYSICS_EXPORT TriangleMembrane3D : public Spring3D {
	public:
		int _big_displacements;
		//corners
		int pid0;
		int pid1;
		int pid2;
		//material
		Tensor2222 _mat;
		//ref coords
		double r1;
		double r2;
		double s2;
		double thickness;
		//local derivatives
		Tensor32 dN;
	
	public:
		TriangleMembrane3D (int pid0, int pid1, int pid2, double r1, double r2, double s2, double thickness)
			: Spring3D(),
			  _big_displacements(1),
			  pid0(pid0),
			  pid1(pid1),
			  pid2(pid2),
			  _mat(),
			  r1(r1),
			  r2(r2),
			  s2(s2),
			  thickness(thickness),
			  dN() {
			  dN(0,0) = - 1. / r1;
			  dN(0,1) = (r2 - r1) / (r1 * s2);
			  dN(1,0) = 1. / r1;
			  dN(1,1) = - r2 / (r1 * s2);
			  dN(2,0) = 0.;
			  dN(2,1) = 1. / s2;
			  }

		void set_material (const Tensor2222& mat) {
			_mat = mat;
		}
		
		double surface () {
			return r1 * s2 / 2.;
		}
		Tensor32 displacement (const P3D_list& particules, const Frame3& local_frame);
		Tensor32 displacement (const P3D_list& particules);
		Tensor22 gradU (const Tensor32& U);
		Tensor22 strain (const Tensor22& dU);
		Tensor22 strain (const P3D_list& particules) {
			return strain(gradU(displacement(particules) ) );
		}
		Tensor3222 strain_derivative (const Tensor22& dU);
		Tensor22 stress (const Tensor22& E);
		Tensor22 stress (const P3D_list& particules) {
			return stress(strain(particules) );
		}
		Tensor3222 stress_derivative (const Tensor3222& dE);
		
		void assign_forces (P3D_list& particules);
	};

};//mechanics
};//physics
#endif //__CPHYSICS_SPRING_FEM_H__


/* -*-c++-*- 
 *------------------------------------------------------------------------------
 *                                                                              
 *        openalea.cmechanics: spring fem package                               
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

#include "cmechanics/spring_fem.h"

namespace mechanics {
	/* *******************************************************
	*
	*	general
	*
	*********************************************************/
	Frame3 triangle_frame (const Vector3& pt1, const Vector3& pt2, const Vector3& pt3) {
		//std::cout << "triangle frame" << std::endl;
		//std::cout << "pt1" << pt1 << std::endl;
		//std::cout << "pt2" << pt2 << std::endl;
		//std::cout << "pt3" << pt3 << std::endl;
		Frame3 ret;
		Vector3 tmp;
		//TODO tmp patch
		tmp = pt2 - pt1;
		tmp.normalize();
		ret.er = tmp; //tmp / norm(tmp);
		tmp = ret.er ^ (pt3 - pt1);
		tmp.normalize();
		ret.et = tmp; //tmp / norm(tmp);
		ret.es = ret.et ^ ret.er;
		ret.O = pt1;
		return ret;
	}
	
	/* *******************************************************
	*
	*	TriangleMembrane3D
	*
	*********************************************************/
	Tensor32 TriangleMembrane3D::displacement (const P3D_list& particules, const Frame3& local_frame) {
		//std::cout << "compute disp" << std::endl;
		Tensor32 U;
		const Vector3& pt0 = particules[pid0].pos;
		const Vector3& pt1 = particules[pid1].pos;
		const Vector3& pt2 = particules[pid2].pos;
		
		U(0,0) = 0.;
		U(0,1) = 0.;
		U(1,0) = (pt1 - local_frame.O) * local_frame.er - r1;
		U(1,1) = 0.;
		U(2,0) = (pt2 - local_frame.O) * local_frame.er - r2;
		U(2,1) = (pt2 - local_frame.O) * local_frame.es - s2;
		//std::cout << "pt2" << pt2 << std::endl;
		//std::cout << "0" << local_frame.O << std::endl;
		//std::cout << "es" << local_frame.es << std::endl;
		//std::cout << "s2" << s2 << std::endl;
		//std::cout << U(2,1) << std::endl;
		return U;
	}
	
	Tensor32 TriangleMembrane3D::displacement (const P3D_list& particules) {
		return displacement(particules,triangle_frame(particules[pid0].pos,
		                                              particules[pid1].pos,
		                                              particules[pid2].pos) );
	}
	
	Tensor22 TriangleMembrane3D::gradU (const Tensor32& U) {
		Tensor22 dU;
		double sum;
		for (int i = 0; i < 2; ++i) {
			for (int j = 0; j < 2; ++j) {
				sum = 0.;
				for (int n = 0; n < 3; ++n) {
					sum += U(n,i) * dN(n,j);
				}
				dU(i,j) = sum;
			}
		}
		
		return dU;
	}
	
	Tensor22 TriangleMembrane3D::strain (const Tensor22& dU) {
		int bd = _big_displacements;
		Tensor22 E;
		double sum;
		
		for (int i = 0; i < 2; ++i) {
			for (int j = 0; j < 2; ++j) {
				sum = 0.;
				for (int k = 0; k < 2; ++k) {
					sum += dU(k,i) * dU(k,j);
				}
				E(i,j) = 0.5 * ( dU(j,i) + dU(i,j) + bd * sum );
			}
		}
		
		return E;
	}
	
	Tensor3222 TriangleMembrane3D::strain_derivative (const Tensor22& dU) {
		int bd = _big_displacements;
		//initialise
		Tensor3222 dE;
		
		//fill coefficients
		for (int n = 0; n < 3; ++n) {
			for (int m = 0; m < 2; ++m) {
				for (int i = 0; i < 2; ++i) {
					for (int j = 0; j < 2; ++j) {
						dE(n,m,i,j) = 0.5 * ( dN(n,i) * ( kron(m,j) + bd * dU(m,j) )
											+ dN(n,j) * ( kron(m,i) + bd * dU(m,i) ) );
					}
				}
			}
		}
		
		//return
		return dE;
	}
	
	Tensor22 TriangleMembrane3D::stress (const Tensor22& E) {
		Tensor22 S;
		double sum;
		
		for (int i = 0; i < 2; ++i) {
			for (int j = 0; j < 2; ++j) {
				sum = 0.;
				for (int k = 0; k < 2; ++k) {
					for (int l = 0; l < 2; ++l) {
						sum += _mat(i,j,k,l) * E(k,l);
					}
				}
				S(i,j) = sum;
			}
		}
		
		return S;
	}
	
	Tensor3222 TriangleMembrane3D::stress_derivative (const Tensor3222& dE) {
		//initialise
		Tensor3222 dS;
		double sum;
		
		//fill coefficients
		for (int n = 0; n < 3; ++n) {
			for (int m = 0; m < 2; ++m) {
				for (int i = 0; i < 2; ++i) {
					for (int j = 0; j < 2; ++j) {
						sum = 0.;
						for (int k = 0; k < 2; ++k) {
							for (int l = 0; l < 2; ++l) {
								sum += _mat(i,j,k,l) * dE(n,m,k,l);
							}
						}
						dS(n,m,i,j) = sum;
					}
				}
			}
		}
		
		//return
		return dS;
	}
	
	void TriangleMembrane3D::assign_forces (P3D_list& particules) {
		//local actual frame
		Frame3 lf = triangle_frame(particules[pid0].pos
								  ,particules[pid1].pos
								  ,particules[pid2].pos);
		
		//displacement
		Tensor32 U = displacement(particules,lf);
		/*std::cout << "displacement" << std::endl;
		for (int i = 0; i < 3; ++i) {
			for (int j = 0; j < 2; ++j) {
				std::cout << U(i,j) << std::endl;
			}
		}*/
		Tensor22 dU = gradU(U);
		
		//strain / stress
		Tensor22 E = strain(dU);
		Tensor22 S = stress(E);
		
		//strain / stress derivatives
		Tensor3222 dE = strain_derivative(dU);
		Tensor3222 dS = stress_derivative(dE);
		
		//surface for integration
		double V = surface() * thickness;
		
		//compute local forces
		Tensor32 dW;
		double sum;
		
		for (int n = 0; n< 3; ++n) {
			for (int m = 0; m < 2; ++m) {
				sum = 0.;
				for (int i = 0; i < 2; ++i) {
					for (int j = 0; j < 2; ++j) {
						sum += dS(n,m,i,j) * E(i,j) + S(i,j) * dE(n,m,i,j);
					}
				}
				dW(n,m) = 0.5 * V * sum;
				//std::cout << n << "," << m << ": " << sum << std::endl;
			}
		}
		
		//assign global forces
		particules[pid0].force -= lf.er * dW(0,0) + lf.es * dW(0,1);
		particules[pid1].force -= lf.er * dW(1,0) + lf.es * dW(1,1);
		particules[pid2].force -= lf.er * dW(2,0) + lf.es * dW(2,1);
	}
	
};//mechanics


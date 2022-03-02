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

#ifndef __CPHYSICS_GEOMETRY_UTILS_H__
#define __CPHYSICS_GEOMETRY_UTILS_H__

#include <vector>
using std::vector;

#include "plantgl/math/util_vector.h"
#include "config.h"

TOOLS_USING_NAMESPACE

namespace physics {
namespace mechanics {
	struct CPHYSICS_EXPORT Frame3 {
		Vector3 O;
		Vector3 er;
		Vector3 es;
		Vector3 et;

		Frame3 ()
			: O(),
			  er(),
			  es(),
			  et() {}
	};
	
	class CPHYSICS_EXPORT Tensor22 {
	private:
		vector<vector<double> > _coeff;
	public:
		Tensor22 ();
		
		double& operator() (int i, int j) {
			return _coeff[i][j];
		}
		
		double operator() (int i, int j) const {
			return _coeff[i][j];
		}
		
	};

	class CPHYSICS_EXPORT Tensor32 {
	private:
		vector<vector<double> > _coeff;
	public:
		Tensor32 ();
		
		double& operator() (int i, int j) {
			return _coeff[i][j];
		}
		
		double operator() (int i, int j) const {
			return _coeff[i][j];
		}
		
	};

	class CPHYSICS_EXPORT Tensor2222 {
	private:
		vector<vector<vector<vector<double> > > > _coeff;
	public:
		Tensor2222 ();
		
		double& operator() (int i, int j, int k, int l) {
			return _coeff[i][j][k][l];
		}
		
		double operator() (int i, int j, int k, int l) const {
			return _coeff[i][j][k][l];
		}
		
	};

	class CPHYSICS_EXPORT Tensor3222 {
	private:
		vector<vector<vector<vector<double> > > > _coeff;
	public:
		Tensor3222 ();
		
		double& operator() (int i, int j, int k, int l) {
			return _coeff[i][j][k][l];
		}
		
		double operator() (int i, int j, int k, int l) const {
			return _coeff[i][j][k][l];
		}
		
	};

};//mechanics
};//physics
#endif //__CPHYSICS_GEOMETRY_UTILS_H__


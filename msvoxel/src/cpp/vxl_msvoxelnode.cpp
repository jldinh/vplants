/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 *
 *       $Source$
 *       $Id: vxl_msvoxelnode.cpp 3268 2007-06-06 16:44:27Z dufourko $
 *
 *       Forum for AMAPmod developers    : amldevlp@cirad.fr
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */



#include "vxl_msvoxelnode.h"
#include "tool/util_math.h"
#include <bitset>

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

/* ----------------------------------------------------------------------- */

MSVoxelNode::MSVoxelNode(Tile * Complex,
                       unsigned char Scale,
                       TileType Type,
                       const uint16_t Num,
                       const Vector3& PMin,
                       const Vector3& PMax,
		       const int _nx,
		       const int _ny,
		       const int _nz
) :
    Voxel(Complex,Scale,Type,Num,PMin,PMax),
    __components(NULL),
    __objects(0),
    __gridIndex(-1){
  nx = _nx ;  ny = _ny ;  nz = _nz; 
  interceptedTrianglesArea=0.;
}
MSVoxelNode::MSVoxelNode(Tile * Complex,
		     unsigned char Scale,
		     TileType Type,
		     const int _nx,
		     const int _ny,
		     const int _nz
) :
    Voxel(Complex,Scale,Type,0, TOOLS(Vector3::ORIGIN),
			TOOLS(Vector3::ORIGIN)),
	__components(NULL),
		__objects(0),
    __gridIndex(-1){
  nx = _nx ;  ny = _ny ;  nz = _nz; 
  interceptedTrianglesArea=0.;
}



MSVoxelNode::~MSVoxelNode(){
    if(__components) delete [] __components;
}

bool MSVoxelNode::setComponents(MSVoxelNode * _components){
    __components =_components;
    return true;
}

bool MSVoxelNode::isDecomposed() const{
    return (__components != NULL);
}


MSVoxelNode *  MSVoxelNode::decompose(const int v_nx,const int v_ny,const int v_nz)
{
  assert(v_nx>0);
  assert(v_ny>0);
  assert(v_nz>0);

  int size = nx * ny * nz;
  real_t __xInit, __yInit, __zInit, __x, __y, __z;
  __x = __xInit = (__ur.x() - __ll.x()) / nx ;
  __y = __yInit = (__ur.y() - __ll.y()) / ny ;
  __z = __zInit = (__ur.z() - __ll.z()) / nz ;
//printf ("init : (%.2f,%.2f,%.2f)\n",__x,__y,__z);
  if(!__components)
  {
    
    Vector3 __center = (__ll+__ur)/2;
    if(!(fabs(__xInit) > GEOM_EPSILON &&
	 fabs(__yInit) > GEOM_EPSILON &&
	 fabs(__yInit) > GEOM_EPSILON ))
      {
	__components = NULL;
	return __components;
      }

    __components = new MSVoxelNode[size];
    for(uint16_t _i1 = 0; _i1 < size ; _i1++)
      __components[_i1] = MSVoxelNode(this,(unsigned int)(__scale+1),__type,0,__ll,__ur, v_nx, v_ny, v_nz);
 
    __z = __ll.z();  
    int index = 0;
    for(uint16_t _k = 0; _k < nz ; _k++)
    {
		__y = __ll.y();
		for(uint16_t _j = 0; _j < ny ; _j++)
		{
			__x = __ll.x();
			for(uint16_t _i = 0; _i < nx ; _i++)
			{
				__components[index].getNum() = index;
				__components[index].getMinCoord() = Vector3( __x          , __y          , __z          ) ;
				__components[index].getMaxCoord() = Vector3( __x + __xInit, __y + __yInit, __z + __zInit) ;
				//printf ("init coo Min : (%.2f, %.2f, %.2f), Max : (%.2f,%.2f,%.2f)\n", __components[index].getMinCoord().x(), __components[index].getMinCoord().y(), __components[index].getMinCoord().z(), __components[index].getMaxCoord().x(), __components[index].getMaxCoord().y(), __components[index].getMaxCoord().z());
				__x += __xInit;
				index ++;
			}
			//printf("\n");
			__y += __yInit;
		}  
		__z += __zInit;
	//	printf("\n");
     }
	
  }
  return __components;
  
}


/* ----------------------------------------------------------------------- */

MSVoxelNode * MSVoxelNode::getRight() const {
    if(!__Complex) return NULL;
    MSVoxelNode * _a = (MSVoxelNode *)__Complex;
	assert(int(__num) < nx*ny*nz);
    int y = (int(__num) / nx) % ny;
    
    if( y == (ny-1) )
      {
      
	y *= -nx;
	_a = _a->getRight();
	if(!(_a) || !_a->isDecomposed()) return _a;
      }
    else
      y = nx;
    return _a->getComponent( __num + y );
}

MSVoxelNode * MSVoxelNode::getLeft() const {
    if(!__Complex) return NULL;
    MSVoxelNode * _a = (MSVoxelNode *)__Complex;
	assert(int(__num) < nx*ny*nz);
    int y = (int(__num) / nx) % ny; // 3 ol au lieu de 2(conversion) : bitset<8> location(__num);

    if( y == 0 )
      {
      // assert(int(__num) > 3);
	y = nx * (ny-1); // + 3 ol
	_a = _a->getLeft();
	if(!(_a) || !_a->isDecomposed()) return _a;
      }
    else
      y = -nx;

    return _a->getComponent( __num + y ); // location.flip(2).to_ulong() // -1
}

MSVoxelNode * MSVoxelNode::getUp() const {
    if(!__Complex) return NULL;
    MSVoxelNode * _a = (MSVoxelNode *)__Complex;
	assert(int(__num) < nx*ny*nz);
    int z = int(__num) / (nx * ny);   
 
    if( z == (nz-1) )
      {
	z *= - nx * ny;
	_a = _a->getUp();
	if(!(_a) || !_a->isDecomposed()) return _a;
      }
    else
      z = nx * ny;

    return _a->getComponent( __num + z );
}

MSVoxelNode * MSVoxelNode::getDown() const {
    if(!__Complex) return NULL;
    MSVoxelNode * _a = (MSVoxelNode *)__Complex;
	assert(int(__num) < nx*ny*nz);
    int z = int(__num) / (nx * ny);

    if( z == 0 )
      {
	z = nx * ny * (nz-1);
	_a = _a->getDown();
	if(!(_a) || !_a->isDecomposed()) return _a;
      }
    else
      z = - nx * ny;

    return _a->getComponent( __num + z );
}

MSVoxelNode * MSVoxelNode::getFront() const {
    if(!__Complex) return NULL;
    MSVoxelNode * _a = (MSVoxelNode *)__Complex;
	assert(int(__num) < nx*ny*nz);
	assert(int(__num) >=0);
    int x = int(__num) % nx ;

    if( x == (nx-1) )
      {
	x*=-1;
	_a = _a->getFront();
	if(!(_a) || !_a->isDecomposed()) return _a;
      }
    else
      x = 1;

    return _a->getComponent( __num + x );
}

MSVoxelNode * MSVoxelNode::getBack() const {
    if(!__Complex) return NULL;
    MSVoxelNode * _a = (MSVoxelNode *)__Complex;
	assert(int(__num) < nx*ny*nz);
	
    int x = int(__num) % nx ;

    if( x == 0 )
      {
	x = nx - 1;
	_a = _a->getBack();
	if(!(_a) || !_a->isDecomposed()) return _a;
      }
    else 
      x = -1;

    return _a->getComponent( __num + x );
}


int MSVoxelNode::getNx() const{
  return nx;
}
 
int MSVoxelNode::getNy() const{
  return ny;
}
  
 
int MSVoxelNode::getNz() const{
  return nz;
}

void MSVoxelNode::setN(int _nx, int _ny, int _nz){
  nx = _nx; ny = _ny; nz = _nz;
}

int MSVoxelNode::getNxNyNz() const{
  return (nx * ny * nz);
}






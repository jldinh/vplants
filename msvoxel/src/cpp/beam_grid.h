/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): O. Puech (puech.olivier@orange.fr)
 *						 F. Boudon (frederic.boudon@cirad.fr)
 *
 *       $Source$
 *       $Id: beam_grid.h 3268 2007-06-06 16:44:27Z dufourko $
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

/*! \file beam_ray.h
    \brief Definition of GeomRay.
*/



#ifndef __beam_grid_h__
#define __beam_grid_h__


/* ----------------------------------------------------------------------- */

#include "plantgl/pgl_namespace.h"
#include "plantgl/scenegraph/container/indexarray.h"

#include "plantgl/pgl_math.h"
#include <math.h>
#include <list>


/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

/** 
    
*/

/* ----------------------------------------------------------------------- */
;

struct equation
{
        TOOLS(Vector3) ABC;
        real_t D;
};

class   GeomGrid
{

private :
  
  /// grid dimensions.
  int nx, ny, nz;
  
public :

  /// Constructor x,y,z are the grid dimensions along x,y,z
  GeomGrid(int x, int y, int z);

  /// Destructor
  ~GeomGrid();
 
  /*! returns the code of a discrete point defined by its discrete coordinates */
  // if this is a 100*100*100 grid
  // for ex. (x=2,y=6,z=98) returns an int that identifies 
  // uniquely the corresponding voxel (which is used in MSVoxel
  // see method Node* getComponent(int code)

  int code(int x,int y, int z);

  /*! returns the code of a real_t point defined by its coordinates */
  int code(const TOOLS(Vector3)& v);

  /* tests that a point belongs to the grid for different types of coordinates */
  bool IsInTheGrid(int x,int y, int z);
  bool IsInTheGrid(const TOOLS(Vector3)& v);
  int getNx() const {
    return nx;
  } 
  /// return grid size on x
  int& getNx() {
    return nx;
  } 
  /// return grid size on y
  int getNy() const {
    return nx;
  }  
  /// return grid size on y
  int& getNy() {
    return nx;
  }
  /// return grid size on z
  int getNz() const {
    return nz;
  } 
  /// return grid size on z
  int& getNz() {
    return nz;
  }
  
  /*! gives the list of voxels whitch pave the triangle */
  // Sres is the resulting list of voxels (encoded as ints)
  // cooVox is the triangle points (a,b,c)
  void intersectTriangle(std::list<int>& Sres, TOOLS(Vector3) cooVox[]);


  /*! compute the 2-D intersection of the grid projection and triangle projection */
  void algoByPlane( int a, int b , // a=0, b=1 means plane x,y; a=0, b=2 means plane x,z; ...
                    TOOLS(Vector3) cooVoxel[], // cooVox is the triangle points (a,b,c)
                    int *tabMin[3], // result: 
                    int *tabMax[3], // result:
                    const TOOLS(Vector3)& VMin, // Min point of the bounding boxe
                    const TOOLS(Vector3)& VMax, // Max point of the bounding boxe
                    int sort[3][3] 
                  );


  /*! compute Min or max value of an AB segment */
  void marquer( int *tab[], //result (usually tabMin or tabMax)
                const TOOLS(Vector3)& VMin, // Min point of the bounding boxe
                const TOOLS(Vector3)& VMax, // Max point of the bounding boxe
                const int a,  // absciss axes
                const int b,  // ordonnée axes
                TOOLS(Vector3) vertexA , // Point A of the AB Segment
                TOOLS(Vector3) wid_dir3D // wid_dir of the AB vector
              );  
};

/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif


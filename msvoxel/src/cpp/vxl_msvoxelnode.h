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
 *       $Id: vxl_msvoxelnode.h 3268 2007-06-06 16:44:27Z dufourko $
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


/*! \file vxl_MSVoxelnode.h
    \brief Definition of OctreeNode.
*/


#ifndef __vxl_msvoxelnode_h__
#define __vxl_msvoxelnode_h__

/* ----------------------------------------------------------------------- */

#include "tool/config.h"
#include "plantgl/algo/grid/voxel.h"
#include "plantgl/scenegraph/scene/scene.h"

/* ----------------------------------------------------------------------- */

 /**
     \class OctreeNode
     \brief A Octree Node is a Voxel that can be decomposed into 8 sub voxel to make an octree.
 */

/* ----------------------------------------------------------------------- */
PGL_USING_NAMESPACE

class GEOM_API MSVoxelNode : public Voxel {

     public :


     /** Default constructor. */
        MSVoxelNode(Tile * Complex = 0,
                   const unsigned char Scale = 0,
                   const TileType Type = Empty,
                   const uint16_t Num = 0,
                   const TOOLS(Vector3)& PMin = TOOLS(Vector3::ORIGIN),
                   const TOOLS(Vector3)& PMax = TOOLS(Vector3::ORIGIN),
		   const int _nx = 2,
		   const int _ny = 2,
		   const int _nz = 2
		  );
        MSVoxelNode(Tile * Complex,
	          const unsigned char Scale,
		  const TileType Type,
		  const int _nx,
		  const int _ny,
		  const int _nz
	    );
     /// Destructor
     virtual ~MSVoxelNode();


     /// Return components of \e self.
     const MSVoxelNode * getComponents() const {
        return __components;
     }

     /** Set components \e _components to \e self.
        \pre
        - \e the number of components must be equal to 8. */
     bool setComponents(MSVoxelNode * _components);

     virtual uchar_t getComponentsSize() const {
        return (__components ? uchar_t(getNxNyNz()) : uchar_t(0));
     }

     /** Returns the \e i-th components  of \e self
        \pre
       - \e i must be strictly less than the number of components of \e self. */
    inline MSVoxelNode * getComponent(uint16_t i) const {
           return &(__components[i]);
    }

  /// Return geometry intersecting \e self.
  const ScenePtr& getGeometry() const {
    return __objects;
  }

  /// Return geometry intersecting \e self.
  ScenePtr getGeometry() {
    return __objects;
  }

  /// Set the geometry intersecting \e self.
  void setGeometry( const ScenePtr& scene ) {
    __objects= scene;
  }

  /** Returns the \e i-th geometry intersecting  \e self
      \pre
      - \e i must be strictly less than the number of components of \e self. */
  inline  Shape3DPtr getGeometry(uint32_t i) const {
    return __objects->getAt(i);
  }

  virtual uint32_t getGeometrySize() const {
    return __objects->getSize();
  }

  virtual bool isDecomposed() const;

     /*! Decompose \e self into 8 sub MSVoxel nodes with default values :
       \post
       -  complex is \e self
       -  scale is self's scale + 1
       -  type is the same has \e self
       -  Num are automaticaly attributed
       -  pmin and pmax are calculated
       -
       -  z = 0,
       -  ----------> y
       -  | 0 | 4 |
       -  -----
       -  | 1 | 5 |
       -  -----
       -  |
       -  x
       -
       -  and z = 1
       -  ----------> y
       -  | 2 | 6 |
       -  -----
       -  | 3 | 7 |
       -  -----
       -  |
       -  x

     */
  virtual MSVoxelNode *  decompose(const int __nx = 2,const int __ny = 2,const int __nz = 2);

  /// @name 6-connectivity at a scale
  //@{

  /// Return Left neighbour.
  MSVoxelNode * getLeft() const ;

  /// Return Right neighbour.
  MSVoxelNode * getRight() const ;

  /// Return Up neighbour.
  MSVoxelNode * getUp() const ;

  /// Return Down neighbour.
  MSVoxelNode * getDown() const ;

  /// Return Front neighbour.
  MSVoxelNode * getFront() const ;

  /// Return Back neighbour.
  MSVoxelNode * getBack() const ;

  /// Return nx.
  int getNx() const ;

  /// Return ny.
  int getNy() const ;
  
  /// Return nz.
  int getNz() const ;

  /// Return nx * ny * nz.
  int getNxNyNz() const ;

  /// Set nx, ny, nz.
  void setN(int _nx, int _ny, int _nz) ;
  
  /// Return the area intercepted by the voxel.
  double& getArea() { return interceptedTrianglesArea; } ;
  const double& getArea() const { return interceptedTrianglesArea; } ;

  /// Return the index in the grid
  int getGridIndex() const { return __gridIndex; } ;

  /// Return the index in the grid
  int& getGridIndex() { return __gridIndex; } ;

  ///@}



protected :

  /// Components of \e self.
  MSVoxelNode * __components;

  /// Object contains in the node
  ScenePtr __objects;
  
  /// Number of subdivision of this voxel along x,y,z axes
  // useless in 
  int nx, ny, nz;

  /// Surface of the voxel (computed by MSVoxel.top_down())
  double interceptedTrianglesArea;
  int __gridIndex;
};


/* ----------------------------------------------------------------------- */
#endif

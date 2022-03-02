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
 *       $Id: mvs_msvoxel.h 3268 2007-06-06 16:44:27Z dufourko $
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


/*! \file mvs_octree.h
    \brief Definition of Octree.
*/


#ifndef __mvs_msvoxel_h__
#define __mvs_msvoxel_h__

/* ----------------------------------------------------------------------- */
#include "plantgl/algo/grid/mvs.h"

#include "plantgl/algo/grid/voxelintersection.h"
#include "actn_voxelinclusion.h"
#include "beam_grid.h"
#include "vxl_msvoxelnode.h"
#include "tool/timer.h"
#include "tool/util_hashmap.h"
#include <queue>
#include <map>
#include <utility>

// For regression: copied from yann's code
#include "mvs_regression.h"


/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

class TriangleSet;
typedef RCPtr<TriangleSet> TriangleSetPtr;
class Index3Array;
typedef RCPtr<Index3Array> Index3ArrayPtr;
class Ray;
/* ----------------------------------------------------------------------- */

/**
    \class MSVoxel
    \brief A multiscale space partionning based on regular subdivision.
*/

/* ----------------------------------------------------------------------- */

struct BuilderStatByScale
{
private:
  std::vector<real_t> _elapsedTime;
  std::vector<int> _nbTriangles;
  std::vector<double> _averageArea;
  std::vector<double> _varianceArea;
  std::vector<int> _interceptedVoxels;

public:
  BuilderStatByScale() {};
  BuilderStatByScale(int size):
	_elapsedTime(size,0.0),
	_nbTriangles(size,0),
	_averageArea(size,0.0),
	_varianceArea(size,0.0),
	_interceptedVoxels(size,0)
  {
    // resize(size);
  };

	const std::vector<real_t>& elapsedTime() const
	{ return _elapsedTime; }

	const std::vector<int>& nbTriangles() const
	{ return _nbTriangles; }

	const std::vector<double>& averageArea() const
	{ return _averageArea; }

	const std::vector<double>& varianceArea() const
	{ return _varianceArea; }

	const std::vector<int>& interceptedVoxels() const
	{ return _interceptedVoxels; }

	int nbTriangles(int i) const
	{ assert(i < _nbTriangles.size());
	  return _nbTriangles[i]; }

	int& nbTriangles(int i)
	{ assert(i < _nbTriangles.size());
	  return _nbTriangles[i]; }

	int interceptedVoxels(int i) const
	{ assert(i < _interceptedVoxels.size());
	  return _interceptedVoxels[i]; }

	int& interceptedVoxels(int i)
	{ assert(i < _interceptedVoxels.size());
	  return _interceptedVoxels[i]; }

	double averageArea(int i) const
	{ assert(i < _averageArea.size());
	  return _averageArea[i]; }

	double& averageArea(int i)
	{ assert(i < _averageArea.size());
	  return _averageArea[i]; }

	double varianceArea(int i) const
	{ assert(i < _varianceArea.size());
	  return _varianceArea[i]; }

	double& varianceArea(int i)
	{ assert(i < _varianceArea.size());
	  return _varianceArea[i]; }

	real_t elapsedTime(int i) const
	{ assert(i < _elapsedTime.size());
	  return _elapsedTime[i]; }

	real_t& elapsedTime(int i)
	{ assert(i < _elapsedTime.size());
	  return _elapsedTime[i]; }


/*  void resize(int size){
    elapsedTime.resize(size);
    nbTriangles.resize(size);
    averageArea.resize(size);
    varianceArea.resize(size);
    interceptedVoxels.resize(size);

    for( int i = 0 ; i < size ; i++){
      elapsedTime[i] = 0;
      nbTriangles[i] = 0;
      averageArea[i] = 0;
      varianceArea[i] = 0;
      interceptedVoxels[i] = 0;
    }
  };*/

};

struct xyzVoxel
{
  int *x, *y,*z;
  int topScale;
  int scale;
  xyzVoxel(int _t)
  {
     topScale = _t ; // Static ?
     scale = 0 ;
     x = new int[topScale];
     y = new int[topScale];
     z = new int[topScale];

     for(int s = 0 ; s < topScale ; s++)
     {
        x[s] = 0 ;
        y[s] = 0 ;
        z[s] = 0 ;
     }
  };

  ~xyzVoxel()
  {

    delete [] x;
    delete [] y;
    delete [] z;

  };

  bool update(int _scale, int _x, int _y, int _z)
  {
     if(topScale > _scale)
     {
        scale    = _scale ;
        x[scale] = _x     ;
        y[scale] = _y     ;
        z[scale] = _z     ;
        return 1;
     }
     else
     {
        return 0;
     }
  };

};


// Both classes Octree and MSVoxel inherit from MVS

class GEOM_API MSVoxel : public Mvs
{

public:

  /// Default constructor. Use Bouding Box of \e Scene for center and Size of the space.
  // If the nb of elements of splitting list is lesser than maxscale the last element
  // is duplicated.
  MSVoxel( const ScenePtr& Scene,
           std::vector<int> splittingList,
           uint32_t maxscale = 4,
           uint32_t maxelements = 0 );

  /// Constructor. Use center and Size to define a subpart of the scene as the decomposed space.
  MSVoxel( const ScenePtr& Scene,
           std::vector<int> splittingList,
           TOOLS(Vector3) Center, TOOLS(Vector3) Size,
           uint32_t maxscale = 4,
          uint32_t maxelements = 0);

  /// Constructor.
  /// In using this ctor, triangles are stored instead of shapes in MSVoxel.
  /// When nbelt > maxelt,
//  MSVoxel( const ScenePtr& Scene,
//          uint32_t maxscale = 10, uint32_t maxelts= 10);

  /// Destructor
  virtual ~MSVoxel( );

  ///  Get the scene from \e self.
  virtual const ScenePtr& getScene() const;

  ///  Get the size from \e self.
  virtual const TOOLS(Vector3)& getSize() const{
    return __size;
  }
  ///  Root node of the multiscale structure \e self.
  virtual const MSVoxelNode& getNode() const{
    return __node;
  }
  ///  Get the center from \e self.
  virtual const TOOLS(Vector3)& getCenter() const{
    return __center;
  }


  ///  Return the maximum scale from \e self.
  virtual const uint32_t& getDepth() const{
    return __maxscale;
  }

  virtual const std::vector<int>& getSplittingList() const{
    return __splittingList;
  }

  ///  Set the scene \e scene to \e self.
  virtual bool setScene( const ScenePtr&  scene);

  ///  Add the scene \e scene to \e self.
  virtual bool addScene( const ScenePtr&  scene);

  /// Returns whether \e self is valid.
  virtual bool isValid( ) const;

  /// Return a representation of the MSVoxel.
  ScenePtr getRepresentation() const;

  /// Return the volume of the MSVoxel at a scale
  std::vector<real_t> getVolume(int scale = -1) const;

  /*! Return the details of the MSVoxel.
    on a vector of set of real_t values.
    the set contains the scale, the nb of entity filled, undetermined, empty. (a tab of 4 uint32_t)
  */
  std::vector<std::vector<uint32_t> > getDetails() const;

  /// Return the size of the entity at the different scale.
  std::vector<TOOLS(Vector3) > getSizes() const;



  bool intersect( const Ray& ray, TOOLS(Vector3)& intersection ) const;

  bool contains(const TOOLS(Vector3)& v) const;
  const std::vector<double>& getVarianceArea() ;
  const std::vector<int>& getInterceptedVoxels() const;
  std::vector<int> getContraction( int scale = -1);
  std::vector<real_t> getVolumeUnits( int scale = -1);

  std::vector<real_t> getLacunarity(int type=0) ;

  double getMaxMassDimension();
  double getMinMassDimension();
  double getAverageMassDimension();
  double getVarianceMassDimension();

  double getMaxYIntercept();
  double getMinYIntercept();
  double getAverageYIntercept();
  double getVarianceYIntercept();

  double getMaxR2();
  double getMinR2();
  double getAverageR2();
  double getVarianceR2();

  std::vector<std::map<const int, long> > getNmassr(const std::vector<int>& radius, bool all = 1);
  std::vector<std::map<const int, double> > getQSr(const std::vector<int>& radius, bool all = 1);

	// sic : by copy todo
  const BuilderStatByScale& getBuilderStatByScale() const{
          return builderStatByScale;
  }

  uint32_t buildGridIndex();

  uint32_t getNbFilledNodes( ) 
	{
	return __filledNodes.size();
	}

  uint32_t getNbFilledNodes( uint32_t scale ) 
	{
      int count = 0;
      for (int k=0; k<getNbFilledNodes(); k++)
         if (nodeScale(k) < scale) continue;
         else if (nodeScale(k) == scale) count++;
         else break;

	    return count;
	}

  const MSVoxelNode* getFilledNodes(uint32_t k) 
	{
	return __filledNodes[k];
	}

  const MSVoxelNode* getFilledNodes(int scale, uint32_t k2) 
	{

      int mink = __minmaxkAtScale[scale].first;      
      int maxk = __minmaxkAtScale[scale].second;

      int k = mink + k2; // passage du k relatif à cette échelle au k absolu

      if (k > maxk) return NULL;
  	  else return __filledNodes[k];

	}
  const int getFilledNodeScale(uint32_t k) 
	{
    uint32_t s;
    int kmin;
    for(s=0;s<__maxscale;s++) {
      kmin = __minmaxkAtScale[s].first;
      if (kmin > s) break;
    }
	  return s;
	}

  int nodeScale(uint32_t k) const 
  {return __nodeScale[k];}

  int getFilledNodesX(uint32_t k) 
	{	return __jx[k];	}
  int getFilledNodesY(uint32_t k) 
	{	return __jy[k];	}
  int getFilledNodesZ(uint32_t k) 
	{	return __jz[k];	}

  /// return the MSVoxelNode at the grid index (x,y,z) at the scale scale.
  const MSVoxelNode* getNode(int scale, uint16_t x, uint16_t y, uint16_t z) const;

protected:


  bool interiorTest(MSVoxelNode* node, VoxelInclusion &inclusion);

  void build2();

  uint32_t getNX(int scale) const;
  uint32_t getNY(int scale) const;
  uint32_t getNZ(int scale) const;
  uint32_t getNbPasOnNX(int scale = 0, int topScale = -1 ) const;
  uint32_t getNbPasOnNY(int scale = 0, int topScale = -1 ) const;
  uint32_t getNbPasOnNZ(int scale = 0, int topScale = -1 ) const;
  
  MSVoxelNode* getComponent(int x,int y,int z, int X, int Y, int Z) ;
  long getComponentValue(int x,int y,int z, int X, int Y, int Z) ;
  long getNmassRl(const int x, const int y, const int z, const int X, const int Y, const int Z, const int radius, const int radiusItPlus1);
  void setNmassRl(std::vector<std::map<const int, long> >& Nm, const int x, const int y, const int z, const int X, const int Y, const int Z, const std::vector<int>& radius);
//  void getZ1Z2(std::vector<double>& Z1, std::vector<double>& Z2, const std::vector<int>& radius, bool all);

  int getZ1Z2(std::vector<double> *Z1, std::vector<double> *Z2, MSVoxelNode *node, xyzVoxel* xyzVox1, int depth=0);
  void updateMass(int* mass, MSVoxelNode *node, xyzVoxel* xyzVox1, xyzVoxel* xyzVox2);
  int getDistance(const xyzVoxel* xyzVox1, const xyzVoxel* xyzVox2);
  int getDistanceToBorder(const xyzVoxel* xyzVox1);

  void computeLacunarity() ;
  int computeMassDimensions( MSVoxelNode* node, xyzVoxel* xyzVox1, const int &size, int depth = 0) ;
  int computeVarianceMassDimensions( MSVoxelNode* node, xyzVoxel* xyzVox1, const int &size, int depth = 0) ;
  void computeMD() ;
//  bool interiorTest(MSVoxelNode* node, VoxelInclusion &inclusion);

  /// The recursive structure.
  MSVoxelNode __node;

  /// Scene contained in the MSVoxel.
  ScenePtr __scene;

  // it is possible to redefine the bounding box of the scene
  // for example to focus on a subpart of the entire scene

  /// Size of the scene using an arbitrary unit (ex: 300, 400, 512.4 in cms)
  TOOLS(Vector3) __size;

  /// Center of the scene = center of the bounding boxe of the scene
  TOOLS(Vector3) __center;

  /// Maximum scale of the MSVoxel starting from scale 0
  uint32_t __maxscale;

  /// Maximum number of elements store by each node.
  // No longer used
  uint32_t __maxelts;

  /// number of node  of the MSVoxel.
  // No longer used ?
  uint32_t __nbnode;

  /// array of subdivisions at each scale (should be less than __maxscale):
  // for example if __maxscale = 7 and __splittingList = [2,6,4]
  // then the subdivision of each complex at each scale will be:
  // [[1,1,1],[2,2,2],[6,6,6],[4,4,4],[4,4,4],[4,4,4],[4,4,4],[4,4,4]]
  // Note that because of the coding strategy of voxels defined
  // in class "MVS" it is not yet possible to define splitting numbers
  // greater or equal to 6 (6^3 < 256 = code stored on 1 character)
  std::vector<int> __splittingList;

  //bool interiorTest();

  // array of 3 real_ts L[0] = Lacunarite -, L[1] = Lacunarite +,L[2] = Lacunarite totale
  std::vector<real_t> *L;

  // For each voxel at __maxscale, the local dimension of this voxel
  // (slope="a" value of the regression) is computed
  // and the min, max, mean, var values of this computation over all the voxels
  // at this max scale are stored respectively in the array massDimension
  // (array of 4 doubles)
  double *massDimension;
  double *MD_yIntercept; // same thing for the "b" value of the regression (intercept)
  double *MD_r2;         // same thing for the "r2" value of the regression

  // During building of a MSVoxel, this structure is used to compute and store
  // statistical information on the MSVoxel (nb of triangle per scale, ellapse time
  // per scale, etc.
  BuilderStatByScale builderStatByScale;
  
  std::vector<MSVoxelNode*> __filledNodes;
  std::vector<int> __nodeScale;
  std::vector< std::pair<int,int> > __minmaxkAtScale;
  std::vector<int> __jx;
  std::vector<int> __jy;
  std::vector<int> __jz;

private:
  Index3ArrayPtr intersect( const TriangleSetPtr& mesh,
                            const MSVoxelNode* voxel ) const;

  /// get the deepest node where point is suituated
  const MSVoxelNode* getLeafNode( const TOOLS(Vector3)& point,
                                 const TOOLS(Vector3)& dir,
                                 const MSVoxelNode* iComplex ) const;

  bool topDown( MSVoxelNode* voxel,
                const TriangleSetPtr& mesh,
                Index3ArrayPtr triangles[]
              );

  template <class T> static T power( const T& a, uint16_t b )
    {
    T r= a;
    for( uint16_t i= 0; i < b-1; i++ )
      r*= a;
    return r;
    }
}; // class MSVoxel


template<class condition>
        ScenePtr getCondRepresentation(const MSVoxel& o, condition a) {
    ScenePtr _scene(new Scene());
        std::queue<const MSVoxelNode *> _myQueue;
    const MSVoxelNode * node = &o.getNode();
    _myQueue.push(node);
    while(!_myQueue.empty()){
      node = _myQueue.front();
      if(node->isDecomposed()){
        for(uint16_t i = 0 ; i <  node->getNxNyNz() ; i++)
          _myQueue.push(node->getComponent(i));
      }
      if(a(node))
                  if(node->getType() != Tile::Empty)
                        _scene->add(node->representation());
      _myQueue.pop();
        }
    return _scene;
  }


/// MSVoxel Pointer
typedef RCPtr<MSVoxel> MSVoxelPtr;

/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
// __mvs_MSVoxel_h__
#endif

//#define CPL_DEBUG
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
 *       $Id: mvs_msvoxel.cpp 3854 2007-10-16 14:10:26Z boudon $
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

#include <limits.h>

#include "mvs_msvoxel.h"
#include "plantgl/algo/grid/tile.h"
#include "plantgl/algo/raycasting/ray.h"
#include "plantgl/algo/raycasting/rayintersection.h"

#include "plantgl/pgl_geometry.h"
#include "plantgl/pgl_algo.h"
#include "plantgl/scenegraph/appearance/material.h"
#include "plantgl/scenegraph/scene/shape.h"

#include "tool/timer.h"
#include "tool/util_math.h"


PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

#define NX 3
#define NY 3
#define NZ 3
//#define DO_INTERIOR_TEST

using namespace std;
STDEXT_USING_NAMESPACE

MSVoxel::MSVoxel(const ScenePtr&  Scene,
                 vector<int> splittingList,
                 uint32_t maxscale,
                 uint32_t maxelements ) :
    __size(0,0,0),
    __center(0,0,0),
    __scene(Scene),
    __maxscale(maxscale),
    __maxelts(maxelements),
    __nbnode(0),
	__filledNodes(), __jx(), __jy(), __jz()
{
        __splittingList = splittingList;
        __node = MSVoxelNode(0,0,Tile::Undetermined,getNX(0),getNY(0),getNZ(0));
    build2();

    L = NULL;
    massDimension = MD_yIntercept = MD_r2 = NULL;

   	// cout << "MSVoxel 1" << endl;
	  buildGridIndex(); // defines a unique index for each node in the decomposition graph

}

MSVoxel::MSVoxel(const ScenePtr&  Scene,
                                 vector<int> splittingList,
                 Vector3 Center, Vector3 Size,
                 uint32_t maxscale,
                 uint32_t maxelements) :
    __size(Size),
    __center(Center),
    __scene(Scene),
    __maxscale(maxscale),
    __maxelts(maxelements),
    __nbnode(0),
	__filledNodes(), __jx(), __jy(), __jz()
	{
        __splittingList = splittingList;
    __node = MSVoxelNode(0,0,Tile::Undetermined,getNX(0),getNY(0),getNZ(0));
    __node.getMinCoord() = Center-Size;
    __node.getMaxCoord() = Center+Size;
    build2();

    L = NULL;
    massDimension = MD_yIntercept = MD_r2 = NULL;

//     cout << "MSVoxel 2" << endl;
	 buildGridIndex(); // defines a unique index for each node in the decomposition graph

}

MSVoxel::~MSVoxel(){
    if( L ) delete [] L ;
    if( massDimension ) delete [] massDimension ;
    if( MD_yIntercept ) delete [] MD_yIntercept ;
    if( MD_r2 ) delete [] MD_r2 ;
}

const ScenePtr& MSVoxel::getScene() const{
    return __scene;
}

bool MSVoxel::setScene( const ScenePtr& scene){
  __scene = scene;
  __node = MSVoxelNode(0,0,Tile::Undetermined,getNX(0),getNY(0),getNZ(0));
  build2();
  return true;
}

bool MSVoxel::addScene( const ScenePtr& scene){
    __scene->merge(scene);
    return false;
#ifdef __GNUC__
#warning MSVoxel::addScene() not yet implemented
#endif
}

bool MSVoxel::isValid( ) const {
    return true;
}

#define URDELTA_P(a) a *= (a >= 0 ? 1.1 : 0.9 );
#define URDELTA(a) URDELTA_P(a.x())URDELTA_P(a.y())URDELTA_P(a.z())

#define LLDELTA_P(a) a *= (a >= 0 ? 0.9 : 1.1 );
#define LLDELTA(a) LLDELTA_P(a.x())LLDELTA_P(a.y())LLDELTA_P(a.z())

bool MSVoxel::interiorTest(MSVoxelNode* node, VoxelInclusion& inclusion)
{
    inclusion.setVoxel(node);
    Scene::iterator _it;
    for( _it = __scene->getBegin(); _it!=__scene->getEnd(); _it++ )
                if((*_it)->apply(inclusion)) return true;
    return false;
}

/*

  This method builds a 3D tiling based on the triangle representation of the
  scene stored in the MSVoxel

*/

/////////////////////////////////////////////////////////////////////////////
void MSVoxel::build2()
/////////////////////////////////////////////////////////////////////////////
{

  // builderStatByScale.resize(__maxscale + 1);
  builderStatByScale = BuilderStatByScale(__maxscale + 1);

  Timer t;
  uint16_t iterationMarqueur =1;
  uint32_t iterationMarqueur2 = 0;
  cout << "Building MSVoxel..." << endl;
  Tesselator discretizer;

  BBoxComputer bboxcomputer(discretizer);
  VoxelIntersection intersection(bboxcomputer);
  VoxelInclusion inclusion(bboxcomputer);
  if( __size   == Vector3::ORIGIN )
  {
    if(bboxcomputer.process(__scene))
    {

      BoundingBoxPtr bb(bboxcomputer.getBoundingBox());

      //        bb->getUpperRightCorner() *= 1.1;
      //        bb->getLowerLeftCorner() *= 1.1;
      // URDELTA(bb->getUpperRightCorner());
      // LLDELTA(bb->getLowerLeftCorner());
      __node.setBBox(bb);
      __center = bb->getCenter();
      __size = bb->getSize();
      cout << "Center :" << __center << ", Size :" << __size << endl;

    }
  }

  __scene->applyGeometryOnly(discretizer);
  MSVoxelNode * node = NULL;
  MSVoxelNode * Complex = NULL;

  queue<MSVoxelNode *> _myQueue;

  _myQueue.push(&__node);
  __node.setGeometry(__scene);


  uint16_t i;
  uint32_t max_count2= 0;
  uint32_t total_triangles= 0;
  while(!_myQueue.empty()){
    t.start();

    Complex = _myQueue.front();
    if(iterationMarqueur == Complex->getScale())
    {
      cout<<"\n iteration "<<int(iterationMarqueur)<< " |  triangles traites: "<<builderStatByScale.nbTriangles(iterationMarqueur-1)<<" en "<<builderStatByScale.elapsedTime(iterationMarqueur-1)<<" de secondes"<<endl;
      iterationMarqueur++;
      iterationMarqueur2 = 0 ;
    }
    else
    {
      if((builderStatByScale.nbTriangles(Complex->getScale())/30000) > iterationMarqueur2)
      {
        iterationMarqueur2 += 1 ;
        cout<<"\r \t triangles traites: "<<builderStatByScale.nbTriangles(iterationMarqueur-1)
                                       <<" en "<<builderStatByScale.elapsedTime(iterationMarqueur-1)
                                       <<" de secondes"<<flush;
      }
    }
    int size = Complex->getNxNyNz();
    max_count2 += size;

    if( Complex->getType() == Tile::Undetermined &&
      Complex->getScale() < __maxscale )
    {
      if( Complex->decompose( getNX(Complex->getScale()),
		                      getNY(Complex->getScale()),
                              getNZ(Complex->getScale())) )
      {
        //          count+=800.0;
        ScenePtr s(Complex->getGeometry());
        ScenePtr * n            = new ScenePtr[size];
        uint32_t   * nb_triangles = new uint32_t[size];

        for( i = 0 ; i <  size ; i++ )
        {
          n[i]= ScenePtr(new Scene());
          nb_triangles[i]= 0;
        }
        // on parcourt tous les triangles du noeud complex (pere)
        // on les repartit dans le fils adequat
        Scene::iterator _it;
        for( _it = s->getBegin(); _it!=s->getEnd(); _it++ )
        {
          if((*_it)->apply(discretizer))
          {

            TriangleSetPtr ts= discretizer.getTriangulation();

            Index3ArrayPtr * triangles = new Index3ArrayPtr[size];

            // Computes for each triangles stored in voxel "complex"
            // the list of component voxels intersected (at the next scale)
            // The result is stored in array "triangles" which has a size
            // corresponding to the decomposition of "complex" into sub-voxels.

            topDown(Complex, ts, triangles);

           for( i = 0 ; i <  size ; i++ )
            {
              if( ! triangles[i]->isEmpty() )
              {
                nb_triangles[i]+= triangles[i]->getSize();
                TriangleSetPtr tri(new TriangleSet( ts->getPointList(),
                  triangles[i],
				  ts->getNormalPerVertex(),
                  ts->getCCW(),
                  ts->getSolid(),
                  ts->getSkeleton()));

                n[i]->add(ShapePtr( new Shape( GeometryPtr::Cast(tri), AppearancePtr() )));

              }
            }
            delete [] triangles;
          }
        }

        for( i = 0 ; i <  size ; i++ )
        {
          node = Complex->getComponent(i);
          if( ! nb_triangles[i] )
          {
          #ifdef DO_INTERIOR_TEST
            if(interiorTest(node , inclusion))
              node->getType() = Tile::Filled;
            else
              node->getType() = Tile::Empty;
          #else
              node->getType() = Tile::Empty;
          #endif
          }
          else
          {
            node->setGeometry(n[i]);
            builderStatByScale.interceptedVoxels(node->getScale())++;
            builderStatByScale.averageArea(node->getScale()) += node->getArea();

            if( nb_triangles[i] < __maxelts )
            {
              node->getType() = Tile::Filled;
              total_triangles+= nb_triangles[i];
            }
            else
            {
              node->getType() = Tile::Undetermined;
              Vector3 ns = node->getSize()/2.;

              builderStatByScale.nbTriangles(Complex->getScale()) += nb_triangles[i];

              if( 1 ) /* node->getArea < ??? */
             {
                _myQueue.push(node);
                if( node->getScale() == __maxscale )
                  total_triangles+= nb_triangles[i];
              }
              else
                total_triangles+= nb_triangles[i];
            }
          }
        } // for 2
        //builderStatByScale.averageArea[] /= builderStatByScale.interceptedVoxels[];
        delete [] n;
        delete [] nb_triangles;
          } //if2
        }//if1

      t.stop();
      builderStatByScale.elapsedTime(Complex->getScale()) += t.elapsedTime();
      _myQueue.pop();
    }

    __nbnode = (uint32_t)max_count2;

    builderStatByScale.interceptedVoxels(0)=1;

  for(i = 0 ; i < (this->__maxscale+1) ; i++){
      builderStatByScale.averageArea(i) /= builderStatByScale.interceptedVoxels(i) ;
  }

}

ScenePtr MSVoxel::getRepresentation() const{
    ScenePtr _scene(new Scene());
    queue<const MSVoxelNode *> _myQueue;
    const MSVoxelNode * node = &__node;
    _myQueue.push(node);

    while(!_myQueue.empty()){
        node = _myQueue.front();
        if(node->isDecomposed()){
            for(unsigned int i = 0 ; i <  node->getNxNyNz() ; i++)
                _myQueue.push(node->getComponent(i));
        }
        else
          {
                if(node->getType() != Tile::Empty)
                        _scene->add(node->representation());
          }
        _myQueue.pop();
    }
    return _scene;
}

// *********************  Grid information  ********************************

uint32_t MSVoxel::getNX(int scale) const
{

  if( __splittingList.size() > scale )
    return __splittingList[scale];
  else if(__splittingList.size() != 0)
    return __splittingList[ __splittingList.size() -1 ];
  else
    return NX;
}
uint32_t MSVoxel::getNY(int scale) const
{
  if( __splittingList.size() > scale )
    return __splittingList[scale];
  else if(__splittingList.size() != 0)
    return __splittingList[ __splittingList.size() -1 ];
  else
    return NY;
}
uint32_t MSVoxel::getNZ(int scale) const
{
  if( __splittingList.size() > scale )
    return __splittingList[scale];
  else if(__splittingList.size() != 0)
    return __splittingList[ __splittingList.size() -1 ];
  else
    return NZ;

}

uint32_t MSVoxel::getNbPasOnNX(int scale, int topScale) const
{
  if(topScale == -1) topScale = __maxscale ;
    int v = 1;
    for(int i = scale ; i < topScale ; i++)
        v *= getNX(i);
    return v;
}
uint32_t MSVoxel::getNbPasOnNY(int scale, int topScale) const
{
  if(topScale == -1) topScale = __maxscale ;
    int v = 1;
    for(int i = scale ; i < topScale ; i++)
        v *= getNY(i);
    return v;
}
uint32_t MSVoxel::getNbPasOnNZ(int scale, int topScale) const
{
  if(topScale == -1) topScale = __maxscale ;
    int v = 1;
    for(int i = scale ; i < topScale ; i++)
        v *= getNZ(i);
    return v;

}


// ************************             Units             ***************

vector<int> MSVoxel::getContraction( int scale )
{
  // cerr << "scale = " << scale << endl;
  // cerr << "maxscale = " << __maxscale << endl;

  if((scale > __maxscale) || (scale < 0)) scale = __maxscale;
  vector<int> contraction;
  int v = 1;


  for(int i = 0 ; i <= scale ; i++)
  {
    // cerr << "v = " << v << endl;
    contraction.push_back(v);
    v *= getNX(i); // * getNY(i) * getNZ(i);
  }
 

  return contraction;

}

vector<real_t> MSVoxel::getVolumeUnits( int scale )
{
  if((scale > __maxscale) || (scale < 0)) scale = __maxscale;
  vector<real_t> vUnits;

  real_t vUnit = __size.x() * __size.y() * __size.z();
//  vUnits.push_back(vUnit);

  for(int i = 0 ; i <= scale ; i++)
  {
    vUnits.push_back(vUnit);
    vUnit /= (getNX(i) * getNY(i) * getNZ(i));
  }

  return vUnits;
}

// ************************ Fractal Dimension ***************

/////////////////////////////////////////////////////////////////////////////
vector<real_t> MSVoxel::getVolume(int scale) const
/////////////////////////////////////////////////////////////////////////////
{
  if((scale > __maxscale) || (scale < 0)) scale = __maxscale;
  vector<real_t> array(scale+1);

  real_t vUnits = __size.x() * __size.y() * __size.z();


  for(int i = 0 ; i <= scale ; i++)
  {
    array[i] = vUnits * builderStatByScale.interceptedVoxels(i);
    vUnits /= (getNX(i) * getNY(i) * getNZ(i));
  }

  return array;
}


const vector<int>& MSVoxel::getInterceptedVoxels() const
{
   return builderStatByScale.interceptedVoxels();
}


const vector<double>& MSVoxel::getVarianceArea()
{
  int i;
  queue<MSVoxelNode *> _myQueue;
  MSVoxelNode * node = &__node;
  _myQueue.push(node);
  while(!_myQueue.empty()){
    node = _myQueue.front();
    if(node->isDecomposed()){
      for( i = 0 ; i <  node->getNxNyNz() ; i++ )
        _myQueue.push(node->getComponent(i));
    }
    if(node->getType() != Tile::Empty){
      builderStatByScale.varianceArea(node->getScale()) +=
          pow((node->getArea() - builderStatByScale.averageArea(node->getScale())), 2);
    }
    _myQueue.pop();
  }

  return builderStatByScale.varianceArea();
}
// *********************** Lacunarity *********************

MSVoxelNode* MSVoxel::getComponent(int x,int y,int z, int X, int Y, int Z)
{
    // error if !( (x < X) && (y < Y) && (z < Z) && (x >= 0) && (y >= 0) && (z >= 0) )
      MSVoxelNode * node = &__node ;
      int i = 0;
    X /= getNX(0);
    Y /= getNY(0);
    Z /= getNZ(0);

      unsigned char num;
      int xV,yV,zV;
      while((X>=1) && node->isDecomposed())
      {
          xV = (x / X) ;
          yV = (y / Y) ;
          zV = (z / Z) ;

          num = xV + (yV + zV * getNY(i) ) * getNX(i);
          node = node->getComponent( num );

          x -= xV * X;
          y -= yV * Y;
          z -= zV * Z;

          X /= getNX(i);
          Y /= getNY(i);
          Z /= getNZ(i++);
      }
    return node;

}

long MSVoxel::getComponentValue(int x,int y,int z, int X, int Y, int Z)
{
  bool tx1, tx2, ty1, ty2, tz1, tz2 ;
  if( (tx1=(x < X)) && (ty1=(y < Y)) && (tz1=(z < Z)) )
  {
    if ( (tx2=(x >= 0)) && (ty2=(y >= 0)) && (tz2=(z >= 0)) )
    {
      return ( getComponent(x, y, z, X, Y, Z)->getType() != Tile::Empty );
    }
    else
    {
      return 0;
      // mirror : return ( getComponent((2*tx2-1) * x, (2*ty2-1) * y, (2*tz2-1) * z, X, Y, Z)->getType() != Tile::Empty );
    }
  }
    else
  {
    return 0;
    // mirror : return ( getComponent(x - tx1*(1+X-x), y - ty1*(1+Y-y), z - tz1*(1+Z-z), X, Y, Z)->getType() != Tile::Empty );
  }
}

long MSVoxel::getNmassRl(const int x, const int y, const int z, const int X, const int Y, const int Z, const int radius, const int radiusItPlus1)
{
    int Nmass=0;
    int rx,ry,rz;
    for( rz = radius+1  ; rz <= radiusItPlus1 ; rz ++)
      for( ry = radius+1 ; ry <= radiusItPlus1 ; ry ++)
          for( rx = radius+1 ; rx <= radiusItPlus1 ; rx ++)
          // 8 sommets, 8 symétries
          Nmass += getComponentValue(x + rx, y + ry, z + rz, X, Y, Z) +
                   getComponentValue(x + rx, y + ry, z - rz, X, Y, Z) +
                   getComponentValue(x + rx, y - ry, z + rz, X, Y, Z) +
                   getComponentValue(x + rx, y - ry, z - rz, X, Y, Z) +
                   getComponentValue(x - rx, y + ry, z + rz, X, Y, Z) +
                   getComponentValue(x - rx, y + ry, z - rz, X, Y, Z) +
                   getComponentValue(x - rx, y - ry, z + rz, X, Y, Z) +
                   getComponentValue(x - rx, y - ry, z - rz, X, Y, Z) ;

    for( rz = - radius  ; rz <= radius ; rz ++)
      for( ry = radius+1 ; ry <= radiusItPlus1 ; ry ++)
          for( rx = radius+1 ; rx <= radiusItPlus1 ; rx ++)
          // 12 arrêtes, 12 symétries
          Nmass += getComponentValue(x + rz, y + rx, z + ry, X, Y, Z) +
                   getComponentValue(x + rz, y + rx, z - ry, X, Y, Z) +
                   getComponentValue(x + rz, y - rx, z + ry, X, Y, Z) +
                   getComponentValue(x + rz, y - rx, z - ry, X, Y, Z) +

                   getComponentValue(x + ry, y + rz, z + rx, X, Y, Z) +
                   getComponentValue(x - ry, y + rz, z + rx, X, Y, Z) +
                   getComponentValue(x + ry, y + rz, z - rx, X, Y, Z) +
                   getComponentValue(x - ry, y + rz, z - rx, X, Y, Z) +

                   getComponentValue(x + rx, y + ry, z + rz, X, Y, Z) +
                   getComponentValue(x + rx, y - ry, z + rz, X, Y, Z) +
                   getComponentValue(x - rx, y + ry, z + rz, X, Y, Z) +
                   getComponentValue(x - rx, y - ry, z + rz, X, Y, Z) ;

    for( rz = -radius  ; rz <= radius ; rz ++)
      for( ry = -radius ; ry <= radius ; ry ++)
          for( rx = radius+1 ; rx <= radiusItPlus1 ; rx ++)
          // 6 faces, 6 symétries
          Nmass += getComponentValue(x + rx, y + ry, z + rz, X, Y, Z) +
                   getComponentValue(x - rx, y + ry, z + rz, X, Y, Z) +

                   getComponentValue(x + rz, y + rx, z + ry, X, Y, Z) +
                   getComponentValue(x + rz, y - rx, z + ry, X, Y, Z) +

                   getComponentValue(x + ry, y + rz, z + rx, X, Y, Z) +
                   getComponentValue(x + ry, y + rz, z - rx, X, Y, Z) ;
  return Nmass;
}

void MSVoxel::setNmassRl(vector<map<const int, long> >& Nm, const int x, const int y, const int z, const int X, const int Y, const int Z, const vector<int>& radius)
{

  map<const int, long>::iterator it;
  long Nmass = getComponentValue(x, y, z, X, Y, Z);

  for(int i = 0 ; i < radius.size() - 1; i++ )
  {
     Nmass += getNmassRl(x, y, z, X, Y, Z, radius[i], radius[i+1]);

     if(Nmass >= 0)
     {
         it = Nm[i].find(Nmass);
         if(it!=Nm[i].end()) (*it).second = (*it).second + 1;
         else Nm[i][Nmass] = long(1);
       }
  }
}


vector<map<const int, long> > MSVoxel::getNmassr(const vector<int>& radius, bool all) {

  Timer t;
  t.start();
  vector<map<const int, long> > Nmassr(radius.size() - 1);
  //map<const int, long>::iterator it;
  int X = getNbPasOnNX(0, __maxscale);
  int Y = getNbPasOnNY(0, __maxscale);
  int Z = getNbPasOnNZ(0, __maxscale);

  for(int z = 0 ; z < Z ; z++)
    for(int y = 0 ; y < Y ; y++)
      for(int x = 0 ; x < X ; x++)
        if ( (all) || (getComponent(x, y, z, X, Y, Z)->getType() != Tile::Empty) )
            setNmassRl(Nmassr, x, y, z, X, Y, Z, radius);
  t.stop();
  return Nmassr;
}

vector<map<const int, double> > MSVoxel::getQSr(const vector<int>& radius, bool all) {
  int i;

  vector<map<const int, long> > NmassStat = getNmassr(radius, all);
  vector<map<const int, double> > QSr(NmassStat.size());

  for( i = 0 ; i < NmassStat.size() ; i++ )
  {
    double XMax = getNbPasOnNX(0, __maxscale) - radius[i+1] + 1;
    double YMax = getNbPasOnNY(0, __maxscale) - radius[i+1] + 1;
    double ZMax = getNbPasOnNZ(0, __maxscale) - radius[i+1] + 1;

    for( map<const int, long>::iterator it = NmassStat[i].begin() ; it != NmassStat[i].end() ; it++)
      QSr[i][(*it).first] = (( (*it).second / XMax ) / YMax ) / ZMax;
  }

  return QSr;
}

vector<real_t> MSVoxel::getLacunarity(int type) {
  if(L == NULL) computeLacunarity();
  return L[type];

}

void MSVoxel::computeLacunarity() {
  int i;
  int size = max(getNbPasOnNX(), max(getNbPasOnNY(),getNbPasOnNZ()));

  if(L != NULL) delete [] L;
  vector<double> *Z1, *Z2;

    Z1 = new vector<double>[2];
    Z2 = new vector<double>[2];
    L = new vector<real_t>[3];
    for(i = 0; i < 2 ; i++) { Z1[i].resize(size); Z2[i].resize(size); L[i].resize(size);}
    L[2].resize(size);

  for( i = 0 ; i < size ; i++) { Z1[0][i] = Z2[0][i] = Z1[1][i] = Z2[1][i] = 0 ; }

  xyzVoxel xyzVox1( __maxscale + 1 );

  double Nb = getZ1Z2(Z1, Z2, &__node, &xyzVox1);

  double NbTot = getNbPasOnNX() * getNbPasOnNY() * getNbPasOnNZ();
  for( i = 0 ; i < size ; i++)
  {
    L[0][i] = real_t((Z2[0][i] * (NbTot - Nb))            / (Z1[0][i] * Z1[0][i])) ;
    L[1][i] = real_t((Z2[1][i] * (Nb) ) / (Z1[1][i] * Z1[1][i])) ;
    L[2][i] = real_t(((Z2[0][i] + Z2[1][i] ) * NbTot) / ((Z1[0][i] + Z1[1][i] ) * (Z1[0][i] + Z1[1][i] ) )) ;
  }

  delete [] Z1;
  delete [] Z2;
}
// *************************************************************************
int MSVoxel::getZ1Z2(vector<double> *Z1, vector<double> *Z2, MSVoxelNode* node, xyzVoxel* xyzVox1, int depth)
{
  unsigned int i ;

  if( xyzVox1->scale < __maxscale )
  {
      i = 0;
      int Nb = 0;
      int scale = xyzVox1->scale;
      if(node->isDecomposed())
      {
        for(int z=0 ; z<getNZ(scale) ; z++) for(int y=0 ; y<getNY(scale) ; y++) for(int x=0 ; x<getNX(scale) ; x++)
        {
           // if(depth == 0) cout<<"\r i="<<i<<flush;
           xyzVox1->update( scale+1, x, y, z );
           Nb += getZ1Z2(Z1, Z2, node->getComponent(i++), xyzVox1, depth+1);
        }
      }
      // nécessaire pour calculer L- et L !
      ///*
      else
      {
        for(int z=0 ; z<getNZ(scale) ; z++) for(int y=0 ; y<getNY(scale) ; y++) for(int x=0 ; x<getNX(scale) ; x++)
        {
           // if(depth == 0) cout<<"\r i="<<i<<flush;
           xyzVox1->update( scale+1, x, y, z );
           getZ1Z2(Z1, Z2, node, xyzVox1);
        }
      }
      //*/
      // if(depth == 0) cout<<endl;
      return Nb;
  }
  else
  {
      int isNotEmpty = (node->getType() != Tile::Empty) ;
      // if(!isNotEmpty) {return 0; } // à supprimer pour calculer L- et L !
      int *mass = new int[Z1[0].size()];
      for(i = 0 ; i < Z1[0].size() ; i++ ) mass[i] = 0 ;
      int Nmass = 0;
      xyzVoxel xyzVox2(__maxscale + 1);

      updateMass(mass, &__node, xyzVox1, &xyzVox2) ;

      for(i = 0 ; i < Z1[0].size() ; i++ )
      {
         Nmass += mass[i];
         Z1[isNotEmpty][i] += Nmass ;
         Z2[isNotEmpty][i] += Nmass * Nmass ;
      }
      delete [] mass;
      return isNotEmpty;
  }
}
double MSVoxel::getAverageYIntercept()
{
  computeMD();
  return MD_yIntercept[1];
}
double MSVoxel::getVarianceYIntercept()
{
  computeMD();
  return MD_yIntercept[3];
}
double MSVoxel::getMinYIntercept()
{
  computeMD();
  return MD_yIntercept[0];
}
double MSVoxel::getMaxYIntercept()
{
  computeMD();
  return MD_yIntercept[2];
}
double MSVoxel::getAverageR2()
{
  computeMD();
  return MD_r2[1];
}
double MSVoxel::getVarianceR2()
{
  computeMD();
  return MD_r2[3];
}
double MSVoxel::getMinR2()
{
  computeMD();
  return MD_r2[0];
}
double MSVoxel::getMaxR2()
{
  computeMD();
  return MD_r2[2];
}
double MSVoxel::getMaxMassDimension()
{
  computeMD();
  return massDimension[2];
};

double MSVoxel::getMinMassDimension()
{
  computeMD();
  return massDimension[0];
};

double MSVoxel::getAverageMassDimension()
{
  computeMD();
  return massDimension[1];
};

double MSVoxel::getVarianceMassDimension()
{
  computeMD();
  return massDimension[3];
};

void MSVoxel::computeMD()
{
  if( massDimension == NULL)
  {
    massDimension = new double[4] ;
    MD_yIntercept = new double[4] ;
    MD_r2         = new double[4] ;

    massDimension[0] = MD_yIntercept[0] = MD_r2[0] = -1 ;
    massDimension[1] = MD_yIntercept[1] = MD_r2[1] = 0. ;
    massDimension[2] = MD_yIntercept[2] = MD_r2[2] = -1 ;
    massDimension[3] = MD_yIntercept[3] = MD_r2[3] = 0. ;

    xyzVoxel xyzVox1(__maxscale + 1);
    int nbElem = computeMassDimensions( &__node, &xyzVox1, max(getNbPasOnNX(), max(getNbPasOnNY(),getNbPasOnNZ())) );
    massDimension[1] /= nbElem;
    MD_yIntercept[1] /= nbElem;
    MD_r2[1] /= nbElem;
    xyzVoxel xyzVox2(__maxscale + 1);
    computeVarianceMassDimensions( &__node, &xyzVox2, max(getNbPasOnNX(), max(getNbPasOnNY(),getNbPasOnNZ())) );
  }
}


int MSVoxel::computeMassDimensions( MSVoxelNode* node, xyzVoxel* xyzVox1, const int &size, int depth )
{
  unsigned int i ;

  if(node->isDecomposed())
  {
      i = 0;
      int scale = xyzVox1->scale;
      int nbElem = 0;
      for(int z=0 ; z<getNZ(scale) ; z++) for(int y=0 ; y<getNY(scale) ; y++) for(int x=0 ; x<getNX(scale) ; x++)
      {
         // if(depth == 0) cout<<"\r i="<<i<<flush;
         xyzVox1->update( scale+1, x, y, z );
         nbElem += computeMassDimensions( node->getComponent(i++), xyzVox1, size, depth );
      }
      // if(depth == 0) cout<<endl;
      return nbElem;
  }
  else if (node->getType() != Tile::Empty)
  {
      int **mass = new int*[2];
      mass[0] = new int[size];
      mass[1] = new int[size];
      for(i = 0 ; i < size ; i++ ) { mass[0][i] = 1 + 2 * i ; mass[1][i] = 0 ; }
      xyzVoxel xyzVox2(__maxscale + 1);

      updateMass(mass[1], &__node, xyzVox1, &xyzVox2) ;
      for(i = 1 ; i < size ; i++ ) mass[1][i] += mass[1][i-1];
      int localSize = 1 + getDistanceToBorder(xyzVox1);

      MsvRegression r(localSize, mass);
      double _a = r.getA();
      double _b = r.getB();
      double _r2 = r.getR2();

      massDimension[1] += _a;
      MD_yIntercept[1] += _b ;
      MD_r2[1] += _r2;

      if(massDimension[0] != -1)
      {
        if(massDimension[0] > _a) massDimension[0] = _a ;
        if(MD_yIntercept[0] > _b) MD_yIntercept[0] = _b ;
        if(MD_r2[0] > _r2) MD_r2[0] = _r2 ;

        if(massDimension[2] < _a) massDimension[2] = _a ;
        if(MD_yIntercept[2] < _b) MD_yIntercept[2] = _b ;
        if(MD_r2[2] < _r2) MD_r2[2] = _r2 ;
      }
      else
      {
        massDimension[0] = _a ;
        MD_yIntercept[0] = _b ;
        MD_r2[0] = _r2 ;

        massDimension[2] = _a ;
        MD_yIntercept[2] = _b ;
        MD_r2[2] = _r2 ;
      }

      delete []mass[0];
      delete []mass[1];
      delete []mass;
      return 1;
  }
  return 0;
}

int MSVoxel::computeVarianceMassDimensions( MSVoxelNode* node, xyzVoxel* xyzVox1, const int &size, int depth )
{
  unsigned int i ;

  if(node->isDecomposed())
  {
      i = 0;
      int scale = xyzVox1->scale;
      int nbElem = 0;
      for(int z=0 ; z<getNZ(scale) ; z++) for(int y=0 ; y<getNY(scale) ; y++) for(int x=0 ; x<getNX(scale) ; x++)
      {
         xyzVox1->update( scale+1, x, y, z );
         nbElem += computeVarianceMassDimensions( node->getComponent(i++), xyzVox1, size, depth );
      }
      // if(depth == 0) cout<<endl;
      return nbElem;
  }
  else if (node->getType() != Tile::Empty)
  {
      int **mass = new int*[2];
      mass[0] = new int[size];
      mass[1] = new int[size];
      for(i = 0 ; i < size ; i++ ) { mass[0][i] = 1 + 2 * i ; mass[1][i] = 0 ; }
      xyzVoxel xyzVox2(__maxscale + 1);

      updateMass(mass[1], &__node, xyzVox1, &xyzVox2) ;
      for(i = 1 ; i < size ; i++ ) mass[1][i] += mass[1][i-1];
      int localSize = 1 + getDistanceToBorder(xyzVox1);

      MsvRegression r(localSize, mass);
      double _a = r.getA();
      double _b = r.getB();
      double _r2 = r.getR2();

      massDimension[3] += pow( _a - massDimension[1], 2 ) ;
      MD_yIntercept[3] += pow( _b - MD_yIntercept[1], 2 ) ;
      MD_r2[3]         += pow( _r2 - MD_r2[1], 2 ) ;

      delete []mass[0];
      delete []mass[1];
      delete []mass;
      return 1;
  }
  return 0;
}


void MSVoxel::updateMass(int* mass, MSVoxelNode* node, xyzVoxel* xyzVox1, xyzVoxel* xyzVox2)
{
  if(node->isDecomposed())
  {
    uint32_t i = 0;
    uint32_t scale = xyzVox2->scale;
    for(uint32_t z = 0 ; z < getNZ(scale) ; z++)
      for(uint32_t y = 0 ; y < getNY(scale) ; y++)
        for(uint32_t x = 0 ; x < getNX(scale) ; x++)
        {
           xyzVox2->update( scale+1, x, y, z ) ;
           updateMass(mass, node->getComponent(i++), xyzVox1, xyzVox2);
        }
  }
  else if(node->getType() != Tile::Empty)
  {
     mass[getDistance(xyzVox1, xyzVox2)]++;
  }
}

int MSVoxel::getDistance(const xyzVoxel* xyzVox1, const xyzVoxel* xyzVox2)
{
  uint32_t s;
  int tailleX = getNbPasOnNX() ; int tailleY = getNbPasOnNY() ; int tailleZ = getNbPasOnNZ() ;
  int deltaX = 0 ; int deltaY = 0 ; int deltaZ = 0 ;
  for ( s = 0 ; s <= __maxscale ; s++ )
  {
     deltaX += tailleX * ( xyzVox1->x[s] - xyzVox2->x[s] ) ;
     deltaY += tailleY * ( xyzVox1->y[s] - xyzVox2->y[s] ) ;
     deltaZ += tailleZ * ( xyzVox1->z[s] - xyzVox2->z[s] ) ;
     tailleX /= getNX(s); tailleY /= getNY(s); tailleZ /= getNZ(s);
  }

  return ( max( max(abs(deltaX), abs(deltaY)), abs(deltaZ)) );
}

int MSVoxel::getDistanceToBorder(const xyzVoxel* xyzVox1)
{
  uint32_t s;
  int tailleX = getNbPasOnNX()/getNX(0) ; int tailleY = getNbPasOnNY()/getNY(0) ; int tailleZ = getNbPasOnNZ()/getNZ(0) ;
  int deltaX1 = 0 ; int deltaY1 = 0 ; int deltaZ1 = 0 ; int deltaX2 = 0 ; int deltaY2 = 0 ; int deltaZ2 = 0 ;
  for ( s = 1 ; s <= __maxscale ; s++ )
  {
     deltaX1 += tailleX * ( getNX(s) - xyzVox1->x[s] - 1) ;
     deltaY1 += tailleY * ( getNY(s) - xyzVox1->y[s] - 1) ;
     deltaZ1 += tailleZ * ( getNZ(s) - xyzVox1->z[s] - 1) ;

     deltaX2 += tailleX * ( xyzVox1->x[s] ) ;
     deltaY2 += tailleY * ( xyzVox1->y[s] ) ;
     deltaZ2 += tailleZ * ( xyzVox1->z[s] ) ;

     tailleX /= getNX(s); tailleY /= getNY(s); tailleZ /= getNZ(s);
  }

  return max(
              max( max(deltaX1, deltaY1), deltaZ1),
              max( max(deltaX2, deltaY2), deltaZ2)
            );
}

// ********************** Lacunarity end *********************************


/////////////////////////////////////////////////////////////////////////////
vector<vector<uint32_t> >
MSVoxel::getDetails() const
/////////////////////////////////////////////////////////////////////////////
{
#ifdef GEOM_DEBUG
  double count = 0;
  real_t count_percent = 0;
  double nbnode = __nbnode / 100;
#endif

  vector<vector<uint32_t> > result(__maxscale+1,vector<uint32_t>(4,0));
  for(uint32_t i = 1 ; i < __maxscale+1; i++){
    result[i][0] = i;
  }
  queue<const MSVoxelNode *> _myQueue;
  const MSVoxelNode * node = &__node;
  _myQueue.push(node);
  while(!_myQueue.empty()){
    node = _myQueue.front();
    if(node->isDecomposed()){
      for(unsigned char i = 0 ; i < node->getNxNyNz() ; i++)
        _myQueue.push(node->getComponent(i));
    }
    if(node->getType() == Tile::Empty){
      result[node->getScale()][3]++;
    }
    else if(node->getType() == Tile::Undetermined){
      result[node->getScale()][2]++;
    }
    else if(node->getType() == Tile::Filled){
      result[node->getScale()][1]++;
    }
    _myQueue.pop();
#ifdef GEOM_DEBUG
    count++;
    if(count / nbnode - count_percent > 1){
      count_percent = count / nbnode;
      cerr << "\x0d" << "Already computed " << (uint32_t)count_percent << " %" << flush;
    }
#endif
  }
  return result;
}

/////////////////////////////////////////////////////////////////////////////
vector<Vector3>
MSVoxel::getSizes() const
/////////////////////////////////////////////////////////////////////////////
{

  vector<Vector3> result(__maxscale+1,__size);
  for(uint32_t i = 1 ; i < __maxscale+1; i++){
    result[i] /= pow((double)2,(double)i);
  }
  return result;
}

/////////////////////////////////////////////////////////////////////////////
Index3ArrayPtr MSVoxel::intersect( const TriangleSetPtr& mesh,
                                  const MSVoxelNode* voxel ) const
/////////////////////////////////////////////////////////////////////////////
{

  Point3ArrayPtr points(mesh->getPointList());
  Index3ArrayPtr indices(mesh->getIndexList());

  Index3ArrayPtr result( new Index3Array());
  // result->reserve(mesh->getIndexList()->getSize());

/*
  for(Point3Array::iterator _it1 = points->getBegin();
      _it1 != points->getEnd();
      _it1++)
    if(__voxel->intersect( *_it1))return true;
*/

  Index3Array::iterator _it;
  for( _it = indices->getBegin(); _it != indices->getEnd(); _it++ )
    {
    Vector3 p0= points->getAt(_it->getAt(0));
    Vector3 p1= points->getAt(_it->getAt(1));
    Vector3 p2= points->getAt(_it->getAt(2));

    if( voxel->intersect( p0 ) || voxel->intersect( p1 ) ||
        voxel->intersect( p2 ) || voxel->intersect( (p0+p1+p2)/3.) )
      result->pushBack(*_it);
    else
    if( voxel->intersect( p0, p1 ) )
      result->pushBack(*_it);
    else
    if( voxel->intersect( p1, p2 ) )
      result->pushBack(*_it);
    else
    if( voxel->intersect( p2, p0 ) )
      result->pushBack(*_it);
    else
    if( voxel->intersect( p0, p1, p2 ) )
      result->pushBack(*_it);
    }

  return result;
}

/*
void printVoxel( const Tile* voxel )
{
 if( voxel->getComplex() )
   printVoxel(voxel->getComplex());
   // cout<<int(voxel->getNum());
}
*/

/////////////////////////////////////////////////////////////////////////////
bool MSVoxel::intersect( const Ray& ray,
                        Vector3& intersection ) const
/////////////////////////////////////////////////////////////////////////////
{
  const Vector3& P= ray.getOrigin();
  const Vector3& D= ray.getDirection();

  bool x_plus= (D.x()>=0);
  bool y_plus= (D.y()>=0);
  bool z_plus= (D.z()>=0);
  /*if(fabs(D.x()) < GEOM_EPSILON)D.x() = GEOM_EPSILON;
  if(fabs(D.y()) < GEOM_EPSILON)D.y() = GEOM_EPSILON;
  if(fabs(D.z()) < GEOM_EPSILON)D.z() = GEOM_EPSILON;*/

  // on calcul le voxel dans lequel est situe le point P
  const MSVoxelNode* voxel= getLeafNode( P, D, &__node );

  // on intersecte les triangles contenus dans le voxel avec le rayon
  Discretizer discretizer;
  RayIntersection actionRay(discretizer);
  actionRay.setRay(ray);

  bool isOk= false;
  Vector3 pt(P);

#ifdef CPL_DEBUG
  int loop= 0;
#endif

  while( voxel )
    {
    if(voxel->getGeometry())
      {
      isOk= voxel->getGeometry()->applyGeometryOnly(actionRay);
      if(isOk) break;
      }

#ifdef CPL_DEBUG
  loop++;
#endif

    // quel est le noeud suivant?
    real_t x= pt.x(), y= pt.y(), z= pt.z();
    real_t Px= (x_plus) ? voxel->getMaxCoord().x() : voxel->getMinCoord().x();
    real_t Py= (y_plus) ? voxel->getMaxCoord().y() : voxel->getMinCoord().y();
    real_t Pz= (z_plus) ? voxel->getMaxCoord().z() : voxel->getMinCoord().z();

    real_t lx= (fabs(D.x()) < GEOM_EPSILON ? REAL_MAX : (Px-x)/D.x());
    real_t ly= (fabs(D.y()) < GEOM_EPSILON ? REAL_MAX : (Py-y)/D.y());
    real_t lz= (fabs(D.z()) < GEOM_EPSILON ? REAL_MAX : (Pz-z)/D.z());
    assert(lx>=0); assert(ly>=0); assert(lz>=0); // on avance !!

    real_t l= 0;
    if( lx > ly )
      if( ly > lz )
        {
        if( z_plus )
          voxel= voxel->getUp();
        else
          voxel= voxel->getDown();
        l= lz;
        }
      else
        {
        if( y_plus )
          voxel= voxel->getRight();
        else
          voxel= voxel->getLeft();
        l= ly;
        }
    else
      if( lx > lz )
        {
        if( z_plus )
          voxel= voxel->getUp();
        else
          voxel= voxel->getDown();
        l= lz;
        }
      else
        {
        if( x_plus )
          voxel= voxel->getFront();
        else
          voxel= voxel->getBack();
        l= lx;
        }

    if(!voxel)
      return false;

    pt+= D * l; // nouveau pt
    voxel= getLeafNode(pt, D, voxel);
    }
#ifdef CPL_DEBUG
  cerr<<"nb de voxels parcourus: "<<loop<<endl;
#endif

  if(isOk)
    {
    // liste des points, prendre le plus proche
    real_t dist= REAL_MAX;
    Point3ArrayPtr pts= actionRay.getIntersection();
    assert(!pts->isEmpty());
#ifdef CPL_DEBUG
    cerr<<"nb pts: "<<pts->getSize()<<endl;
#endif

    Point3Array::const_iterator it= pts->getBegin();
    for( ; it != pts->getEnd(); it++ )
      {
      real_t d_cur= normSquared(P-(*it));
#ifdef CPL_DEBUG
    cerr<<"distance "<<d_cur<<" au point d'int "<< *it <<endl;
#endif
      if( d_cur < dist )
        {
        intersection= *it;
        dist= d_cur;
        }
      }
    return true;
    }
  else
    return false;
}

/////////////////////////////////////////////////////////////////////////////
const MSVoxelNode* MSVoxel::getLeafNode( const TOOLS(Vector3)& point,
                                       const TOOLS(Vector3)& dir,
                                       const MSVoxelNode* iComplex ) const
/////////////////////////////////////////////////////////////////////////////
{
  const MSVoxelNode* node= iComplex;
  while( node->isDecomposed() )
    {
      Vector3 pointRecentre = point - node->getMinCoord();

      Vector3 pas
        ( (real_t(node->getMaxCoord().x() - node->getMinCoord().x()) / real_t(node->getNx())),
          (real_t(node->getMaxCoord().y() - node->getMinCoord().y()) / real_t(node->getNy())),
          (real_t(node->getMaxCoord().z() - node->getMinCoord().z()) / real_t(node->getNz())) );

      int cooX = (int(pointRecentre.x() / pas.x()));
      int cooY = (int(pointRecentre.y() / pas.y()));
      int cooZ = (int(pointRecentre.z() / pas.z()));

      Vector3 rest
        ( pointRecentre.x() - cooX * pas.x(),// x - 'binf du pas contenant x'
          pointRecentre.y() - cooY * pas.y(),
          pointRecentre.z() - cooZ * pas.z() );

    // x,y,z ou x,z,y ???
    if( ( rest.x() < GEOM_EPSILON ) && ( dir.x() <  0 ) ){
      cooX += -1 ;}
    else{
        if( ( rest.x() + pas.x() < -GEOM_EPSILON ) && ( dir.x() >= 0 ) )
          cooX+= 1 ;}

    if( ( rest.y() < GEOM_EPSILON ) && ( dir.y() <  0 ) ){
      cooY += -1 ;}
    else{
      if( ( rest.y() + pas.y() < -GEOM_EPSILON ) && ( dir.y() >= 0 ) )
        cooY+= 1 ;}

    if( ( rest.z() < GEOM_EPSILON ) && ( dir.z() <  0 ) ){
      cooZ += -1 ;}
    else{
      if( ( rest.z() + pas.z() < -GEOM_EPSILON ) && ( dir.z() >= 0 ) )
        cooZ+= 1 ;}

    // le point appartient toujours a la boite?
    node= node->getComponent(cooX + cooY * node->getNx() + cooZ * node->getNx() * node->getNy() );
    }
  return node;
}

bool MSVoxel::contains(const Vector3& v) const
{
  return __node.intersect(v);
}

/////////////////////////////////////////////////////////////////////////////
bool MSVoxel::topDown( MSVoxelNode* voxel,
                     const TriangleSetPtr& mesh,
                     Index3ArrayPtr triangles[]
                     )
/////////////////////////////////////////////////////////////////////////////
{
   GeomGrid grid(voxel->getNx(), voxel->getNy(), voxel->getNz());

  Vector3 center= voxel->getCenter();
  uchar_t i= 0;
  for( i= 0; i <  voxel->getNxNyNz() ; i++ )
    {
      triangles[i]= Index3ArrayPtr( new Index3Array());
    }

  Point3ArrayPtr points(mesh->getPointList());
  Index3ArrayPtr indices(mesh->getIndexList());
  // Donnees a ajouter : n[3], m[3]
  Vector3 p[3],d[3],h[3],cooVoxel[3];

  Index3Array::iterator _it;
  for( _it = indices->getBegin(); _it != indices->getEnd(); _it++ )
  {
      // Analyse des 3 points du triangle
          Vector3 pas
            ( (real_t(voxel->getMaxCoord().x() - voxel->getMinCoord().x()) / real_t(voxel->getNx())),
              (real_t(voxel->getMaxCoord().y() - voxel->getMinCoord().y()) / real_t(voxel->getNy())),
              (real_t(voxel->getMaxCoord().z() - voxel->getMinCoord().z()) / real_t(voxel->getNz())) );

      for( int i = 0 ; i < 3 ; i++)
          {
                p[i] = points->getAt(_it->getAt(i));
                d[i] = p[i] - center;
                h[i] = p[i] - p[(i+1)%3];

                // Changement de repere -> le point (i,j,k) est dans le voxel n°(floor(i),floor(j),floor(k))
                Vector3 pointRecentre = p[i] - voxel->getMinCoord();
                cooVoxel[i].setAt(0, pointRecentre.x() / pas.x()  );
                cooVoxel[i].setAt(1, pointRecentre.y() / pas.y()  );
                cooVoxel[i].setAt(2, pointRecentre.z() / pas.z()  );
          }

      Vector3 triCenter = ( cooVoxel[0] + cooVoxel[1] + cooVoxel[2] ) / 3 ;
      if( grid.IsInTheGrid(triCenter) )
            voxel->getComponent(grid.code(triCenter))->getArea() +=
                 norm ( cross ( p[1] - p[0], p[2] - p[0] ) ) / 2 ;

      list<int> lstVoxelTriangle;

      grid.intersectTriangle(lstVoxelTriangle, cooVoxel);

      for( list<int>::iterator VoxelTriangle = lstVoxelTriangle.begin() ;
           VoxelTriangle != lstVoxelTriangle.end()                      ;
           VoxelTriangle++                                              )
              triangles[*VoxelTriangle]->pushBack(*_it);

  }
  return true;
}

////////////////////////////////////////////////////////////////////////////
uint32_t MSVoxel::buildGridIndex()
/////////////////////////////////////////////////////////////////////////////
{
  int count= 0;
  int scale = 0;

  __filledNodes = std::vector<MSVoxelNode*>(); // .reserve(__nbnode);
  __jx = std::vector<int>(); // .reserve(__nbnode);
  __jy = std::vector<int>(); // .reserve(__nbnode);
  __jz = std::vector<int>(); // .reserve(__nbnode);

  __minmaxkAtScale = std::vector< std::pair<int,int> >(); // .reserve(__maxscale); // valeurs min et max de k à chaque échelle

  for (int i=0; i<__maxscale; i++) __minmaxkAtScale.push_back(pair<int,int>(INT_MAX,0));

  real_t Mx = __node.getMinCoord().x();
  real_t My = __node.getMinCoord().y();
  real_t Mz = __node.getMaxCoord().z();

  // cout << "ROOT " << count << " scale " << scale 
  //         << "(" << Mx << "," << My << "," << Mz << ") " << endl;

  std::queue<MSVoxelNode *> _myQueue;
  std::queue<int> _scaleQueue;

  MSVoxelNode * node = &__node;
  _myQueue.push(node);
  _scaleQueue.push(scale);

  while(!_myQueue.empty())
	{
    node = _myQueue.front();
    scale = _scaleQueue.front();

    if ( /* node->getScale() < scale && */ node->isDecomposed() )
    { // breadth first strategy: indexes at scale s+1 will be all
      // greater than those at scale s

      for(uint16_t i = 0 ; i <  node->getNxNyNz() ; i++) {
        _myQueue.push(node->getComponent(i));
        _scaleQueue.push(scale+1);
      }
    } 
  
    if(node->getType() != Tile::Empty)
      {
      __filledNodes.push_back(node);
      __nodeScale.push_back(scale);
      
      real_t x = node->getMinCoord().x();
      real_t y = node->getMinCoord().y();
      real_t z = node->getMaxCoord().z();

      // cout << "node " << count << " scale " << scale 
      //     << "(" << x << "," << "," << y << "," << z << ") " << flush;

      // size is the distance between center and extremities
      Vector3 vxl_size= node->getSize()*2;
      Vector3 veps= vxl_size/10.;
      real_t eps= min(veps.x(),min(veps.y(),veps.z()));

      // cout << " eps = " << eps << flush;

      real_t nx= ( x - Mx + eps) / vxl_size.x();
      real_t ny= ( y - My + eps) / vxl_size.y();
      real_t nz= ( Mz - z + eps) / vxl_size.z();

      // cout << " (" << int(nx)+1 << "," << int(ny)+1 << "," << int(nz)+1 << ") " << endl;

      __jx.push_back(int(nx)+1);      
      __jy.push_back(int(ny)+1);      
      __jz.push_back(int(nz)+1);      

      int mink = __minmaxkAtScale[scale].first;      
      int maxk = __minmaxkAtScale[scale].second;

      // Updating the table defining k min and max at each scale
      if (count < mink) __minmaxkAtScale[scale].first=count;
      if (count > maxk) __minmaxkAtScale[scale].second=count;

      // donner count à MSVoxelNode todo
      node->getGridIndex()=count;
      count++;

    }

    _myQueue.pop();
    _scaleQueue.pop();
    }


  return __filledNodes.size();
}


const MSVoxelNode* MSVoxel::getNode(int scale, uint16_t x, uint16_t y, uint16_t z) const
{
 if( scale > getDepth() )
   return 0;

 int nx=1, ny= 1, nz= 1;
 int i= 0;
 for( i= 0; i <= scale; i++ )
   {
   nx*= getNX(i);
   ny*= getNY(i);
   nz*= getNZ(i);
   }

 if( ( x >= nx ) || ( y >= ny ) || ( z >= nz ) )
   return 0;

 const MSVoxelNode* node= &__node;
 uint16_t jx= x, jy=y, jz= z;
 int size_x= nx, size_y= ny, size_z= nz;
 for( i= 0; i <= scale; i++ )
   {
   nx= node->getNx(); ny= node->getNy(); nz= node->getNz();
   size_x/= nx; size_y/= ny; size_z/= nz;

   register uint16_t ix= jx/size_x, iy= jy/size_y, iz= jz/size_z;
   jx %= size_x; jy %= size_y; jz %= size_z;   
   if(node->isDecomposed())
     node= node->getComponent(ix + iy * nx + iz * nx * ny );
   else
     return 0;
   }
 return node;
}

/*
// ACIENNE VERSION A VIRER APRES verification dde CVS
// ==================================================
const MSVoxelNode* MSVoxel::getNode(int scale, uint16_t x, uint16_t y, uint16_t z) const
{
  if( scale > getDepth() )
    return 0;

  int nx=1, ny= 1, nz= 1;
  int i= 0;
  for( i= 0; i <= scale; i++ )
    {
    nx*= getNX(i);
    ny*= getNY(i);
    nz*= getNZ(i);
    }

  if( ( x >= nx ) || ( y >= ny ) || ( z >= nz ) )
    return 0;

  const MSVoxelNode* node= &__node;
  uint16_t jx= x, jy=y, jz= z;
  int size_x= nx, size_y= ny, size_z= nz;
  for( i= 0; i <= scale; i++ )
    {
    nx= node->getNx(); ny= node->getNy(); nz= node->getNz(); 
    size_x/= nx; size_y/= ny; size_z/= nz;

    register uint16_t ix= jx/size_x, iy= jy/size_y, iz= jz/size_z;
    jx %= size_x; jy %= size_y; jz %= size_z;    

    if(node->isDecomposed())
      node= node->getComponent(ix + iy * nx + iz * nx * ny );
    else
      return 0;
    }
  return node;
}

*/

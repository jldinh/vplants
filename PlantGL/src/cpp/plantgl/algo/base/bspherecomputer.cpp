/* -*-c++-*-
 * ----------------------------------------------------------------------------
 *
 *       PlantGL: Modeling Plant Geometry
 *
 *       Copyright 2000-2006 - Cirad/Inria/Inra - Virtual Plant Team
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr) et al.
 *
 *       Development site : https://gforge.inria.fr/projects/openalea/
 *
 * ----------------------------------------------------------------------------
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
 * ----------------------------------------------------------------------------
 */


#include <plantgl/math/util_math.h>
#include "bspherecomputer.h"

#include <plantgl/pgl_appearance.h>
#include <plantgl/pgl_geometry.h>
#include <plantgl/pgl_transformation.h>
#include <plantgl/pgl_scene.h>
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/scenegraph/container/geometryarray2.h>

#include "discretizer.h"

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

using namespace std;
/* ----------------------------------------------------------------------- */


#define GEOM_BSPHERECOMPUTER_CHECK_CACHE(geom) \
  if (!geom->unique()) { \
    Cache<BoundingSpherePtr>::Iterator _it = __cache.find(geom->getId()); \
    if (! (_it == __cache.end())) { \
       __result = _it->second; \
      return true; \
    }; \
  };


#define GEOM_BSPHERECOMPUTER_UPDATE_CACHE(geom) \
  if (!geom->unique()) \
     __cache.insert(geom->getId(),__result);


#define GEOM_BSPHERECOMPUTER_DISCRETIZE(geom) \
  GEOM_BSPHERECOMPUTER_CHECK_CACHE(geom); \
  geom->apply(__discretizer); \
  ExplicitModelPtr _explicitGeom = __discretizer.getDiscretization(); \
  GEOM_ASSERT(_explicitGeom); \
  _explicitGeom->apply(*this); \
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE(geom); \
  return true; \

#define GEOM_BSPHERECOMPUTER_EXPLICIT( geom ) \
  GEOM_ASSERT( geom ); \
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( geom ); \
  Vector3 center = geom->getPointList()->getCenter(); \
  real_t radius = 0; \
  for(Point3Array::iterator _it = geom->getPointList()->begin(); \
                _it != geom->getPointList()->end(); _it++) \
                radius = max(norm(*_it-center),radius); \
  __result = BoundingSpherePtr(new BoundingSphere(center,radius)); \
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( geom ); \
  return true; \

#define GEOM_BSPHERECOMPUTER_EXPLICIT2D( geom ) \
  GEOM_ASSERT( geom ); \
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( geom ); \
  Vector2 center = geom->getPointList()->getCenter(); \
  real_t radius = 0; \
  for(Point2Array::iterator _it = geom->getPointList()->begin(); \
                _it != geom->getPointList()->end(); _it++) \
                radius = max(norm(*_it-center),radius); \
  __result = BoundingSpherePtr(new BoundingSphere(Vector3(center,0),radius)); \
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( geom ); \
  return true; \

#define GEOM_BSPHERECOMPUTER_TRANSFORM( geom ) \
  GEOM_ASSERT( geom); \
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( geom ); \
  if(!geom->getGeometry()->apply(*this))return false; \
  GEOM_ASSERT(__result); \
  Matrix4TransformationPtr _transformation = dynamic_pointer_cast<Matrix4Transformation>(geom->getTransformation()); \
  GEOM_ASSERT(_transformation); \
  Matrix4 _matrix = _transformation->getMatrix(); \
  __result->transform(_matrix); \
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( geom ); \
  return true; \

#define GEOM_BSPHERECOMPUTER_TRANSFORMNULL( geom ) \
  GEOM_ASSERT( geom); \
  if(!geom->getGeometry()->apply(*this))return false; \
  return true; \


/* ----------------------------------------------------------------------- */


BSphereComputer::BSphereComputer(Discretizer& dis) :
  Action(),
  __result(),
  __discretizer(dis)
{
}

BSphereComputer::~BSphereComputer()
{
}

Discretizer&
BSphereComputer::getDiscretizer(){
  return __discretizer;
}

const Discretizer&
BSphereComputer::getDiscretizer() const{
  return __discretizer;
}

BoundingSpherePtr
BSphereComputer::getResult() const {
  return __result;
}

/* ----------------------------------------------------------------------- */


bool
BSphereComputer::beginProcess()
{
  return true;
}

bool
BSphereComputer::endProcess()
{
  return true;
}


/* ----------------------------------------------------------------------- */



bool
BSphereComputer::process( Inline * geominline )
{
  GEOM_ASSERT( geominline );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Shape * Shape )
{
  GEOM_ASSERT( Shape );
  if(! Shape->geometry)return false;
  return Shape->geometry->apply(*this);
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Material * material )
{
  GEOM_ASSERT( material );
  return false;
}


/* ----------------------------------------------------------------------- */

bool
BSphereComputer::process( ImageTexture * texture )
{
  GEOM_ASSERT( texture );
  return false;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Texture2D * texture )
{
  GEOM_ASSERT( texture );
  return false;
}


/* ----------------------------------------------------------------------- */

bool
BSphereComputer::process( Texture2DTransformation * texture )
{
  GEOM_ASSERT( texture );
  return false;
}


/* ----------------------------------------------------------------------- */

bool
BSphereComputer::process( MonoSpectral * monoSpectral )
{
  GEOM_ASSERT( monoSpectral );
  return false;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( MultiSpectral * multiSpectral )
{
  GEOM_ASSERT( multiSpectral );
  return false;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( AmapSymbol * amapSymbol )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT( amapSymbol )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( AsymmetricHull * asymmetricHull )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( asymmetricHull );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( AxisRotated * axisRotated )
{
        GEOM_BSPHERECOMPUTER_TRANSFORMNULL( axisRotated );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( BezierCurve * bezierCurve )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( bezierCurve );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( BezierPatch * bezierPatch )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( bezierPatch );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Box * box )
{
  GEOM_ASSERT( box );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( box );
  __result = BoundingSpherePtr(new BoundingSphere(Vector3::ORIGIN,norm(box->getSize())));
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( box );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Cone * cone )
{
  GEOM_ASSERT( cone );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( cone );
  Vector3 center(0,0,cone->getHeight()/3);
  real_t radius = max ( (real_t)(2 * cone->getHeight() / 3), (real_t)(sqrt(sq(cone->getHeight()/3)+sq(cone->getRadius()))));
  __result = BoundingSpherePtr(new BoundingSphere(center,radius));
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( cone  );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Cylinder * cylinder )
{
  GEOM_ASSERT( cylinder );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( cylinder );
  __result = BoundingSpherePtr(new BoundingSphere(Vector3(0,0,cylinder->getHeight()/2),norm(Vector3(cylinder->getRadius(),0,cylinder->getHeight()/2))));
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( cylinder  );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( ElevationGrid * elevationGrid )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( elevationGrid );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( EulerRotated * eulerRotated )
{
  GEOM_BSPHERECOMPUTER_TRANSFORMNULL( eulerRotated );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( ExtrudedHull * extrudedHull )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( extrudedHull );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Extrusion * extrusion )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( extrusion );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( FaceSet * faceSet )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT( faceSet )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Frustum * frustum )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( frustum );

/*  GEOM_ASSERT( frustum );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( frustum ); */
#ifdef __GNUC__
#warning to do
#endif
  /* GEOM_BSPHERECOMPUTER_UPDATE_CACHE( frustum );
  return true; */
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Group * group )
{
  GEOM_ASSERT( group );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( group );

  const GeometryArrayPtr& _group = group->getGeometryList();
  uint_t _size = _group->size();
  if(!_group->getAt(0)->apply(*this))return false;
  GEOM_ASSERT(__result);
  BoundingSphere res(*__result);

  for (uint_t _i = 1; _i < _size; _i++) {
          if(_group->getAt(_i)->apply(*this)){
                  res += *__result;
          }
  };
  __result = BoundingSpherePtr(new BoundingSphere(res));
  GEOM_ASSERT(__result);

  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( group );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( IFS * ifs )
{
        GEOM_BSPHERECOMPUTER_DISCRETIZE( ifs );
/*  GEOM_ASSERT( ifs );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( ifs ); */
#ifdef __GNUC__
#warning to do
#endif
/*  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( ifs );
  return true; */
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( NurbsCurve * nurbsCurve )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( nurbsCurve );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( NurbsPatch * nurbsPatch )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( nurbsPatch );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Oriented * oriented )
{
  GEOM_BSPHERECOMPUTER_TRANSFORMNULL( oriented );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Paraboloid * paraboloid )
{
        GEOM_BSPHERECOMPUTER_DISCRETIZE( paraboloid );
  /*GEOM_ASSERT( paraboloid );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( paraboloid );
  __result = new BoundingSphere(Vector3::ORIGIN,max(paraboloid->getRadius(),paraboloid->getHeight())); */
#ifdef __GNUC__
#warning to do
#endif
  /* GEOM_BSPHERECOMPUTER_UPDATE_CACHE( paraboloid );
  return true;*/
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( PointSet * pointSet )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT( pointSet )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Polyline * polyline )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT( polyline )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Revolution * revolution )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( revolution );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( QuadSet * quadSet )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT( quadSet )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Scaled * scaled )
{
  GEOM_BSPHERECOMPUTER_TRANSFORM( scaled );
}

/* ----------------------------------------------------------------------- */


bool BSphereComputer::process( ScreenProjected * scp) {
  GEOM_ASSERT(scp);

  return (scp->getGeometry()?scp->getGeometry()->apply(*this):false);
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Sphere * sphere )
{
  GEOM_ASSERT( sphere );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( sphere );
  __result = BoundingSpherePtr(new BoundingSphere(Vector3::ORIGIN,sphere->getRadius()));
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( sphere );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Swung * swung )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( swung );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Tapered * tapered )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( tapered );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Translated * translated )
{
  GEOM_BSPHERECOMPUTER_TRANSFORM( translated );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( TriangleSet * triangleSet )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT( triangleSet )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( BezierCurve2D * bezierCurve )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( bezierCurve );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Disc * disc )
{
  GEOM_ASSERT( disc );
  GEOM_BSPHERECOMPUTER_CHECK_CACHE( disc );
  __result = BoundingSpherePtr(new BoundingSphere(Vector3::ORIGIN,disc->getRadius()));
  GEOM_BSPHERECOMPUTER_UPDATE_CACHE( disc );
  return true;
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( NurbsCurve2D * nurbsCurve )
{
  GEOM_BSPHERECOMPUTER_DISCRETIZE( nurbsCurve );
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( PointSet2D * pointSet )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT2D( pointSet )
}


/* ----------------------------------------------------------------------- */


bool
BSphereComputer::process( Polyline2D * polyline )
{
  GEOM_BSPHERECOMPUTER_EXPLICIT2D( polyline )
}


/* ----------------------------------------------------------------------- */


bool BSphereComputer::process( Text * text ) {
  GEOM_ASSERT(text);
  __result = BoundingSpherePtr();
  return false;
}

bool BSphereComputer::process( Font * font ) {
  GEOM_ASSERT(font);
  __result = BoundingSpherePtr();
  return false;
}

/* ----------------------------------------------------------------------- */

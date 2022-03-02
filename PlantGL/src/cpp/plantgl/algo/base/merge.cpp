/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Modeling Plant Geometry
 *
 *       Copyright 2000-2006 - Cirad/Inria/Inra - Virtual Plant Team
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr) et al.
 *
 *       Development site : https://gforge.inria.fr/projects/openalea/
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

#include "merge.h"
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/scenegraph/container/indexarray.h>

PGL_USING_NAMESPACE

/////////////////////////////////////////////////////////////////////////////
Merge::Merge( Discretizer& discretizer,
              ExplicitModelPtr& model ) :
    __model(model),
    __discretizer(discretizer),
    __isoModel(false)
/////////////////////////////////////////////////////////////////////////////
{
  if( !init() )
    __model= ExplicitModelPtr();
}

void Merge::setModel(const ExplicitModelPtr& model)
{
  __model = model;
  if( !init() )
    __model= ExplicitModelPtr();
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::init()
/////////////////////////////////////////////////////////////////////////////
{
  if( !__model )
    return false;

  if( !__model->isValid() )
    return false;

  __type= getType( __model );

  if( __type == OTHER )
    return false;

  if (!__model->unique()){
	  // duplication of index List fields to avoid
	  // modification of others objects
	  if( __type == TRIANGLE_SET )
	  {
		  TriangleSetPtr m = dynamic_pointer_cast<TriangleSet>(__model);
		  Index3ArrayPtr index(new Index3Array(*(m->getIndexList())));
		  m->getIndexList()= index;
	  }
	  else
		  if( __type == QUAD_SET )
		  {
			  QuadSetPtr m = dynamic_pointer_cast<QuadSet>(__model);
			  Index4ArrayPtr index(new Index4Array(*(m->getIndexList())));
			  m->getIndexList()= index;
		  }
		  else
		  {
			  FaceSetPtr m = dynamic_pointer_cast<FaceSet>(__model);
			  IndexArrayPtr index(new IndexArray(*(m->getIndexList())));
			  m->getIndexList()= index;
		  }
  }
  return true;
}

/////////////////////////////////////////////////////////////////////////////
Merge::MODEL_TYPE Merge::getType( const ExplicitModelPtr& model )
/////////////////////////////////////////////////////////////////////////////
{
  MODEL_TYPE type= OTHER;

  PointSetPtr pointSet = dynamic_pointer_cast<PointSet>(model);
  if( pointSet )
    type= POINT_SET;
  else
    {
    PolylinePtr polyline = dynamic_pointer_cast<Polyline>(model);
    if( polyline )
      type= POLYLINE;
    else
      {
      FaceSetPtr faceset = dynamic_pointer_cast<FaceSet>(model);
      if( faceset )
        type= FACE_SET;
      else
        {
        QuadSetPtr quadset = dynamic_pointer_cast<QuadSet>(model);
        if( quadset )
          type= QUAD_SET;
        else
          {
          TriangleSetPtr triangleset = dynamic_pointer_cast<TriangleSet>(model);
          if( triangleset )
            type= TRIANGLE_SET;
          }
        }
      }
    }

  return type;
}

/////////////////////////////////////////////////////////////////////////////
void Merge::setIsoModel( uint_t nbObjects )
/////////////////////////////////////////////////////////////////////////////
{
GEOM_TRACE("setIsoModel "<<nbObjects);

  __isoModel= true;
  if( (__model ) && __type != OTHER )
    {
    Point3ArrayPtr& points= __model->getPointList();
    uint_t sizeP= points->size();
    points->reserve( sizeP * nbObjects );

    if( __type != POLYLINE && __type != POINT_SET )
      {
      uint_t sizeI= dynamic_pointer_cast<Mesh>(__model)->getIndexListSize();
      sizeI*= nbObjects;
      if( __type == TRIANGLE_SET )
        {
        TriangleSetPtr m = dynamic_pointer_cast<TriangleSet>(__model);
        m->getIndexList()->reserve(sizeI);
        }
      else
      if( __type == QUAD_SET )
        {
        QuadSetPtr m = dynamic_pointer_cast<QuadSet>(__model);
        m->getIndexList()->reserve(sizeI);
        }
      else
        {
        FaceSetPtr m = dynamic_pointer_cast<FaceSet>(__model);
        m->getIndexList()->reserve(sizeI);
        }
      }
    }
GEOM_TRACE("<--setIsoModel ");
}


/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( GeometryPtr& geom )
/////////////////////////////////////////////////////////////////////////////
{
GEOM_TRACE("apply GeometryPtr");
  if( !geom ) return false;
  if( !geom->isValid() ) return false;
  if( !geom->apply(__discretizer) ) return false;

  ExplicitModelPtr _geom = __discretizer.getDiscretization();

  return apply(_geom);
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( ExplicitModelPtr& geom )
/////////////////////////////////////////////////////////////////////////////
{
GEOM_TRACE("apply ExplicitModelPtr");
  if( !geom ) return false;
  if( !geom->isValid() ) return false;

  MODEL_TYPE t= getType( geom );
  switch( t )
    {
    case POINT_SET:
      {
      PointSetPtr pointSet = dynamic_pointer_cast<PointSet>(geom);
      GEOM_ASSERT(pointSet);
      return apply(*pointSet);
      }
    case POLYLINE:
      {
      PolylinePtr polyline = dynamic_pointer_cast<Polyline>(geom);
      GEOM_ASSERT(polyline);
      return apply(*polyline);
      }
    case FACE_SET:
      {
      FaceSetPtr faceset = dynamic_pointer_cast<FaceSet>(geom);
      GEOM_ASSERT(faceset);
      return apply(*faceset);
      }
    case QUAD_SET:
      {
      QuadSetPtr quadset = dynamic_pointer_cast<QuadSet>(geom);
      GEOM_ASSERT(quadset);
      return apply(*quadset);
      }
    case TRIANGLE_SET:
      {
      TriangleSetPtr triangleset = dynamic_pointer_cast<TriangleSet>(geom);
      GEOM_ASSERT(triangleset);
      return apply(*triangleset);
      }
    default:
      return false;
    }
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( PointSet& geom)
/////////////////////////////////////////////////////////////////////////////
{
GEOM_TRACE("apply PointSet");
  if( __type != POINT_SET )
    return false;

  Point3ArrayPtr& points= __model->getPointList();
  Point3ArrayPtr pts= geom.getPointList();

  Point3Array::iterator _it;
  for( _it= pts->end()-2; _it != pts->begin()-1; _it++ )
    if( !points->contains(*_it) )
      points->push_back(*_it);

  return true;
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( Polyline& geom )
/////////////////////////////////////////////////////////////////////////////
{
#ifdef __GNUC__
#warning: not yet implemented
#endif
GEOM_TRACE("apply Poly");
  return false;
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( QuadSet& geom )
/////////////////////////////////////////////////////////////////////////////
{
GEOM_TRACE("apply QuadSet");
if( __type != QUAD_SET ){
	FaceSet fs( geom );
	if(__type == FACE_SET) return apply(fs);
	else if(__type == TRIANGLE_SET) {
		setModel(ExplicitModelPtr(new FaceSet(*dynamic_pointer_cast<TriangleSet>(__model))));
		return apply(fs);
	}
    else return false;
}

  Point3ArrayPtr& points= __model->getPointList();
  Point3ArrayPtr pts= geom.getPointList();
  uint_t size = points->size();

  points->insert( points->end(),pts->begin(),pts->end());

  QuadSetPtr model = dynamic_pointer_cast<QuadSet>(__model);
  GEOM_ASSERT(model);

  checkNormals(geom);
  Point3ArrayPtr& normals= model->getNormalList();
  Point3ArrayPtr n= geom.getNormalList();

  if(n)normals->insert( normals->end(),n->begin(),n->end());

  Index4ArrayPtr& index= model->getIndexList();
  Index4ArrayPtr index1= geom.getIndexList();

  bool ccw= model->getCCW();
  bool ccw1= geom.getCCW();

  Index4Array::const_iterator _it;
  if( ccw == ccw1 )
    {
    for( _it= index1->begin(); _it != index1->end(); _it++ )
      {
      index->push_back( Index4( _it->getAt(0)+size,
                               _it->getAt(1)+size,
                               _it->getAt(2)+size,
                               _it->getAt(3)+size ) );
      }
    }
  else
    for( _it= index1->begin(); _it != index1->end(); _it++ )
      index->push_back( Index4( _it->getAt(3)+size,
                               _it->getAt(2)+size,
                               _it->getAt(1)+size,
                               _it->getAt(0)+size ) );

  return true;
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( TriangleSet& geom )
/////////////////////////////////////////////////////////////////////////////
{
GEOM_TRACE("apply TriangleSet");
  if( __type != TRIANGLE_SET ){
	FaceSet fs( geom );
	if(__type == FACE_SET) return apply(fs);
	else if(__type == QUAD_SET) {
		setModel(ExplicitModelPtr(new FaceSet(*dynamic_pointer_cast<QuadSet>(__model))));
		return apply(fs);
	}
    else return false;
  }

  Point3ArrayPtr& points= __model->getPointList();
  Point3ArrayPtr pts= geom.getPointList();
  uint_t size = points->size();

  points->insert( points->end(),pts->begin(),pts->end());

  TriangleSetPtr model = dynamic_pointer_cast<TriangleSet>(__model);
  GEOM_ASSERT(model);

  checkNormals(geom);
  Point3ArrayPtr& normals= model->getNormalList();
  Point3ArrayPtr n= geom.getNormalList();

  if(n)normals->insert( normals->end(),n->begin(),n->end());

  Index3ArrayPtr& index= model->getIndexList();
  Index3ArrayPtr index1= geom.getIndexList();

  bool ccw= model->getCCW();
  bool ccw1= geom.getCCW();

  Index3Array::const_iterator _it;
  if( ccw == ccw1 )
    for( _it= index1->begin(); _it != index1->end(); _it++ )
      index->push_back( Index3( _it->getAt(0)+size,
                               _it->getAt(1)+size,
                               _it->getAt(2)+size ) );
  else
    for( _it= index1->begin(); _it != index1->end(); _it++ )
      index->push_back( Index3( _it->getAt(3)+size,
                               _it->getAt(2)+size,
                               _it->getAt(1)+size ) );
  return true;
}

/////////////////////////////////////////////////////////////////////////////
bool Merge::apply( FaceSet& geom )
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_TRACE("apply FaceSet");
  if( __type != FACE_SET ){
	if(__type == QUAD_SET) {
		setModel(ExplicitModelPtr(new FaceSet(*dynamic_pointer_cast<QuadSet>(__model))));
	}
	else if(__type == TRIANGLE_SET) {
		setModel(ExplicitModelPtr(new FaceSet(*dynamic_pointer_cast<TriangleSet>(__model))));
	}
    else return false;
  }

  Point3ArrayPtr& points= __model->getPointList();
  Point3ArrayPtr pts= geom.getPointList();
  uint_t size = points->size();

  points->insert( points->end(),pts->begin(),pts->end());

  FaceSetPtr model = dynamic_pointer_cast<FaceSet>(__model);
  GEOM_ASSERT(model);

  checkNormals(geom);
  Point3ArrayPtr& normals= model->getNormalList();
  Point3ArrayPtr n= geom.getNormalList();
  if(n)normals->insert( normals->end(),n->begin(),n->end());

  IndexArrayPtr& index= model->getIndexList();
  IndexArrayPtr index1= geom.getIndexList();

  bool ccw= model->getCCW();
  bool ccw1= geom.getCCW();

  IndexArray::const_iterator _it;
  Index::const_iterator _it2;

  for( _it= index1->begin(); _it != index1->end(); _it++ )
    {
    register uint_t n= _it->size();
    Index _new(n);
    uint_t idi= ( ccw == ccw1 ) ? 0 : n-1;
    for( _it2=_it->begin();
         _it2 != _it->end();
         _it2++, ( ccw == ccw1 ) ? idi++ : idi--)
       _new.setAt(idi,*_it2+size);
    index->push_back(_new);
    }

  return true;
}

/////////////////////////////////////////////////////////////////////////////
void Merge::checkNormals(Mesh& geom)
/////////////////////////////////////////////////////////////////////////////
{
  MeshPtr model = dynamic_pointer_cast<Mesh>(__model);
  if(model->hasNormalList() && geom.hasNormalList()){
	if(model->getNormalPerVertex() != geom.getNormalPerVertex()){
		if(!model->getNormalPerVertex()){
			model->computeNormalList(true);
		}
		if(!geom.getNormalPerVertex()){
			geom.computeNormalList(true);
		}
	}
  }
  else if(model->hasNormalList()){
	geom.computeNormalList(model->getNormalPerVertex());
  }
  else if(geom.hasNormalList()){
 	  model->computeNormalList(geom.getNormalPerVertex());
  }
}

/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: The Plant Graphic Library
 *
 *       Copyright 1995-2007 UMR CIRAD/INRIA/INRA DAP 
 *
 *       File author(s): F. Boudon et al.
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


#include "ifs.h"
#include "mattransformed.h"
#include <plantgl/scenegraph/geometry/curve.h>
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/scenegraph/container/pointmatrix.h>
#include <plantgl/scenegraph/core/pgl_messages.h>
#include <plantgl/math/util_math.h>

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

/* ----------------------------------------------------------------------- */

const uchar_t IFS::DEFAULT_DEPTH(1);
#define MAX_OBJECTS 3e5

/* ----------------------------------------------------------------------- */

/////////////////////////////////////////////////////////////////////////////
IT::IT( uchar_t depth,
        const Transform4ArrayPtr& transfoList ) :
Transformation3D(),
__depth(depth),
__transfoList(transfoList),
__transfoNodes()
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(isValid());
  init();
}

IT::~IT( )
{}

const Matrix4ArrayPtr&
IT::getAllTransfo() const
{ return __transfoNodes;}


/////////////////////////////////////////////////////////////////////////////
void IT::init()
/////////////////////////////////////////////////////////////////////////////
{
  // compute all transformations with an iterative system
  uint_t n= __transfoList->size();
  uint_t size= IFS::power( n , __depth );
  __transfoNodes= Matrix4ArrayPtr( new Matrix4Array( size ));
  Matrix4Array::iterator it= __transfoNodes->begin();
  apply( __depth, it, size );
}

/////////////////////////////////////////////////////////////////////////////
void IT::apply( uchar_t depth, Matrix4Array::iterator& it, uint_t size )
/////////////////////////////////////////////////////////////////////////////
{
  if( depth < 1 )
    return;

  uint_t n= __transfoList->size();
  uint_t step= size / n;

  Matrix4 transfo= *it;
  uint_t i= 0;
  Matrix4Array::iterator it_sub= it;
  for( i= 0; i < n; i++ )
    {
    *it_sub= __transfoList->getAt(i)->getMatrix() * transfo;
    apply( depth-1, it_sub, step );
    it_sub+= step;
    }
}

/////////////////////////////////////////////////////////////////////////////
bool IT::isValid( ) const
/////////////////////////////////////////////////////////////////////////////
{
  if( (__transfoList->size() == 0) || (!__transfoList->isValid()) )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IT","TransfoList","Must be a list of valid transformations");
    return false;
    }

  if( __depth && (! finite(__depth)) )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IT","Depth","Must Be finite");
    return false;
    }

  return true;
}

/////////////////////////////////////////////////////////////////////////////
Point3ArrayPtr IT::transform( const Point3ArrayPtr& points ) const
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(points);
  uint_t n= __transfoNodes->size();

  Point3ArrayPtr _tPoints(new Point3Array(n*points->size()));

  Point3Array::iterator _ti = _tPoints->begin();

  Matrix4Array::const_iterator _mi= __transfoNodes->begin();
  Matrix4Array::const_iterator _mib= __transfoNodes->begin();
  Matrix4Array::const_iterator _mie= __transfoNodes->end();
  Point3Array::const_iterator _i = points->begin();
  Point3Array::const_iterator _ib = points->begin();
  Point3Array::const_iterator _ie = points->end();

  for( _mi= _mib; _mi != _mie; _mi++ )
    for( _i = _ib; _i != _ie; _i++ )
      *_ti++= (*_mi) * (*_i);

  return _tPoints;
}

/////////////////////////////////////////////////////////////////////////////
Point4ArrayPtr IT::transform( const Point4ArrayPtr& points ) const
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(points);
  uint_t n= __transfoNodes->size();

  Point4ArrayPtr _tPoints(new Point4Array(n*points->size()));

  Point4Array::iterator _ti = _tPoints->begin();

  Matrix4Array::const_iterator _mi= __transfoNodes->begin();
  Matrix4Array::const_iterator _mib= __transfoNodes->begin();
  Matrix4Array::const_iterator _mie= __transfoNodes->end();
  Point4Array::const_iterator _i = points->begin();
  Point4Array::const_iterator _ib = points->begin();
  Point4Array::const_iterator _ie = points->end();

  for( _mi= _mib; _mi != _mie; _mi++ )
    for( _i = _ib; _i != _ie; _i++ )
      *_ti++= (*_mi) * (*_i);

  return _tPoints;
}

/////////////////////////////////////////////////////////////////////////////
Point3MatrixPtr IT::transform( const Point3MatrixPtr& points ) const
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(points);
  uint_t n= __transfoNodes->size();

  Point3MatrixPtr _tPoints(new Point3Matrix(n*points->size()));

  Point3Matrix::iterator _ti = _tPoints->begin();

  Matrix4Array::const_iterator _mi= __transfoNodes->begin();
  Matrix4Array::const_iterator _mib= __transfoNodes->begin();
  Matrix4Array::const_iterator _mie= __transfoNodes->end();
  Point3Matrix::const_iterator _i = points->begin();
  Point3Matrix::const_iterator _ib = points->begin();
  Point3Matrix::const_iterator _ie = points->end();

  for( _mi= _mib; _mi != _mie; _mi++ )
    for( _i = _ib; _i != _ie; _i++ )
      *_ti++= (*_mi) * (*_i);

  return _tPoints;
}

/////////////////////////////////////////////////////////////////////////////
Point4MatrixPtr IT::transform( const Point4MatrixPtr& points ) const
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(points);
  uint_t n= __transfoNodes->size();

  Point4MatrixPtr _tPoints(new Point4Matrix(n*points->size()));

  Point4Matrix::iterator _ti = _tPoints->begin();

  Matrix4Array::const_iterator _mi= __transfoNodes->begin();
  Matrix4Array::const_iterator _mib= __transfoNodes->begin();
  Matrix4Array::const_iterator _mie= __transfoNodes->end();
  Point4Matrix::const_iterator _i = points->begin();
  Point4Matrix::const_iterator _ib = points->begin();
  Point4Matrix::const_iterator _ie = points->end();

  for( _mi= _mib; _mi != _mie; _mi++ )
    for( _i = _ib; _i != _ie; _i++ )
      *_ti++= (*_mi) * (*_i);

  return _tPoints;
}

/* ----------------------------------------------------------------------- */

/////////////////////////////////////////////////////////////////////////////
IFS::Builder::Builder( ) :
  Transformed::Builder(),
  Depth(0),
  TransfoList(0),
  Geometry(0)
/////////////////////////////////////////////////////////////////////////////
{
//GEOM_TRACE("Constructor IFS::Builder");
}


/////////////////////////////////////////////////////////////////////////////
IFS::Builder::~Builder( )
/////////////////////////////////////////////////////////////////////////////
{
  // nothing to do
//GEOM_TRACE("Destructor IFS::Builder");
}


/////////////////////////////////////////////////////////////////////////////
SceneObjectPtr IFS::Builder::build( ) const
/////////////////////////////////////////////////////////////////////////////
{
//GEOM_TRACE("Build IFS::Builder");

  if( isValid() )
    {
    GEOM_ASSERT(TransfoList);
    GEOM_ASSERT(Geometry);
    return SceneObjectPtr(
      new IFS( (Depth) ? (*Depth) : (DEFAULT_DEPTH),
               *TransfoList, *Geometry ));
    }

  // Returns null as self is not valid.
  return SceneObjectPtr();
}


/////////////////////////////////////////////////////////////////////////////
void IFS::Builder::destroy( )
/////////////////////////////////////////////////////////////////////////////
{
//GEOM_TRACE("destroy IFS::Builder");
  if( Depth ) delete Depth; Depth= 0;
  if( TransfoList ) delete TransfoList; TransfoList= 0;
  if( Geometry ) delete Geometry; Geometry= 0;
}

/////////////////////////////////////////////////////////////////////////////
bool IFS::Builder::isValid( ) const
/////////////////////////////////////////////////////////////////////////////
{
//GEOM_TRACE("validate IFS::Builder");
  if(! Geometry)
    {
    pglErrorEx(PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),"IFS","Geometry");
    return false;
    }
  if(! (*Geometry) )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IFS","Geometry","Must be a valid Geometry Object.");
    return false;
    }
  if(! (*Geometry)->isValid() )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IFS","Geometry","Must be a valid Geometry Object.");
    return false;
    }
  if(! TransfoList )
    {
    pglErrorEx(PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),"IFS","TransfoList");
    return false;
    }

  if( ((*TransfoList)->size() == 0) || (!(*TransfoList)->isValid()) )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IFS","TransfoList","Must be a list of valid transformations");
    return false;
    }

  if( Depth && (! finite(*Depth)) )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IFS","Depth","Must Be finite");
    return false;
    }

  if( Depth )
    {
    uint_t n= (*TransfoList)->size();
    uint_t size= IFS::power( n , *Depth );

    if( size > MAX_OBJECTS )
      {
      pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"IFS","Depth","Must be decreased");
      return false;
      }
    }

  return true;
}


/* ----------------------------------------------------------------------- */


/////////////////////////////////////////////////////////////////////////////
IFS::IFS() :
/////////////////////////////////////////////////////////////////////////////
  Transformed(),
  __depth(DEFAULT_DEPTH),
  __transfoList(),
  __geometry()
{ }

/////////////////////////////////////////////////////////////////////////////
IFS::IFS( uchar_t depth,
          const Transform4ArrayPtr& transfoList,
          const GeometryPtr& geometry ) :
/////////////////////////////////////////////////////////////////////////////
  Transformed(),
  __depth(depth),
  __transfoList(transfoList),
  __geometry(geometry)
{
  GEOM_ASSERT(isValid());
}


IFS::~IFS( )
{ }

/////////////////////////////////////////////////////////////////////////////
bool IFS::isValid( ) const
/////////////////////////////////////////////////////////////////////////////
{
  Builder _builder;
  _builder.Depth = const_cast<uchar_t *>(&__depth);
  _builder.TransfoList = const_cast<Transform4ArrayPtr *>(&__transfoList);
  _builder.Geometry = const_cast<GeometryPtr *>(&__geometry);
  return _builder.isValid();
}

/////////////////////////////////////////////////////////////////////////////
SceneObjectPtr IFS::copy(DeepCopier& copier ) const
/////////////////////////////////////////////////////////////////////////////
{
  IFS * ptr = new IFS(*this);
  copier.copy_recursive_attribute(ptr->getTransfoList());
  copier.copy_object_attribute(ptr->getGeometry());
  return SceneObjectPtr(ptr);
}

/* ----------------------------------------------------------------------- */

Transformation3DPtr
IFS::getTransformation( ) const
{
  return Transformation3DPtr(new IT(__depth, __transfoList));
}

const uchar_t
IFS::getDepth( ) const
{
  return __depth;
}

uchar_t&
IFS::getDepth( )
{
  return __depth;
}

const Transform4ArrayPtr&
IFS::getTransfoList( ) const
{
  return __transfoList;
}

Transform4ArrayPtr&
IFS::getTransfoList( )
{
  return __transfoList;
}

const GeometryPtr
IFS::getGeometry( ) const
{
  return __geometry;
}

GeometryPtr&
IFS::getGeometry( )
{
  return __geometry;
}

bool
IFS::isACurve( ) const
{
  return __geometry->isACurve();
}

bool
IFS::isASurface( ) const
{
  return __geometry->isASurface();
}

bool
IFS::isAVolume( ) const
{
  return __geometry->isAVolume();
}

bool
IFS::isExplicit( ) const
{
  return __geometry->isExplicit();
}

bool
IFS::isDepthToDefault( ) const
{
  return (__depth == DEFAULT_DEPTH);
}

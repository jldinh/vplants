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




#include "swung.h"
#include <plantgl/scenegraph/core/pgl_messages.h>
#include "curve.h"
#include "profile.h"
#include <plantgl/scenegraph/container/geometryarray2.h>
#include <plantgl/scenegraph/container/pointarray.h>

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

/* ----------------------------------------------------------------------- */

const bool Swung::DEFAULT_CCW(true);
const uint_t Swung::DEFAULT_DEGREE(ProfileInterpolation::DEFAULT_DEGREE);
const uint_t Swung::DEFAULT_STRIDE(ProfileInterpolation::DEFAULT_STRIDE);

/* ----------------------------------------------------------------------- */


/////////////////////////////////////////////////////////////////////////////
Swung::Builder::Builder( ) :
  SOR::Builder(),
  CCW(0),
  ProfileList(0),
  AngleList(0),
  Degree(0),
  Stride(0)
/////////////////////////////////////////////////////////////////////////////
{ }


/////////////////////////////////////////////////////////////////////////////
Swung::Builder::~Builder( )
/////////////////////////////////////////////////////////////////////////////
{
  // nothing to do
}


/////////////////////////////////////////////////////////////////////////////
SceneObjectPtr Swung::Builder::build( ) const
/////////////////////////////////////////////////////////////////////////////
{
  ProfileInterpolation::Builder _builder;

  _builder.ProfileList = const_cast<Curve2DArrayPtr *>(ProfileList);
  _builder.KnotList = const_cast<RealArrayPtr *>(AngleList);
  _builder.Degree= const_cast<uint_t *>(Degree);
  _builder.Stride= const_cast<uint_t *>(Stride);

  bool valid= _builder.isValid();

  if( valid )
    {
    ProfileInterpolationPtr _profiles(_builder.build( ));

    return SceneObjectPtr(
      new Swung( _profiles,
                          (Slices) ? (*Slices) : (DEFAULT_SLICES),
                          (CCW)    ? (*CCW)    : (DEFAULT_CCW),
                          (Degree) ? (*Degree) : (ProfileInterpolation::DEFAULT_DEGREE),
                          (Stride) ? (*Stride) : (ProfileInterpolation::DEFAULT_STRIDE)));
    }

  // Returns null as self is not valid.
  return SceneObjectPtr();
}


/////////////////////////////////////////////////////////////////////////////
void Swung::Builder::destroy( )
/////////////////////////////////////////////////////////////////////////////
{
  SORDestroy();
  if( CCW )
    {
    delete CCW;
    CCW= 0;
    }
  if( ProfileList )
    {
    delete ProfileList;
    ProfileList= 0;
    }
  if( AngleList )
    {
    delete AngleList;
    AngleList= 0;
    }
  if( Degree )
    {
    delete Degree;
    Degree= 0;
    }
  if( Stride )
    {
    delete Stride;
    Stride= 0;
    }
}

/////////////////////////////////////////////////////////////////////////////
bool Swung::Builder::isValid( ) const
/////////////////////////////////////////////////////////////////////////////
{
  if(! SORValid() )
    return false;

  ProfileInterpolation::Builder _builder;

  _builder.ProfileList = const_cast<Curve2DArrayPtr *>(ProfileList);
  _builder.KnotList = const_cast<RealArrayPtr *>(AngleList);

  return _builder.isValid();
}



/* ----------------------------------------------------------------------- */


/////////////////////////////////////////////////////////////////////////////
Swung::Swung() :
/////////////////////////////////////////////////////////////////////////////
  SOR(),
  __profiles(),
  __ccw(DEFAULT_CCW),
  __degree(DEFAULT_DEGREE),
  __stride(DEFAULT_STRIDE)
{ }

/////////////////////////////////////////////////////////////////////////////
Swung::Swung( const ProfileInterpolationPtr& profiles,
                                uchar_t slices,
                                bool ccw,
                                uint_t degree,
                                uint_t stride ) :
/////////////////////////////////////////////////////////////////////////////
  SOR(slices),
  __profiles(profiles),
  __ccw(ccw),
  __degree(degree),
  __stride(stride)
{ 
  GEOM_ASSERT(isValid());
}

/////////////////////////////////////////////////////////////////////////////
Swung::Swung( const Curve2DArrayPtr& profileList,
                                const RealArrayPtr& angleList,
                                uchar_t slices,
                                bool ccw,
                                uint_t degree,
                                uint_t stride ) :
/////////////////////////////////////////////////////////////////////////////
  SOR(slices),
  __profiles(),
  __ccw(ccw),
  __degree(degree),
  __stride(stride)
{
  ProfileInterpolation::Builder _builder;

  _builder.ProfileList = const_cast<Curve2DArrayPtr *>(&profileList);
  _builder.KnotList = const_cast<RealArrayPtr *>(&angleList);
  _builder.Degree= const_cast<uint_t *>(&degree);
  _builder.Stride= const_cast<uint_t *>(&stride);

  GEOM_ASSERT(_builder.isValid());
  __profiles= ProfileInterpolationPtr(_builder.build( ));

  GEOM_ASSERT(isValid());
}

Swung::~Swung( )
    { }


SceneObjectPtr Swung::copy(DeepCopier& copier) const {
  Swung * ptr = new Swung(*this);
  if(ptr->__profiles) ptr->__profiles = ptr->__profiles->deepcopy(copier);
  return SceneObjectPtr(ptr);
}


/////////////////////////////////////////////////////////////////////////////
const Curve2DArrayPtr& Swung::getProfileList( ) const
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(isValid());
  return __profiles->getProfileList();
}

/////////////////////////////////////////////////////////////////////////////
Curve2DArrayPtr& Swung::getProfileList( )
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(isValid());
  return __profiles->getProfileList();
}

/////////////////////////////////////////////////////////////////////////////
const RealArrayPtr& Swung::getAngleList( ) const
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(isValid());
  return __profiles->getKnotList();
}

/////////////////////////////////////////////////////////////////////////////
RealArrayPtr& Swung::getAngleList( )
/////////////////////////////////////////////////////////////////////////////
{
  GEOM_ASSERT(isValid());
  return __profiles->getKnotList();
}

/////////////////////////////////////////////////////////////////////////////
bool Swung::isValid( ) const
/////////////////////////////////////////////////////////////////////////////
{
  if( __profiles )
    return __profiles->isValid();
  else
    return false;
}


/* ----------------------------------------------------------------------- */

const bool Swung::getCCW( ) const
{
  return __ccw;
}

bool& Swung::getCCW( )
{
  return __ccw;
}

const ProfileInterpolationPtr& 
Swung::getProfileInterpolation( ) const
{
  return __profiles;
}

ProfileInterpolationPtr& 
Swung::getProfileInterpolation( )
{
  return __profiles;
}

const uint_t& Swung::getDegree() const
{
  return __degree;
}

uint_t& Swung::getDegree()
{
  return __degree;
}

const uint_t& Swung::getStride() const
{
  return __stride;
}

uint_t& Swung::getStride()
{
  return __stride;
}

bool Swung::isCCWToDefault( ) const
{
  return (__ccw == DEFAULT_CCW);
}

bool Swung::isDegreeToDefault( ) const
{
  return (__degree == DEFAULT_DEGREE);
}

bool Swung::isStrideToDefault( ) const
{
  return (__stride == DEFAULT_STRIDE);
}

bool Swung::isACurve( ) const
{ return false; }

bool Swung::isASurface( ) const
{ return true; }

bool Swung::isAVolume( ) const
{ return false; }

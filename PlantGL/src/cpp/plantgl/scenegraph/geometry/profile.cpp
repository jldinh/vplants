//#define DEBUG
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


#include "profile.h"
#include <plantgl/scenegraph/core/pgl_messages.h>

#include <plantgl/scenegraph/transformation/scaled.h>
#include <plantgl/scenegraph/transformation/mattransformed.h>
#include <plantgl/scenegraph/transformation/orthotransformed.h>

#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/scenegraph/container/geometryarray2.h>

#include "interpol.h"
#include "polyline.h"
#include "nurbscurve.h"

#include <plantgl/math/util_math.h>

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace std;

/* ----------------------------------------------------------------------- */

ProfileTransformation::ProfileTransformation(Point2ArrayPtr _scalingList,
                                             RealArrayPtr _orientationList,
                                             RealArrayPtr _knotList ):
    __scalingList(_scalingList),
    __orientationList(_orientationList),
    __knotList(_knotList){
}

ProfileTransformation::~ProfileTransformation(){}

/* ----------------------------------------------------------------------- */

real_t ProfileTransformation::getUMin() const {
    return (__knotList ? __knotList->getAt(0) : 0);
}

real_t ProfileTransformation::getUMax() const {
    return (__knotList ? __knotList->getAt((__knotList->size())-1) : 1 );
}

const Point2ArrayPtr& ProfileTransformation::getScale() const {
    return __scalingList;
}

const RealArrayPtr& ProfileTransformation::getOrientation() const {
    return __orientationList;
}

Point2ArrayPtr& ProfileTransformation::getScale() {
    return __scalingList;
}

RealArrayPtr& ProfileTransformation::getOrientation(){
    return __orientationList;
}

const RealArrayPtr ProfileTransformation::getKnotList() const {
    if(__knotList)return __knotList;
    else {
        uint_t _size = max(__scalingList->size(),__orientationList->size());
        if(_size<1)_size = 2;
        RealArrayPtr a(new RealArray(_size));
        a->setAt(0,0.0);
        for(uint_t _i = 1; _i < _size; _i++)
            a->setAt(_i, ((real_t)_i /(real_t)(_size - 1)));
        a->setAt(_size-1,1.0);
        return a;
    }
}

RealArrayPtr& ProfileTransformation::getKnotList(){
    return __knotList;
}

/* ----------------------------------------------------------------------- */

Transformation2DPtr ProfileTransformation::operator() (real_t u) const {
    Matrix3TransformationPtr val;
    uint_t _i = 0;
    real_t _t = 0;

    if((!__scalingList)||__scalingList->empty() ||(__scalingList==DEFAULT_SCALE_LIST));
    else if(__scalingList->size() == 1){
        val = Matrix3TransformationPtr(new Scaling2D(__scalingList->getAt(0)));
    }
    else if(__knotList){
        if(u <= __knotList->getAt(0)){
            val = Matrix3TransformationPtr(new Scaling2D(__scalingList->getAt(0)));
        }
        else if (u >= __knotList->getAt((__knotList->size())-1)){
            val = Matrix3TransformationPtr(new Scaling2D(__scalingList->getAt((__knotList->size())-1)));
        }
        else {
            for(RealArray::iterator _it = __knotList->begin();
                ((_it!=__knotList->end())&&(*_it < u )) ;
                _it++)_i++;
            if(__knotList->getAt(_i) == u)val = Matrix3TransformationPtr(new Scaling2D(__scalingList->getAt(_i)));
            else{
                _t = (__knotList->getAt(_i) - u)/(__knotList->getAt(_i) -  __knotList->getAt(_i-1)) ;
                val = Matrix3TransformationPtr(new Scaling2D((__scalingList->getAt(_i-1)*(_t)+(__scalingList->getAt(_i)*(1-_t)))));
            }
        }
    }
    else {
        if(u <= 0 ){
            val = Matrix3TransformationPtr(new Scaling2D(__scalingList->getAt(0)));
        }
        else if (u >= 1 ){
            val = Matrix3TransformationPtr(new Scaling2D(*(__scalingList->end()-1)));
        }
        else {
            real_t _interval = (real_t)(__scalingList->size() - 1);
            _i = (int)(u * _interval);
            _t = u*_interval - ((real_t)(_i));
//                      printf("u = %f - i = %i - t = %f - interval = %f \n",u,_i,_t,_interval);
            if(_t <= GEOM_EPSILON)val = Matrix3TransformationPtr(new Scaling2D(__scalingList->getAt(_i)));
            else{
                val = Matrix3TransformationPtr(new Scaling2D((__scalingList->getAt(_i)*(1-_t)+(__scalingList->getAt(_i+1)*(_t)))));
            }
        }
    }

    Matrix3TransformationPtr val2;
    if((!__orientationList) ||__orientationList->empty() ||(__orientationList==DEFAULT_ORIENTATION_LIST));
    else if(__orientationList->size() == 1){
        real_t _c = cos(__orientationList->getAt(0));
        real_t _s = sin(__orientationList->getAt(0));
        val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
    }
    else
    if(__knotList){
        if(u <= __knotList->getAt(0)){
            real_t _c = cos(__orientationList->getAt(0));
            real_t _s = sin(__orientationList->getAt(0));
            val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
        }
        else if (u >= __knotList->getAt((__knotList->size())-1)){
            real_t _c = cos(__orientationList->getAt((__knotList->size())-1));
            real_t _s = sin(__orientationList->getAt((__knotList->size())-1));
            val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
        }
        else {
            _i = 0;
            for(RealArray::iterator _it = __knotList->begin();
                ((_it!=__knotList->end())&&(*_it < u )) ;
                _it++)_i++;
            real_t _angle;
            if(__knotList->getAt(_i) == u){
                _angle = __orientationList->getAt(_i);
            }
            else{
                _t = (__knotList->getAt(_i) - u)/(__knotList->getAt(_i) -  __knotList->getAt(_i-1)) ;
                _angle = (__orientationList->getAt(_i-1)*_t)+(__orientationList->getAt(_i)*(1-_t));
            }
            real_t _c = cos(_angle);
            real_t _s = sin(_angle);
            val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
        }
    }
    else {
        if(u <= 0){
            real_t _c = cos(__orientationList->getAt(0));
            real_t _s = sin(__orientationList->getAt(0));
            val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
        }
        else if (u >= 1){
            real_t _c = cos(*(__orientationList->end()-1));
            real_t _s = sin(*(__orientationList->end()-1));
            val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
        }
        else {

            real_t _interval = (real_t)(__orientationList->size() - 1);
            _i = (int)(u / _interval);
            _t = u - (real_t)_i;
            real_t _angle;
            if(_t <= GEOM_EPSILON){
                _angle = __orientationList->getAt(_i);
            }
            else{
                _angle = (__orientationList->getAt(_i)*(1-_t))+(__orientationList->getAt(_i+1)*_t);
            }
            real_t _c = cos(_angle);
            real_t _s = sin(_angle);
            val2 = Matrix3TransformationPtr(new OrthonormalBasis2D(Matrix2(_c,_s,-_s,_c)));
        }
    }

    if (!val && !val2) return Transformation2DPtr(new Scaling2D(Vector2(1.0,1.0)));
    else if (!val){
//      cerr << "Orientation(" << u << ") : "  << val2->getMatrix() << endl;
        return Transformation2DPtr(val2);
    }
    else if (!val2){
//      cerr << "Scale(" << u << ") : "  << val->getMatrix() << endl;
        return Transformation2DPtr(val);
    }
    else{
        Matrix3 mat = val->getMatrix()*val2->getMatrix();
//      cerr << "Transf("<< u << ") : " << mat << endl;
        return Transformation2DPtr(new GeneralMatrix3Transformation(mat));
    }
}

/* ----------------------------------------------------------------------- */

const bool
ProfileTransformation::isKnotListToDefault() const{
    if(!__knotList)return true;
    uint_t _size = max((__scalingList == NULL || __scalingList->empty()?0:__scalingList->size()),
					   (__orientationList == NULL ||__orientationList->empty()?0:__orientationList->size()));
    if(__knotList->getAt(0) > GEOM_EPSILON )return false;
    for(uint_t _i = 1; _i < _size; _i++)
        if(fabs(__knotList->getAt(_i) - ((real_t)_i /(real_t)(_size - 1))) > GEOM_EPSILON ) return false;
    return true;
}

/* ----------------------------------------------------------------------- */


bool ProfileTransformation::isValid( ) const{

    if(__scalingList){
        if(!(__scalingList)->isValid()) {
            pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"Extrusion","Scale","Must be a valid Object.");
            return false;
        };
        if((__scalingList)->size() == 0 ){
            pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"Extrusion","Scale","Must have more values.");
            return false;
        }
    }
    if(__orientationList)
        if((__orientationList)->size() == 0 ){
            pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"Extrusion","Orientation","Must have more values.");
            return false;
        }

    if( (__scalingList) && (__orientationList) &&
        (__scalingList->size() !=1) &&
        (__orientationList->size() !=1) &&
        (__scalingList->size()!=__orientationList->size()) ){
        pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"Extrusion","Orientation",
                   "Must specifie Scale and Orientation with the same number of value.");
        return false;
    }

    if((__knotList) && ((__scalingList) || (__orientationList))){
        uint_t _size = 0;
        if(__scalingList) _size = __scalingList->size();
        if(__orientationList) _size = max(_size,__orientationList->size());
        if(_size > 1 && __knotList->size() != _size){
            pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"Extrusion","KnotList",
                       "Must specifie Scale or Orientation with more than one value.");
            return false;
        }
    }
    return true;
}

ProfileTransformationPtr 
ProfileTransformation::deepcopy(DeepCopier& copier) const
{
	ProfileTransformationPtr ptr = new ProfileTransformation(*this);
	copier.copy_attribute(ptr->getScale());
	copier.copy_attribute(ptr->getOrientation());
	copier.copy_attribute(ptr->getKnotList());
	return ptr;
}

/* ----------------------------------------------------------------------- */

const
Point2ArrayPtr ProfileTransformation::DEFAULT_SCALE_LIST(new Point2Array(1,Vector2(1,1)));

const
RealArrayPtr ProfileTransformation::DEFAULT_ORIENTATION_LIST(new RealArray((unsigned int)1,0));


/* ----------------------------------------------------------------------- */

const uint_t ProfileInterpolation::DEFAULT_DEGREE(3);
const uint_t ProfileInterpolation::DEFAULT_STRIDE(0);


/////////////////////////////////////////////////////////////////////////////

ProfileInterpolation::Builder::Builder() :
                               ProfileList(0),
                               KnotList(0),
                               Degree(0),
                               Stride(0)
{ }

/////////////////////////////////////////////////////////////////////////////

ProfileInterpolation::Builder::~Builder()
{ }

/////////////////////////////////////////////////////////////////////////////

ProfileInterpolationPtr ProfileInterpolation::Builder::build( ) const
{
  ProfileInterpolation* interpolant= 0;

  if( isValid() )
    {
    interpolant= new ProfileInterpolation( *ProfileList,
                                           *KnotList,
                                           (Degree ? *Degree : DEFAULT_DEGREE),
                                           (Stride ? *Stride : DEFAULT_STRIDE) );
    bool diagnosis= interpolant->interpol();
    if( !diagnosis )
      {
      delete interpolant;
      interpolant= 0;
      }
    }

  return ProfileInterpolationPtr(interpolant);
}

/////////////////////////////////////////////////////////////////////////////

void ProfileInterpolation::Builder::destroy()
{
  if( ProfileList )
    {
    delete ProfileList;
    ProfileList= 0;
    }
  if( KnotList )
    {
    delete KnotList;
    KnotList= 0;
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

bool ProfileInterpolation::Builder::isValid( ) const
{
  if( !ProfileList )
    {
    pglErrorEx( PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),
                "ProfileInterpolation",
                "ProfileList" );
    return false;
    }
  if( !(*ProfileList) )
    {
    pglErrorEx( PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),
                "ProfileInterpolation",
                "*ProfileList" );
    return false;
    }
  if( (*ProfileList)->size() == 0 )
    {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),
               "ProfileInterpolation",
               "ProfileList",
               "Must have more values.");
    return false;
    }
  if( ! (*ProfileList)->isValid() )
    {
    pglErrorEx( PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),
                "ProfileInterpolation",
                "ProfileList",
                "Must be a list of valid Geometry Objects." );
    return false;
    }


  if( !KnotList )
    {
    pglErrorEx( PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),
                "ProfileInterpolation",
                "KnotList" );
    return false;
    }
  if( !(*KnotList) )
    {
    pglErrorEx( PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),
                "ProfileInterpolation",
                "*KnotList" );
    return false;
    }

  uint_t nbKnots= (*KnotList)->size();
  uint_t nbProfiles= (*ProfileList)->size();
  if( nbKnots != nbProfiles )
    {
    pglErrorEx( PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),
                "ProfileInterpolation",
                "KnotList",
                "Must have the same number of value than ProfileList." );
    return false;
    }

 return true;
}


/* ----------------------------------------------------------------------- */

/////////////////////////////////////////////////////////////////////////////

ProfileInterpolation::ProfileInterpolation( ) :
    __profileList(),
    __knotList(),
    __stride(DEFAULT_STRIDE),
    __degree(DEFAULT_DEGREE),
    __evalPt2D(),
    __fctList2D(),
    __evalPt3D(),
    __fctList3D(),
    __is2D(true)
{
}

/////////////////////////////////////////////////////////////////////////////

ProfileInterpolation::ProfileInterpolation( Curve2DArrayPtr _profileList,
                                            RealArrayPtr    _knotList,
                                            uint_t          _degree,
                                            uint_t          _stride ) :
  __profileList(_profileList),
  __knotList(_knotList),
  __stride(_stride),
  __degree(_degree),
  __evalPt2D(),
  __fctList2D(),
  __evalPt3D(),
  __fctList3D(),
  __is2D(true)
{
  GEOM_ASSERT( isValid() );
}

ProfileInterpolation::~ProfileInterpolation( ) {}

/////////////////////////////////////////////////////////////////////////////

bool ProfileInterpolation::isValid( ) const
{
  Builder _builder;
  RealArrayPtr _knot;

  _builder.ProfileList= const_cast< Curve2DArrayPtr* >(&__profileList);

  if( !isKnotListToDefault() )
    _builder.KnotList= const_cast< RealArrayPtr* >(&__knotList);

  if( !isDegreeToDefault() )
    _builder.Degree= const_cast< uint_t* >(&__degree);

  if( !isStrideToDefault() )
    _builder.Stride= const_cast< uint_t* >(&__stride);

  return _builder.isValid();
}

/////////////////////////////////////////////////////////////////////////////

bool ProfileInterpolation::isDegreeToDefault() const
{
  return ( __degree == DEFAULT_DEGREE );
}

/////////////////////////////////////////////////////////////////////////////

bool ProfileInterpolation::isStrideToDefault() const
{
  return ( __stride == DEFAULT_STRIDE );
}

/////////////////////////////////////////////////////////////////////////////

bool ProfileInterpolation::isKnotListToDefault() const
{
  return false;
}

/////////////////////////////////////////////////////////////////////////////

real_t ProfileInterpolation::getUMin() const
{
  return ( (__knotList) ? __knotList->getAt(0) : 0);
}

/////////////////////////////////////////////////////////////////////////////

real_t ProfileInterpolation::getUMax() const
{
  return ( (__knotList) ? __knotList->getAt((__knotList->size())-1) : 1 );
}

/////////////////////////////////////////////////////////////////////////////

const Point2ArrayPtr& ProfileInterpolation::getSection2DAt(real_t u) const
{
// #ifdef DEBUG
  cout<<"-> getSectionAt "<< u << endl;
// #endif

  if( !__fctList2D )
    return __evalPt2D;

  GEOM_ASSERT( __is2D );
  GEOM_ASSERT( __evalPt2D && __fctList2D );
  GEOM_ASSERT( __evalPt2D->size() == __fctList2D->size() );

  Curve2DArray::const_iterator itBegin= __fctList2D->begin();
  Curve2DArray::const_iterator itEnd=   __fctList2D->end();
  Curve2DArray::const_iterator it= itBegin;

  Point2Array::iterator itPt= __evalPt2D->begin();

  for( it= itBegin; it < itEnd; it++, itPt++ )
    {
    Curve2DPtr nurbs= *it;
    *itPt= nurbs->getPointAt(u);
    }
#ifdef DEBUG
//cout<<"<-"<<endl;
#endif
  return __evalPt2D;
}

/////////////////////////////////////////////////////////////////////////////

const Point3ArrayPtr& ProfileInterpolation::getSection3DAt(real_t u) const
{
#ifdef DEBUG
//cout<<"-> getSectionAt "<< u <<endl;
#endif

  if( !__fctList3D )
    return __evalPt3D;

  GEOM_ASSERT( !__is2D );
  GEOM_ASSERT( __evalPt3D && __fctList3D );
  GEOM_ASSERT( __evalPt3D->size() == __fctList3D->size() );

  CurveArray::const_iterator itBegin= __fctList3D->begin();
  CurveArray::const_iterator itEnd=   __fctList3D->end();
  CurveArray::const_iterator it= itBegin;

  Point3Array::iterator itPt= __evalPt3D->begin();

  for( it= itBegin; it < itEnd; it++, itPt++ )
    {
    LineicModelPtr nurbs= *it;
    *itPt= nurbs->getPointAt(u);
    }
#ifdef DEBUG
//cout<<"<-"<<endl;
#endif
  return __evalPt3D;
}

bool ProfileInterpolation::check_interpolation() {
    return __fctList3D || __fctList2D;
}

/////////////////////////////////////////////////////////////////////////////
const Curve2DArrayPtr&
ProfileInterpolation::getProfileList( ) const
{
  return __profileList;
}

Curve2DArrayPtr&
ProfileInterpolation::getProfileList( )
{
  return __profileList;
}

const RealArrayPtr&
ProfileInterpolation::getKnotList() const
{
  return __knotList;
}

RealArrayPtr&
ProfileInterpolation::getKnotList()
{
  return __knotList;
}

const uint_t&
ProfileInterpolation::getStride( ) const
{
  return __stride;
}

uint_t&
ProfileInterpolation::getStride( )
{
  return __stride;
}

const uint_t&
ProfileInterpolation::getDegree( ) const
{
  return __degree;
}

uint_t&
ProfileInterpolation::getDegree( )
{
  return __degree;
}

const bool&
ProfileInterpolation::is2DInterpolMode() const
{
  return __is2D;
}



/////////////////////////////////////////////////////////////////////////////

bool ProfileInterpolation::interpol()
{

#ifdef DEBUG
cout<<"-> interpol"<<endl;
#endif

  uint_t n= __profileList->size();

  // uint_t i= 0;
  if( __stride <= 2 )
    {
    __stride= 0;

    Curve2DArray::const_iterator itBegin= __profileList->begin();
    Curve2DArray::const_iterator it= itBegin;
    Curve2DArray::const_iterator itEnd= __profileList->end();

    for( it= itBegin; it != itEnd; it++ )
      {
      Curve2DPtr p= *it;
      uint_t stride= p->getStride();

      if( stride > __stride )
        __stride= stride;
      }

    if( __stride < 2 ) __stride= 2;
  }

#ifdef DEBUG
   printf("Stride: %i\n",__stride);
#endif

  if( n == 1 )
    {
    __is2D= true;
    Curve2DPtr p = __profileList->getAt(0);
    Polyline2DPtr poly2D = dynamic_pointer_cast<Polyline2D>( p );

    if( is_valid_ptr(poly2D) && __stride == poly2D->getStride())
      {
         __evalPt2D= poly2D->getPointList();
      }
    else
      {
      real_t u_start= p->getFirstKnot();
      real_t u_end=   p->getLastKnot();
      real_t step= (u_end - u_start) / real_t(__stride);

      __evalPt2D= Point2ArrayPtr( new Point2Array( __stride+1 ) );

      real_t u= u_start;
      for(uint_t i= 0; i <= __stride; i++ )
        {
           Vector2 point= p->getPointAt(u);
           __evalPt2D->setAt( i, point );
           u+= step;
        }
	    
        // __evalPt2D->setAt( __stride, p->getPointAt(u_end) );
	}

    __fctList2D= Curve2DArrayPtr();
    __evalPt3D= Point3ArrayPtr();
    __fctList3D= CurveArrayPtr();

    return true;
    }

//  if( n <= 3 )
    __is2D= true;
/*  else
    __is2D= false;*/

#ifdef DEBUG
cout<<"is2D? "<<__is2D<<endl;
#endif

  Point2ArrayPtr allPts2D;
  Point3ArrayPtr allPts3D;

  if( __is2D )
    allPts2D= Point2ArrayPtr ( new Point2Array( n * (__stride+1)) );
  else
    allPts3D= Point3ArrayPtr( new Point3Array( n * (__stride+1)) );

  real_t cosa= 0., sina= 0.;
  uint_t j= 0;
  for( j= 0; j < n ; j++ )
    {
    Curve2DPtr p= __profileList->getAt(j);

    real_t u_start= p->getFirstKnot();
    real_t u_end=   p->getLastKnot();
    real_t step= (u_end - u_start) / real_t(__stride);
    real_t u= u_start;

    if( !__is2D )
      {
      real_t angle= __knotList->getAt(j);
      cosa= cos(angle);
      sina= sin(angle);
      }
    for(uint_t i= 0; i <= __stride; ++i )
      {
      Vector2 pt= p->getPointAt(u);
      GEOM_ASSERT( j+i*n < n * __stride );
      if( __is2D )
        allPts2D->setAt( j+i*n, pt );
      else
        {
        real_t r= pt.x();
        Vector3 pt3(r*cosa, r*sina, pt.y());
        allPts3D->setAt( j+i*n, pt3 );
        }
      u+= step;
      }
    }

  if(__is2D)
    {
   __fctList2D= Curve2DArrayPtr( new Curve2DArray(__stride+1) );
    Point2ArrayPtr pts;
    Point2Array::iterator itpBegin= allPts2D->begin();
    Point2Array::iterator itpEnd= itpBegin + n;
    for(uint_t i= 0; i <= __stride; i++ )
      {
      pts= Point2ArrayPtr(new Point2Array(itpBegin, itpEnd));
      Point3ArrayPtr pts3D( new Point3Array(*pts, 1.) );
      Interpol local(pts3D, __knotList, __degree, 1 );
#ifdef DEBUG
cout<<"get2DCurve "<<i<<endl;
#endif
      __fctList2D->getAt(i)= local.get2DCurve();
      if(itpEnd != allPts2D->end()){ itpBegin+= n; itpEnd+= n; }
      }
    __evalPt2D= Point2ArrayPtr( new Point2Array( __stride+1 ) );
    __evalPt3D= Point3ArrayPtr();
    __fctList3D= CurveArrayPtr();

    }
  else
  {
	  __fctList3D= CurveArrayPtr( new CurveArray(__stride+1) );
	  Point3ArrayPtr pts;
	  Point3Array::iterator itpBegin= allPts3D->begin();
	  Point3Array::iterator itpEnd= itpBegin + n;
	  for(uint_t i= 0; i <= __stride; i++ )
	  {
		  pts= Point3ArrayPtr(new Point3Array(itpBegin, itpEnd));
		  Interpol local(pts, __knotList, __degree, 1 );
#ifdef DEBUG
		  cout<<"get3DCurve "<<i<<endl;
#endif
		  __fctList3D->getAt(i)= local.get3DCurve();
		  if(itpEnd != allPts3D->end()){ itpBegin+= n; itpEnd+= n; }
	  }
	  __evalPt3D= Point3ArrayPtr(new Point3Array( __stride+1 ));
	  __fctList2D= Curve2DArrayPtr();
	  __evalPt2D= Point2ArrayPtr();
  }

#ifdef DEBUG
cout<<"<-"<<endl;
#endif

  return true;
}

ProfileInterpolationPtr 
ProfileInterpolation::deepcopy(DeepCopier& copier) const
{
	ProfileInterpolationPtr ptr = new ProfileInterpolation(*this);
	copier.copy_recursive_object_attribute(ptr->getProfileList());
	copier.copy_attribute(ptr->getKnotList());
	return ptr;
}


/////////////////////////////////////////////////////////////////////////////

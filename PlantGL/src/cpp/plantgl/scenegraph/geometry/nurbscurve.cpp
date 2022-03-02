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


 

#include "nurbscurve.h"
#include <plantgl/scenegraph/core/pgl_messages.h>
#include <plantgl/tool/util_string.h>
#include <plantgl/math/util_math.h>
#include <plantgl/scenegraph/container/pointarray.h>
#include <plantgl/tool/util_array2.h>
#include <plantgl/tool/util_array.h>
#ifdef _WIN32
#include <malloc.h>
#define alloca _alloca
#endif

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

using namespace std;

/* ----------------------------------------------------------------------- */


const uint_t NurbsCurve::DEFAULT_NURBS_DEGREE(3);


/* ----------------------------------------------------------------------- */


NurbsCurve::Builder::Builder( ) :
  BezierCurve::Builder(),
  KnotList(0)
  {
}


NurbsCurve::Builder::~Builder( ) {
  // nothing to do
}


SceneObjectPtr NurbsCurve::Builder::build( ) const {
  if (isValid()){
      uint_t _degree=0;
      RealArrayPtr *_knots;
      if( ! Degree ){
      if( ! KnotList ) _degree = min ( DEFAULT_NURBS_DEGREE,(*CtrlPointList)->size() - 1) ;
      else _degree = (*KnotList)->size() - (*CtrlPointList)->size() - 1;
#ifdef GEOM_DEBUG
      cout << "Degree value assign to " << _degree <<endl;
#endif
    }
    else _degree = (*Degree);

    if( ! KnotList ){
      _knots = new RealArrayPtr(NurbsCurve::defaultKnotList((*CtrlPointList)->size(), _degree));

      SceneObjectPtr myNurbsPtr(new NurbsCurve(  *CtrlPointList , *_knots ,_degree, (Stride ? *Stride : DEFAULT_STRIDE),  (Width ? *Width : DEFAULT_WIDTH)));
      delete _knots;
      return myNurbsPtr;
    }
    else return  SceneObjectPtr(new NurbsCurve(  *CtrlPointList , *KnotList,_degree,(Stride ? *Stride : DEFAULT_STRIDE),  (Width ? *Width : DEFAULT_WIDTH) ) );
  }
  return SceneObjectPtr();
}


void NurbsCurve::Builder::destroy( ) {
  BCdestroy();
  if (KnotList) delete KnotList;
}


bool NurbsCurve::Builder::isValid( ) const {

  // CtrlPointList field
  if ( !CtrlPointList ) {
    pglErrorEx(PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),"Nurbs Curve","CtrlPointList");
    return false;
  }

  uint_t _size = (*CtrlPointList)->size();
  if ( _size < 3 ) {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"Nurbs Curve","CtrlPointList","Must be greater than 2.");
    return false;
  }

  for (uint_t i=0; i<_size;i++)
    if (fabs((*CtrlPointList)->getAt(i).w()) < GEOM_TOLERANCE) {
      pglErrorEx
        (PGLWARNINGMSG(INVALID_FIELD_ITH_VALUE_ssss),"Nurbs Curve","CtrlPointList",number(i + 1).c_str(),"Weigth must be not null.");
      return false;
    }


  // Degree field
  if ( Degree && (*Degree < 1 ||  *Degree >= _size ) ) {
      pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"Nurbs Curve","Degree","Number of knot Must be greater than 0 and smaller than the number of control points.");
      return false;
  }


  // knot list
  if( KnotList  && (*KnotList)->size() < _size + 2 ){
      pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"Nurbs Curve","KnotList","Number of knots must be greater than the number of control points.");
      return false;
  };

  // Stride field
  if ( Stride && *Stride < 1 ) {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"Nurbs Curve","Stride","Must be greater than 0.");
    return false;
  };



  // Clamped knot vector test
  if( KnotList ){
      uint_t _deg;
      if (Degree !=NULL) _deg = (*Degree);
      else _deg =  ((*KnotList)->size()) - _size -1;
      real_t _val = (*KnotList)->getAt(0);
      for (uint_t i = 1 ; i < _deg+1 ; i++ )
          if( (!(fabs ((*KnotList)->getAt(i) - _val ) <GEOM_TOLERANCE ))){
              pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VECTOR_TYPE_ssss),"Nurbs Curve","KnotList",number(i+1).c_str(),"Must be a clamped vector.");
              return false;
          }
      uint_t _knsize = (*KnotList)->size();
      _val = (*KnotList)->getAt(_knsize -1  );
      for (uint_t j = _knsize - _deg - 1 ; j < _knsize ; j++ )
          if( !(fabs ((*KnotList)->getAt(j) -_val ) <GEOM_TOLERANCE )){
              pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VECTOR_TYPE_ssss),"Nurbs Curve","KnotList",number(j+1).c_str(),"Must be a clamped vector.");
              return false;
          }

  };


  // Fields dependency
  if (  Degree != NULL &&
        KnotList != NULL  &&
        _size != ( (*KnotList)->size() -  *Degree - 1)) {
    string _val = "Must be " + number(_size+(*Degree)+1) + ". Number of knots must be coherent with degree and number of control points.";
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"Nurbs Curve","KnotList",_val.c_str());
    return false;
  };

  return true;

}


/* ----------------------------------------------------------------------- */


NurbsCurve::NurbsCurve(  ) :
  BezierCurve(),
  __degree(DEFAULT_NURBS_DEGREE),
  __knotList()
  {
}

NurbsCurve::NurbsCurve(  const Point4ArrayPtr& ctrlPoints,
                         const RealArrayPtr  knots,
                         uint_t degree,
                         uint_t stride, 
		                 uchar_t width ) :
  BezierCurve(ctrlPoints, stride, width),
  __degree(degree),
  __knotList(knots)
  {
    if(!__knotList)setKnotListToDefault();
  // initialisation de l'objet
  GEOM_ASSERT(isValid());
}

NurbsCurve::NurbsCurve(  const Point4ArrayPtr& ctrlPoints,
                         uint_t degree,
                         const RealArrayPtr  knots,
                         uint_t stride, 
		                 uchar_t width ) :
  BezierCurve(ctrlPoints, stride, width),
  __degree(degree),
  __knotList(knots)
  {
    if(!__knotList)setKnotListToDefault();
  // initialisation de l'objet
  GEOM_ASSERT(isValid());
}

NurbsCurve::NurbsCurve(  const Point3ArrayPtr& ctrlPoints,
                         uint_t degree,
                         const RealArrayPtr  knots,
                         uint_t stride, 
		                 uchar_t width ) :
  BezierCurve(ctrlPoints, stride, width),
  __degree(degree),
  __knotList(knots)
  {
    if(!__knotList)setKnotListToDefault();
  // initialisation de l'objet
  GEOM_ASSERT(isValid());
}

NurbsCurve::~NurbsCurve( ) {
}
/* ----------------------------------------------------------------------- */

const uint_t
NurbsCurve::getDegree( ) const {
  return __degree;
}

uint_t&
NurbsCurve::getDegree( ) {
  return __degree;
}

bool
NurbsCurve::isDegreeToDefault( ) const {
  return __degree == DEFAULT_NURBS_DEGREE;
}

const RealArrayPtr&
NurbsCurve::getKnotList( ) const {
  return __knotList;
}

RealArrayPtr&
NurbsCurve::getKnotList( ){
  return __knotList;
}

const real_t
NurbsCurve::getFirstKnot( ) const {
  return __knotList->getAt(0);
}

const real_t
NurbsCurve::getLastKnot( ) const {
  return __knotList->getAt((__knotList->size())-1);
}

/* ----------------------------------------------------------------------- */

bool NurbsCurve::setKnotListToDefault( ){
    if(!__ctrlPointList) return false;
    else __knotList = defaultKnotList(__ctrlPointList->size(),__degree);
    return true;
}

TOOLS(RealArrayPtr) NurbsCurve::defaultKnotList( uint_t nbCtrlPoints, uint_t degree)
{
    uint_t _size = nbCtrlPoints + degree + 1;
    RealArrayPtr knotList = RealArrayPtr(new RealArray(_size));
    for (uint_t i = 0 ; i < degree+1 ; i++ )
        knotList->setAt(i , 0.0);

    for( uint_t j =   degree+1 ; j<_size - degree - 1; j++ )
        knotList->setAt(j ,(real_t) ( j - degree )  /(real_t)(_size - (2 * degree)  - 1 ));

    for (uint_t k = _size - degree - 1 ; k < _size ; k++ )
        knotList->setAt(k , 1.0);
    return knotList;
}

bool NurbsCurve::isKnotListToDefault( ) const {
    return defaultKnotListTest(getKnotList(),__ctrlPointList->size(),__degree);
}

bool NurbsCurve::defaultKnotListTest(const TOOLS(RealArrayPtr)& knots, uint_t nbCtrlPoints, uint_t degree )
{
    if( !knots ) return true;
    uint_t _size=knots->size();
    if (_size != nbCtrlPoints + degree + 1) return false;
    real_t _val = knots->getAt(0);
    for (uint_t i = 1 ; i < degree+1 ; i++ )
        if( !(fabs (knots->getAt(i) -_val ) <GEOM_TOLERANCE) ) return false;

    _val = real_t(1.0) / (real_t)(_size - (2 * degree)  - 1 );
    for(uint_t j= degree+1;j<_size - degree -1;j++)
        if(!(fabs(fabs(knots->getAt(j+1)-knots->getAt(j))-_val)<GEOM_EPSILON))
            return false;

    _val = knots->getAt(_size -1  );
    for (uint_t k = _size - degree - 1 ; k < _size ; k++ )
        if( !(fabs (knots->getAt(k) -_val ) <GEOM_TOLERANCE) ) return false;
    return true;
}

bool NurbsCurve::isValid( ) const {
  Builder _builder;
  _builder.CtrlPointList = const_cast< Point4ArrayPtr *>(&__ctrlPointList);
  _builder.Degree = const_cast<uint_t *>(&__degree);
  _builder.KnotList = const_cast<RealArrayPtr *>(&__knotList);
  _builder.Stride = const_cast<uint_t *>(&__stride);
  return _builder.isValid();
}

SceneObjectPtr
NurbsCurve::copy(DeepCopier& copier) const
{
  NurbsCurve * ptr = new NurbsCurve(*this);
  copier.copy_attribute(ptr->getCtrlPointList());
  copier.copy_attribute(ptr->getKnotList());
  return SceneObjectPtr(ptr);
}

/* ----------------------------------------------------------------------- */
/*                   Computational Algorithms                              */
/* ----------------------------------------------------------------------- */

/*
  Determine the knot Span index.
  From the Nurbs Book : A2.1 p68
  Used only for clamped knot vector.
*/
uint_t NurbsCurve::findSpan(real_t u)  const  {
    return PGL::findSpan(u,__degree,__knotList);
}

RealArrayPtr
NurbsCurve::computeBasisFunctions(uint_t span, real_t u) const  {
    return basisFunctions(span,u,__degree,__knotList);
}

/* Algo A2.3 p72 Nurbs Book */
RealArray2Ptr NurbsCurve::computeDerivatesBasisFunctions(int n,real_t u, int span ) const {
    return derivatesBasisFunctions(n,u,span,__degree,__knotList);
}

Point4ArrayPtr  NurbsCurve::deriveAtH(real_t u, int d, int span ) const {
    int du = ( d < (int)__degree ? d : __degree);
    Point4ArrayPtr ders(new Point4Array(d+1));
    RealArray2Ptr derF = computeDerivatesBasisFunctions(du,u,span) ;

    for(int k=du;k>=0;--k){
        ders->setAt(k,Vector4(0,0,0,0)) ;
        for(int j=__degree;j>=0;--j){
            ders->setAt(k, ders->getAt(k) + __ctrlPointList->getAt(span-__degree+j)*derF->getAt(k,j)) ;
        }
    }
    return ders;
}

Point4ArrayPtr NurbsCurve::deriveAt(real_t  u, int d, int span ) const{
    Point4ArrayPtr ders(new Point4Array(d+1));
    Point4ArrayPtr dersW = deriveAtH(u,d,span) ;
    Vector4 v ;
    int k,i ;

    RealArray2 Bin(d+1,d+1);
    int n,l ;
    // compute a Binomial Coefficient Matrix
    // Setup the first line
    Bin.setAt(0,0,1.0) ;
    for( l = d ; l > 0 ; --l )
        Bin.setAt( 0 , l , 0.0 ) ;
    // Setup the other lines
    for( n = 0 ; n < d ; n++ ){
        Bin.setAt( n+1 , 0 , 1.0 );
        for( l = 1 ; l < d+1 ; l++ )
            if( n+1 < l )
                Bin.setAt( n , l , 0.0 ) ;
            else
                Bin.setAt( n+1 , l , Bin.getAt( n , l ) + Bin.getAt( n , l-1 ) ) ;
    }


    // Compute the derivative at the parmeter u

    for( k = 0 ; k <= d ; k++ ){
        v.x() = dersW->getAt(k).x() ;
        v.y() = dersW->getAt(k).y() ;
        v.z() = dersW->getAt(k).z() ;
        for(i=k ;i>0 ;--i){
            v -= ders->getAt(k-i)*(Bin.getAt(k,i)*dersW->getAt(i).w()) ;
        }
        ders->setAt(k,v) ;
        ders->setAt(k, ders->getAt(k) / dersW->getAt(0).w()) ;
    }
    return ders;
}


Vector4 NurbsCurve::getDerivativeAt(real_t u, int d) const {
    if (d > __degree) return Vector4(0,0,0,0);
    int span = findSpan(u) ;
    Point4ArrayPtr ders = deriveAt(u,d, span) ;
    return ders->getAt(d) ;
}


Point4ArrayPtr NurbsCurve::getDerivativesAt(real_t u) const {
    int span = findSpan(u) ;
    return deriveAt(u,__degree, span) ;
}



Vector3 NurbsCurve::getPointAt(real_t u) const{
    GEOM_ASSERT( (getFirstKnot() -u ) < GEOM_EPSILON &&  !((u - getLastKnot()) > GEOM_EPSILON));

    uint_t span = findSpan(u);
    RealArrayPtr _basisFunctions = computeBasisFunctions(span,u);
    Vector4 Cw(0.0,0.0,0.0,0.0);
    for (uint_t j = 0; j <= __degree; j++) {
        Vector4 Pj = __ctrlPointList->getAt( span - __degree + j );
        Pj.x() *= Pj.w();
        Pj.y() *= Pj.w();
        Pj.z() *= Pj.w();

        Cw += Pj * _basisFunctions->getAt(j);
    }

    if (fabs(Cw.w()) < GEOM_TOLERANCE)
        return Vector3(Cw.x(),Cw.y(),Cw.z());

    return Cw.project();
}

Vector3 NurbsCurve::getTangentAt(real_t u) const {
    GEOM_ASSERT( (getFirstKnot() -u ) < GEOM_EPSILON &&  !((u - getLastKnot()) > GEOM_EPSILON));
    Vector4 _derivate = getDerivativeAt( u, 1 );
    if(!_derivate.w())
        return Vector3(_derivate.x(),_derivate.y(),_derivate.z());
    else return _derivate.project();
}

Vector3 NurbsCurve::getNormalAt(real_t u) const{
    GEOM_ASSERT( (getFirstKnot() -u ) < GEOM_EPSILON &&  !((u - getLastKnot()) > GEOM_EPSILON));
    Vector3 _tangent = getTangentAt(u);
    Vector4 _derivate = getDerivativeAt( u, 2 );
    Vector3 _normal3;
    if(!_derivate.w())
        _normal3 = Vector3(_derivate.x(),_derivate.y(),_derivate.z());
    else _normal3 = _derivate.project();
    return (cross(cross(_tangent,_normal3),_tangent))/pow(norm(_tangent),real_t(4));
}

/*!
  \brief project a point onto the curve

  It finds the closest point in the curve to a point $p$.
  For more information, see A6.4 and A6.5 on p 231 of the 
  NURBS book

  \param p  the point \a p being projected
  \param guess  initial guess
  \param u  the parametric value for which \a C(u) is closest to \a p.
  \param r  the point at \a C(u)
  \param e1  the minimal error
  \param e2  the maximal error
  \param maxTry  the maximum number of times to try before returning from the function

  \author Philippe Lavoie 
  \date 24 January 1997
*/
Vector3 NurbsCurve::projectTo(const Vector3& p, 
								real_t guess, real_t& u,
								real_t e1, real_t e2,int maxTry) const{
  Vector3 r;
  real_t un ;
  real_t c1, c2;
//  Vector< Point_nD<T,N> > Cd ;
  Vector3 c, cd,cdd ;
  int t = 0 ;
  u = guess ;

  if(u<getFirstKnot()) u = getFirstKnot() ;
  if(u>getLastKnot()) u = getLastKnot() ;

  while(1) {
    ++t ;
    if(t>maxTry){
      r = c ;
      return r;
    }
    c = getPointAt(u) ;
 /*   getDerivativeAt(u,2,Cd) ;
    cd = Cd[1] ;
    cdd = Cd[2] ;*/
	cd = getDerivativeAt(u,1).project();
	cdd = getDerivativeAt(u,2).project();
    c1 = normSquared(c-p) ;
    if(c1<e1*e1){
      r = c ;
      return r;
    }
    c2 = dot(cd,(c-p)) ;
    /// c2 = norm(cd*(c-p)) ;
    //c2 *= c2 ;
    c2 /= norm(cd)*norm(c-p) ;
    //if(c2<e2*e2){
    if(c2<e2){
      r =c ;
      return r;
    }
    
    un = u- cd*(c-p)/(cdd*(c-p)+normSquared(cd)) ;
    
    if(un<getFirstKnot()) un = getFirstKnot() ;
    if(un>getLastKnot()) un = getLastKnot() ;

    if(normSquared(cd*(un-u))<e1*e1){
      r = c ;
      return r;
    }
    u = un ;
  }
  return r;
}


uint_t 
PGL(findSpan)(real_t u,  
	 uint_t _degree, 
	 const RealArrayPtr& _knotList ){
    uint_t n = _knotList->size()-_degree -1;

  if( u >= _knotList->getAt( n ) )return ( n -1 );
  if( u <= _knotList->getAt( _degree )  )return ( _degree );

  uint_t low = _degree;
  uint_t high = n ;
  uint_t mid = ( low + high ) / 2;
  real_t _knot =  _knotList->getAt(mid);

  while (u < _knot  || u >= _knotList->getAt(mid+1) ){
    if ( u < _knot ) high = mid;
    else low = mid;
    mid = ( low + high ) / 2;
    _knot = _knotList->getAt(mid);
  }

  return mid;

}

RealArrayPtr
PGL(basisFunctions)(uint_t span, real_t u, uint_t _degree, const RealArrayPtr& _knotList) {
  RealArrayPtr BasisFunctions(new RealArray(_degree + 1));
  if( span >= _knotList->size()-_degree - 1){ // for clamped vector only
    for(uint_t _i = 0 ; _i <_degree ; _i ++)
      BasisFunctions->setAt(_degree - _i ,1.0);
    return BasisFunctions;
  }

  /// memory set with alloca is automatically freed at the end of the function
  real_t * left = (real_t*)alloca(2*( _degree+1)*sizeof(real_t));
  real_t * right= &left[ _degree+1 ];
  real_t saved;

  BasisFunctions->setAt(0,1.0);

  for( uint_t j = 1 ; j <= _degree ; j++ ){
    left[j] = u - _knotList->getAt(span + 1 -j) ;
    right[j] = _knotList->getAt(span + j) - u ;
    saved = 0.0;
    for ( uint_t r = 0 ; r < j ; r++){
        if(right[r+1] + left[j-r] ==0){
            for(uint_t m = 0 ; m <2*(_degree+1) ; m++)cerr << left[m] << " - ";
            cerr << "right[" << r << "+1] = " << right[r+1] << " & left["
                 << j << '-' << r << "] = " << left[j-r] << endl;
        }
        assert(right[r+1] + left[j-r] != 0);
        real_t temp = BasisFunctions->getAt(r) / ( right[r+1] + left[j-r] );
        BasisFunctions->setAt(r, saved + ( right[r+1] * temp ));
        saved = left[j-r] * temp;
    }
    BasisFunctions->setAt(j,saved);
  }
  return BasisFunctions;
}

/* Algo A2.3 p72 Nurbs Book */
RealArray2Ptr
PGL(derivatesBasisFunctions)(int n,real_t u, int span,  uint_t _degree, const RealArrayPtr& _knotList ){
  real_t * left = (real_t *) alloca(2*(_degree+1)*sizeof(real_t)) ;
  real_t * right = &left[_degree+1] ;

  RealArray2 ndu(_degree+1,_degree+1) ;
  real_t saved,temp ;
  int r, j;

  RealArray2Ptr ders(new RealArray2(n+1,_degree+1));

  ndu.setAt(0,0,1.0) ;

  for(j=1; j <= (int)_degree ;j++){
      left[j] = u-_knotList->getAt(span+1-j) ;
      right[j] = _knotList->getAt(span+j)-u ;
      saved = 0.0 ;

      for(r=0;r<j ; r++){
          // Lower triangle
          ndu.setAt(j,r,right[r+1]+left[j-r]) ;
          temp = ndu.getAt(r,j-1)/ndu.getAt(j,r) ;
          // Upper triangle
          ndu.setAt(r,j,saved+right[r+1] * temp) ;
          saved = left[j-r] * temp ;
      }

      ndu.setAt(j,j,saved) ;
  }

  for(j=_degree;j>=0;--j)
      ders->setAt(0,j,ndu.getAt(j,_degree)) ;

  // Compute the derivatives
  RealArray2 a(_degree+1,_degree+1) ;
  for(r=0;r<=(int)_degree;r++){
      int s1,s2 ;
      s1 = 0 ; s2 = 1 ; // alternate rows in array a
      a.setAt(0,0,1.0) ;
      // Compute the kth derivative
      for(int k=1;k<=n;k++){
          real_t d ;
          int rk,pk,j1,j2 ;
          d = 0.0 ;
          rk = r-k ; pk = _degree-k ;

          if(r>=k){
              a.setAt(s2,0,(a.getAt(s1,0)/ndu.getAt(pk+1,rk))) ;
              d = a.getAt(s2,0)*ndu.getAt(rk,pk) ;
          }

          if(rk>=-1){
              j1 = 1 ;
          }
          else{
              j1 = -rk ;
          }

          if(r-1 <= pk){
              j2 = k-1 ;
          }
          else{
              j2 = _degree-r ;
          }

          for(j=j1;j<=j2;j++){
              a.setAt(s2,j,((a.getAt(s1,j)-a.getAt(s1,j-1))/ndu.getAt(pk+1,rk+j))) ;
              d += a.getAt(s2,j)*ndu.getAt(rk+j,pk) ;
          }

      if(r<=pk){
        a.setAt(s2,k,-(a.getAt(s1,k-1))/ndu.getAt(pk+1,r)) ;
        d += a.getAt(s2,k)*ndu.getAt(r,pk) ;
      }
      ders->setAt(k,r, d) ;
      j = s1 ; s1 = s2 ; s2 = j ; // Switch rows
    }
  }

  // Multiply through by the correct factors
  r = _degree ;
  for(int k=1;k<=n;k++){
      for(j=_degree;j>=0;--j)
          ders->setAt(k,j,ders->getAt(k,j)*r) ;
      r *= _degree-k ;
  }
  return ders;

}

/* ----------------------------------------------------------------------- */


NurbsCurve2D::Builder::Builder( ) :
  BezierCurve2D::Builder(),
  KnotList(0)
  {
}


NurbsCurve2D::Builder::~Builder( ) {
  // nothing to do
}


SceneObjectPtr NurbsCurve2D::Builder::build( ) const {
  if (isValid()){
      uint_t _degree=0;
      RealArrayPtr *_knots;
      if( ! Degree ){
      if( ! KnotList ) _degree = min ( NurbsCurve::DEFAULT_NURBS_DEGREE,(*CtrlPointList)->size() - 1) ;
      else _degree = (*KnotList)->size() - (*CtrlPointList)->size() - 1;
#ifdef GEOM_DEBUG
      cout << "Degree value assign to " << _degree <<endl;
#endif
    }
    else _degree = (*Degree);

    if( ! KnotList ){
      _knots = new RealArrayPtr(NurbsCurve::defaultKnotList((*CtrlPointList)->size(),_degree));
      SceneObjectPtr myNurbsPtr(new NurbsCurve2D(  *CtrlPointList , *_knots , _degree, (Stride ? *Stride : NurbsCurve::DEFAULT_STRIDE), (Width ? *Width : DEFAULT_WIDTH) ));
      delete _knots;
      return myNurbsPtr;
    }
    else return  SceneObjectPtr(new NurbsCurve2D(  *CtrlPointList , *KnotList, _degree, (Stride ? *Stride : NurbsCurve::DEFAULT_STRIDE), (Width ? *Width : DEFAULT_WIDTH) ) );
  }
  return SceneObjectPtr();
}


void NurbsCurve2D::Builder::destroy( ) {
  if (CtrlPointList) delete CtrlPointList;
  if (KnotList) delete KnotList;
  if (Degree) delete Degree;
  if (Stride) delete Stride;
  if (Width) delete Width;
}


bool NurbsCurve2D::Builder::isValid( ) const {

  // CtrlPointList field
  if ( !CtrlPointList ) {
    pglErrorEx(PGLWARNINGMSG(UNINITIALIZED_FIELD_ss),"NurbsCurve2D","CtrlPointList");
    return false;
  }

  uint_t _size = (*CtrlPointList)->size();
  if ( _size < 3 ) {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"NurbsCurve2D","CtrlPointList","Must be greater than 2.");
    return false;
  }

  for (uint_t i=0; i<_size;i++)
    if (fabs((*CtrlPointList)->getAt(i).z()) < GEOM_TOLERANCE) {
      pglErrorEx
        (PGLWARNINGMSG(INVALID_FIELD_ITH_VALUE_ssss),"NurbsCurve2D","CtrlPointList",number(i + 1).c_str(),"Weigth must be not null.");
      return false;
    }


  // Degree field
  if ( Degree && (*Degree < 1 ||  *Degree >= _size ) ) {
      pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"NurbsCurve2D","Degree","Number of knot Must be greater than 0 and smaller than the number of control points.");
      return false;
  }


  // knot list
  if( KnotList  && (*KnotList)->size() < _size + 2 ){
      pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"NurbsCurve2D","KnotList","Number of knots must be greater than the number of control points.");
      return false;
  };

  // Stride field
  if ( Stride && *Stride < 1 ) {
    pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VALUE_sss),"NurbsCurve2D","Stride","Must be greater than 0.");
    return false;
  };



  // Clamped knot vector test
  if( KnotList ){
      uint_t _deg;
      if (Degree !=NULL) _deg = (*Degree);
      else _deg =  ((*KnotList)->size()) - _size -1;
      real_t _val = (*KnotList)->getAt(0);
      for (uint_t i = 1 ; i < _deg+1 ; i++ )
          if( (!(fabs ((*KnotList)->getAt(i) - _val ) <GEOM_TOLERANCE ))){
              pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VECTOR_TYPE_ssss),"NurbsCurve2D","KnotList",number(i+1).c_str(),"Must be a clamped vector.");
              return false;
          }
      uint_t _knsize = (*KnotList)->size();
      _val = (*KnotList)->getAt(_knsize -1  );
      for (uint_t j = _knsize - _deg - 1 ; j < _knsize ; j++ )
          if( !(fabs ((*KnotList)->getAt(j) -_val ) <GEOM_TOLERANCE )){
              pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_VECTOR_TYPE_ssss),"NurbsCurve2D","KnotList",number(j+1).c_str(),"Must be a clamped vector.");
              return false;
          }

  };


  // Fields dependency
  if (  Degree != NULL &&
        KnotList != NULL  &&
        _size != ( (*KnotList)->size() -  *Degree - 1)) {
      pglErrorEx(PGLWARNINGMSG(INVALID_FIELD_SIZE_sss),"NurbsCurve2D","KnotList","Number of knots must be coherent with degree and number of control points.");
      return false;
  };

  return true;

}


/* ----------------------------------------------------------------------- */

NurbsCurve2D::NurbsCurve2D(   ) :
  BezierCurve2D(),
  __degree(NurbsCurve::DEFAULT_NURBS_DEGREE),
    __knotList(){
}

NurbsCurve2D::NurbsCurve2D(  const Point3ArrayPtr& ctrlPoints, const RealArrayPtr  knots, uint_t degree, uint_t stride, uchar_t width ) :
  BezierCurve2D(ctrlPoints, stride, width),
  __degree(degree),
  __knotList(knots)
  {
  if(!__knotList)setKnotListToDefault();
  // initialisation de l'objet
  GEOM_ASSERT(isValid());
}

NurbsCurve2D::NurbsCurve2D(  const Point3ArrayPtr& ctrlPoints, uint_t degree, const RealArrayPtr  knots, uint_t stride , uchar_t width ) :
  BezierCurve2D(ctrlPoints, stride, width),
  __degree(degree),
  __knotList(knots)
  {
  if(!__knotList)setKnotListToDefault();
  // initialisation de l'objet
  GEOM_ASSERT(isValid());
}

  NurbsCurve2D::NurbsCurve2D(  const Point2ArrayPtr& ctrlPoints, uint_t degree, const RealArrayPtr  knots, uint_t stride, uchar_t width ) :
  BezierCurve2D(ctrlPoints, stride, width),
  __degree(degree),
  __knotList(knots)
  {
  if(!__knotList)setKnotListToDefault();
  // initialisation de l'objet
  GEOM_ASSERT(isValid());
}

NurbsCurve2D::~NurbsCurve2D( ) {
}

/* ----------------------------------------------------------------------- */


const uint_t
NurbsCurve2D::getDegree( ) const {
  return __degree;
}

uint_t&
NurbsCurve2D::getDegree( ) {
  return __degree;
}

bool
NurbsCurve2D::isDegreeToDefault( ) const {
  return __degree == NurbsCurve::DEFAULT_NURBS_DEGREE;
}

const RealArrayPtr&
NurbsCurve2D::getKnotList( ) const {
  return __knotList;
}

RealArrayPtr&
NurbsCurve2D::getKnotList( ) {
  return __knotList;
}

const real_t
NurbsCurve2D::getFirstKnot( ) const {
  return __knotList->getAt(0);
}

const real_t
NurbsCurve2D::getLastKnot( ) const {
  return __knotList->getAt((__knotList->size())-1);
}

/* ----------------------------------------------------------------------- */

bool NurbsCurve2D::setKnotListToDefault( ){
    if(!__ctrlPointList) return false;
    else __knotList = NurbsCurve::defaultKnotList(__ctrlPointList->size(),__degree);
    return true;
}


bool NurbsCurve2D::isKnotListToDefault( ) const {
    return NurbsCurve::defaultKnotListTest(getKnotList(),__ctrlPointList->size(),__degree);
}



bool NurbsCurve2D::isValid( ) const {
  Builder _builder;
  _builder.CtrlPointList = const_cast< Point3ArrayPtr *>(&__ctrlPointList);
  _builder.Degree = const_cast<uint_t *>(&__degree);
  _builder.KnotList = const_cast<RealArrayPtr *>(&__knotList);
  _builder.Stride = const_cast<uint_t *>(&__stride);
  return _builder.isValid();
}


SceneObjectPtr
NurbsCurve2D::copy(DeepCopier& copier) const
{
  NurbsCurve2D * ptr = new NurbsCurve2D(*this);
  copier.copy_attribute(ptr->getCtrlPointList());
  copier.copy_attribute(ptr->getKnotList());
  return SceneObjectPtr(ptr);
}


/* ----------------------------------------------------------------------- */
/*                   Computational Algorithms                              */
/* ----------------------------------------------------------------------- */

uint_t NurbsCurve2D::findSpan(real_t u) const {
    return PGL::findSpan(u,__degree,__knotList);
}

Vector2 NurbsCurve2D::getPointAt(real_t u) const{
  GEOM_ASSERT( (getFirstKnot() -u ) < GEOM_EPSILON &&  !((u - getLastKnot()) > GEOM_EPSILON));

  uint_t span = findSpan(u);
  RealArrayPtr _basisFunctions = basisFunctions(span,u,__degree,__knotList);
  Vector3 Cw(0.0,0.0,0.0);
  for (uint_t j = 0; j <= __degree; j++) {
      Vector3 Pj = __ctrlPointList->getAt( span - __degree + j );
      Pj.x() *= Pj.z();
      Pj.y() *= Pj.z();

      Cw += Pj * _basisFunctions->getAt(j);
  }

  if (fabs(Cw.z()) < GEOM_TOLERANCE)
    return Vector2(Cw.x(),Cw.y());

  return Cw.project();
}

/* Algo A2.3 p72 Nurbs Book */
RealArray2Ptr NurbsCurve2D::computeDerivatesBasisFunctions(int n,real_t u, int span ) const {
    return derivatesBasisFunctions(n,u,span,__degree,__knotList);
}

Point3ArrayPtr  NurbsCurve2D::deriveAtH(real_t u, int d, int span ) const {
    int du = ( d < (int)__degree ? d : __degree);
    Point3ArrayPtr ders(new Point3Array(d+1));
    RealArray2Ptr derF = computeDerivatesBasisFunctions(du,u,span) ;

    for(int k=du;k>=0;--k){
        ders->setAt(k,Vector3(0,0,0)) ;
        for(int j=__degree;j>=0;--j){
            ders->setAt(k, ders->getAt(k) + __ctrlPointList->getAt(span-__degree+j)*derF->getAt(k,j)) ;
        }
    }
    return ders;
}

Point3ArrayPtr NurbsCurve2D::deriveAt(real_t  u, int d, int span ) const{
    Point3ArrayPtr ders(new Point3Array(d+1));
    Point3ArrayPtr dersW = deriveAtH(u,d,span) ;
    Vector3 v ;
    int k,i ;

    RealArray2 Bin(d+1,d+1);
    int n,l ;
    // compute a Binomial Coefficient Matrix
    // Setup the first line
    Bin.setAt(0,0,1.0) ;
    for( l = d ; l > 0 ; --l )
        Bin.setAt( 0 , l , 0.0 ) ;
    // Setup the other lines
    for( n = 0 ; n < d ; n++ ){
        Bin.setAt( n+1 , 0 , 1.0 );
        for( l = 1 ; l < d+1 ; l++ )
            if( n+1 < l )
                Bin.setAt( n , l , 0.0 ) ;
            else
                Bin.setAt( n+1 , l , Bin.getAt( n , l ) + Bin.getAt( n , l-1 ) ) ;
    }


    // Compute the derivative at the parmeter u

    for( k = 0 ; k <= d ; k++ ){
        v.x() = dersW->getAt(k).x() ;
        v.y() = dersW->getAt(k).y() ;
        v.z() = dersW->getAt(k).z() ;
        for(i=k ;i>0 ;--i){
            v -= ders->getAt(k-i)*(Bin.getAt(k,i)*dersW->getAt(i).z()) ;
        }
        ders->setAt(k,v) ;
        ders->setAt(k, ders->getAt(k) / dersW->getAt(0).z()) ;
    }
    return ders;
}


Vector3 NurbsCurve2D::getDerivativeAt(real_t u, int d) const {
    if (d > __degree) return Vector3(0,0,0);
    int span = findSpan(u) ;
    Point3ArrayPtr ders = deriveAt(u,d, span) ;
    return ders->getAt(d) ;
}


Point3ArrayPtr NurbsCurve2D::getDerivativesAt(real_t u) const {
    int span = findSpan(u) ;
    return deriveAt(u,__degree, span) ;
}
Vector2 NurbsCurve2D::getTangentAt(real_t u) const {
    GEOM_ASSERT( (getFirstKnot() -u ) < GEOM_EPSILON &&  !((u - getLastKnot()) > GEOM_EPSILON));
    Vector3 _derivate = getDerivativeAt( u, 1 );
    if(!_derivate.z())
        return Vector2(_derivate.x(),_derivate.y());
    else return _derivate.project();
}

Vector2 NurbsCurve2D::getNormalAt(real_t u) const{
    GEOM_ASSERT( (getFirstKnot() -u ) < GEOM_EPSILON &&  !((u - getLastKnot()) > GEOM_EPSILON));
    Vector2 _tangent = getTangentAt(u);
    Vector3 _derivate = getDerivativeAt( u, 2 );
    Vector2 _normal2;
    if(!_derivate.z())
        _normal2 = Vector2(_derivate.x(),_derivate.y());
    else _normal2 = _derivate.project();
    Vector3 nml3 = cross(cross(Vector3(_tangent,0),Vector3(_normal2,0)),Vector3(_tangent,0))/pow(norm(_tangent),real_t(4));
	return Vector2(nml3[0],nml3[1]);
}
/* ----------------------------------------------------------------------- */

/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       PlantGL: Modeling Plant Geometry
 *
 *       Copyright 2000-2006 - Cirad/Inria/Inra - Virtual Plant Team
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
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

/*! \file actn_amaptranslator.h
    \brief Definition of the action class AmapTranslator.
*/

#ifndef __actn_amaptranslator_h__
#define __actn_amaptranslator_h__

/* ----------------------------------------------------------------------- */

#include "../algo_config.h"
#include <plantgl/scenegraph/core/action.h>
#include <plantgl/tool/rcobject.h>
#include <plantgl/math/util_vector.h>

/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

class Discretizer;
typedef RCPtr<AmapSymbol> AmapSymbolPtr;

/* ----------------------------------------------------------------------- */

/**
   \class AmapTranslator
   \brief An action which translate a GEOM object in an AMAP Symbol.
*/

/* ----------------------------------------------------------------------- */

class ALGO_API AmapTranslator : public Action {

  public:

    /// Constructs an Action.
    AmapTranslator(Discretizer& _discretizer);

    /// Destructor.
  virtual ~AmapTranslator() ;

    /// Return the last computed translation.
  AmapSymbolPtr getSymbol();

    /// Set the normalization.
  void setNormalized(bool b);

    /// tell if the symbol are normalized.
  const bool isNormalized();


  const TOOLS(Vector3)& getNormalizationFactors() const {
          return __normfactor;
  }

  const TOOLS(Vector3)& getTranslation() const {
          return __translation;
  }

    /// @name Shape
    //@{
    virtual bool process(Shape * Shape);

    //@}

  /// @name Material
  //@{

    virtual bool process( Material * material );

    virtual bool process( MonoSpectral * monoSpectral );

    virtual bool process( MultiSpectral * multiSpectral );

    virtual bool process( ImageTexture * textureimg );

    virtual bool process( Texture2D * texture );

    virtual bool process( Texture2DTransformation * texturetransformation );

    //@}

  /// @name Geom3D
  //@{

    virtual bool process( AmapSymbol * amapSymbol );

    virtual bool process( AsymmetricHull * asymmetricHull );

    virtual bool process( AxisRotated * axisRotated );

    virtual bool process( BezierCurve * bezierCurve );

    virtual bool process( BezierPatch * bezierPatch );

    virtual bool process( Box * box );

    virtual bool process( Cone * cone );

    virtual bool process( Cylinder * cylinder );

    virtual bool process( ElevationGrid * elevationGrid );

    virtual bool process( EulerRotated * eulerRotated );

    virtual bool process( ExtrudedHull * extrudedHull );

    virtual bool process( FaceSet * faceSet );

    virtual bool process( Frustum * frustum );

    virtual bool process( Extrusion * extrusion );

    virtual bool process( Group * group );

    virtual bool process( IFS * ifs );

    virtual bool process( NurbsCurve * nurbsCurve );

    virtual bool process( NurbsPatch * nurbsPatch );

    virtual bool process( Oriented * oriented );

    virtual bool process( Paraboloid * paraboloid );

    virtual bool process( PointSet * pointSet );

    virtual bool process( Polyline * polyline );

    virtual bool process( QuadSet * quadSet );

    virtual bool process( Revolution * revolution );

    virtual bool process( Swung* swung );

    virtual bool process( Scaled * scaled );

    virtual bool process( ScreenProjected * scp );

    virtual bool process( Sphere * sphere );

    virtual bool process( Tapered * tapered );

    virtual bool process( Translated * translated );

    virtual bool process( TriangleSet * triangleSet );

  //@}

  /// @name Geom2D
  //@{
    virtual bool process( BezierCurve2D * bezierCurve );

    virtual bool process( Disc * disc );

    virtual bool process( NurbsCurve2D * nurbsCurve );

    virtual bool process( PointSet2D * pointSet );

    virtual bool process( Polyline2D * polyline );


    //@}

	virtual bool process( Text * text );

	virtual bool process( Font * font );

  protected:

    /// The points to fit.
    Discretizer& __discretizer;

    /// The resulting Amap Symbol.
    AmapSymbolPtr __symbol;

    /// The resulting normalisation factor.
    TOOLS(Vector3) __normfactor;

    /// The resulting translation factor.
    TOOLS(Vector3) __translation;

    /// If Symbol must be normalized.
    bool __normalized;
};


/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */

// __actn_amaptranslator_h__
#endif


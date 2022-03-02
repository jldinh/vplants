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

/*! \file actn_statisticcomputer.h
    \brief Definition of the action class StatisticComputer.
*/


#ifndef __actn_statisticcomputer_h__
#define __actn_statisticcomputer_h__

#include <plantgl/pgl_config.h>
#include "../algo_config.h"
#include <plantgl/scenegraph/core/action.h>

//#ifndef _WIN32
//#include <features.h>
//#endif

#include <vector>
#include <plantgl/tool/util_types.h>
#include <plantgl/tool/util_hashset.h>

/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

/**
   \class StatisticComputer
   \brief An action which compute statistics on a scene.
*/



class ALGO_API StatisticComputer : public Action
{
public:

  /** Constructs a  StatisticComputer*/
  StatisticComputer();

  /// Destructor
  virtual ~StatisticComputer( ) ;

  /// Get the number of element of a scene.
  virtual const uint_t getSize() const;

  /// Get the number of named element of a scene.
  virtual const uint_t getNamed() const;

  /// Get the memory size of the scene.
  virtual const uint_t getMemorySize() const ;


  /// Get the all elements of the scene.
  virtual const std::vector<uint_t>& getElements() const;



  /// @name Shape
  //@{
  virtual bool process(Shape * Shape);

  /// Get the number of shape.
  const uint_t getShape() const ;
  //@}

  /// @name Material
  //@{

  virtual bool process( Material * material );

  /// Get the number of Material.
  const uint_t getMaterial() const;

  virtual bool process( MonoSpectral * monoSpectral );

  /// Get the number of MonoSpectral.
  const uint_t getMonoSpectral() const;

  virtual bool process( MultiSpectral * multiSpectral );

  /// Get the number of MultiSpectral.
  const uint_t getMultiSpectral() const;

  virtual bool process( ImageTexture * texture );

  /// Get the number of ImageTexture.
  const uint_t getImageTexture() const;

  virtual bool process( Texture2D * texture );

  /// Get the number of Texture2D.
  const uint_t getTexture2D() const;

  virtual bool process( Texture2DTransformation * texturetransformation );

  /// Get the number of Texture2DTransformation.
  const uint_t getTexture2DTransformation() const;
  //@}

  /// @name Geom3D
  //@{
  virtual bool process( AmapSymbol * amapSymbol );

  /// Get the number of AmapSymbol.
  const uint_t getAmapSymbol() const;

  virtual bool process( AsymmetricHull * asymmetricHull );

  /// Get the number of AsymmetricHull.
  const uint_t getAsymmetricHull() const;

  virtual bool process( AxisRotated * axisRotated );

  /// Get the number of AxisRotated.
  const uint_t getAxisRotated() const ;

  virtual bool process( BezierCurve * bezierCurve );

  /// Get the number of BezierCurve.
  const uint_t getBezierCurve() const ;

  virtual bool process( BezierPatch * bezierPatch );

  /// Get the number of BezierPatch.
  const uint_t getBezierPatch() const ;

  virtual bool process( Box * box );

  /// Get the number of Box.
  const uint_t getBox() const ;

  virtual bool process( Cone * cone );

  /// Get the number of Cone.
  const uint_t getCone() const ;

  virtual bool process( Cylinder * cylinder );

  /// Get the number of Cylinder.
  const uint_t getCylinder() const ;

  virtual bool process( ElevationGrid * elevationGrid );

  /// Get the number of ElevationGrid.
  const uint_t getElevationGrid() const ;

  virtual bool process( EulerRotated * eulerRotated );

  /// Get the number of EulerRotated.
  const uint_t getEulerRotated() const ;

  virtual bool process( ExtrudedHull * extrudedHull );

  /// Get the number of ExtrudedHull.
  const uint_t getExtrudedHull() const;

  virtual bool process( FaceSet * faceSet );

  /// Get the number of FaceSet.
  const uint_t getFaceSet() const ;

  virtual bool process( Frustum * frustum );

  /// Get the number of Frustum.
  const uint_t getFrustum() const;

  virtual bool process( Extrusion * extrusion );

  /// Get the number of Extrusion.
  const uint_t getExtrusion() const ;

  virtual bool process( Group * group );

  /// Get the number of Group.
  const uint_t getGroup() const;

  virtual bool process( NurbsCurve * nurbsCurve );

  /// Get the number of NurbsCurve.
  const uint_t getNurbsCurve() const ;

  virtual bool process( NurbsPatch * nurbsPatch );

  /// Get the number of NurbsPatch.
  const uint_t getNurbsPatch() const ;

  virtual bool process( Oriented * oriented );

  /// Get the number of Oriented.
  const uint_t getOriented() const;

  virtual bool process( Paraboloid * paraboloid );

  /// Get the number of Paraboloid.
  const uint_t getParaboloid() const;

  virtual bool process( PointSet * pointSet );

  /// Get the number of PointSet.
  const uint_t getPointSet() const;

  virtual bool process( Polyline * polyline );

  /// Get the number of Polyline.
  const uint_t getPolyline() const;

  virtual bool process( QuadSet * quadSet );

  /// Get the number of QuadSet.
  const uint_t getQuadSet() const ;

  virtual bool process( Revolution * revolution );

  /// Get the number of Revolution.
  const uint_t getRevolution() const ;

  virtual bool process( Scaled * scaled );

  /// Get the number of Scaled.
  const uint_t getScaled() const ;

  virtual bool process( ScreenProjected * screenprojected );

  const uint_t getScreenProjected() const;

  virtual bool process( Sphere * sphere );

  /// Get the number of Sphere.
  const uint_t getSphere() const ;

  virtual bool process( Tapered * tapered );

  /// Get the number of Tapered.
  const uint_t getTapered() const ;

  virtual bool process( Translated * translated );

  /// Get the number of Translated.
  const uint_t getTranslated() const;

  virtual bool process( TriangleSet * triangleSet );

  /// Get the number of TriangleSet.
  const uint_t getTriangleSet() const;

  //@}

  /// @name Geom2D
  //@{
  virtual bool process( BezierCurve2D * bezierCurve );

  /// Get the number of BezierCurve2D.
  const uint_t getBezierCurve2D() const ;

  virtual bool process( Disc * disc );

  /// Get the number of Disc.
  const uint_t getDisc() const ;

  virtual bool process( NurbsCurve2D * nurbsCurve );

  /// Get the number of NurbsCurve2D.
  const uint_t getNurbsCurve2D() const;

  virtual bool process( PointSet2D * pointSet );

  /// Get the number of PointSet2D.
  const uint_t getPointSet2D() const ;

  virtual bool process( Polyline2D * polyline );

  /// Get the number of Polyline2D.
  const uint_t getPolyline2D() const;

  virtual bool process( Swung * revolution );

  /// Get the number of Swung.
  const uint_t getSwung() const;

  virtual bool process( IFS * ifs );

  /// Get the number of IFS.
  const uint_t getIFS() const;
  //@}

  virtual bool process( Text * text );

  const uint_t getText() const;

  virtual bool process( Font * font );

  const uint_t getFont() const;

  protected:

  /// The cache where to store the already printed objects
  pgl_hash_set_uint32 __cache;

  /// nb element.
  uint_t __element;

  /// nb named element.
  uint_t __named;

  /// nb shape by class.
  std::vector<uint_t> __shape;

  /// memory size.
  uint_t __memsize;

};


/* ------------------------------------------------------------------------- */

// __actn_statisticcomputer_h__
/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif


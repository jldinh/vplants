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


/*! \file actn_plyprinter.h
    \brief Definition of the action class PlyPrinter.
*/

#ifndef __actn_plyprinter_h__
#define __actn_plyprinter_h__

/* ----------------------------------------------------------------------- */

#include "printer.h"
#include <plantgl/tool/rcobject.h>

/* ----------------------------------------------------------------------- */

TOOLS_BEGIN_NAMESPACE
class bofstream;
TOOLS_END_NAMESPACE

/* ----------------------------------------------------------------------- */

PGL_BEGIN_NAMESPACE

/* ----------------------------------------------------------------------- */

class Discretizer;
class Scene;
typedef RCPtr<Scene> ScenePtr;

/* ----------------------------------------------------------------------- */


/**
  \class PlyPrinter
  \brief An action to write GEOM object in Ply Ascii Format.
*/


class CODEC_API PlyPrinter : public Printer
{

public :

  /*! \enum ply_format
  This enum specifies the Format of the ply printer output.
  */
  /*!
  \var ply_format ply_ascii
        Ascii format
  */
  /*!
  \var ply_format ply_binary_little_endian
    Binary format in little endian
  */
  /*!
  \var ply_format ply_binary_big_endian
    Binary format in big endian
  */

  enum ply_format {
    ply_ascii,
    ply_binary_little_endian,
    ply_binary_big_endian
  };

  /// Constructor.
  PlyPrinter( std::ostream& stream , Discretizer& discretizer);

  /// Destructor.
  virtual ~PlyPrinter();


  /// Add comment in the header of the outpu file.
  virtual bool header(const char * comment = NULL);

  /// Return whether the output is in binary format or not.
  virtual bool isBinary() const {
    return false;
  }

  /// Return whether the output is in ascii format or not.
  virtual bool isAscii() const {
    return true;
  }

  /// @name Pre and Post Processing
  //@{

  /// Begining of the Action.
  virtual bool beginProcess();

  /// End of the Action.
  virtual bool endProcess();

  //@}

  /// @name Shape
  //@{

  /** Applies \e self to an object of type of Shape.
    \warning
      - \e Shape must be non null and valid. */
  virtual bool process( Shape * Shape );

  /** Applies \e self to an object of type of Inline.
    \warning
      - \e geominline must be non null and valid. */
  virtual bool process( Inline * geominline );

  //@}

  /// @name Material
  //@{

  /** Applies \e self to an object of type of Material.
    \warning
      - \e material must be non null and valid. */
  virtual bool process( Material * material );

  /** Applies \e self to an object of type of MonoSpectral.
    \warning
      - \e monoSpectral must be non null and valid. */
  virtual bool process( MonoSpectral * monoSpectral );

  /** Applies \e self to an object of type of MultiSpectral.
    \warning
      - \e multiSpectral must be non null and valid. */
  virtual bool process( MultiSpectral * multiSpectral );

  /** Applies \e self to an object of type of Texture2D.
    \warning
      - \e texture must be non null and valid. */
  virtual bool process( Texture2D * texture );

  /** Applies \e self to an object of type of ImageTexture.
    \warning
      - \e texture must be non null and valid. */
  virtual bool process( ImageTexture * texture );

  /** Applies \e self to an object of type of Texture2DTransformation.
    \warning
      - \e texture must be non null and valid. */
  virtual bool process( Texture2DTransformation * texture );

  //@}

  /// @name Geom3D
  //@{

  /** Applies \e self to an object of type of AmapSymbol.
    \warning
      - \e amapSymbol must be non null and valid. */
  virtual bool process( AmapSymbol * amapSymbol );

  /** Applies \e self to an object of type of AsymmetricHull.
    \warning
      - \e amapSymbol must be non null and valid. */
  virtual bool process( AsymmetricHull * amapSymbol );

  /** Applies \e self to an object of type of AxisRotated.
    \warning
      - \e axisRotated must be non null and valid. */
  virtual bool process( AxisRotated * axisRotated );

  /** Applies \e self to an object of type of BezierCurve.
    \warning
      - \e bezierCurve must be non null and valid. */
  virtual bool process( BezierCurve * bezierCurve );

  /** Applies \e self to an object of type of BezierPatch.
    \warning
      - \e bezierPatch must be non null and valid. */
  virtual bool process( BezierPatch * bezierPatch );

  /** Applies \e self to an object of type of Box.
    \warning
      - \e box must be non null and valid. */
  virtual bool process( Box * box );

  /** Applies \e self to an object of type of Cone.
    \warning
      - \e cone must be non null and valid. */
  virtual bool process( Cone * cone );

  /** Applies \e self to an object of type of Cylinder.
    \warning
      - \e cylinder must be non null and valid. */
  virtual bool process( Cylinder * cylinder );

  /** Applies \e self to an object of type of ElevationGrid.
    \warning
      - \e elevationGrid must be non null and valid. */
  virtual bool process( ElevationGrid * elevationGrid );

  /** Applies \e self to an object of type of EulerRotated.
    \warning
      - \e eulerRotated must be non null and valid. */
  virtual bool process( EulerRotated * eulerRotated );

  /** Applies \e self to an object of type of ExtrudedHull.
    \warning
      - \e amapSymbol must be non null and valid. */
  virtual bool process( ExtrudedHull * amapSymbol );

  /** Applies \e self to an object of type of FaceSet.
    \warning
      - \e faceSet must be non null and valid. */
  virtual bool process( FaceSet * faceSet );

  /** Applies \e self to an object of type of Frustum.
    \warning
      - \e frustum must be non null and valid. */
  virtual bool process( Frustum * frustum );

  /** Applies \e self to an object of type of Extrusion.
    \warning
      - \e extrusion must be non null and valid. */
  virtual bool process( Extrusion * extrusion );

  /** Applies \e self to an object of type of Group.
    \warning
      - \e group must be non null and valid. */
  virtual bool process( Group * group );

  /** Applies \e self to an object of type of NurbsCurve.
    \warning
      - \e nurbsCurve must be non null and valid. */
  virtual bool process( NurbsCurve * nurbsCurve );

  /** Applies \e self to an object of type of NurbsPatch.
    \warning
      - \e nurbsPatch must be non null and valid. */
  virtual bool process( NurbsPatch * nurbsPatch );

  /** Applies \e self to an object of type of Oriented.
    \warning
      - \e oriented must be non null and valid. */
  virtual bool process( Oriented * oriented );

  /** Applies \e self to an object of type of Paraboloid.
    \warning
      - \e paraboloid must be non null and valid. */
  virtual bool process( Paraboloid * paraboloid );

  /** Applies \e self to an object of type of PointSet.
    \warning
      - \e pointSet must be non null and valid. */
  virtual bool process( PointSet * pointSet );

  /** Applies \e self to an object of type of Polyline.
    \warning
      - \e polyline must be non null and valid. */
  virtual bool process( Polyline * polyline );

  /** Applies \e self to an object of type of QuadSet.
    \warning
      - \e quadSet must be non null and valid. */
  virtual bool process( QuadSet * quadSet );

  /** Applies \e self to an object of type of Revolution.
    \warning
      - \e revolution must be non null and valid. */
  virtual bool process( Revolution * revolution );

  /** Applies \e self to an object of type of Scaled.
    \warning
      - \e scaled must be non null and valid. */
  virtual bool process( Scaled * scaled );

  /** Applies \e self to an object of type of ScreenProjected.
    \warning
      - \e scaled must be non null and valid. */
  virtual bool process( ScreenProjected * scp );

  /** Applies \e self to an object of type of Sphere.
    \warning
      - \e sphere must be non null and valid. */
  virtual bool process( Sphere * sphere );

  /** Applies \e self to an object of type of Tapered.
    \warning
      - \e tapered must be non null and valid. */
  virtual bool process( Tapered * tapered );

  /** Applies \e self to an object of type of Translated.
    \warning
      - \e translated must be non null and valid. */
  virtual bool process( Translated * translated );

  /** Applies \e self to an object of type of TriangleSet.
    \warning
      - \e triangleSet must be non null and valid. */
  virtual bool process( TriangleSet * triangleSet );

  //@}

  /// @name Geom2D
  //@{

  /** Applies \e self to an object of type of BezierCurve2D.
    \warning
      - \e bezierCurve must be non null and valid. */
  virtual bool process( BezierCurve2D * bezierCurve );

  /** Applies \e self to an object of type of Disc.
    \warning
      - \e disc must be non null and valid. */
  virtual bool process( Disc * disc );

  /** Applies \e self to an object of type of NurbsCurve2D.
    \warning
      - \e nurbsCurve must be non null and valid. */
  virtual bool process( NurbsCurve2D * nurbsCurve );

  /** Applies \e self to an object of type of PointSet2D.
    \warning
      - \e pointSet must be non null and valid. */
  virtual bool process( PointSet2D * pointSet );

  /** Applies \e self to an object of type of Polyline2D.
    \warning
      - \e polyline must be non null and valid. */
  virtual bool process( Polyline2D * polyline );

  //@}

  virtual bool process( Text * text );

  virtual bool process( Font * font );

  /** Applies \e self to an object of type of ScenePtr.
    \warning
      - \e scene must be non null and valid. */
  virtual bool process(ScenePtr scene, const char * comment);

  /// Print the scene \e scene in the file \e filename in ply format.
  static bool print(ScenePtr scene,std::string filename,const char * comment = NULL, ply_format format = ply_ascii );

  /// Print the scene \e scene in the file \e filename in ply format.
  static bool print(ScenePtr scene,Discretizer & discretizer,
                    std::string filename,const char * comment = NULL, ply_format format = ply_ascii);

protected :

  /// Discretizer.
  Discretizer& __discretizer;

  /// contains the current pass in the scene.
  int __pass;

  /// number of vertex in the scene.
  uint_t __vertex;

  /// number of face in the scene.
  uint_t __face;

  /// current red color.
  int __red;

  /// current green color.
  int __green;

  /// current blue color.
  int __blue;

  /// index of point.
  uint_t __index;


};


/* ----------------------------------------------------------------------- */

/**
  \class PlyBinaryPrinter
  \brief An action to write GEOM object in Ply Binary Format.
*/

class CODEC_API PlyBinaryPrinter : public PlyPrinter
{

public :

  /// Constructor.
  PlyBinaryPrinter( TOOLS(bofstream)& stream ,
                    Discretizer& discretizer ,
                    ply_format format = ply_binary_little_endian );

  /// Destructor.
  virtual ~PlyBinaryPrinter();


  /// Add comment in the header of the outpu file.
  virtual bool header(const char * comment = NULL);

  /// Return whether the output is in binary format or not.
  virtual bool isBinary() const {
    return true;
  }

  /// Return whether the output is in ascii format or not.
  virtual bool isAscii() const {
    return false;
  }

  /// Return whether the output is in binary little endian format or not.
  virtual bool isLittleEndian() const {
    return (__format == ply_binary_little_endian);
  }

  /// Return whether the output is in binary big endian format or not.
  virtual bool isBigEndian() const {
    return (__format == ply_binary_big_endian);
  }


  /** Applies \e self to an object of type of AmapSymbol.
    \warning
      - \e amapSymbol must be non null and valid. */
  virtual bool process( AmapSymbol * amapSymbol );

  /** Applies \e self to an object of type of FaceSet.
    \warning
      - \e faceSet must be non null and valid. */
  virtual bool process( FaceSet * faceSet );

  /** Applies \e self to an object of type of QuadSet.
    \warning
      - \e quadSet must be non null and valid. */
  virtual bool process( QuadSet * quadSet );

  /** Applies \e self to an object of type of TriangleSet.
    \warning
      - \e triangleSet must be non null and valid. */
  virtual bool process( TriangleSet * triangleSet );

  /** Applies \e self to an object of type of ScenePtr.
    \warning
      - \e scene must be non null and valid. */
  virtual bool process(ScenePtr scene, const char * comment);

protected :

  /// Output stream.
  TOOLS(bofstream)& stream;

  /// Format of the output.
  ply_format __format;

};


/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
// __actn_plyprinter_h__
#endif


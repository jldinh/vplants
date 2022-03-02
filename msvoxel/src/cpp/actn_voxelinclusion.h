/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s):  O. Puech (puech.olivier@orange.fr)
 *
 *       $Source$
 *       $Id: actn_voxelinclusion.h 3268 2007-06-06 16:44:27Z dufourko $
 *
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

/** 
   
   This file is a copy of actn_voxel_intersection

   This action takes a geometric object and detects if the center of the voxel 
   is inside the geometric surface.
 
   The voxel to be tested needs to be set in the action object before the test.

   WARNING: by default (because of the copy of the code), actions are those 
   of actn_voxel_intersection, which means that true is returned if
   the voxel intersects the geometric object.

   Actions have until now only been implemented on boxes.
 

   This should contain in a near future actions for computing 
   voxels inside a closed geometric surface
*/


/*! \file actn_voxelinclusion.h
    \brief Algorithm of Voxel Intersection with GEOM object. see VoxelInclusion.
*/


#ifndef __actn_voxelinclusion_h__
#define __actn_voxelinclusion_h__

/* ----------------------------------------------------------------------- */
#include "tool/config.h"
#include "plantgl/scenegraph/scene/scene.h"
#include "plantgl/scenegraph/core/action.h"
#include "plantgl/algo/base/bboxcomputer.h"
#include "plantgl/algo/grid/voxel.h"

#include "plantgl/pgl_math.h"

/* ----------------------------------------------------------------------- */


PGL_USING_NAMESPACE
//PGL_BEGIN_NAMESPACE


/* ----------------------------------------------------------------------- */

/**
    \class VoxelInclusion
    \brief Compute intersection beetwen a Voxel and a GEOM object.
*/

/* ----------------------------------------------------------------------- */

class GEOM_API VoxelInclusion : public Action {


    public :

    /// Default constructor.
    VoxelInclusion(BBoxComputer& bboxcomputer);

    /// Destructor
    virtual ~VoxelInclusion();

    /// set the Voxel to test to \e voxel.
    void setVoxel(Voxel * voxel);


    /// Returns the BBoxComputer attached to \e self.
    BBoxComputer& getBBoxComputer( ) {
        return __bboxComputer;
    }

   /// Return whether the voxel is filled by last GEOM object examined.
    bool isFilled() const{
        return __filled;
    }

    /** Applies \e self to an object of type of Shape.
        \warning
        - \e geomShape must be non null and valid. */
    virtual bool process(Shape * geomshape);

    /** Applies \e self to an object of type of Inline.
        \warning
       - \e inline must be non null and valid. */
    virtual bool process(Inline * geominline);

    /// @name Geom3D
    //@{


   virtual bool process( AmapSymbol * amapSymbol );

   virtual bool process( AsymmetricHull * asymmetricHull );

   virtual bool process( AxisRotated * axisRotated );

   virtual bool process( BezierCurve * bezierCurve );

   virtual bool process( BezierPatch * bezierPatch );

   virtual bool process( Box * box ); // only method implemented up to now

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

   virtual bool process( Scaled * scaled );

   virtual bool process( Sphere * sphere );

   virtual bool process( Swung * swung );

   virtual bool process( Tapered * tapered );

   virtual bool process( Translated * translated );

   virtual bool process( TriangleSet * triangleSet );

   //@}
   /// @name Appearance
   //@{

   virtual bool process( Material * material ) {
       GEOM_ASSERT(material);
     // nothing to do.
     __filled = false;
     return false;
   }

   virtual bool process( ImageTexture * texture ) {
       GEOM_ASSERT(texture);
     // nothing to do.
     __filled = false;
     return false;
   }

   virtual bool process( MonoSpectral * monoSpectral ) {
       GEOM_ASSERT(monoSpectral);
     // nothing to do.
     __filled = false;
     return false;
   }

   virtual bool process( MultiSpectral * multiSpectral ) {
     GEOM_ASSERT(multiSpectral);
     // nothing to do.
     __filled = false;
     return false;
   }

   //@}
   /// @name Geom2D
   //@{


   virtual bool process( BezierCurve2D * bezierCurve );

   virtual bool process( Disc * disc );

   virtual bool process( NurbsCurve2D * nurbsCurve );

   virtual bool process( PointSet2D * pointSet );

   virtual bool process( Polyline2D * polyline );


   //@}

   virtual bool process( Text * text ){
       GEOM_ASSERT(text);
     // nothing to do.
     __filled = false;
     return false;
   }

   virtual bool process( Font * font ){
       GEOM_ASSERT(font);
     // nothing to do.
     __filled = false;
     return false;
   }

   // virtual bool process(ScenePtr& scene);

 protected:

   /// The result : is __voxel is filled by last GEOM object examined.
   bool __filled;

   /// The octree in which we insert the GEOM objetcs.
   Voxel * __voxel;

   /** A BBoxComputer is used to compute the bounding box of objects and compute a first
       value of intersection. */
   BBoxComputer& __bboxComputer;


   /// Stack of succesive transformation.
   std::vector<TOOLS(Matrix4)> __transformstack;

};

/* ----------------------------------------------------------------------- */

//PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif
/* ----------------------------------------------------------------------- */

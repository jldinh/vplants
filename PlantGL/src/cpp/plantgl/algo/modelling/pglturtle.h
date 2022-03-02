/* ---------------------------------------------------------------------------
 *
 *       PlantGL: Modeling Plant Geometry
 *
 *       Copyright 2000-2006 - Cirad/Inria/Inra - Virtual Plant Team
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr) et al.
 *
 *       Development site : https://gforge.inria.fr/projects/openalea/
 *
 # ---------------------------------------------------------------------------
 #
 #                      GNU General Public Licence
 #
 #       This program is free software; you can redistribute it and/or
 #       modify it under the terms of the GNU General Public License as
 #       published by the Free Software Foundation; either version 2 of
 #       the License, or (at your option) any later version.
 #
 #       This program is distributed in the hope that it will be useful,
 #       but WITHOUT ANY WARRANTY; without even the implied warranty of
 #       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 #       GNU General Public License for more details.
 #
 #       You should have received a copy of the GNU General Public
 #       License along with this program; see the file COPYING. If not,
 #       write to the Free Software Foundation, Inc., 59
 #       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 #
 # ---------------------------------------------------------------------------
 */

#ifndef __PGL_TURTLE_GEOM_H__
#define __PGL_TURTLE_GEOM_H__

#include "turtle.h"

#include <plantgl/scenegraph/geometry/geometry.h>
#include <plantgl/scenegraph/geometry/polyline.h>
#include <plantgl/scenegraph/appearance/material.h>
#include <plantgl/scenegraph/scene/scene.h>
#include <plantgl/tool/util_hashmap.h>


PGL_BEGIN_NAMESPACE

class ALGO_API PglTurtle : public Turtle {
public:
    // static Polyline2DPtr DEFAULT_CROSS_SECTION;
	static AppearancePtr HEADING_FRAME_MATERIAL;
	static AppearancePtr UP_FRAME_MATERIAL;
	static AppearancePtr LEFT_FRAME_MATERIAL;
	static GeometryPtr DEFAULT_SPHERE;

    typedef pgl_hash_map_string<GeometryPtr> SurfaceMap;

    PglTurtle(TurtleParam * param = NULL);

    virtual ~PglTurtle();

    virtual void reset();
    
    void clear();

	ScenePtr partialView();
    
    virtual void interpolateColors(int val1, int val2, real_t alpha = 0.5);

    void clearColorList();
    
    const std::vector<AppearancePtr>& getColorList() const;
    
    void setColorList(const std::vector<AppearancePtr>&);
    
    void clearSurfaceList();
    
    const SurfaceMap& getSurfaceList() const;
    
    void defaultValue();
        
    const ScenePtr& getScene() const
	{ return __scene;  }
    
    size_t getColorListSize() const
	{ return __appList.size(); }

    void appendMaterial(const AppearancePtr& mat);
    
    void setMaterial(size_t pos, const AppearancePtr& mat);

    void insertMaterial(size_t pos, const AppearancePtr& mat);

    inline void appendMaterial(const ImageTexturePtr& mat)
	{ appendMaterial(AppearancePtr(new Texture2D(mat))); }
    
    void setMaterial(size_t pos, const ImageTexturePtr& mat)
	{ setMaterial(pos,AppearancePtr(new Texture2D(mat))); }

    void insertMaterial(size_t pos, const ImageTexturePtr& mat)
	{ insertMaterial(pos,AppearancePtr(new Texture2D(mat))); }

    AppearancePtr getMaterial(size_t pos);

    void appendColor(uint_t red, uint_t green, uint_t blue);

    void appendColor(float red, float green, float blue);

    void appendColor(const Color3& mat);
    
    void setColorAt(size_t pos, uint_t red, uint_t green, uint_t blue );

    void setColorAt(size_t pos, float red, float green, float blue );

    void setColorAt(size_t pos, const Color3& mat);

    void removeColor(size_t pos);
    
    void setSurface(const std::string& name, const GeometryPtr& surf)
    {  __surfList[name] = surf; } 
    
    void removeSurface(const std::string& name);

    GeometryPtr getSurface(const std::string& name);

    void customGeometry(const GeometryPtr smb, real_t scale = 1.0);

protected:

    AppearancePtr getCurrentMaterial() const;
    AppearancePtr getCurrentInitialMaterial() const;

    GeometryPtr getCircle(real_t radius) const;

    GeometryPtr transform(const GeometryPtr& obj, bool scaled = true) const;

    virtual void _addToScene(const GeometryPtr geom, bool customid = false, AppearancePtr app = NULL);

	/// draw a frustum of length = length, bottom diameter = current width and top diameter = topdiam
    virtual void _frustum(real_t length,real_t topdiam);
        
	/// draw a cylinder of length = length, diameter = current width
    virtual void _cylinder(real_t length);

	/// draw the polygon with current polygon points
    virtual void _polygon(const Point3ArrayPtr& points, bool concavetest = false);
    
    virtual void _generalizedCylinder(const Point3ArrayPtr& points,
									  const std::vector<TOOLS(Vector3)>& left,
                                      const std::vector<real_t>& radius,
									  const Curve2DPtr& crossSection,
									  bool crossSectionCCW,
									  bool currentcolor = false);

    virtual void _sphere(real_t radius);
        
    /// draw a circle in yz plane of radius = radius (default : current width) 
    virtual void _circle(real_t radius);
    
    virtual void _box(real_t radius, real_t botradius, real_t topradius);

    virtual void _quad(real_t radius, real_t botradius, real_t topradius);

    /// draw the surface identified by name, scaled by a factor scale
    virtual void _surface(const std::string& name,real_t scale);

    virtual void _label(const std::string& text , int size = -1);
 
	virtual void _frame(real_t heigth, real_t cap_heigth_ratio, real_t cap_radius_ratio, real_t color, real_t transparency);

	SurfaceMap __surfList;
    std::vector<AppearancePtr> __appList;

	ScenePtr __scene;
};

/* ----------------------------------------------------------------------- */

PGL_END_NAMESPACE

/* ----------------------------------------------------------------------- */
#endif

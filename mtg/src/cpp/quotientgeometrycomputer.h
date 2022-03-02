/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 *
 *       $Source$
 *       $Id: quotientgeometrycomputer.h 15687 2014-02-05 10:15:41Z gbaty $
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



#ifndef _quotient_geometry_computer_
#define _quotient_geometry_computer_

#include "plantgl/pgl_scene.h"
#include "plantgl/pgl_container.h"

// OLD INCLUDE
//#include "GEOM/scne_scene.h"
//#include "GEOM/scne_shape.h"
//#include "GEOM/geom_pointarray.h"


#include "tool/util_hashmap.h"

#include "aml/fnode.h"
#include "linetree.h"

#include "plant.h"
#include "aml/array.h"


PGL_BEGIN_NAMESPACE
class Discretizer;
PGL_END_NAMESPACE


/* ----------------------------------------------------------------------- */

/// A structure that store info for each macro vertex.
class MacroVtxInfo {


public :

  /// The geometric class name.
  std::string _geomclassname;

  /// The appearance.
  std::string _appearance;

  /// A point list.
  Point3ArrayPtr _points;

  /// A point list.
  Point2ArrayPtr _radius;

  /// Store if radius are needed.
  bool _need;

  /// Reuse shape.
  ScenePtr _reuseshapes;

  /// father of the vertex if known
  int _father;

  /// Set the geometric class name.
  void setClassName(const std::string& name);

  /// Return whether radius are needed.
  const bool areRadiusNeeded() const{
    return _need;
  }

  /// set the need in radius to \e b.
  void setRadiusNeed(bool b){
    _need = b;
  }

  /// Set the Appearance.
  void setAppearance(const std::string& name);

  /// Add a \e point to the list.
  void addPoint(TOOLS(Vector3) point);
  
  /// Add a \e point list to the list.
  void addPoints(PGL(Point3ArrayPtr) points);

  /// Add a \e point and scale to the list.
  void addInfo(TOOLS(Vector3) point,real_t radius);

  /// Add a \e shape to the list.
  void addInfo(ShapePtr sh);

  // Return whether some shapes are already computed.
  bool hasShapeComputed() const {
    return (_reuseshapes);
  }

  /// Return the shapes.
  const ScenePtr& getShapes() const{
    return _reuseshapes;
  }

  /// Constructor.
  MacroVtxInfo();
  
  /// Constructor with a name and a point.
  MacroVtxInfo(const std::string& name,const std::string& appearance);

  /// Constructor with a name and a point.
  MacroVtxInfo(const std::string& name,const std::string& appearance, const TOOLS(Vector3) point);
  
  /// Constructor with a name and a point.
  MacroVtxInfo(const std::string& name,const std::string& appearance, const PGL(Point3ArrayPtr) points);
  
  /// Constructor with a name and a point.
  MacroVtxInfo(const std::string& name,const std::string& appearance, const TOOLS(Vector3) point, const real_t radius);

  /// Constructor with a name and a point.
  MacroVtxInfo(const std::string& name, ShapePtr sh);

  /// Destructor.
  ~MacroVtxInfo();

};

/// A structure that store info for all macro vertex.
typedef tool_hash_map< int , MacroVtxInfo> MacroInfoList;





/* ----------------------------------------------------------------------- */

/**

   \class QuotientGeometryComputer
   \brief Contains informations for computing macroscopic geometry of the plant.
   The macroscopic geometry is computed at an existing scale (if _quotient_scale
   is given) or a computed scale (if _quotient_fun is given).
*/

class QuotientGeometryComputer {


  public:

    /// Default Constructor.
    QuotientGeometryComputer(LineTree * lt);
    
    /// Constructor with a quotient function.
    QuotientGeometryComputer(LineTree * lt,
			     FNode* quotient_fun,
			     FNode* quotient_geometry_fun, 
			     FNode* quotient_appearance_fun,
				 FNode* consider_fun = 0);

    /// Constructor with a quotient function.
    QuotientGeometryComputer(LineTree * lt,
			     FNode* quotient_fun,
				 const std::string& quotient_geometry_name, 
			     FNode* quotient_appearance_fun,
				 FNode* consider_fun = 0);

    /// Constructor with a scale.
    QuotientGeometryComputer(LineTree * lt,
			     int quotient_scale, 
			     FNode* quotient_geometry_fun, 
			     FNode* quotient_appearance_fun,
				 FNode* consider_fun = 0);
    
    /// Constructor with a scale.
    QuotientGeometryComputer(LineTree * lt,
			     int quotient_scale, 
			     const std::string& quotient_geometry_name, 
			     FNode* quotient_appearance_fun,
				 FNode* consider_fun = 0);
    
    /// Destructor.
    ~QuotientGeometryComputer();
    
    /// To re-affect a quotient information with a quotient scale. 
    void setQuotientGeometryComputer(int quotient_scale, 
				     FNode* quotient_geometry_fun, 
				     FNode* quotient_appearance_fun,
					 FNode* consider_fun = 0);
    
    void setQuotientGeometryComputer(int quotient_scale, 
			         const std::string& quotient_geometry_name, 
				     FNode* quotient_appearance_fun,
					 FNode* consider_fun = 0);
    
    /// To re-affect a quotient information with a quotient function. 
    void setQuotientGeometryComputer(FNode* quotient_fun, 
				     FNode* quotient_geometry_fun, 
				     FNode* quotient_appearance_fun,
					 FNode* consider_fun = 0);
  
    /// To re-affect a quotient information with a quotient function. 
    void setQuotientGeometryComputer(FNode* quotient_fun, 
			         const std::string& quotient_geometry_name, 
				     FNode* quotient_appearance_fun,
					 FNode* consider_fun = 0);

    /// Set the QuotientScale Value.
    void  setQuotientScale(int quotient_scale);

    /// Set the QuotientFun Value.
    void setQuotientFun(FNode* quotient_fun);
    
    /// Set the QuotientGeometryFun Value.
    void setQuotientGeometryFun(FNode* quotient_geometry_fun);

    /// Set the QuotientGeometryFun Value.
    void setQuotientGeometryName(const std::string& quotient_geometry_name);

    /// Set the QuotientAppearanceFun Value.
    void setQuotientAppearanceFun(FNode* quotient_appearance_fun);
  
    /// Set the Consider Function Value.
    void setConsiderFun(FNode* consider);
  
    /// Set the ViewMode Value.
    void  setViewMode(int viewMode);

    /// Get the QuotientScale Value.
    const int getQuotientScale() const ;

    /// Get the QuotientFun Value.
    FNode* getQuotientFun() const;
    
    /// Get the QuotientGeometryFun Value.
    FNode* getQuotientGeometryFun() const;

    /// Get the QuotientGeometryName Value.
    const std::string& getQuotientGeometryName() const;

    /// Get the QuotientAppearanceFun Value.
    FNode* getQuotientAppearanceFun() const;
  
    /// Get the Consider Function Value.
    FNode* getConsiderFun() const;
  
   /// get the ViewMode Value.
    const int getViewMode() const;
 
    /// Compute the macroscopic geometry on a plantframe.
    bool computeGeometry(const PlantFrame*);
    bool recomputeGeometry(const PlantFrame*);

    /// Compute the macroscopic geometry on a plantframe.
    bool compressGeometry( const PlantFrame* _pf,
						   real_t& rate,
						   real_t& time,
						   real_t& ftime,
						   int sorttype = 0);

    /// return true if a geometry has been computed.
    bool isSceneEmpty() const;

    /// Get the computed scene.
    const ScenePtr & getScene() const;

    bool computeMacroGeometry(const PlantFrame* _pf);

    /// Compute a simple quotiented graph.
    SLArray* computeQuotientedGraph(const PlantFrame* _pf);

  private:

	bool consider(VId vtx) const;

    /// Compute Macro Info using a macro scale.
    MacroInfoList * computeMacroInfo( const PlantFrame* _pf);

    /// Compute quotient Info using quotient function.
    MacroInfoList * computeQuotientInfo( const PlantFrame* _pf);

    /// Compute quotient Info using quotient function.
//    MacroInfoList computeQuotientInfo2( const PlantFrame* _pf);

    /// Return the root of the computed complex of \e vertex.
    VId quotient_complex(VId vertex,const MTG* _mtg);

    // Information for computing macroscopic geometry of the plant is stored
    // here:

    /// The existing scale to compute the geometry for.
    int _quotient_scale;

    /// A function for computing the macroscopic scale.
    FNode* _quotient_fun;

    /*! The Quotient Geometry Function.
      This Function associate each vertex of the macroscopic scale
      with a Geometric class name.
    */
    FNode* _quotient_geometry_fun;
	std::string _quotient_geometry_name;

    /*! The Quotient Appearance Function.
      This Function associate each vertex of the macroscopic scale
      with an Appearance object.
    */
    FNode* _quotient_appearance_fun;

    FNode* _consider_fun;

    /// ViewMode of the Linetree : 0 All, 1 Micro Geom Only, 2 Macro Geom Only
    int _view_mode;

    /// The resulting computed geometry.
    ScenePtr _scene;

  /// The linetree.
  LineTree * _lt;

  MacroInfoList * __cache;

	void addInfoTo(MacroVtxInfo& m,
				   VId vtx,
				   const PlantFrame* _pf,
				   PGL(Discretizer) & discretizer);
	void createInfoTo(MacroInfoList& macroinfos,
					  VId vtx,
					  VId father,
					  const PlantFrame* _pf,
					  PGL(Discretizer) & discretizer);
};


#endif // _quotient_geometry_computer_

/* ----------------------------------------------------------------------- */

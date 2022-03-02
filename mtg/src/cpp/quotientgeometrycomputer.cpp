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
 *       $Id: quotientgeometrycomputer.cpp 15687 2014-02-05 10:15:41Z gbaty $
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



#include "plantframe.h"
#include "dressingfile.h"
#include "quotientgeometrycomputer.h"

// OLD INCLUDES
//#include "GEOM/geom.h"
//#include "Geomext/actn_fit.h"
//#include "Geomext/branchcompressor.h"
#include "plantgl/pgl_algo.h"
#include "plantgl/algo/fitting/branchcompressor.h"
#include "plantgl/scenegraph/core/smbtable.h"

#include "plantgl/tool/util_string.h"

TOOLS_USING_NAMESPACE
using namespace std;
STDEXT_USING_NAMESPACE

/* ----------------------------------------------------------------------- */


MacroVtxInfo::MacroVtxInfo() :
    _points(0),
    _radius(0),
    _need(false),
    _reuseshapes(0),
    _father(Shape::NOID){
}

MacroVtxInfo::MacroVtxInfo(const string& name,
						   const string& appearance) :
    _geomclassname(name),
    _appearance(appearance),
    _points(new Point3Array),
    _radius(0),
    _need(false),
    _reuseshapes(0),
    _father(Shape::NOID){
}

MacroVtxInfo::MacroVtxInfo(const string& name,
			   const string& appearance,
			   const Vector3 point) :
    _geomclassname(name),
    _appearance(appearance),
    _points(new Point3Array(1)),
    _radius(0),
    _need(false),
    _reuseshapes(0),
    _father(Shape::NOID){
    _points->setAt(0,point);
}

MacroVtxInfo::MacroVtxInfo(const string& name,
			   const string& appearance, 
			   const PGL(Point3ArrayPtr) points) :
    _geomclassname(name),
    _appearance(appearance),
    _points(new Point3Array(*points)),
    _radius(0),
    _need(false),
    _reuseshapes(0),
    _father(Shape::NOID){
}

MacroVtxInfo::MacroVtxInfo(const string& name,
			   const string& appearance,
			   const Vector3 point, 
			   const real_t radius) :
    _geomclassname(name),
    _appearance(appearance),
    _points(new Point3Array(1)),
    _radius(new Point2Array(1)),
    _need(true),
    _reuseshapes(0),
    _father(Shape::NOID){
    _points->setAt(0,point);
    _radius->setAt(0,Vector2(radius,radius));
}

MacroVtxInfo::MacroVtxInfo(const string& name,
			   ShapePtr sh) :
    _geomclassname(name),
    _points(0),
    _radius(0),
    _need(false),
    _reuseshapes(new Scene()),
    _father(Shape::NOID){
  _reuseshapes->add(Shape3DPtr(sh));
}

MacroVtxInfo::~MacroVtxInfo(){
}


void MacroVtxInfo::setClassName(const string& name){
    _geomclassname = name;
}


void MacroVtxInfo::setAppearance(const string& name){
    _appearance = name;
}


void MacroVtxInfo::addPoint(Vector3 point){
    _points->pushBack(point);
}

void MacroVtxInfo::addPoints(PGL(Point3ArrayPtr) points){
    if(points)_points->insert(_points->getEnd(),
							  points->getBegin(),
							  points->getEnd());
}


void MacroVtxInfo::addInfo(Vector3 point,real_t radius){
    _points->pushBack(point);
    _radius->pushBack(Vector2(radius,radius));
}

void MacroVtxInfo::addInfo(ShapePtr sh){
  if(!_reuseshapes)_reuseshapes = ScenePtr(new Scene());
  _reuseshapes->add(Shape3DPtr(sh));
}
/* ----------------------------------------------------------------------- */


QuotientGeometryComputer::QuotientGeometryComputer(LineTree * lt) :
    _quotient_scale(-1),
    _quotient_fun(0),
    _quotient_geometry_fun(0),
    _quotient_appearance_fun(0),
	_consider_fun(0),
    _view_mode(0),
    _scene(new Scene()),
    _lt(lt),
	__cache(0){
}

QuotientGeometryComputer::QuotientGeometryComputer(LineTree * lt,
												   FNode* quotient_fun,
												   FNode* quotient_geometry_fun, 
												   FNode* quotient_appearance_fun,
												   FNode* consider_fun):
    _quotient_scale(-1),
    _quotient_fun(quotient_fun),
    _quotient_geometry_fun(quotient_geometry_fun),
    _quotient_appearance_fun(quotient_appearance_fun),
	_consider_fun(consider_fun),
    _view_mode(0),
    _scene(new Scene()),
    _lt(lt),
	__cache(0){
}

QuotientGeometryComputer::QuotientGeometryComputer(LineTree * lt,
												   FNode* quotient_fun,
												   const string& quotient_geometry_name, 
												   FNode* quotient_appearance_fun,
												   FNode* consider_fun):
    _quotient_scale(-1),
    _quotient_fun(quotient_fun),
    _quotient_geometry_fun(0),
    _quotient_geometry_name(quotient_geometry_name),
    _quotient_appearance_fun(quotient_appearance_fun),
	_consider_fun(consider_fun),
    _view_mode(0),
    _scene(new Scene()),
    _lt(lt),
	__cache(0){
}

QuotientGeometryComputer::QuotientGeometryComputer(LineTree * lt,
												   int quotient_scale, 
												   FNode* quotient_geometry_fun, 
												   FNode* quotient_appearance_fun,
												   FNode* consider_fun):
    _quotient_scale(quotient_scale),
    _quotient_fun(0),
    _quotient_geometry_fun(quotient_geometry_fun),
    _quotient_appearance_fun(quotient_appearance_fun),
	_consider_fun(consider_fun),
    _view_mode(0),
    _scene(new Scene()),
    _lt(lt),
	__cache(0){
}

QuotientGeometryComputer::QuotientGeometryComputer(LineTree * lt,
												   int quotient_scale, 
												   const string& quotient_geometry_name, 
												   FNode* quotient_appearance_fun,
												   FNode* consider_fun):
    _quotient_scale(quotient_scale),
    _quotient_fun(0),
    _quotient_geometry_fun(0),
    _quotient_geometry_name(quotient_geometry_name),
    _quotient_appearance_fun(quotient_appearance_fun),
	_consider_fun(consider_fun),
    _view_mode(0),
    _scene(new Scene()),
    _lt(lt),
	__cache(0){
}


QuotientGeometryComputer::~QuotientGeometryComputer(){
	if(__cache){
	  delete __cache;
	  __cache = NULL;
	}
    // The FNode will be delete by the symbol table.
}

/* ----------------------------------------------------------------------- */

void QuotientGeometryComputer::setQuotientGeometryComputer(int quotient_scale, 
														   FNode* quotient_geometry_fun, 
														   FNode* quotient_appearance_fun,
														   FNode* consider_fun){
    _quotient_scale = quotient_scale;
    _quotient_fun = NULL;
    _quotient_geometry_fun = quotient_geometry_fun;
    _quotient_geometry_name = string();
    _quotient_appearance_fun = quotient_appearance_fun;
	_consider_fun = consider_fun;
    _view_mode=0;
	if(__cache)delete __cache;
	__cache = NULL;
}

void QuotientGeometryComputer::setQuotientGeometryComputer(int quotient_scale, 
														   const string& quotient_geometry_name, 
														   FNode* quotient_appearance_fun,
														   FNode* consider_fun){
    _quotient_scale = quotient_scale;
    _quotient_fun = NULL;
    _quotient_geometry_fun = NULL;
    _quotient_geometry_name = quotient_geometry_name;
    _quotient_appearance_fun = quotient_appearance_fun;
	_consider_fun = consider_fun;
    _view_mode=0;
	if(__cache)delete __cache;
	__cache = NULL;
}



void QuotientGeometryComputer::setQuotientGeometryComputer(FNode* quotient_fun,
														   FNode* quotient_geometry_fun, 
														   FNode* quotient_appearance_fun,
														   FNode* consider_fun){
    _quotient_scale = -1;
    _quotient_fun = quotient_fun;
    _quotient_geometry_fun = quotient_geometry_fun;
    _quotient_geometry_name = string();
    _quotient_appearance_fun = quotient_appearance_fun;
	_consider_fun = consider_fun;
    _view_mode=0;
	if(__cache)delete __cache;
	__cache = NULL;
}


void QuotientGeometryComputer::setQuotientGeometryComputer(FNode* quotient_fun,
														   const string& quotient_geometry_name, 
														   FNode* quotient_appearance_fun,
														   FNode* consider_fun){
    _quotient_scale = -1;
    _quotient_fun = quotient_fun;
    _quotient_geometry_fun = NULL;
    _quotient_geometry_name = quotient_geometry_name;
    _quotient_appearance_fun = quotient_appearance_fun;
	_consider_fun = consider_fun;
    _view_mode=0;
	if(__cache)delete __cache;
	__cache = NULL;
}


void QuotientGeometryComputer::setQuotientScale(int quotient_scale) {
    _quotient_scale = quotient_scale;
    _quotient_fun = NULL;
	if(__cache)delete __cache;
	__cache = NULL;
}


void QuotientGeometryComputer::setQuotientFun(FNode* quotient_fun) {
    _quotient_scale = -1;
    _quotient_fun = quotient_fun;
	if(__cache)delete __cache;
	__cache = NULL;
}


void QuotientGeometryComputer::setQuotientGeometryFun(FNode* quotient_geometry_fun){
    _quotient_geometry_fun = quotient_geometry_fun;
    _quotient_geometry_name = string();
}

void QuotientGeometryComputer::setQuotientGeometryName(const string& quotient_geometry_name){
    _quotient_geometry_fun = NULL;
    _quotient_geometry_name = quotient_geometry_name;
}



void QuotientGeometryComputer::setQuotientAppearanceFun(FNode* quotient_appearance_fun){
    _quotient_appearance_fun = quotient_appearance_fun;
}

void QuotientGeometryComputer::setConsiderFun(FNode* consider_fun){
	_consider_fun = consider_fun;
	if(__cache)delete __cache;
	__cache = NULL;
}

void  QuotientGeometryComputer::setViewMode(int viewMode){
    _view_mode=viewMode;
}

/* ----------------------------------------------------------------------- */


const int QuotientGeometryComputer::getQuotientScale() const{
    return  _quotient_scale;
}

FNode* QuotientGeometryComputer::getQuotientFun() const{
    return _quotient_fun;
}

FNode* QuotientGeometryComputer::getQuotientGeometryFun() const{
    return _quotient_geometry_fun;
}

const string& QuotientGeometryComputer::getQuotientGeometryName() const{
    return _quotient_geometry_name;
}

FNode* QuotientGeometryComputer::getQuotientAppearanceFun() const{
    return _quotient_appearance_fun;
}

FNode* QuotientGeometryComputer::getConsiderFun() const{
    return _consider_fun;
}

const int QuotientGeometryComputer::getViewMode() const{
    return _view_mode;
}

/* ----------------------------------------------------------------------- */


const ScenePtr & QuotientGeometryComputer::getScene() const{
    return _scene;
}

bool QuotientGeometryComputer::isSceneEmpty() const{
    return _scene->isEmpty();
}


/* ----------------------------------------------------------------------- */

bool QuotientGeometryComputer::consider(VId vtx) const{
  if(_consider_fun == 0) return true;
  else {
	AMObjVector args(1);
	args[0] = AMObj(AMObjType::VTX, vtx);
	AMObj ret = (*_consider_fun)(args);
	if(ret.type() == AMObjType::BOOL)
	  return ret.val.b;
	else if(ret.type() == AMObjType::INTEGER)
	  return ret.val.i != 0;
	else if(ret.type() == AMObjType::REAL)
	  return ret.val.r != 0;
	else cerr << "Error in value of Consider option for vertex " << vtx << '\n';
  }
  return true;
}
/* ----------------------------------------------------------------------- */

bool 
QuotientGeometryComputer::compressGeometry(const PlantFrame* _pf,
										   real_t& rate,
										   real_t& time,
										   real_t& ftime,
										   int sorttype)
{
  cerr << "Collect Geometry" << '\n';
  _scene->clear();
  Plant* p = _pf->_plant;
  IntType nb_branches = p->nbBranches();
  vector<BranchInput> input;
  AppearancePtr appe;
  vector<VId> added_roots;
  tool_hash_set<VId> roots;
  
  for (IntType i=0;i<nb_branches;i++) {	
	const Branch& b = p->findBranch(i); // gets the ith branch of the plant
	const BranchCompoList& compo = b.branchComponents();
	size_t nbb = compo.entries(); // nb of vertices in a branch
	if(_lt->isVirtualElement(compo.at(0).getVertex())){
	  for(size_t j=0;j<nbb;j++) {
		VId vtx = compo.at(j).getVertex(); // jth vertex of branch b
  		ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
		_scene->add(ptr);
	  }
	}
	else {
	  Point3ArrayPtr _points(new Point3Array());
	  Point2ArrayPtr _radius(new Point2Array());
	  BranchInput in;
	  bool newbranch = true;
	  for(size_t j=0;j<nbb;j++) {
		VId vtx = compo.at(j).getVertex(); // jth vertex of branch b
		if(!newbranch){
		  if(_lt && _lt->getScene()){
			ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
			if (ptr && ptr->appearance) newbranch = (in.appearance != ptr->appearance);
			if (newbranch) {
				VId father = p->topoFather(vtx,ANY);
				if(father != -1){
					ValType coord[3];
					_pf->coord3D(father,coord);
					Vector3 pt(coord[0],coord[1],coord[2]);
					if(_points->isEmpty() || _points->getAt(_points->getSize()-1) != pt){
						_points->pushBack(pt);
						real_t radius(_pf->topDia(father)/2);
						Vector2 rad (radius,radius);
						_radius->pushBack(rad);
					}
				}
				added_roots.push_back(vtx);
				BranchInput in2(in);
				in2.points = _points;
				in2.radius = _radius;
				input.push_back(in2);
				_points = Point3ArrayPtr(new Point3Array());
				_radius = Point2ArrayPtr(new Point2Array());
			}
		  }
		}
		if(newbranch){
		  in.id = vtx;
		  VId father = p->topoFather(vtx,ANY);
		  if(father!=-1){
			while (father != -1){
				if(roots.find(father) != roots.end())break;
				father = p->topoFather(father,ANY);
			}
		  }
		  if (father!=-1) in.father = father;
		  else in.father = 0;
		  if(_lt && _lt->getScene()){
			ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
			if(ptr) in.appearance = ptr->appearance;
			else in.appearance = Material::DEFAULT_MATERIAL;
		  }
		  else in.appearance = Material::DEFAULT_MATERIAL;
		  roots.insert(vtx);
		  newbranch = false;
		}
		ValType coord[3];
		_pf->coord3DOrigin(vtx,coord);
		Vector3 pt(coord[0],coord[1],coord[2]);
		if(_points->isEmpty() || _points->getAt(_points->getSize()-1) != pt){
		  _points->pushBack(pt);
		  real_t radius(_pf->botDia(vtx)/2);
		  Vector2 rad(radius,radius);
		  _radius->pushBack(rad);
		}
		if(j == nbb-1){
		  _pf->coord3D(vtx,coord);
		  pt = Vector3(coord[0],coord[1],coord[2]);
		  if(_points->isEmpty() || _points->getAt(_points->getSize()-1) != pt){
			_points->pushBack(pt);
			real_t radius(_pf->topDia(vtx)/2);
			Vector2 rad (radius,radius);
			_radius->pushBack(rad);
		  }
		}
	  }
	  in.points = _points;
	  in.radius = _radius;
	  input.push_back(in);
	}
  }

/*  cerr << "roots = [";
  for (vector<BranchInput>::const_iterator itNode = input.begin(); itNode != input.end(); ++itNode ){
	  if (itNode != input.begin())cerr << ',';
	  cerr << itNode->id;
  }
  cerr << "]" << std::endl;*/
  cerr << "Number of branches : " << input.size()  << '\n';
  cerr << "Compress Geometry" << '\n';
  BranchCompressor b;
  b.setData(input,sorttype);
  _scene->merge(b.compress(rate,&rate,&time,&ftime));
  cerr << "Scene computed" << '\n';
  return (_scene->isValid());
  return false;
}

/* ----------------------------------------------------------------------- */

bool QuotientGeometryComputer::computeGeometry( const PlantFrame* _pf) {

    if(_quotient_scale ==-1 && !_quotient_fun)return false;
    if(_quotient_scale !=-1 )cerr << "PlantFrame computed at scale " << _pf->_plant->getLevel() << '\n';
    if(_quotient_scale !=-1 && _pf->_plant->getLevel() <= _quotient_scale)return false;
	if(__cache){
	  delete __cache;
	  __cache = NULL;
	}
    _scene->clear();
    if(_quotient_scale !=-1)
        cerr << "Compute Macroscopic Geometry at scale " << _quotient_scale << "." << '\n';

     // if(!_quotient_geometry_fun || !_quotient_appearance_fun) return false;

    MacroInfoList * mi =NULL;
    if(_quotient_scale !=-1)mi = computeMacroInfo(_pf);
    else mi = computeQuotientInfo(_pf);

    cerr  << "Collect microscopic Information ... done. [" << (mi!=NULL?mi->size():0) << ']' << '\n';
	__cache = mi;
	if(mi == NULL) return false;
	return computeMacroGeometry(_pf);
}

bool QuotientGeometryComputer::recomputeGeometry( const PlantFrame* _pf) {
	if(__cache == NULL)return computeGeometry(_pf);
	string oldclass,classname,appearance;
	int id;
	AMObjVector args(1);
    _scene->clear();

    for(MacroInfoList::iterator _it = __cache->begin(); 
		_it != __cache->end(); _it++){
	  oldclass = _it->second._geomclassname;
	  id = _it->first;
	  args[0] = AMObj(AMObjType::VTX, id);
	  if(_quotient_geometry_fun){
		AMObj ret = (*_quotient_geometry_fun)(args);
		if(ret.type() == AMObjType::STRING){
		  classname = ((const AMString*)(ret.val.p))->data();
		  if(classname.empty())
			cerr << "Error with function QuotientGeometry for vertex " << id << '\n';
		}
	  }
	  else if(!_quotient_geometry_name.empty()){
		classname = _quotient_geometry_name;
	  }
	  if(toUpper(classname) != toUpper(oldclass)){
		if((toUpper(classname) == "SELF") != _it->second.hasShapeComputed()){
		  cerr << "Must recollect microscopic Information." << '\n';
		  return computeGeometry(_pf);
		}
		if(Fit::areRadiusNeeded(classname) != _it->second.areRadiusNeeded()){
		  cerr << "Must recollect microscopic Information." << '\n';
		  return computeGeometry(_pf);
		}
		_it->second._geomclassname = classname;
	  }
	  if(_quotient_appearance_fun){
		AMObj ret2 = (*_quotient_appearance_fun)(args);
		if(ret2.type() == AMObjType::STRING){
		  appearance = ((const AMString*)(ret2.val.p))->data();
		  _it->second._appearance = appearance;
		}
		else  cerr << "Error with function QuotientAppearance for vertex " << id << '\n';
	  }
	}
	return computeMacroGeometry(_pf);
}


bool QuotientGeometryComputer::computeMacroGeometry(const PlantFrame* _pf) {
    MacroInfoList * mi = __cache;
	if(mi == NULL) return false;
    AppearanceSymbolTable * app = _pf->getDressingFile()->_mat_table;
    AppearanceSymbolTable::iterator _ait;
    AppearancePtr _material(new Material("Default_Transparent",Color3(0,100,0),
                                         Material::DEFAULT_DIFFUSE,
                                         Material::DEFAULT_SPECULAR,
                                         Material::DEFAULT_EMISSION,
                                         Material::DEFAULT_SHININESS,
                                         0.6));

    int nb = 0 ;
    int size = mi->size();
    double prev_ratio = 0.0;
    double ratio = 0.0;
    Fit _action;
    for(MacroInfoList::iterator _it = mi->begin(); _it != mi->end(); _it++){
      if(toUpper(_it->second._geomclassname)=="SELF"){
        if(_it->second.getShapes())_scene->merge(_it->second.getShapes());
      }
      else {
        AppearancePtr the_app;
        _action.setPoints(_it->second._points);
        _action.setRadius(_it->second._radius);
        GeometryPtr _geom = _action.use(_it->second._geomclassname);
        if ((_geom) && (_geom->isValid())){
          if(!_it->second._appearance.empty() && (app)){
            _ait=app->find(_it->second._appearance);
            if(_ait!=app->end())the_app = _ait->second;
            else the_app = _material;
          }
          else the_app = _material;
          _scene->add(ShapePtr(new Shape(_geom,the_app, _it->first,_it->second._father)));
        }
        else {
#ifdef DEBUG
          if(_it->second._points){
            cerr << "Points : [ ";
            for(Point3Array::iterator _it2 = _it->second._points->getBegin();
                _it2 != _it->second._points->getEnd() - 1;
                _it2++)
              cerr << *_it2 << " , ";
            cerr << *(_it->second._points->getEnd() - 1) << " ]" << '\n';
          }
          if(_it->second._radius){
            cerr << "Radius : [ ";
            for(Point2Array::iterator _it2 = _it->second._radius->getBegin();
                _it2 != _it->second._radius->getEnd() - 1;
                _it2++)
              cerr << _it2->x() << " , ";
            cerr << (_it->second._radius->getEnd() - 1)->x() << " ]" << '\n';
          }
          //if(_geom) cerr << *_geom << '\n';
#endif
        }
      }
      nb++;
      ratio = ((double)nb)/(double)size;
      if (ratio >= prev_ratio+0.1) {
        prev_ratio = ratio;
        cerr << "\x0d" << "Already computed : " << (int)(ratio*100) << " % " << flush;
      }
    }
    cerr << "\x0d" << "Already computed : 100 % ... done." << '\n';
    cerr << "Add " << _scene->getSize() << " shape(s)." << '\n';
    return (_scene->isValid());
}


/* ----------------------------------------------------------------------- */

void 
QuotientGeometryComputer::addInfoTo(MacroVtxInfo& m,
									VId vtx,
									const PlantFrame* _pf,
									Discretizer & discretizer) {
    if(!consider(vtx))return;
	
	if(m.hasShapeComputed()){
		ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
		if(ptr)m.addInfo(ptr);
	}
	else {
		if(m.areRadiusNeeded()){
			ValType coord[3];
			_pf->coord3DOrigin(vtx,coord);
			m.addInfo(Vector3((real_t)coord[0],(real_t)coord[1],(real_t)coord[2]),
				      (real_t)(_pf->botDia(vtx)));
		}
		else{
			ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
			bool r = false;
			if(ptr){
				if(ptr->apply(discretizer)){
					ExplicitModelPtr e = discretizer.getDiscretization();
					if(e){
						r = true;
						m.addPoints(e->getPointList());
					}
				}
			}
			if(!r){
				ValType coord[3];
				_pf->coord3DOrigin(vtx,coord);
				m.addPoint(Vector3((real_t)coord[0],(real_t)coord[1],(real_t)coord[2]));
			}
		}
	}
}

void 
QuotientGeometryComputer::createInfoTo(MacroInfoList& macroinfos,
									   VId vtx,
									   VId father,
									   const PlantFrame* _pf,
									   Discretizer & discretizer) {

	string classname,appearance;
	AMObjVector args(1);
	args[0] = AMObj(AMObjType::VTX, father);
	
	if(_quotient_geometry_fun){
		AMObj ret = (*_quotient_geometry_fun)(args);
		if(ret.type() == AMObjType::STRING)
		  classname = ((const AMString*)(ret.val.p))->data();
		if(classname.empty()){
			args[0] = AMObj(AMObjType::VTX, vtx);
			AMObj ret = (*_quotient_geometry_fun)(args);
			if(ret.type() == AMObjType::STRING)
			  classname = ((const AMString*)(ret.val.p))->data();
			else  cerr << "Error with function QuotientGeometry for vertex " << father << '\n';
			if(classname.empty())
			  args[0] = AMObj(AMObjType::VTX, father);
		}
	}
	else if(!_quotient_geometry_name.empty()){
	  classname = _quotient_geometry_name;
	}
	if(toUpper(classname) != "SELF"){
		if(_quotient_appearance_fun){
			AMObj ret2 = (*_quotient_appearance_fun)(args);
			if(ret2.type() == AMObjType::STRING)
			  appearance = ((const AMString*)(ret2.val.p))->data();
			else  cerr << "Error with function QuotientAppearance for vertex " << father << '\n';
		}
		ValType coord[3];
		_pf->coord3DOrigin(vtx,coord);
		if(!consider(vtx)){
		  macroinfos[(int)father]=MacroVtxInfo(classname,appearance);
		}
		else if(!Fit::areRadiusNeeded(classname)){
			ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
			bool r = false;
			if(ptr){
				if(ptr->apply(discretizer)){
					ExplicitModelPtr e = discretizer.getDiscretization();
					if(e){
						r = true;
						macroinfos[(int)father]=MacroVtxInfo(classname,
							appearance,e->getPointList());
					}
				}
			}
			if(!r){
				ValType coord[3];
				_pf->coord3DOrigin(vtx,coord);
				macroinfos[(int)father]=MacroVtxInfo(classname,appearance,
				Vector3((real_t)coord[0],(real_t)coord[1],(real_t)coord[2]));
			}
		}
		else {
			macroinfos[(int)father]=MacroVtxInfo(classname,appearance,
				Vector3((real_t)coord[0],(real_t)coord[1],(real_t)coord[2]),(real_t)(_pf->botDia(vtx)));
		}
	}
	else if(consider(vtx)){
		ShapePtr ptr = _lt->getScene()->getShapeId(vtx);
		if(ptr)macroinfos[(int)father]=MacroVtxInfo(classname,ptr);
	}
}

MacroInfoList *
QuotientGeometryComputer::computeMacroInfo( const PlantFrame* _pf) {
    MacroInfoList *  mi = new MacroInfoList;
	MacroInfoList& macroinfos = *mi;
    Plant* p = _pf->_plant;
    MTG* g = p->getMtg();

	Discretizer discretizer;
    // Scan the plantframe _pf
    // and get the top coordinates of each element

    IntType nb_branches = p->nbBranches();

    for (IntType i=0;i<nb_branches;i++) {

        const Branch& b = p->findBranch(i); // gets the ith branch of the plant

        const BranchCompoList& compo = b.branchComponents();

        size_t nbb = compo.entries(); // nb of vertices in a branch

        for(size_t j=0;j<nbb;j++) {

            VId vtx = compo.at(j).getVertex(); // jth vertex of branch b
            VId complex = g->si_complex(vtx,_quotient_scale);
			if(complex == -1){
				VId ftr = _lt->fatherOfVirtualElement(vtx);
				if(ftr != -1){ // isVirtualElement
				  complex = g->si_complex(ftr,_quotient_scale);
				  if(complex == -1)
					cerr << "Cannot find complex for element " << vtx << '\n';
				}
			}
			if(complex!=-1){
				MacroInfoList::iterator _it;
				if((_it=macroinfos.find((int)complex))==macroinfos.end()){
					createInfoTo(macroinfos, vtx, complex, _pf, discretizer);
                    /// find father of complex
                    VId father = g->si_father(complex);
                    if (father != UNDEF) macroinfos[(int)complex]._father = father;
				}
				else {
					addInfoTo(_it->second, vtx, _pf, discretizer);
				}
				if(j==nbb-1 && !macroinfos[(int)complex].hasShapeComputed() && macroinfos[(int)complex].areRadiusNeeded()){
					ValType coord[3];
					_pf->coord3D(vtx,coord);
					macroinfos[(int)complex].addInfo(Vector3((real_t)coord[0],(real_t)coord[1],(real_t)coord[2]),(real_t)(_pf->topDia(vtx)));
				}
			}
        }
    }
	if(!mi->empty())return mi;
	else {
	  delete mi;
	  return NULL;
	}
}



/* ----------------------------------------------------------------------- */


MacroInfoList *
QuotientGeometryComputer::computeQuotientInfo( const PlantFrame* _pf) {
    MacroInfoList *  mi = new MacroInfoList;
	MacroInfoList& macroinfos = *mi;
    Plant* p = _pf->_plant;
    MTG* g = p->getMtg();
	
	Discretizer discretizer;
	
    tool_hash_map<VId,VId> roots;
	
    // Scan the plantframe _pf
    // and get the top coordinates of each element
	
    IntType nb_branches = p->nbBranches();
    int size = 0 ,nb = 0 ;
    double ratio = 0.0, prev_ratio = 0.0 ;
	
    for (IntType i1=0;i1<nb_branches;i1++) {
		
        const Branch& b = p->findBranch(i1); // gets the ith branch of the plant		
        const BranchCompoList& compo = b.branchComponents();
		
        size += compo.entries(); // nb of vertices in a branch
    }
	
	
    for (IntType i=0;i<nb_branches;i++) {
		
        const Branch& b = p->findBranch(i); // gets the ith branch of the plant		
        const BranchCompoList& compo = b.branchComponents();
		
        size_t nbb = compo.entries(); // nb of vertices in a branch
		
        for(size_t j=0;j<nbb;j++) {
			
            VId vtx = compo.at(j).getVertex(); // jth vertex of branch b
            VId father = vtx;
            tool_hash_map<VId,VId>::iterator _it1;
            if((_it1=roots.find(vtx))!=roots.end())
                father=_it1->second;
            else{
                AMObjVector args(1);
                args[0] = AMObj(AMObjType::VTX, vtx);
                AMObj ret = (*_quotient_fun)(args);
				bool result = false;
				if(ret.type() == AMObjType::BOOL)
					result = ret.val.b;
				else if(ret.type() == AMObjType::INTEGER)
					result = (ret.val.i != 0);
				else if(ret.type() == AMObjType::REAL)
					result = (ret.val.r != 0);
				else  cerr << "Error with function Quotient for vertex " << father 
					<< ": return a " << ret.type().string() << " value\n" ;
				
                if(result){
                    roots[vtx]=vtx;
                }
                else{
                    vector<VId> path;
                    while(!result){
                        father = g->si_father(father);
						if(father == -1 /*&& _lt->isVirtualElement(vtx)*/){
							father = _lt->fatherOfVirtualElement(vtx);
							if(father == -1)
							cerr << "Cannot find father for element " << vtx << '\n';
						}
                        if((father!=-1) && ((_it1=roots.find(father))!=roots.end())){
                            VId root = _it1->second;
                            roots[vtx]=root;
                            if(!path.empty())
                                for(vector<VId>::iterator _it2=path.begin();_it2!=path.end();_it2++)
                                    roots[*_it2]=root;
								father=root;
								result=true;
                        }
                        else{
                            if(father!=-1){
                                AMObjVector args(1);
                                args[0] = AMObj(AMObjType::VTX, father);
                                AMObj ret = (*_quotient_fun)(args);
                                result = ret.val.b;
                            }
                            else result=true;
                            if(result){
                                if(father!=-1)roots[father]=father;
                                roots[vtx]=father;
                                if(!path.empty())
                                    for(vector<VId>::iterator _it2=path.begin();_it2!=path.end();_it2++)
                                        roots[*_it2]=father;
                            }
                            else
                                path.push_back(father);
                        }
                    }
                }
            }
            if(father !=-1){
				MacroInfoList::iterator _it;
				if((_it=macroinfos.find((int)father))==macroinfos.end()){
					createInfoTo(macroinfos, vtx, father, _pf, discretizer);
                    // compute father of complex
                    VId grandfather = g->si_father(father);
                    if ( grandfather != UNDEF){
                        tool_hash_map<VId,VId>::iterator _itf;
                        if((_itf=roots.find(grandfather))!=roots.end())
                            macroinfos[(int)father]._father = _itf->second;
                    }
				}
				else {
					addInfoTo(_it->second, vtx, _pf, discretizer);
					
				}
				if(j==nbb-1 && !macroinfos[(int)father].hasShapeComputed() && macroinfos[(int)father].areRadiusNeeded()){
                    ValType coord[3];
                    _pf->coord3D(vtx,coord);
					macroinfos[(int)father].addInfo(Vector3((real_t)coord[0],(real_t)coord[1],(real_t)coord[2]),(real_t)(_pf->topDia(vtx)));
                }
            }
        }
        nb+=nbb;
        ratio = ((double)nb)/(double)size;
        if (ratio >= prev_ratio+0.1) {
            prev_ratio = ratio;
            cerr << "\x0d" << "Already computed : " << (int)(ratio*100) << " % " << flush;
        }
    }
    cerr << "\x0d" << "Already computed : 100 % ... done." << '\n';
	if(!mi->empty())return mi;
	else {
	  delete mi;
	  return NULL;
	}
}

/* ----------------------------------------------------------------------- */

SLArray *
QuotientGeometryComputer::computeQuotientedGraph( const PlantFrame* _pf) {
    Plant* p = _pf->_plant;
    MTG* g = p->getMtg();

    tool_hash_map<VId, vector< VId > > graph;
    tool_hash_map<VId,VId> roots;

    // Scan the plantframe _pf
    // and get the top coordinates of each element

    IntType nb_branches = p->nbBranches();
    int size = 0 ,nb = 0 ;
    double ratio = 0.0, prev_ratio = 0.0 ;

    for (IntType i1=0;i1<nb_branches;i1++) {

        const Branch& b = p->findBranch(i1); // gets the ith branch of the plant
        const BranchCompoList& compo = b.branchComponents();
        size += compo.entries(); // nb of vertices in a branch
    }


    for (IntType i=0;i<nb_branches;i++) {

        const Branch& b = p->findBranch(i); // gets the ith branch of the plant
        const BranchCompoList& compo = b.branchComponents();

        size_t nbb = compo.entries(); // nb of vertices in a branch

        for(size_t j=0;j<nbb;j++) {

            VId vtx = compo.at(j).getVertex(); // jth vertex of branch b
            VId father = vtx;
            tool_hash_map<VId,VId>::iterator _it1;
            if((_it1=roots.find(vtx))!=roots.end())
                father=_it1->second;
            else{
                AMObjVector args(1);
                args[0] = AMObj(AMObjType::VTX, vtx);
                AMObj ret = (*_quotient_fun)(args);
				bool result = false;
				if(ret.type() == AMObjType::BOOL)
				  result = ret.val.b;
				else if(ret.type() == AMObjType::INTEGER)
					result = (ret.val.i != 0);
				else if(ret.type() == AMObjType::REAL)
					result = (ret.val.r != 0);
				else  cerr << "Error with function Quotient for vertex " << father << '\n';
                if(result){
                    roots[vtx]=vtx;
                }
                else{
                    vector<VId> path;
                    while(!result){
                        father = g->si_father(father);
						if(father == -1 /*&& _lt->isVirtualElement(vtx)*/){
							father = _lt->fatherOfVirtualElement(vtx);
							if(father == -1)
							cerr << "Cannot find father for element " << vtx << '\n';
						}
                        if((father!=-1) && ((_it1=roots.find(father))!=roots.end())){
                            VId root = _it1->second;
                            roots[vtx]=root;
                            if(!path.empty())
                                for(vector<VId>::iterator _it2=path.begin();_it2!=path.end();_it2++)
                                    roots[*_it2]=root;
                            father=root;
                            result=true;
                        }
                        else{
                            if(father!=-1){
                                AMObjVector args(1);
                                args[0] = AMObj(AMObjType::VTX, father);
                                AMObj ret = (*_quotient_fun)(args);
								if(ret.type() == AMObjType::BOOL)
									result = ret.val.b;
								else if(ret.type() == AMObjType::INTEGER)
									result = (ret.val.i != 0);
								else if(ret.type() == AMObjType::REAL)
									result = (ret.val.r != 0);
								else  cerr << "Error with function Quotient for vertex " << father 
								  << ": return a " <<ret.type().string() << " value" << '\n';
                            }
                            else result=true;
                            if(result){
                                if(father!=-1)roots[father]=father;
                                roots[vtx]=father;
                                if(!path.empty())
                                    for(vector<VId>::iterator _it2=path.begin();_it2!=path.end();_it2++)
                                        roots[*_it2]=father;
                            }
                            else
                                path.push_back(father);
                        }
                    }
                }
            }
            if(father !=-1){
                (graph[(int)father]).push_back(vtx);
            }
        }
        nb+=nbb;
        ratio = ((double)nb)/(double)size;
        if (ratio >= prev_ratio+0.1) {
            prev_ratio = ratio;
            cerr << "\x0d" << "Already computed : " << (int)(ratio*100) << " % " << flush;
        }
    }
    cerr << "\x0d" << "Already computed : 100 % ... done." << '\n';
    SLArray * graph2=new SLArray;
    for(tool_hash_map< VId, vector< VId > >::iterator _it3=graph.begin();_it3!=graph.end();_it3++){
        SLArray *macro_vtx=new SLArray;
        for(vector< VId >::iterator _it4 = (_it3->second).begin();_it4!=(_it3->second).end();_it4++)
            (*macro_vtx)+=AMObj(AMObjType::VTX,*_it4);
        (*graph2)+=AMObj(AMObjType::ARRAY,macro_vtx);
    }
    return graph2;
}



/* ----------------------------------------------------------------------- */

VId
QuotientGeometryComputer::quotient_complex(VId vertex,const MTG* _mtg){
    VId father = vertex;

    AMObjVector args(1);
    args[0] = AMObj(AMObjType::VTX, vertex);
    AMObj ret = (*_quotient_fun)(args);
    bool result = ret.val.b;
    if(result) return vertex;
    else{
        while(!result){
            father = _mtg->si_father(father);
            if(father !=-1){
                AMObjVector args(1);
                args[0] = AMObj(AMObjType::VTX, father);
                AMObj ret = (*_quotient_fun)(args);
                result = ret.val.b;
            }
            else return -1;
        }
        return father;
    }
}


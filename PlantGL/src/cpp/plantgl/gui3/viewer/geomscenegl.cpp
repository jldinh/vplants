/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *                           UMR PIAF INRA-UBP Clermont-Ferrand
 *
 *       File author(s): F. Boudon
 *
 *       $Source$
 *       $Id: geomscenegl.cpp 4276 2008-01-29 13:14:17Z boudon $
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

#include "geomscenegl.h"

/// Tools
#include <plantgl/tool/util_string.h>
#include <plantgl/algo/opengl/util_appegl.h>

/// GEOM
#include <plantgl/scenegraph/scene/shape.h>
#include <plantgl/scenegraph/appearance/appearance.h>
#include <plantgl/scenegraph/geometry/explicitmodel.h>
#include <plantgl/algo/base/wirecomputer.h>
#include <plantgl/algo/base/tesselator.h>

/// Viewer
#include "../base/light.h"
#include "../base/camera.h"
#include "../base/zbuffer.h"

#include "geomevent.h"

/// Qt
#include <qslider.h>
#include <qlistview.h>
#include <qmessagebox.h>
#include <qapplication.h>
#include <qclipboard.h>
#include <qgl.h>

#include <plantgl/algo/codec/scne_parser.h>

#ifdef QT_THREAD_SUPPORT
#ifndef _DEBUG
#define GEOM_THREAD
#endif
#endif

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace std;
using namespace STDEXT;
/* ----------------------------------------------------------------------- */

ViewGeomSceneGL3::ViewGeomSceneGL3(ViewCameraGL3 * camera,
                                 ViewLightGL3 * light,
                                 QGLWidget * parent,
                                 const char * name) :
  ViewModalRendererGL3(camera,light,parent,name),
  __scene(0),
  __discretizer(),
  __renderer(__discretizer,parent),
  __skelComputer(__discretizer),
  __bboxComputer(__discretizer),
  __skelRenderer(__skelComputer),
  __bboxRenderer(__bboxComputer),
  __ctrlPtRenderer(__discretizer),
  __bbox(new BoundingBox(Vector3(-1,-1,-1),Vector3(1,1,1))),
  __selectedShapes()
#ifdef QT_THREAD_SUPPORT
  ,__reader(0)
#endif
{
  __renderingOption[0] = false;
  __renderingOption[1] = false;
  parserVerbose(false);
  __renderer.setSelectionMode(GLRenderer::SceneObjectId);
//  __renderer.setRenderingMode(GLRenderer::Dynamic);

  //  QObject::connect(QApplication::clipboard(),SIGNAL(dataChanged()),
//				   this,SLOT(clipboard()));

}

ViewGeomSceneGL3::~ViewGeomSceneGL3()
{
}
bool 
ViewGeomSceneGL3::useThread()
{
#ifdef GEOM_THREAD
	return true;
#else
	return false;
#endif
}

/// Connect this to a GL Widget.
void ViewGeomSceneGL3::connectTo(QGLWidget * glw)
{
	ViewRendererGL3::connectTo(glw);
	__renderer.setGLFrame(glw);
}

/* ----------------------------------------------------------------------- */

bool
ViewGeomSceneGL3::sceneChangeEvent( ViewSceneChangeEvent3 * k)
{
  if(k->getSceneType() == 1){
    GeomSceneChangeEvent3 * event = ( GeomSceneChangeEvent3 * )k;
    if(event->addition)addScene(ScenePtr(event->scene));
        else setScene(event->scene);
    if(!event->error.isEmpty()){
      error(event->error);
    }
    setFilename(event->file);
    return true;
  }
  else return false;
}

void
ViewGeomSceneGL3::clear()
{
  __scene = ScenePtr(0);
  __bbox= BoundingBoxPtr(new BoundingBox(Vector3(-1,-1,-1),Vector3(1,1,1)));
  setFilename("");
  clearCache();
}

void
ViewGeomSceneGL3::clearCache()
{
  __discretizer.clear();
  __selectedShapes.clear();
  clearDisplayList();
}

void
ViewGeomSceneGL3::clearDisplayList()
{
  __renderer.clear();
  __skelComputer.clear();
  __bboxComputer.clear();
  __skelRenderer.clear();
  __bboxRenderer.clear();
  __ctrlPtRenderer.clear();
}

ScenePtr
ViewGeomSceneGL3::getScene( ) const
{
  return __scene;
}

std::vector<uint_t>
ViewGeomSceneGL3::getSelectionIds() const
{
  std::vector<uint_t> res;
  for(hash_map<uint_t,Shape3DPtr>::const_iterator _it = __selectedShapes.begin();
  _it !=__selectedShapes.end(); _it++)
	  res.push_back(_it->second->getId());
  return res;
}

uint_t
ViewGeomSceneGL3::translateId(uint_t id) const
{
    Shape3DPtr ptr;
    for(Scene::iterator _it = __scene->getBegin();
        _it != __scene->getEnd(); _it++){
      if( ptr.cast(*_it).isValid() && (ptr->SceneObject::getId() == id))
	    return ptr->getId();
    }
	return id;
}


ScenePtr 
ViewGeomSceneGL3::getSelection( ) const
{
  ScenePtr scene(new Scene);
  for(hash_map<uint_t,Shape3DPtr>::const_iterator _it = __selectedShapes.begin();
  _it !=__selectedShapes.end(); _it++)
	  scene->add(_it->second);
  return scene;
}

ScenePtr 
ViewGeomSceneGL3::getNotSelection( ) const
{
  ScenePtr scene(new Scene);
  uint_t id;
  for(Scene::const_iterator _it = __scene->getBegin(); _it !=__scene->getEnd(); _it++){
	id = (*_it)->SceneObject::getId();
	if(__selectedShapes.find(id)==__selectedShapes.end())
	  scene->add(*_it);
  }	  
  return scene;
}

const BoundingBoxPtr
ViewGeomSceneGL3::getGlobalBoundingBox() const
{
  return __bbox;
}

const BoundingBoxPtr
ViewGeomSceneGL3::getSelectionBoundingBox() 
{
  BoundingBoxPtr bbox;
  for(hash_map<uint_t,Shape3DPtr>::const_iterator _it = __selectedShapes.begin();
  _it !=__selectedShapes.end(); _it++)
	  if(_it->second->apply(__bboxComputer)){
		if(bbox)bbox->extend(__bboxComputer.getBoundingBox());
		else bbox = new BoundingBox(*__bboxComputer.getBoundingBox());
	  }
  return bbox;
}


/* ----------------------------------------------------------------------- */
void
ViewGeomSceneGL3::changeDisplayListUse(){
  if(__renderer.getRenderingMode() == GLRenderer::Dynamic){
	__renderer.setRenderingMode(GLRenderer::Normal);
	emit displayList(true);
  }
  else {
	__renderer.setRenderingMode(GLRenderer::Dynamic);
	emit displayList(false);
  }
}

void
ViewGeomSceneGL3::useDisplayList(bool b){
  if( getDisplayListUse() != b){
	changeDisplayListUse();
  }
}

bool 
ViewGeomSceneGL3::getDisplayListUse() const {
  return __renderer.getRenderingMode() != GLRenderer::Dynamic;
}

void 
ViewGeomSceneGL3::refreshDisplay() {
  if(__scene)setScene(ScenePtr(__scene));
}

/* ----------------------------------------------------------------------- */
int
ViewGeomSceneGL3::addScene( const ScenePtr& scene )
{
  if (!scene){
    QString _mess = "<b>[GeomSceneGL] "+tr("GEOM Error")+" !!</b><br>"+tr("Empty Scene to Add")+"<br>";
	if(!BASHMODE)
		QMessageBox::critical(__frame,tr("GEOM Error"),_mess,1,0,0);
	else warning(_mess);
    return -1;
  }
  ScenePtr scenunion = scene;
  if(__scene)scenunion->merge(__scene);
  return setScene(scenunion);
}

int
ViewGeomSceneGL3::setScene( const ScenePtr& scene )
{
  if (!scene){
	  QString _mess = "<b>[GeomSceneGL] "+tr("GEOM Error")+" !!</b><br>"+tr("Empty Scene")+"<br>";
	  if(!BASHMODE){
		QMessageBox::critical(__frame,tr("GEOM Error"),_mess,1,0,0);
	  }
	  else warning("*** Warning : "+_mess);
    return -1;
  }
  if (!scene->isValid()){
		  QString _mess1 = "<b>[GeomSceneGL] "+tr("GEOM Error")+" !!</b><br>"+tr("Scene Not Valid")+"<br>"
			  +tr("To continue can cause dysfunction of this program")+"<br>";
		  QString _mess2 = _mess1 + "<b>"+tr("File")+" :</b> " + QString(__FILE__) + "<br>";
		  _mess2 += "<b>"+tr("Line")+" :</b> " + QString::number(__LINE__) + "<br>";
	  if(!BASHMODE){
		  int res = QMessageBox::critical(__frame,tr("GEOM Error"),_mess2,tr("Abort"),tr("Continue"),tr("Validity"));
		  if(res == 0 || res == -1)return -1;
		  else if(res == 2){
			  stringstream _errlog(ios::out) ;
			  bool res2 = scene->isValid(_errlog);
			  std::string _msg = _errlog.str();
			  if(!_msg.empty())error(_msg.c_str());
			  if(!res2){
				  QString _mess3 = _mess1 + "<b>"+tr("File")+" :</b> " + QString(__FILE__) + "<br>";
				  _mess3 += "<b>"+tr("Line")+" :</b> " + QString::number(__LINE__) + "<br>";
				  res = QMessageBox::critical(__frame,tr("GEOM Error"),tr(_mess3),tr("Abort"),tr("Continue"));
				  if(res == 0 || res == -1)return -1;
			  }
		  }
	  }
	  else warning("*** Warning : "+_mess2);
  }

  // Clears all the actions
  __scene = ScenePtr(0);
  __bbox= BoundingBoxPtr();
  clearCache();

  // Sets the scene
  __scene = scene;

  // Computes the global bounding box
  if (! __scene->isEmpty()) {
    if(__bboxComputer.process(__scene))
      __bbox = __bboxComputer.getBoundingBox();
    QString _msg(tr("Display")+" ");
    _msg+=QString::number(__scene->getSize());
    _msg+=(" "+tr("geometric shapes."));
    status(_msg,10000);

  }
  else{
    status(tr("Display empty scene."));
  }
  __camera->buildCamera(__bbox);
  emit sceneChanged();
  if(__frame != NULL && __frame->isVisible())emit valueChanged();
  return 1;
}

void  
ViewGeomSceneGL3::computeCamera()
{
  __camera->buildCamera(__bbox, true);
}

/* ----------------------------------------------------------------------- */

void
ViewGeomSceneGL3::initializeGL()
{
	glTexGenf(GL_S,GL_TEXTURE_GEN_MODE,GL_OBJECT_LINEAR);
	GLfloat f[] = { 0.,1.,0.,0.};
	glTexGenfv(GL_S,GL_OBJECT_PLANE,f);
	glTexGenf(GL_T,GL_TEXTURE_GEN_MODE,GL_OBJECT_LINEAR);
	GLfloat f2[] = { 0.,0.,1.,0.};
	glTexGenfv(GL_T,GL_OBJECT_PLANE,f2);
}

void
ViewGeomSceneGL3::paintGL()
{

    if (__scene && !__scene->isEmpty()){

    switch (__renderingMode) {
    case 1:
      if(__lightEnable)__light->enable();
      else __light->disable();
      glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
      glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
      if(__renderer.beginSceneList()){
		if(__renderer.getRenderingMode() == GLRenderer::Dynamic)
			__scene->apply(__renderer);
		else {
			int cur = 0;
			int tot = __scene->getSize();
			int tenpercent = max(1,tot / 10);
			int cpercent = 0;
			__renderer.beginProcess();
			for(Scene::iterator it = __scene->getBegin();it != __scene->getEnd(); it++){
				(*it)->apply(__renderer);
				cur++;
				if(cur / tenpercent > cpercent){ 
					cpercent = cur / tenpercent;
					progress(cur,tot);
				}
			}
			progress(tot,tot);
			__renderer.endProcess();
		}
        __renderer.endSceneList();
      }
      if(GEOM_GL_ERROR) clear();
      break;
    case 2:
      __light->disable();
      glBlendFunc(GL_ONE,GL_ZERO);
      glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
      if(__renderer.beginSceneList()){
        __scene->apply(__renderer);
        __renderer.endSceneList();
      }
      if(GEOM_GL_ERROR) clear();
      break;
    case 3:
      __light->disable();
      glBlendFunc(GL_ONE,GL_ZERO);
      if(__skelRenderer.beginSceneList()){
        __scene->apply(__skelRenderer);
        __skelRenderer.endSceneList();
      }
      if(GEOM_GL_ERROR) clear();
      break;
    case 4:
      __light->disable();
      glBlendFunc(GL_ONE,GL_ZERO);
      glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
      if(__renderer.beginSceneList()){
        __scene->apply(__renderer);
        __renderer.endSceneList();
      }
      if(__lightEnable)__light->enable();
      else __light->disable();
      glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
      glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
      if(__renderer.beginSceneList()){
        __scene->apply(__renderer);
        __renderer.endSceneList();
      }
      if(GEOM_GL_ERROR) clear();
      break;
    };

    if(__renderingOption[0]){
      if(__lightEnable)__light->enable();
      else __light->disable();
      glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
      glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
      if(__bboxRenderer.beginSceneList()){
        __scene->apply(__bboxRenderer);
        __bboxRenderer.endSceneList();
      }
      if(GEOM_GL_ERROR) clear();
    };
    if(__renderingOption[1]){
      __light->disable();
      glBlendFunc(GL_ONE,GL_ZERO);
	  glGeomColor(Color3(64,64,64));
      if(__ctrlPtRenderer.beginSceneList()){
        __scene->apply(__ctrlPtRenderer);
        __ctrlPtRenderer.endSceneList();
      }
      if(GEOM_GL_ERROR) clear();
    }
    if(!__selectedShapes.empty()){
      __light->disable();
      glBlendFunc(GL_ONE,GL_ZERO);
      glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
	  glGeomColor(Color3(64,64,64));
      for(hash_map<uint_t,Shape3DPtr>::iterator _it = __selectedShapes.begin();
          _it !=__selectedShapes.end(); _it++)
        _it->second->apply(__bboxRenderer);
      if(GEOM_GL_ERROR) clear();
    }
  }
}

void
ViewGeomSceneGL3::selectGL()
{
  if (__scene){
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
    glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
        GLRenderer::RenderingMode rtype = __renderer.getRenderingMode();
    __renderer.setRenderingMode(GLRenderer::Selection);
    __scene->apply(__renderer);
    __renderer.setRenderingMode(rtype);
   if(GEOM_GL_ERROR) clear();
  }
}

void
ViewGeomSceneGL3::selectionEvent(uint_t id)
{
  hash_map<uint_t,Shape3DPtr>::iterator _it =__selectedShapes.find(id);
  if(_it!=__selectedShapes.end()){
    Shape3DPtr ptr = _it->second;
	__selectedShapes.erase(_it);
    uint_t _id = (ptr->getId() == Shape::NOID?id:ptr->getId());
	info("*** Comment : "+tr("Shape")+" " +QString::number(_id)+ " "+tr("unselected")+".");
	status(tr("Shape")+" "
	  + (ptr->isNamed()?QString((ptr->getName()+" ").c_str()):"")+"(Id=" +QString::number(_id)
	  + ") "+tr("unselected")+".",20000);
  }
  else {
    Shape3DPtr ptr;
    for(Scene::iterator _it = __scene->getBegin();
        _it != __scene->getEnd(); _it++){
      if(ptr.cast(*_it).isValid() && 
		(ptr->SceneObject::getId() == id)){
        __selectedShapes[id]=ptr;
	    uint_t _id = (ptr->getId() == Shape::NOID?id:ptr->getId());
		info("*** Comment : "+tr("Shape")+" " +QString::number(_id)+ " "+tr("selected")+".");
		status(tr("Shape")+" "
		       + (ptr->isNamed()?QString((ptr->getName()+" ").c_str()):"")+"(Id=" +QString::number(_id)
		       + ") "+tr("selected")+".",20000);
		emit selectionChanged(ptr->getName().c_str());
        break;
      }
    }
  }
}

void
ViewGeomSceneGL3::selectionEvent(const vector<uint_t>& id)
{
  hash_map<uint_t,Shape3DPtr>::iterator _it;
  uint_t selected = 0;
  uint_t unselected = 0;
  for(vector<uint_t>::const_iterator _id = id.begin();_id != id.end();_id++){
	_it =__selectedShapes.find(*_id);
	if(_it!=__selectedShapes.end()){
	  __selectedShapes.erase(_it);
	  unselected++;
	}
	else {
	  Shape3DPtr ptr;
	  for(Scene::iterator _it = __scene->getBegin();
	  _it != __scene->getEnd(); _it++){
		if(ptr.cast(*_it).isValid() && ptr->SceneObject::getId() == *_id){
		  __selectedShapes[*_id]=ptr;
		  selected++;
		  break;
		}
	  }
	}
  }

  QString mess;
  if(selected > 0){
	mess = "shape";
	if(selected != 1)mess +='s';
	mess +=" "+tr("selected");
	mess = QString::number(selected) + " "+ tr(mess);
  }
  if(selected > 0 && unselected > 0)mess += " "+tr("and")+" ";
  if(unselected > 0){
	QString mess2 = "shape";
	if(unselected != 1)mess2 +='s';
	mess2 +=" unselected";
	mess += mess + QString::number(unselected)+ " " + tr(mess2);
  }
  mess +='.';
  info("*** Comment : " +mess);
  status(mess,20000);
}

void
ViewGeomSceneGL3::selectionIdEvent(const vector<uint_t>& id)
{
  __selectedShapes.clear();
  uint_t selected = 0;
  for(vector<uint_t>::const_iterator _id = id.begin();_id != id.end();_id++){
	  __scene->lock();
	  for(Scene::const_iterator _it = __scene->getBegin() ; 
					  _it != __scene->getEnd(); 
					  _it++){
		ShapePtr ptr = ShapePtr::Cast(*_it);
		if(ptr.isValid() && ptr->getId() == *_id){
		  __selectedShapes[ptr->SceneObject::getId()]=ptr;
		  selected++;
		}
	  }
	  __scene->unlock();
  }

  QString mess;
  if(selected > 0){
	mess = "shape";
	if(selected != 1)mess +='s';
	mess +=" "+tr("selected");
	mess = QString::number(selected) + " "+ tr(mess);
  }
  mess +='.';
  info("*** Comment : " +mess);
  status(mess,20000);
  emit valueChanged();
}


void
ViewGeomSceneGL3::selectionEvent(QListViewItem * item)
{
  if(item && item->text(2) == "Shape"){
	string name = item->text(0).latin1();
	bool found = false;
    for(Scene::iterator _it = __scene->getBegin();
	!found && _it != __scene->getEnd(); _it++){
	  if((*_it)->getName() == name){
		uint_t id = (*_it)->getId();
		if((*_it)->getId() == Shape::NOID){
		  id = (*_it)->SceneObject::getId();
		}
		hash_map<uint_t,Shape3DPtr>::iterator _it2 
		  =__selectedShapes.find(id);
		if(_it2!=__selectedShapes.end()){
		  __selectedShapes.erase(_it2);
		  info("*** Comment : "+tr("Shape")+" " +QString::number(id)+ " "+tr("unselected")+".");
		  status(tr("Shape")+" " +QString::number(id)+ " "+tr("unselected")+".",20000);
		}
		else {
		  __selectedShapes[id]=*_it;
		  info("*** Comment : "+tr("Shape")+" " +QString::number(id)+ " "+tr("selected")+".");
		  status(tr("Shape")+" " +QString::number(id)+ " "+tr("selected")+".",20000);
		}
		emit valueChanged();
		found = true;
	  }
	}
	if(!found){
	  warning("*** Warning : "+tr("Shape")+" \"" +item->text(0)+ "\" "+tr("not found")+".");
	  status(tr("Shape")+" \"" +item->text(0)+ "\" "+tr("not found")+".",20000);
	}
  }
}

void
ViewGeomSceneGL3::clearSelectionEvent()
{
  __selectedShapes.clear();
  emit valueChanged();
}

void
ViewGeomSceneGL3::removeSelection()
{
  if(__selectedShapes.empty()){
    QMessageBox::warning(__frame,tr("GEOM Error"),
	  tr("Empty Selection. Cannot Remove!"),1,0,0);
	return;
  }
  if(QMessageBox::warning(__frame,tr("Confirmation"),
				tr("Remove Selection?"),tr("Ok"),tr("Cancel")) != 0)
	return;
  GeomSceneChangeEvent3 * e = new GeomSceneChangeEvent3(getNotSelection(),NULL,NULL);
  QApplication::postEvent(this,e);
}

void
ViewGeomSceneGL3::keepSelectionOnly()
{
  if(__selectedShapes.empty()){
    QMessageBox::warning(__frame,tr("GEOM Error"),
	  tr("Empty Selection. Cannot Remove!"),1,0,0);
	return;
  }
  GeomSceneChangeEvent3 * e = new GeomSceneChangeEvent3(getSelection(),NULL,NULL);
  hash_map<uint_t,Shape3DPtr> selection = __selectedShapes;
  QApplication::sendEvent(this,e);
  __selectedShapes = selection;
}

void
ViewGeomSceneGL3::wireSelection()
{
  if(__selectedShapes.empty()){
    QMessageBox::warning(__frame,tr("GEOM Error"),
	  tr("Empty Selection. Cannot Replace!"),1,0,0);
	return;
  }
  ScenePtr scene = getNotSelection();
  WireComputer wire(__discretizer);
  hash_map<uint_t,Shape3DPtr> selection;
  for(hash_map<uint_t,Shape3DPtr>::iterator _it = __selectedShapes.begin();
	  _it != __selectedShapes.end();_it++){
	ShapePtr sh = ShapePtr::Cast(_it->second);
	if(sh){
	  if(sh->apply(wire)){
		sh->geometry = wire.getWire();
		scene->add(Shape3DPtr(new Shape(*sh)));
		selection[sh->SceneObject::getId()] = sh;
	  }
	}
	else {
	  qWarning(QString(__FILE__)+QString(":")+QString::number(__LINE__)+QString(": Wire Transformation not yet implemented on Inline."));
	}
  }		

  GeomSceneChangeEvent3 * e = new GeomSceneChangeEvent3(scene,NULL,NULL);
  QApplication::sendEvent(this,e);
  __selectedShapes = selection;
}
void
ViewGeomSceneGL3::discretizeSelection()
{
  if(__selectedShapes.empty()){
    QMessageBox::warning(__frame,tr("GEOM Error"),
	  tr("Empty Selection. Cannot Replace!"),1,0,0);
	return;
  }
  ScenePtr scene = getNotSelection();
  hash_map<uint_t,Shape3DPtr> selection;
  for(hash_map<uint_t,Shape3DPtr>::iterator _it = __selectedShapes.begin();
	  _it != __selectedShapes.end();_it++){
	ShapePtr sh = ShapePtr::Cast(_it->second);
	if(sh){
	  if(sh->apply(__discretizer)){
		sh->geometry = GeometryPtr(__discretizer.getDiscretization());
		scene->add(Shape3DPtr(new Shape(*sh)));
		selection[sh->SceneObject::getId()] = sh;
	  }
	}
	else {
	  qWarning(QString(__FILE__)+QString(":")+QString::number(__LINE__)+QString(": Discretize Transformation not yet implemented on Inline."));
	}
  }		

  GeomSceneChangeEvent3 * e = new GeomSceneChangeEvent3(scene,NULL,NULL);
  QApplication::sendEvent(this,e);
  __selectedShapes = selection;
}

void
ViewGeomSceneGL3::triangulateSelection()
{
  if(__selectedShapes.empty()){
    QMessageBox::warning(__frame,tr("GEOM Error"),
	  tr("Empty Selection. Cannot Replace!"),1,0,0);
	return;
  }
  ScenePtr scene = getNotSelection();
  hash_map<uint_t,Shape3DPtr> selection;
  for(hash_map<uint_t,Shape3DPtr>::iterator _it = __selectedShapes.begin();
	  _it != __selectedShapes.end();_it++){
	ShapePtr sh = ShapePtr::Cast(_it->second);
	Tesselator t;
	if(sh){
	  if(sh->apply(t)){
		sh->geometry = GeometryPtr(t.getDiscretization());
		scene->add(Shape3DPtr(new Shape(*sh)));
		selection[sh->SceneObject::getId()] = sh;
	  }
	}
	else {
	  qWarning(QString(__FILE__)+QString(":")+QString::number(__LINE__)+QString(": Triangulation Transformation not yet implemented on Inline."));
	}
  }		

  GeomSceneChangeEvent3 * e = new GeomSceneChangeEvent3(scene,NULL,NULL);
  QApplication::sendEvent(this,e);
  __selectedShapes = selection;
}

/* ----------------------------------------------------------------------- */

vector<pair<uint_t,double> > 
ViewGeomSceneGL3::getProjectionSizes(const ScenePtr& sc){
	vector<pair<uint_t,double> > res;
	ViewGLFrame3 * frame = dynamic_cast<ViewGLFrame3 *>(__frame);
	if (!frame) return res;
	bool mode = frame->getCamera()->getProjectionMode();
	if(mode)frame->getCamera()->setOrthographicMode();
	ScenePtr nsc(new Scene());
	size_t tot = sc->getSize();
	size_t per = max(size_t( 1 ),(size_t)((double)tot / 100.0));
	size_t cur = 0;
	for(Scene::const_iterator it = sc->getBegin(); it != sc->getEnd(); it++){
		nsc->clear();
		nsc->add(*it);
		setScene(nsc);
		res.push_back(pair<uint_t,double>((*it)->getId(),frame->getProjectionSize()));
		cur++;
		if(cur % per == 0)
			std::cerr << "\x0d Projections " << cur*100/tot << "% done." << std::flush;

	}
	std::cerr << "\x0d Projections 100% done.\n";
	if(mode)frame->getCamera()->setProjectionMode(mode);
	return res;
}

ViewRayPointHitBuffer3 *
ViewGeomSceneGL3::castRays(const ScenePtr& sc, bool back_test){
	ViewGLFrame3 * frame = dynamic_cast<ViewGLFrame3 *>(__frame);
	if (!frame) return NULL;
	int w = frame->width();
	int h = frame->height();
	ViewRayPointHitBuffer3 * res = new ViewRayPointHitBuffer3(w,h);
	double az = frame->getCamera()->getAzimuth();
	double el = frame->getCamera()->getElevation();
	double b_az = az + 180;
	if(b_az >= 180) b_az -= 360;
        if(b_az <= -180) b_az += 360;
	double b_el = -el;

	ScenePtr nsc(new Scene());
	size_t tot = sc->getSize();
	size_t per = max(size_t( 1 ),(size_t)((double)tot / 100.0));
	size_t cur = 0;
	for(Scene::const_iterator it = sc->getBegin(); it != sc->getEnd(); it++){
		nsc->clear();
		nsc->add(*it);
		uint_t id = (*it)->getId();
		setScene(nsc);
		ViewZBuffer3 * cbuff = frame->grabDepthBuffer(false);
		if(! back_test) {
			for(int c = 0;  c < w; ++c){
				for(int r = 0;  r < h; ++r){
					if (cbuff->getAt(r,c).depth < 1){
						const Vector3& pos = cbuff->getAt(r,c).pos;
						res->getAt(r,c).push_back(RayPointHit3(id,pos,pos));
					}
				}
			}
		}
		else {
			frame->getCamera()->setAngles(b_az,b_el);
			emit valueChanged();
			ViewZBuffer3 * cbackbuff = frame->grabDepthBuffer(false);
			for(int c = 0;  c < w; ++c){
				for(int r = 0;  r < h; ++r){
					if (cbuff->getAt(r,c).depth < 1){
						res->getAt(r,c).push_back(RayPointHit3(id,cbuff->getAt(r,c).pos,cbackbuff->getAt(r,w-1-c).pos));
					}
				}
			}
			delete cbackbuff;
			frame->getCamera()->setAngles(az,el);
		}
		delete cbuff;
		cur++;
		if(cur % per == 0)
			std::cerr << "\x0d Projections " << cur*100/tot << "% done." << std::flush;

	}
	std::cerr << "\x0d Projections 100% done.\n";
	setScene(sc);
	return res;
}

/* ----------------------------------------------------------------------- */

void 
ViewGeomSceneGL3::customEvent(QCustomEvent * e) {
	if(e->type() == 12365){
		GeomProjListEvent3 * myevent = (GeomProjListEvent3 *)e;
		*(myevent->result) = getProjectionSizes(myevent->objlist);
	}
	else if (e->type() == 12367){
		ViewRayBuff2Event3 * myevent = (ViewRayBuff2Event3 *)e;
		*(myevent->result) = castRays(myevent->objlist,myevent->back_test);
	}
	else if (e->type() == 12368){
		GeomGetSceneEvent3 * myevent = (GeomGetSceneEvent3 *)e;
		*(myevent->scene) = __scene;
	}
}


/* ----------------------------------------------------------------------- */

ViewMultiGeomSceneGL3::ViewMultiGeomSceneGL3(ViewCameraGL3 * camera,
                                           ViewLightGL3 * light,
                                           QGLWidget * parent,
                                           const char * name):
  ViewGeomSceneGL3(camera,light,parent,name),
  __transitionRenderer(__discretizer),
  __simpleScene(true),
  __renderingStep(0),
  __transSlider(0),
  __transitionBar(0)
{
}


ViewMultiGeomSceneGL3::~ViewMultiGeomSceneGL3()
{
}

void
ViewMultiGeomSceneGL3::clear()
{
  ViewGeomSceneGL3::clear();
  __transitionRenderer.clear();
  __simpleScene = true;
  __renderingStep = 0;
}

/* ----------------------------------------------------------------------- */

void
ViewMultiGeomSceneGL3::paintGL()
{
  if(__simpleScene)ViewGeomSceneGL3::paintGL();
  else {
    if (__scene){
      switch (__renderingMode) {
      case 1:
        if(__lightEnable)__light->enable();
        else __light->disable();
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
        __transitionRenderer.rend(__renderingStep);
        break;
      case 2:
        __light->disable();
        glBlendFunc(GL_ONE,GL_ZERO);
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
        __transitionRenderer.rend(__renderingStep);
        break;
      case 3:
        __light->disable();
        glBlendFunc(GL_ONE,GL_ZERO);
        if(__skelRenderer.beginSceneList()){
          __scene->apply(__skelRenderer);
          __skelRenderer.endSceneList();
        }
      };

      if(__renderingOption[0]){
        if(__lightEnable)__light->enable();
        else __light->disable();
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA);
        glPolygonMode(GL_FRONT_AND_BACK,GL_FILL);
        if(__bboxRenderer.beginSceneList()){
          __scene->apply(__bboxRenderer);
          __bboxRenderer.endSceneList();
        }
      };
      if(__renderingOption[1]){
        __light->disable();
        glBlendFunc(GL_ONE,GL_ZERO);
        if(__ctrlPtRenderer.beginSceneList()){
          __scene->apply(__ctrlPtRenderer);
          __ctrlPtRenderer.endSceneList();
        }
      }
      if(!__selectedShapes.empty()){
        __light->disable();
        glBlendFunc(GL_ONE,GL_ZERO);
        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE);
        for(hash_map<uint_t,Shape3DPtr>::iterator _it = __selectedShapes.begin();
            _it !=__selectedShapes.end(); _it++)
          _it->second->apply(__bboxRenderer);
      }
    }
  }
}

/* ----------------------------------------------------------------------- */

int
ViewMultiGeomSceneGL3::setScene(const ScenePtr& scene1,const ScenePtr& scene2)
{
  __transSlider->setValue(0);
  if(__transSlider)__transSlider->show();
  ScenePtr scene(new Scene(*scene1));
  scene->merge(scene2);
  int a = ViewGeomSceneGL3::setScene(scene);
  __simpleScene = false;
  __transitionRenderer.setScene(scene1,scene2);
  emit valueChanged();
  return a;
}

/* ----------------------------------------------------------------------- */

void
ViewMultiGeomSceneGL3::setRenderingStep(int i)
{
  __renderingStep = i;
  emit valueChanged();
}

/* ----------------------------------------------------------------------- */


bool 
ViewMultiGeomSceneGL3::sceneChangeEvent( ViewSceneChangeEvent3 * k)
{
  if(k->getSceneType() == 1)
    return ViewGeomSceneGL3::sceneChangeEvent(k);
  else if(k->getSceneType() == 2){
    GeomMultiSceneChangeEvent3 * event = ( GeomMultiSceneChangeEvent3 * )k;
    setScene(event->scene,event->scene2);
    if(!event->error.isEmpty()){
      error(event->error);
    }
    setFilename(event->file);
    if(__transSlider)__transSlider->show();
    return true;
  }
  else return false;
}
/* ----------------------------------------------------------------------- */



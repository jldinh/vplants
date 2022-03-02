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

#include "scenegl.h"
#include "camera.h"
#include "light.h"
#include "filemanager.h"
#include "event.h"
#include <QtCore/qfile.h>
#include <QtGui/qfiledialog.h>
#include <QtOpenGL/qgl.h>
#include <QtGui/qmessagebox.h>

/* ----------------------------------------------------------------------- */

ViewRendererGL::ViewRendererGL(QGLWidget * parent, 
			       const char * name):
  ViewObjectGL(parent,name),
	__readTime(QDateTime::currentDateTime()) 
{
}

ViewRendererGL::~ViewRendererGL()
{
}

bool ViewRendererGL::isEmpty() const { return true; }

void 
ViewRendererGL::connectTo(QGLWidget *g)
{
  ViewObjectGL::connectTo(g);
  __frame = g;
}

void 
ViewRendererGL::connectTo(ViewStatusBar * s)
{
  ViewObjectGL::connectTo(s);
}

void 
ViewRendererGL::connectTo(ViewErrorDialog *e)
{
  ViewObjectGL::connectTo(e);
}


void 
ViewRendererGL::changeModeEvent(ViewGLFrame::Mode m)
{
}

void 
ViewRendererGL::setRotationMode()
{
  emit changeMode(ViewGLFrame::Rotation);
}

void
ViewRendererGL::setSelectionMode()
{
  emit changeMode(ViewGLFrame::Selection);
}

void
ViewRendererGL::selectGL()
{
}

void
ViewRendererGL::selectionEvent(uint_t i)
{
  qDebug("selectionEvent(uint_t) not implemented in current Renderer");
}

void
ViewRendererGL::selectionEvent(const std::vector<uint_t>& i)
{
  for(std::vector<uint_t>::const_iterator _it = i.begin();
	  _it != i.end(); _it++)
	  selectionEvent(*_it);
}

void
ViewRendererGL::selectionIdEvent(const std::vector<uint_t>& i)
{
  for(std::vector<uint_t>::const_iterator _it = i.begin();
	  _it != i.end(); _it++)
	  selectionEvent(*_it);
}

void
ViewRendererGL::selectionEvent(QTreeWidgetItem *)
{
  qDebug("selectionEvent(QTreeWidgetItem *) not implemented in current Renderer");
}

std::vector<uint_t> 
ViewRendererGL::getSelectionIds() const
{
  qDebug("std::vector<uint_t> getSelectionIds() const not implemented in current Renderer");
  return std::vector<uint_t>(0);
}

uint_t 
ViewRendererGL::translateId(uint_t id) const
{
	return id;
}

bool
ViewRendererGL::endSelect()
{
	return false;
}

void 
ViewRendererGL::endEvent()
{
}

void
ViewRendererGL::clearSelectionEvent()
{
}

bool
ViewRendererGL::addOpenEntries(QMenu * menu)
{
  return false;
}

bool 
ViewRendererGL::addImportEntries(QMenu * menu)
{
  return false;
}

bool
ViewRendererGL::addSaveEntries(QMenu * menu)
{
  return false;
}

bool
ViewRendererGL::addExportEntries(QMenu * menu)
{
  return false;
}
  
bool
ViewRendererGL::addProperties(QTabWidget * tab)
{
  return false;
}

bool 
ViewRendererGL::addOtherMenu(QMenuBar * menu)
{
  return false;
}

bool 
ViewRendererGL::addEditEntries(QMenu * menu)
{
	return false;
}

bool 
ViewRendererGL::addOtherToolBar(QMainWindow * menu)
{
  return false;
}

bool ViewRendererGL::browse(QTreeWidget *,bool)
{
  return false;
}

bool 
ViewRendererGL::open(const QString& filename)
{
  return false;
}

bool 
ViewRendererGL::openStream(std::istream& stream)
{
  return false;
}

bool
ViewRendererGL::saveAs(const QString& filename)
{
  return false;
}

void
ViewRendererGL::openFile(const QString& filename)
{
  if(open(filename))
    emit filenameChanged(__filename);
}

void
ViewRendererGL::addFile(const QString& filename)
{
}

void 
ViewRendererGL::save()
{
  saveAs(__filename);
  __readTime = QDateTime::currentDateTime();
}

void 
ViewRendererGL::refresh()
{
  if(!__filename.isEmpty()){
	openFile(__filename);
  }
  else refreshDisplay();
}

void 
ViewRendererGL::refreshDisplay()
{
}

void 
ViewRendererGL::close()
{
  clear();
  emit valueChanged();
}

void 
ViewRendererGL::saveAs()
{
  QString filename = ViewFileManager::getSaveFileName(__filename,"","All Files (*.*)",__frame,"SaveAs");
  if(!filename.isEmpty()){
    if(saveAs(filename)){
      __filename = filename;
	  __readTime = QDateTime::currentDateTime();
      emit filenameChanged(__filename);
    }
  }
}

const QString&
ViewRendererGL::getFilename() const
{
  return __filename;
}

void
ViewRendererGL::setFilename(const QString& file)
{
  bool t = (file != __filename);
  if(t) __filename = file;
  __readTime = QDateTime::currentDateTime();
  if(t) emit filenameChanged(__filename);
}

void
ViewRendererGL::checkFileModification()
{
  if(!__filename.isEmpty()){
	if(QFileInfo(__filename).lastModified() > __readTime){
	  __readTime = QDateTime::currentDateTime();
	  if(QFileInfo(__filename).lastModified() > __readTime)
		__readTime = QFileInfo(__filename).lastModified();
	  if(QMessageBox:: information (__frame, "File Modification", 
		__filename + " has been modified.\nLast Modification : "
		+QFileInfo(__filename).lastModified().toString()
		+" - Reading Time : "
		+__readTime.toString()
		+"\nReload ?","Yes","No") == 0){
		refresh();
	  }
	}
  }
}

void 
ViewRendererGL::clear()
{
  if(__filename != QString::null){
	__filename = QString::null;
	emit filenameChanged(__filename);
  }
}

/// Get the global Bounding Box.
const PGL(BoundingBoxPtr) 
ViewRendererGL::getGlobalBoundingBox() const
{
	return PGL(BoundingBoxPtr)(new PGL(BoundingBox)(Vector3(-1,-1,-1),Vector3(1,1,1)));
}


/* ----------------------------------------------------------------------- */

ViewSceneRendererGL::ViewSceneRendererGL(ViewCameraGL * camera,
					 ViewLightGL * light,
					 QGLWidget * parent, 
					 const char * name):
  ViewRendererGL(parent,name),
  __camera(camera),
  __light(light),
  __animated(eStatic)
{
  if(camera)
	QObject::connect(camera,SIGNAL(needReDim()),this,SLOT(computeCamera()));  
}

ViewSceneRendererGL::~ViewSceneRendererGL()
{
}

ViewCameraGL *
ViewSceneRendererGL::getCamera() const
{
  return __camera;
}

ViewLightGL *
ViewSceneRendererGL::getLight() const
{
  return __light;
}

void
ViewSceneRendererGL::setCamera(ViewCameraGL * camera)
{
  __camera = camera;
  if(camera)
	QObject::connect(camera,SIGNAL(needReDim()),this,SLOT(computeCamera()));  
}

void 
ViewSceneRendererGL::setLight(ViewLightGL * light)
{
  __light = light;
}

void  
ViewSceneRendererGL::computeCamera()
{
}

void 
ViewSceneRendererGL::useDisplayList(bool)
{
}


/* ----------------------------------------------------------------------- */

bool ViewRendererGL::event(QEvent * e)
{
  if(e->type() == ViewEvent::eSceneChange){
    ViewSceneChangeEvent * k = ( ViewSceneChangeEvent * )e;
    return sceneChangeEvent(k);
  }
  else if(e->type() == ViewEvent::eFileChange){
    ViewFileChangeEvent * k = ( ViewFileChangeEvent * )e;
	openFile(k->arg1);
    return true;
  }
  else if(e->type() == ViewEvent::eRefresh){
    // ViewRefreshEvent * k = ( ViewRefreshEvent * )e;
	refresh();
    return true;
  }
  else return(QObject::event(e));
}

bool ViewRendererGL::sceneChangeEvent( ViewSceneChangeEvent * )
{
  return false;
}


/* ----------------------------------------------------------------------- */


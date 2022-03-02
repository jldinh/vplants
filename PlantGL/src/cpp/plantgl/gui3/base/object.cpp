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
 *       $Id: object.cpp 2725 2007-02-27 15:08:52Z boudon $
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

#include "object.h"

#include <qpoint.h>
#include <qmessagebox.h>
#include <qgl.h>

#include "camera.h"
#include "errordialog.h"
#include <stdlib.h>

/* ----------------------------------------------------------------------- */

ViewObjectGL3::ViewObjectGL3(QObject * parent, const char * name) :
  QObject(parent,name),
  __frame(NULL)
{
}

ViewObjectGL3::ViewObjectGL3(QGLWidget * parent, const char * name) :
  QObject(parent,name),
  __frame(parent)
{
  if(parent)
    QObject::connect (this,SIGNAL(valueChanged()),
		      parent,SLOT(updateGL()) ); 	
}

ViewObjectGL3::~ViewObjectGL3()
{
}

void 
ViewObjectGL3::move(QPoint p)
{
  moving(p.x(),p.y());
}

void 
ViewObjectGL3::moving(int dx, int dy)
{
}

void 
ViewObjectGL3::zoom(QPoint p)
{
  zooming(p.x(),p.y());
}

void 
ViewObjectGL3::zooming(int dx, int dy)
{
}

void 
ViewObjectGL3::rotate(QPoint p)
{
  rotating(p.x(),p.y());
}

void 
ViewObjectGL3::rotating(int dx, int dy)
{
}

void 
ViewObjectGL3::initializeGL()
{
}

void 
ViewObjectGL3::resizeGL(int w, int h)
{
}

QPopupMenu * 
ViewObjectGL3::createToolsMenu(QWidget * parent)
{
  return NULL;
}

void ViewObjectGL3::fillToolBar(QToolBar * toolBar)
{
}

void 
ViewObjectGL3::connectTo(ViewStatusBar3 * s)
{
  if(s){
    QObject::connect(this,SIGNAL(statusMessage(const QString&,int)),
		     s,SLOT(message(const QString&,int)) );  
    QObject::connect(this,SIGNAL(statusMessage(const QString&)),
		     s,SLOT(message(const QString&)) );  
		QObject::connect(this,SIGNAL(progressMessage(int,int)),
			s,SLOT(setProgress(int,int)) );  
  }
}

void 
ViewObjectGL3::connectTo(QGLWidget *g)
{
  if(g){
    QObject::connect (this,SIGNAL(valueChanged()),
		      g,SLOT(updateGL()) );
    __frame = g;
  }
}

void 
ViewObjectGL3::connectTo(ViewErrorDialog3 *e)
{
  if(e){
    QObject::connect(this,SIGNAL(errorMessage(const QString&)),
		     e,SLOT(setError(const QString&)) );
    QObject::connect(this,SIGNAL(warningMessage(const QString&)),
		     e,SLOT(appendWarning(const QString&)) );
    QObject::connect(this,SIGNAL(infoMessage(const QString&)),
		     e,SLOT(appendInfo(const QString&)) );
  }
}


void 
ViewObjectGL3::error(const QString& s)
{
  emit errorMessage(s);
}

void 
ViewObjectGL3::warning(const QString& s)
{
  emit warningMessage(s);
}

void 
ViewObjectGL3::info(const QString& s)
{
  emit infoMessage(s);
}

void 
ViewObjectGL3::status(const QString& s)
{
  emit statusMessage(s);
}

void 
ViewObjectGL3::status(const QString& s,int t)
{
  emit statusMessage(s,t);
}

void 
ViewObjectGL3::progress(int p,int t)
{
  emit progressMessage(p,t);
}

bool
ViewObjectGL3::glError(const char * file, int line) const
{
  return glError(__frame, file, line);
}

static bool lock = false;
bool ViewObjectGL3::BASHMODE = false;

bool
ViewObjectGL3::glError(QWidget * widget, const char * file, int line)
{
  GLenum _glerror;
  
  if((_glerror = glGetError()) != GL_NO_ERROR){
	  QString _mess = "<b>[ObjectGL] GL Error ["+QString::number(_glerror)+"] !!</b><br>";
	  int i = 0;
	  while(_glerror != GL_NO_ERROR && i < 10){
		  _mess +=(char *)gluErrorString(_glerror);
		  _mess += "<br>\n";
		  _glerror = glGetError();
		  i++;
	  }
	  if(file != NULL){
		  _mess += "<br><b>File :</b>";
		  _mess += file;
		  _mess += "<br><b>Line :</b>";
		  _mess += QString::number(line);
	  }
	  if(!BASHMODE){
		  if(!lock){
			  lock = true;
			  int res = QMessageBox::critical(widget,"GL Error",tr(_mess),"Abort","Continue");
			  if(res == 0 || res == -1){
				  abort();
			  }
			  lock = false;
		  }
	  }
	  else qWarning(tr(_mess));
	  return true;
  }
  return false;
}

/* ----------------------------------------------------------------------- */

ViewRelativeObjectGL3::ViewRelativeObjectGL3(ViewCameraGL3 *camera, QObject * parent, const char * name):
  ViewObjectGL3(parent,name),
  __step(1){
  if(camera){
    QObject::connect(camera,SIGNAL(stepMoveChanged(int)),this,SLOT(setStep(int)));
    QObject::connect(camera,SIGNAL(coordSys(int)),this,SLOT(coordSys(int)));
  }
}

ViewRelativeObjectGL3::ViewRelativeObjectGL3(ViewCameraGL3 *camera, QGLWidget * parent, const char * name):
  ViewObjectGL3(parent,name),
  __step(1){
  if(camera){
    QObject::connect(camera,SIGNAL(stepMoveChanged(int)),this,SLOT(setStep(int)));  
    QObject::connect(camera,SIGNAL(coordSysChanged(int)),this,SLOT(coordSys(int)));
  }
}

void 
ViewRelativeObjectGL3::connectTo(ViewCameraGL3 *camera)
{
  if(camera)
	QObject::connect(camera,SIGNAL(stepMoveChanged(int)),this,SLOT(setStep(int)));  
}

void 
ViewRelativeObjectGL3::connectTo(ViewStatusBar3 * s)
{
  ViewObjectGL3::connectTo(s);
}

void 
ViewRelativeObjectGL3::connectTo(QGLWidget *g)
{
  ViewObjectGL3::connectTo(g);
}

void 
ViewRelativeObjectGL3::connectTo(ViewErrorDialog3 *e)
{
  ViewObjectGL3::connectTo(e);
}


ViewRelativeObjectGL3::~ViewRelativeObjectGL3()
{
}

void
ViewRelativeObjectGL3::setStep(const int step)
{
  changeStepEvent(step,__step);
  __step = step;
}

void
ViewRelativeObjectGL3::changeStepEvent(const int newStep, const int oldStep)
{
}

const int 
ViewRelativeObjectGL3::getStep() const
{
  return __step;
}

void 
ViewRelativeObjectGL3::coordSys(int i)
{
  if(i == 1)geomCoordSys();
  else if(i == 0)glCoordSys();
}

void 
ViewRelativeObjectGL3::geomCoordSys()
{
}

void 
ViewRelativeObjectGL3::glCoordSys()
{
}

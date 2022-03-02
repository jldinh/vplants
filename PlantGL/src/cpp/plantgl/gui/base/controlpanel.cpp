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



#include <QtGui/qpushbutton.h>
#include <QtGui/qcheckbox.h>
#include <QtGui/qcolordialog.h>
#include <QtGui/qslider.h>
#include <QtGui/qlineedit.h>
#include <QtGui/qgroupbox.h>
#include <QtGui/qlabel.h>
#include <QtGui/qbuttongroup.h>
#include <QtGui/qdial.h>
#include <QtGui/qspinbox.h>
#include <QtGui/qlayout.h>
#include <QtGui/qmainwindow.h>

#include "controlpanel.h"
#include "glframe.h"
#include "camera.h"
#include "light.h"
#include "grid.h"
#include "scenegl.h"
#include "icons.h"
#include "util_qwidget.h"
#include "interface/controlpanelwidget.h"

PGL_USING_NAMESPACE

/* ----------------------------------------------------------------------- */


ViewControlPanel::ViewControlPanel( ViewGLFrame * _glframe,  
			    const QString & label, 
			    QMainWindow * mw )
    : QDockWidget( label, mw ),
	__useSpinBox(true)
{
	setObjectName("ControlPanel");
	// setSizePolicy(QSizePolicy::Maximum,QSizePolicy::Preferred);	
	QWidget * mwidget =  new QWidget(this);

	__panel = new Ui::ViewControlPanelWidget();
	__panel->setupUi(mwidget);
	setWidget(mwidget);
	// qDebug((QString::number(mwidget->size().width())+" x "+QString::number(mwidget->size().height())).toAscii().data());
	// qDebug((QString::number(size().width())+" x "+QString::number(height())).toAscii().data());

	QPixmap logo(ViewerIcon::getPixmap(ViewerIcon::logobar));
	__panel->mLogoButton->setIcon(QIcon(logo));
	__panel->mLogoButton->setIconSize(logo.size());
	QObject::connect(__panel->mLogoButton,SIGNAL(clicked(bool)),mw,SLOT(displayAbout()));


	ViewRendererGL * sc = _glframe->getSceneRenderer();
	ViewSceneRendererGL * sc2 = dynamic_cast<ViewSceneRendererGL *>(sc);

	if(sc2){
        QObject::connect(sc2->getLight(),SIGNAL(enabledChanged(bool)),
			   this,SLOT(setLightEnable(bool)) );
	}

	ViewCameraGL * camera = _glframe->getCamera();
	QObject::connect (__panel->__linkedZoom,SIGNAL(clicked()), camera,SLOT(lockDim()) ); 	
	QObject::connect (camera,SIGNAL(lockDimChanged(bool)), 	this,SLOT(setLinked(bool)) ); 	
	setLinked(camera->isDimLock());

	__panel->__zoomSpin->setRange(-DBL_MAX,DBL_MAX);
	__panel->__zoomSpin->setValue(camera->getZoom());

	__panel->__StepMove->setRange(0.01,DBL_MAX);
	__panel->__StepMove->setValue(camera->getStepMove());

	QObject::connect (camera,SIGNAL(elevationChanged(double)), 	
			__panel->__elevationSpin,SLOT(setValue(double)) ); 	
	QObject::connect (camera,SIGNAL(azimuthChanged(double)), 	
			__panel->__azimuthSpin,SLOT(setValue(double)) ); 	
	QObject::connect (camera,SIGNAL(zoomChanged(double)), 	
			__panel->__zoomSpin,SLOT(setValue(double)) ); 	

	QObject::connect (__panel->__elevationSpin,SIGNAL(valueChanged(double)),
			  camera,SLOT(setElevation(double)) );
	QObject::connect (__panel->__azimuthSpin,SIGNAL(valueChanged(double)),
			  camera,SLOT(setAzimuth(double)) );
	QObject::connect (__panel->__zoomSpin,SIGNAL(valueChanged(double)),
			  camera,SLOT(setZoom(double)) );

	QObject::connect (camera,SIGNAL(stepMoveChanged(double)),
			  __panel->__StepMove,SLOT(setValue(double)) ); 	
	QObject::connect (__panel->__StepMove,SIGNAL(valueChanged(double)),
			  camera,SLOT(setStepMove(double)) );

	//Light azimuth & elevation
	ViewLightGL * light = _glframe->getLight();
	


	__panel->__lightElevationSpin->setValue(light->getElevation());
	__panel->__lightAzimuthSpin->setValue(light->getAzimuth());
	__panel->__LightDistance->setRange(-DBL_MAX,DBL_MAX);
	__panel->__LightDistance->setValue(light->getDistance());

	QObject::connect (light,SIGNAL(elevationChanged(double)),
			  __panel->__lightElevationSpin,SLOT(setValue(double)) );
	QObject::connect (light,SIGNAL(azimuthChanged(double)),
			  __panel->__lightAzimuthSpin,SLOT(setValue(double)) );
	QObject::connect (light,SIGNAL(distanceChanged(double)),
			  __panel->__LightDistance,SLOT(setValue(double)) );

	QObject::connect (__panel->__lightElevationSpin,SIGNAL(valueChanged(double)),
			  light,SLOT(setElevation(double)) );
	QObject::connect (__panel->__lightAzimuthSpin,SIGNAL(valueChanged(double)),
			  light,SLOT(setAzimuth(double)) );
	QObject::connect (__panel->__LightDistance,SIGNAL(valueChanged(double)),
			  light,SLOT(setDistance(double)) );


	__LightAmbient = light->getAmbient();
	fillButton(__panel->__LightAmbientButton,__LightAmbient);

	__LightDiffuse = light->getDiffuse();
	fillButton(__panel->__LightDiffuseButton,__LightDiffuse);

	__LightSpecular = light->getSpecular();
	fillButton(__panel->__LightSpecularButton,__LightSpecular);

	QObject::connect (light,SIGNAL(ambientChanged(const QColor&)), 	
			  this,SLOT(setLightAmbient(const QColor&)) );
	QObject::connect (this,SIGNAL(lightAmbientChanged(const QColor&)),
			  light,SLOT(setAmbient(const QColor&)) );
	QObject::connect (__panel->__LightAmbientButton,SIGNAL(clicked()),
			  this,SLOT(selectLightAmbient()) );

	QObject::connect (light,SIGNAL(diffuseChanged(const QColor&)), 	
			  this,SLOT(setLightDiffuse(const QColor&)) );
	QObject::connect (this,SIGNAL(lightDiffuseChanged(const QColor&)),
			  light,SLOT(setDiffuse(const QColor&)) );
	QObject::connect (__panel->__LightDiffuseButton,SIGNAL(clicked()),
			  this,SLOT(selectLightDiffuse()) );

	QObject::connect (light,SIGNAL(specularChanged(const QColor&)), 	
			  this,SLOT(setLightSpecular(const QColor&)) );
	QObject::connect (this,SIGNAL(lightSpecularChanged(const QColor&)),
			  light,SLOT(setSpecular(const QColor&)) );
	QObject::connect (__panel->__LightSpecularButton,SIGNAL(clicked()),
			  this,SLOT(selectLightSpecular()) );



	//step for the grid
	ViewGridGL * grid = _glframe->getGrid();

    __panel->__unitGrid->setRange(0.01,DBL_MAX);
	__panel->__unitGrid->setValue(grid->getGridUnit());
	QObject::connect (grid,SIGNAL(GridUnitChanged(double)),
			  __panel->__unitGrid,SLOT(setValue(double)) ); 	
	QObject::connect (__panel->__unitGrid,SIGNAL(valueChanged(double)),
			  grid,SLOT(setGridUnit(double)) );

    __panel->__sizeGrid->setRange(1,INT_MAX);
	__panel->__sizeGrid->setValue(grid->getGridSize());

	QObject::connect (grid,SIGNAL(GridSizeChanged(int)),__panel->__sizeGrid,SLOT(setValue(int)) ); 	
	QObject::connect (__panel->__sizeGrid,SIGNAL(valueChanged(int)),grid,SLOT(setGridSize(int)) );

}


ViewControlPanel::~ViewControlPanel()
{
}

void
ViewControlPanel::setLinked(bool b)
{
  if(!b){
   QPixmap linked(ViewerIcon::getPixmap(ViewerIcon::linked));
   __panel->__linkedZoom->setIcon(QIcon(linked));
  }
  else {
   QPixmap unlinked(ViewerIcon::getPixmap(ViewerIcon::unlinked));
   __panel->__linkedZoom->setIcon(QIcon(unlinked));
  }
}

void
ViewControlPanel::setLightEnable(bool a)
{
  if(!a){
    __panel->mLightPage->hide();
  }
  else {
    __panel->mLightPage->show();
  }
}


void 
ViewControlPanel::setLightAmbient(const QColor& color)
{
  __LightAmbient = color;
  fillButton(__panel->__LightAmbientButton,color);
}

void 
ViewControlPanel::selectLightAmbient()
{

  QColor LightAmbient = QColorDialog::getColor(__LightAmbient,this);
  if(LightAmbient.isValid()){
	setLightAmbient(LightAmbient);
    emit lightAmbientChanged(__LightAmbient);
  }
}

void 
ViewControlPanel::setLightDiffuse(const QColor& color)
{
  __LightDiffuse = color;
  fillButton(__panel->__LightDiffuseButton,color);
}

void 
ViewControlPanel::selectLightDiffuse()
{

  QColor LightDiffuse = QColorDialog::getColor(__LightDiffuse,this);
  if(LightDiffuse.isValid()){
	setLightDiffuse(LightDiffuse);
    emit lightDiffuseChanged(__LightDiffuse);
  }
}

void 
ViewControlPanel::setLightSpecular(const QColor& color)
{
  __LightSpecular = color;
  fillButton(__panel->__LightSpecularButton,color);
}

void 
ViewControlPanel::selectLightSpecular()
{

  QColor LightSpecular = QColorDialog::getColor(__LightSpecular,this);
  if(LightSpecular.isValid()){
	setLightSpecular(LightSpecular);
    emit lightSpecularChanged(__LightSpecular);
  }
}

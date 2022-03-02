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

/*! \file view_rotcenter.h
    \brief Definition of the viewer class ViewRotCenterGL.
*/

#ifndef __view_rotcenter_h__
#define __view_rotcenter_h__

/* ----------------------------------------------------------------------- */

#include "object.h"

#include <plantgl/algo/opengl/util_gl.h>
#include <plantgl/math/util_vector.h>

#include <QtGui/qmenu.h>


/* ----------------------------------------------------------------------- */

namespace Ui { class RotCenterEdit; }

/* ----------------------------------------------------------------------- */

class QDockWidget;

/* ----------------------------------------------------------------------- */

/**   
   \class ViewRotCenterGL
   \brief A ViewRotCenterGL for GL Display

*/

/* ----------------------------------------------------------------------- */

class VIEW_API ViewRotCenterGL  : public ViewRelativeObjectGL
{
  Q_OBJECT
  Q_PROPERTY(int X READ x WRITE setX );
  Q_PROPERTY(int Y READ y WRITE setY );
  Q_PROPERTY(int Z READ z WRITE setZ );
  Q_PROPERTY(bool Visible READ isVisible WRITE changeVisibility );
  Q_PROPERTY(bool Active READ isActive WRITE changeActivation );
public:

  /// Constructor.
  ViewRotCenterGL(ViewCameraGL *camera,
		  QGLWidget * parent=0, 
		  const char * name=0);

  /// Destructor.
  virtual ~ViewRotCenterGL();

  /// Return whether self is visible.
  bool isVisible() const ;

  /// Return whether self is active.
  bool isActive() const;
  
  /// x coordinates
  int x() const;

  /// y coordinates
  int y() const;

  /// z coordinates
  int z() const;

  /// get the sliders that control this.
  QDockWidget * getSliders() const;

  /// Create a Tools menu that reflect the functionality of this.
  virtual QMenu * createToolsMenu(QWidget * parent);

  /// Fill toolBar to reflect the functionality of this.
  void fillToolBar(QToolBar * toolBar);

public slots:

  /// reinitialize value.
  void init();

  /// show 
  void show();

  /// hide
  void hide();
  
  /// Change Visibility
  void changeVisibility();

  /// Change Visibility
  void changeVisibility(bool);

  /// activate.
  void activate();

  /// center.
  void center();

  /// desactivate.
  void desactivate();

  /// Change Activation
  void changeActivation();

  /// Change Activation
  void changeActivation(bool);

  /// Set X Coordinates of this to \e x
  void setX(int x);

  /// Set Y Coordinates of this to \e y
  void setY(int y);

  /// Set Z Coordinates of this to \e z
  void setZ(int z);

  /// Set X Coordinates of this to \e x
  void setX(double x);

  /// Set Y Coordinates of this to \e y
  void setY(double y);

  /// Set Z Coordinates of this to \e z
  void setZ(double z);

  /// Initialize the rotating center.
  virtual void initializeGL();

  /// GL command for rotating center.
  virtual void paintGL(); 

  /// Change relative value.
  virtual void changeStepEvent(double newStep, double oldStep);

  signals:

  /// emit when visibility changed.
  void visibilityChanged(bool);
  
  /// emit when activation changed
  void activationChanged(bool);

  /// emit when X Coordinates changed.
  void XvalueChanged(int);
  
  /// emit when Y Coordinates changed.
  void YvalueChanged(int);
  
  /// emit when Z Coordinates changed.
  void ZvalueChanged(int);
  
  /// emit when X Coordinates changed.
  void XvalueChanged(double);
  
  /// emit when Y Coordinates changed.
  void YvalueChanged(double);
  
  /// emit when Z Coordinates changed.
  void ZvalueChanged(double);
  
protected :

  void setSliderStep(const int step);

  /// Sliders to control self coordinates.
  QDockWidget * __sliders;
  Ui::RotCenterEdit * __editor;

  /// Activation of this.
  bool __active;

  /// Visibility if this.
  bool __visible;

  /// Coordinates.
  TOOLS(Vector3) __position;

  /// display list.
  GLuint __displayList;

};

/* ----------------------------------------------------------------------- */
#endif


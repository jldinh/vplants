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
		
/*! \file view_qobjectbrowser.h
    \brief Definition of the viewer class ViewQObjectBrowser.
*/


#ifndef __view_qobjectbrowser_h__
#define __view_qobjectbrowser_h__

/* ----------------------------------------------------------------------- */

#include "util_qwidget.h"

/* ----------------------------------------------------------------------- */



/**   
   \class ViewQObjectBrowser
   \brief The Browser of the QObject of the viewer
*/

class VIEW_API ViewQObjectBrowser : public ViewDialog
{
    Q_OBJECT
	public:
    
    /// Constructor
    ViewQObjectBrowser(  QWidget * parent=0, 
		  const char * name=0, 
		  bool modal=FALSE);

    /// Destructor
    ~ViewQObjectBrowser();



protected:
    
  /// This event handler is called when a key is pressed for this widget. 
  virtual void keyPressEvent (QKeyEvent * e);
   
   
};


/* ----------------------------------------------------------------------- */

// __viewqobjectbrowser_h__
/* ----------------------------------------------------------------------- */
#endif


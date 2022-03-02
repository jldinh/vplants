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
			
#include "translator.h"

#ifndef SYSTEM_IS__CYGWIN

#include <QtCore/qtranslator.h>
#include <QtGui/qapplication.h>
#include <plantgl/tool/util_enviro.h>

static QTranslator * fr = NULL;

void 
removeTranslator(){
  if(fr)qApp->removeTranslator(fr);
}

void setFrenchTranslator()
{
#ifdef __MINGW32__
# warning Translation message not set because of excessive computation time
#else
  if(!fr){
	  // load french translator
	  fr = new QTranslator(NULL);
	  fr->load("pglviewer.fr",(TOOLS(getPlantGLDir())+"share/plantgl/lang/").c_str());
 
  }

  qApp->installTranslator( fr );
 // qWarning("French Translator installed");
#endif
}

QStringList 
getAvailableLanguage(){
  QStringList l("English");
  l.append("French");
  return l;
}
#endif
/* ----------------------------------------------------------------------- */

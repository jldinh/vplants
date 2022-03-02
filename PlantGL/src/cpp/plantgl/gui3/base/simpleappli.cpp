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
 *       $Id: simpleappli.cpp 4276 2008-01-29 13:14:17Z boudon $
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

#include "simpleappli.h"
#include "viewer.h"
#include <qapplication.h>

ViewerSimpleAppli3::ViewerSimpleAppli3():ViewerAppli3(), __viewer(0),__appli(0), __ownappli(false) { launch(); }

ViewerSimpleAppli3::~ViewerSimpleAppli3(){
	if(isRunning()) exit();
	if(__appli && __ownappli)delete __appli;
	if(__viewer) delete __viewer;
}

void 
ViewerSimpleAppli3::startSession()
{ if(!isRunning()) __viewer->show(); }

bool 
ViewerSimpleAppli3::stopSession()
{ if(isRunning()) { __viewer->hide(); return true; } else return false; }

bool 
ViewerSimpleAppli3::exit()
{ 
	if(__appli && __ownappli) { __appli->quit(); return true; }
	else return false;
}

void 
ViewerSimpleAppli3::sendAnEvent(QCustomEvent *e)
{ QApplication::sendEvent(__viewer,e); delete e; }

void 
ViewerSimpleAppli3::postAnEvent(QCustomEvent *e)
{ QApplication::postEvent(__viewer,e); }

bool 
ViewerSimpleAppli3::isRunning() 
{ return __viewer != NULL && __viewer->isShown(); }

bool 
ViewerSimpleAppli3::Wait ( unsigned long time  )
{ return false; }

const std::vector<uint_t> 
ViewerSimpleAppli3::getSelection(){
	if(__viewer)return __viewer->getSelection();
	else return std::vector<uint_t>();
}

QApplication * 
ViewerSimpleAppli3::getApplication()
{ return __appli; }

void
ViewerSimpleAppli3::launch(){
	if(qApp != NULL){
		__appli = qApp;
		__ownappli = false;
		__viewer = build();
		if(__appli->mainWidget() == NULL)
			__appli->setMainWidget(__viewer);
		__viewer->show();
	}
	else {
		int argc = 0;
		__appli = new QApplication(argc,NULL);
		__ownappli = true;
		__viewer = build();
        __appli->setMainWidget(__viewer);
		__viewer->show();
		__appli->exec();
	}
}


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
 *       $Id: threadedappli.cpp 4276 2008-01-29 13:14:17Z boudon $
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



#include "threadedappli.h"

#ifdef QT_THREAD_SUPPORT

#include <qapplication.h>
#include "viewer.h"
#include "event.h"
#include <plantgl/tool/dirnames.h>

TOOLS_USING_NAMESPACE

ViewerThreadedAppli3::ViewerThreadedAppli3() : 
			 ViewerAppli3(), QThread(),
		     __appli(NULL),
			 __viewer(NULL) { launch();}


ViewerThreadedAppli3::~ViewerThreadedAppli3(){ 
};

void 
ViewerThreadedAppli3::startSession(){
    if(!running())   launch();
	else if(!isRunning()) contcond.wakeAll();
}

bool 
ViewerThreadedAppli3::stopSession(){
    if(isRunning()){
	   sendAnEvent(new ViewEndEvent3());
       return true;
    }
    else return false;
}

bool 
ViewerThreadedAppli3::exit() {
    if(running()){
	  startSync();
	  __continue.unlock();
	  if(!__running.locked())contcond.wakeAll();
	  else  sendAnEvent(new ViewEndEvent3());
	  sync();
	  terminate();
      return true;
    }
	else return false;
}

void 
ViewerThreadedAppli3::sendAnEvent(QCustomEvent *e) {
	startSession();
	__viewer.get()->send(e);
}

void 
ViewerThreadedAppli3::postAnEvent(QCustomEvent *e) {
	startSession();
	__viewer.get()->post(e);
}

bool 
ViewerThreadedAppli3::isRunning() {
   return running() && __running.locked(); 
}

bool 
ViewerThreadedAppli3::Wait ( unsigned long time ) {
   return session.wait(time);
}

void 
ViewerThreadedAppli3::launch(){ 	
	if(!__continue.locked())__continue.lock(); 
	startSync(); start(); sync(); 
}

void 
ViewerThreadedAppli3::startSync() { syncmutex.lock(); }

void 
ViewerThreadedAppli3::sync() { synccond.wait(&syncmutex); syncmutex.unlock(); }

void 
ViewerThreadedAppli3::join() { while(syncmutex.locked()); synccond.wakeAll(); }


void 
ViewerThreadedAppli3::init(){
    int argc = 0;
    char ** argv = NULL;
    if(!__appli)  __appli.set(new QApplication(argc,argv));
    if(!__viewer) {
	   __viewer.set(build());
       __appli.get()->setMainWidget(__viewer);
    }
}

void 
ViewerThreadedAppli3::cleanup(){
	if(__viewer)delete __viewer;
	if(__appli)delete __appli;
	__viewer.set(NULL);
	__appli.set(NULL);
}

void 
ViewerThreadedAppli3::exec(){
      __viewer.get()->show();
	  __viewer.get()->displayTrayIcon(false);
	  __appli.get()->exec();
	  __viewer.get()->saveConfig();
	  __selection = __viewer.get()->getSelection();
}

void 
ViewerThreadedAppli3::run(){
	init();
	std::string p = get_cwd();
    __running.lock();
	join();
	while(__continue.locked()){
	  exec();
	  session.wakeAll();
	  if(__continue.locked())
		  contcond.wait(&__running);
	}
    __running.unlock();
	chg_dir(p);
	cleanup();
	join();
}

const std::vector<uint_t>
ViewerThreadedAppli3::getSelection() {
	std::vector<uint_t> res;
    if(isRunning()){
      ViewSelectRecoverEvent3 * event = new ViewSelectRecoverEvent3(&res) ;
      sendAnEvent(event);
    }
    else  res = __selection;
    return res;
}


#endif

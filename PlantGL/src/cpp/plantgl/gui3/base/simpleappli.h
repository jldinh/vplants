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
 *       $Id: simpleappli.h 4276 2008-01-29 13:14:17Z boudon $
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

#ifndef __view_simpleappli_h__
#define __view_simpleappli_h__


#include "appli.h"

class QApplication;
class Viewer;

class ViewerSimpleAppli3 : public ViewerAppli3 {
public:
	ViewerSimpleAppli3();
	virtual ~ViewerSimpleAppli3();

	virtual void startSession();
	virtual bool stopSession();
	virtual bool exit();
	virtual void sendAnEvent(QCustomEvent *e) ;
	virtual void postAnEvent(QCustomEvent *e) ;

    virtual bool isRunning() ;
    virtual bool Wait ( unsigned long time = ULONG_MAX ) ;

	virtual const std::vector<uint_t> getSelection();

	QApplication * getApplication();

protected:

	void launch();

	Viewer3 * __viewer;
	QApplication * __appli;
	bool __ownappli;
};

#endif


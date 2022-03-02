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
 *       $Id: util_serializedobj.h 2725 2007-02-27 15:08:52Z boudon $
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


#ifndef __serialized_obj_h__
#define __serialized_obj_h__

#ifdef QT_THREAD_SUPPORT

#include <qmutex.h>

template <class T>
class ViewSerializedObject3 {

public:
  ViewSerializedObject3(T val):
	  __val(val){
	}

  ViewSerializedObject3 operator = (T val) {
	set(val);
	return *this;
  }

  operator const T () {
	QMutexLocker l(&__mutex);
	const T val = __val;
	return val;
  }

  const T get() {
	QMutexLocker l(&__mutex);
	const T val = __val;
	return val;
  }

  void set(T val) {
	QMutexLocker l(&__mutex);
	__val = val;
  }


private:
  T __val;
  QMutex __mutex;

};

#endif

#endif


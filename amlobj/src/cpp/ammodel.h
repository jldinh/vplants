/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): Ch. Godin (christophe.godin@cirad.fr)
 *
 *       $Source$
 *       $Id: ammodel.h 3259 2007-06-06 13:40:30Z dufourko $
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




#ifndef AMMODEL_HEADER
#define AMMODEL_HEADER

#include <iostream>

#include "amobj.h"

struct GP_window;

class AMModel {

  friend struct AMObj;
  friend class PFNode;

  int _refcount; // nb of existing copies of the object

protected:

        AMModel() :_refcount(0){}
  AMModel(const AMModel&) : _refcount(0){}

  void lock() {_refcount++;}
  void unlock() {_refcount--;assert(_refcount >= 0);}

  int isLocked() const {return (_refcount > 0);}

public:

  virtual ~AMModel() {};

  virtual AMObj display(std::ostream& o, const AMObjVector& args) const;
  virtual AMObj plot(GP_window&, const AMObjVector& args) const;
  virtual AMObj extract(const AMObjVector& args) const;

  virtual AMObj save(const AMObjVector& args) const;
  virtual AMObj print(const AMObjVector& args) const;
  virtual std::ostream& displayOneLine(std::ostream&) const = 0;

};


#endif

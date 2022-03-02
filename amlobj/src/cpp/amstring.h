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
 *       $Id: amstring.h 3259 2007-06-06 13:40:30Z dufourko $
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




#ifndef AMSTRING_HEADER
#define AMSTRING_HEADER

#include "ammodel.h"

class AMString : public RWCString, public AMModel {

public:

  AMString(const char* stg) : RWCString(stg) {};
  AMString( char c) : RWCString(c) {};
  AMString( const RWCString& stg) : RWCString(stg) {};

  virtual ~AMString() {};

  virtual std::ostream& displayOneLine(std::ostream& o) const {return o << *this;}
  virtual AMObj display(std::ostream& o, const AMObjVector& args) const {assert(&args); displayOneLine(o); return AMObj(AMObjType::VOID);}

  virtual AMObj print(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}
  virtual AMObj save(const AMObjVector& args) const {assert(&args); return AMObj(AMObjType::VOID);}

};

#endif

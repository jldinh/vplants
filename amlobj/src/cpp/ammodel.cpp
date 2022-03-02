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
 *       $Id: ammodel.cpp 3259 2007-06-06 13:40:30Z dufourko $
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




#include <stdlib.h>

#include "ammodel.h"
#include "parseraml.h"
#include "kernel_err.h"
#include "amstring.h"

#define  remove_warning(obj)   {if (&obj);}

using namespace std;

static const char* PRINTFILE = "/tmp/lp.aml";


AMObj AMModel::display(ostream& o, const AMObjVector& args) const {
  remove_warning(o);
  remove_warning(args);
  AMLOUTPUT << "Function Display Not Implemented on that object" << endl;
  return AMObj(AMObjType::UNDEF);
}

AMObj AMModel::save(const AMObjVector& args) const {
  remove_warning(args);
  AMLOUTPUT << "Function Save Not Implemented on that object" << endl;
  return AMObj(AMObjType::UNDEF);
}

AMObj AMModel::plot(GP_window&, const AMObjVector& args) const {
  remove_warning(args);
  AMLOUTPUT << "Function Plot Not Implemented on that object" << endl;
  return AMObj(AMObjType::UNDEF);
}

AMObj AMModel::extract(const AMObjVector& args) const {
  remove_warning(args);
  AMLOUTPUT << "Function Extract Not Implemented on that object" << endl;
  return AMObj(AMObjType::UNDEF);
}

AMObj AMModel::print(const AMObjVector& args) const {

  int len = args.length();

  assert(len >= 1);

  AMObjVector newargs(len+1);

  newargs[0] = args[0];
  newargs[1] = AMObj(AMObjType::STRING, new AMString(PRINTFILE));

  for (int i = 1; i<len; i++) newargs[i+1] = args[i];

  save(newargs);

  RWCString command("a2ps ");

  command += PRINTFILE;

  system(command.data());

  command = "\\rm ";
  command += PRINTFILE;

  system(command.data());

  return AMObj(AMObjType::VOID);

}

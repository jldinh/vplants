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
 *       $Id: utils.cpp 3258 2007-06-06 13:18:26Z dufourko $
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
#include "tool/util_math.h"

#include "utils.h"

#ifndef MAXLONG
#define MAXLONG LONG_MAX
#endif

using namespace std;

//static const char rcsid[] = "$Id: utils.cpp 3258 2007-06-06 13:18:26Z dufourko $";

ostream& operator<<(ostream& o, const String& obj) {

  return obj.print(o);

}

const long MAXRANDOM = MAXLONG;

// returns a random long between a and b (included) uniformely.
long randomNbInRange(long a, long b) {

  double r = ((double)random())/(double)MAXRANDOM;

  return (long) (a+ (long) rint((b-a)*r)) ; // rint takes the nearest integer
}


// returns a random double between 0 and 1 (included) uniformely.
double randomDouble() {

  return ((double)random())/(double)MAXRANDOM;

}

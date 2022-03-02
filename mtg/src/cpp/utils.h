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
 *       $Id: utils.h 17611 2014-10-17 13:20:41Z pradal $
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




#ifndef UTILS_HEADER
#define UTILS_HEADER

#include <string.h>

#ifdef _WIN32
#define random rand
#endif

#include "aml/defs.h"

#ifndef _WIN32
inline int max(int a, int b) {return (a<b ? b : a);}
inline int min(int a, int b) {return (a>=b ? b : a);}
#endif

long randomNbInRange(long a, long b);
double randomDouble();

// La class String est utilisee partout ou il y a besoin de chaine de caracteres
// de TAILLE FIXEE dans le code.

class String { // String plus elaboree (C++) de taille fixee.

  friend std::ostream& operator<<(std::ostream&, const String&);

  CString s;

public:

  String() {s[0] = '\0';}
  String(const char* st) {strncpy(s, st, MAXSTRINGSIZE);}
  String(const String& st) {strncpy(s, st.s, MAXSTRINGSIZE);}
  ~String() {}

  String& operator=(const String& st) {strncpy(s, st.s, MAXSTRINGSIZE); return *this;}
  String& operator=(const char* st) {strncpy(s, st, MAXSTRINGSIZE); return *this;}

  AmlBoolean operator==(const String& st) const {return !strcmp(s, st.s);}
  AmlBoolean operator==(const char* st) const {return !strcmp(s, st);}

  const char* operator()() const {return s;}
  char& operator[](int i) {return s[i];}
  const char& operator[](int i) const {return s[i];}

  std::ostream& print(std::ostream& o) const {o << (char*) s; return o;}

};

std::ostream& operator<<(std::ostream& o, const String& obj);


class Intervalle {

  int _min;
  int _max;

public:

  Intervalle() {_min=0; _max=0;}
  Intervalle(int i, int j) {i<=j ? (_min=i, _max=j): (_min=0, _max=MAXINT);}

  int& Min() {return _min;}
  int& Max() {return _max;}

  AmlBoolean isIn(int i) const {return (i>=_min && i<=_max);}

};


#endif

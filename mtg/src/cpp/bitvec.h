#ifndef CPL
#define CPL
#endif
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
 *       $Id: bitvec.h 17611 2014-10-17 13:20:41Z pradal $
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



#ifndef BITVEC_HEADER
#define BITVEC_HEADER


// macro BITS presente dans Irix:<values.h>
#ifndef SYSTEM_IS__IRIX

#include <climits>
#include <float.h>

#define BITS(type)      (CHAR_BIT * (int)sizeof(type))
#else
#include  <values.h>
#endif

#include <iostream>
#ifndef CPL
using namespace std;
#endif
// Classe permettant de gerer des drapeaux dans les objets:
//
// soit un objet O de type Obj. Il contient un champ fs de type BitVec
// qui permet de positionner des flags sur cet objet.
//
// on definit tout d'abord un ensemble de variables de classe constantes
// qui correspondent aux differentes proprietes que l'on veut
// enregistrer sur l'objet:
//
// class Obj {
// ...
// enum FLAGS {BLUE = 0, RED, GREEN};
// BitVec fs;
// ...
// }
//
// Les enum Obj::BLUE et Obj::RED sont des constantes entieres locales a
// la classe Obj.
//
// initialiser un objet: Obj o(RED); qui appelle le constructeur de Obj
// defini par:
//
// Obj::Obj(int i) : fs(i) {
//
// }
// (Ce constructeur utilise la convertion implicite d'un enum -> int)

// A l'utilisation on aura par exemple:
//
// Obj o(RED);          // Le flag RED est positionne ON a la creation de l'objet
// o.fs.print(str)      // imprime 01000000 correspondant a RED
// o.fs.Raise(BLUE);    // Le flag ON est positionne
// o.fs.print(str)      // imprime 11000000 correspondant a RED + BLUE
// o.fs.Clear(RED);     // efface le flag RED
// o.fs.print(str);     // imprime 10000000 correspondant a BLUE

#ifndef CPL
#ifndef AmlBoolean
#define AmlBoolean int
#endif
#else
#include "aml/defs.h"
#endif

typedef unsigned char BITVECTYPE; // 8 bits sont disponibles

class BitVec {

  friend BitVec operator&(const BitVec&, const BitVec&);
  friend BitVec operator|(const BitVec&, const BitVec&);

  BITVECTYPE flags;

public:

  // La classe propose la gestion de BITS(BITVECTYPE) flags
  // ex: pour BITVECTYPE = unsigned int, il y a 32 flags (bits)
  // disponibles numerotes de 0 a 31.

  static int size() {return BITS(BITVECTYPE);}

  BitVec(int i) {flags = (BITVECTYPE)01 << i ;}
  BitVec(BITVECTYPE i) {flags = i;} // unsigned int can be overloaded by int if necessary
  BitVec(const BitVec& fs) {flags = fs.flags;}
  BitVec() {flags = (BITVECTYPE)0;}

  BitVec& operator=(const BitVec& fs) {this->flags = fs.flags; return *this;}

  BitVec& operator|=(const BitVec& fs) {flags |= fs.flags; return *this;}
  BitVec& operator|=(int f) {flags |= ((BITVECTYPE)01 << f) ; return *this;}
  BitVec& operator&=(const BitVec& fs) {flags &= fs.flags; return *this;}
  BitVec& operator&=(int f) {flags &= ((BITVECTYPE)01 << f) ; return *this;}
  BitVec& operator-=(const BitVec& fs) {flags &= ~fs.flags; return *this;}
  BitVec& operator-=(int f) {flags &= ~((BITVECTYPE)01 << f) ; return *this;}

  BitVec operator~() const {return (BITVECTYPE) ~flags;} // {BitVec b; b.flags = ~flags; return b;}

  BitVec& operator()(int f) {flags |= ((BITVECTYPE)01 << f) ; return *this;}

  void set(int f) {flags |= ((BITVECTYPE)01 << f) ;}
  void clear(int f) {flags &= ~((BITVECTYPE)01 << f) ;}
  void clear() {flags = (BITVECTYPE)0;} // clear all bits
  void set() {flags = (BITVECTYPE)0; flags = ~flags;} // set all bits

  AmlBoolean isSet(BitVec fs) const {return (AmlBoolean) (flags & fs.flags);}
  AmlBoolean isSet(int f) const {return (AmlBoolean) (flags & ((BITVECTYPE)01 << f));}
  AmlBoolean isSet() const {return (AmlBoolean) flags;}
  AmlBoolean isOnlySet(BitVec fs) const {return (AmlBoolean) ( (flags & fs.flags) == flags);}
  AmlBoolean isOnlySet(int f) const {return (AmlBoolean) ((flags & ((BITVECTYPE)01 << f)) == flags);}
  AmlBoolean isClear() const { return (AmlBoolean) !flags; }

  int firstTrue() const; // retourne l'index du premier flag leve; ex: 3 si flags == 0010
                         // retourne 0 si tous les flags sont baisses

  AmlBoolean operator*() const {return (AmlBoolean) flags;}         // like isSet

  AmlBoolean operator==(AmlBoolean b) const {return b == isSet();}
  AmlBoolean operator==(const BitVec& fs) const {return flags == fs.flags;}

  AmlBoolean operator!=(AmlBoolean b) const {return b != isSet();}
  AmlBoolean operator!=(const BitVec& fs) const {return flags != fs.flags;}

  int nbBitsSet() const;

  std::ostream& print(std::ostream&) const;
};

BitVec operator&(const BitVec& fs1, const BitVec& fs2);
BitVec operator|(const BitVec& fs1, const BitVec& fs2);

std::ostream& operator<<(std::ostream&, const BitVec&);

#ifdef CPL
typedef BitVec EType;

const EType PLUS(0);
const EType LESS(1);
const EType SLASH(2);
const EType PLUSPLUS(3);
const EType LESSLESS(4);
const EType LESSDOTLESS(5);
const EType PLUSDOTPLUS(6);
const EType NONE;
const EType ANY(~NONE);
const EType ANYTOPO(PLUS | LESS | PLUSPLUS | LESSLESS);
const EType ANYLESS(LESS | LESSLESS);
const EType ANYPLUS(PLUS | PLUSPLUS);
#endif

#endif

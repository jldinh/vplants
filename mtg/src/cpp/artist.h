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
 *       $Id: artist.h 3258 2007-06-06 13:18:26Z dufourko $
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




#ifndef MTGARTIST_HEADER
#define MTGARTIST_HEADER

#include <fstream>

#include "mtg.h"
#include "geom.h"

typedef struct {

  Vect o; // origine
  Vect p; // principal direction
  Vect q; // secundary direction
  Vect r; // p ^ q

} VGeom;

class MTGArtist {

  MTG* _mtg;

  std::ofstream _file;

  void drawSubXtreeMtg(VId);
  void drawSubLtreeMtg(VId, EType, VGeom);
  int writeInfo(const char* file, float age, int nbb, int graine, int simplification, float *max, float *min);
  void writeMTGheader(const MTGHeader* header);
  void findCodeFromRoot(VId v);

public:

  MTGArtist(MTG*);
  ~MTGArtist() {}

  const MTG* mtg() const {return _mtg;}

  int drawXtreeMtg(int scale, const char* file);    // create a file for xtree
  int drawXtreeMtg(const char* file);         // create a file for xtree for every scale

  int drawEdgeMtg(const char* file);         // create a file for xtree for every scale

  int drawLtreeMtg(int scale, const char* file); // create a file for glance

  int createMTGCode(const char* file);

};


#endif

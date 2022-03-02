/*  -*-c++-*-----------------------------------------------------------------
 *  Amapmod                   CIRAD - Laboratoire de Modelisation des Plantes
 *
 *  $Source$
 *  $Id: drawmtg.cpp 3854 2007-10-16 14:10:26Z boudon $
 *
 *  -------------------------------------------------------------------------
 * 
 *  Note: Test le module "mtgartist.[Ch]" 
 *           
 *  -------------------------------------------------------------------------
 *
 *  $Log$
 *  Revision 1.1  2002/10/07 15:40:40  fboudon
 *  no message
 *
 *  Revision 1.1.1.1  2001/01/31 16:54:45  godin
 *  AMAPmod v1.6 imported into CVS
 *
 *  Revision 1.1  2001/01/10 08:34:18  godin
 *  files used for testing the MTG module
 *
 *  Revision 1.1  2000/02/15 11:14:05  amapmod
 *  Initial revision
 *
 *  Revision 1.1  1999/08/10 11:44:03  godin
 *  Initial revision
 *
 *
 *  -------------------------------------------------------------------------
 */

#include <fstream>
#include <string.h>
#include <assert.h>

#include "mtg.h"
#include "artist.h"

//static const char rcsid[] = "$Id: drawmtg.cpp 3854 2007-10-16 14:10:26Z boudon $";



// different scans of the MTG

void createLineTree(MTG* the_mtg) {

  assert(the_mtg);

  MTGArtist painter(the_mtg);

  painter.drawLtreeMtg(1, the_mtg->filename());

}

void createXTree(MTG* the_mtg) {

  assert(the_mtg);

  MTGArtist painter(the_mtg);

  painter.drawXtreeMtg(the_mtg->filename());

}

void createEdgeTree(MTG* the_mtg) {

  assert(the_mtg);

  MTGArtist painter(the_mtg);

  painter.drawEdgeMtg(the_mtg->filename());

}

void createCodeFile(MTG* the_mtg) {

  assert(the_mtg);

  MTGArtist painter(the_mtg);

  painter.createMTGCode(the_mtg->filename());

}

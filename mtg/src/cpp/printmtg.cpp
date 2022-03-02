/*  -*-c++-*-----------------------------------------------------------------
 *  Amapmod                   CIRAD - Laboratoire de Modelisation des Plantes
 *
 *  $Source$
 *  $Id: printmtg.cpp 17611 2014-10-17 13:20:41Z pradal $
 *
 *  -------------------------------------------------------------------------
 * 
 *  Note: 
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
 *  Revision 1.1  1999/08/10 13:37:05  godin
 *  Initial revision
 *
 *
 *  -------------------------------------------------------------------------
 */

#include <fstream>
#include <string.h>
#include <assert.h>

#include "mtg.h"

//static const char rcsid[] = "$Id:";

using namespace std;

static AmlBoolean testLabel(MTG* mtg, VId x, void* c) {

  int xclass = mtg->vclass(x);
  char symb = mtg->classSymbol(xclass);

  if (symb == ((char*) c)[0]) return TRUE;
  else return FALSE;

}


// different scans of the MTG

void printMTGScans(MTG* the_mtg) {

  VId root = the_mtg->mtgRoot();

  cout << "Depth First (prefix) list from vertex 1: \n";
  MTGDepthFirstIter* next = new MTGDepthFirstIter(the_mtg, (VId)1, &MTG::topoSons, ANYTOPO);
  while((*next)()) {
    VId son = next->key();
    cout << son << " ";
  }
  cout << endl;
  delete next;

  cout << "Depth First (postfix) list from vertex 1: \n";
  MTGPostFixIter* next1 = new MTGPostFixIter(the_mtg, 1, &MTG::topoSons, ANYTOPO);
  while((*next1)()) {
    VId son = next1->key();
    cout << son << " ";
  }
  cout << endl;
  delete next1;

  cout << "Depth First (postfix) list from root: \n";
  next1 = new MTGPostFixIter(the_mtg, root, &MTG::topoSons, ANYTOPO);
  while((*next1)()) {
    VId son = next1->key();
    cout << son << " ";
  }
  cout << endl;
  delete next1;

  cout << "Depth First (postfix) list from root with filter: \n";
  next1 = new MTGPostFixIter(the_mtg, root, &MTG::topoSons, ANYTOPO);
  char c = 'A'; // list only the vertex of class A
  while(next1->findNext(testLabel, &c)) {
    VId son = next1->key();
    cout << son << " ";
  }
  cout << endl;
  delete next1;
  /*
  cout << "Breadth First list from vertex 1: \n";
  MTGBreadthFirstIter* next2 = new MTGBreadthFirstIter(the_mtg, 1, &MTG::topoSons, ANYTOPO);
  while((*next2)()) {
    VId son = next2->key();
    cout << son << " ";
  }
  cout << endl;
  delete next2;
  
  cout << "Breadth First list from root: \n";
  next2 = new MTGBreadthFirstIter(the_mtg, root, &MTG::topoSons, ANYTOPO);
  while((*next2)()) {
    VId son = next2->key();
    cout << son << " ";
  }
  cout << endl;
  delete next2;
  */
  cout << "Component lists from root: \n";
  int rootscale = the_mtg->vscale(root);    
  MTGDepthFirstIter* next3 = new MTGDepthFirstIter(the_mtg, root, &MTG::topoSons, ANYTOPO);
  while ((*next3)()) {
    VId son = next3->key();
    cout << "vertex " << son << " : ";      
    MTGDepthFirstIter* next4 = new MTGDepthFirstIter(the_mtg, son, &MTG::sons, SLASH);
    while((*next4)()) {
      VId component = next4->key();
      cout << component << " ";	
    }
    cout << endl;
    delete next4;
  }
  cout << endl;
  delete next3;


}

void printMTG(MTG* the_mtg) {

  assert(the_mtg);

  the_mtg->print(cout);

}

void printMTGStats(MTG* the_mtg) {

  assert(the_mtg);

  the_mtg->printStat(cout);

}


/*  -*-c++-*-----------------------------------------------------------------
 *  Amapmod                   CIRAD - Laboratoire de Modelisation des Plantes
 *
 *  $Source$
 *  $Id: loadmtg.cpp 3854 2007-10-16 14:10:26Z boudon $
 *
 *  -------------------------------------------------------------------------
 * 
 *  Note:
 *           
 *  -------------------------------------------------------------------------
 *
 *  $Log$
 *  Revision 1.2  2002/10/08 11:46:22  fboudon
 *  no message
 *
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
 *  Revision 1.2  1999/12/10 10:48:48  godin
 *  Include of mtg.h as ".." not <..>
 *
 *  Revision 1.1  1999/08/10 13:36:30  godin
 *  Initial revision
 *
 *
 *  -------------------------------------------------------------------------
 */

#include <stdlib.h>
#include <iostream>
#include <string.h>
#include <assert.h>

#include "mtg.h"

extern void createLineTree(MTG*);
extern void createXTree(MTG*);
extern void createEdgeTree(MTG*);
extern void createCodeFile(MTG*);
extern void printMTG(MTG*);
extern void printMTGScans(MTG*);
extern void printMTGStats(MTG*);

using namespace std;

//static const char rcsid[] = "$Id: loadmtg.cpp 3854 2007-10-16 14:10:26Z boudon $";

static int main_usage(char* name) {
  cerr << "usage: " << name << " [+<number>] [-pgxcls] [file]+" << endl;
  cerr << "\t+<nb>: iterates nb times MTG loading and subsequent actions" << endl;
  cerr << "\t-p : list the mtg on the standard output" << endl;
  cerr << "\t-g : create a file which can be read by 'glance' (suffix = .lig)" << endl;
  cerr << "\t-x : create a file which can be read by 'xtree'  (suffix = .xtree)" << endl;
  cerr << "\t-e : create a file which can be read by 'edge'  (suffix = .edge)" << endl;
  cerr << "\t-c : create a file which contains a readable ascii mtg code  (suffix = .MTG)" << endl;
  cerr << "\t-l : give different scans and listings on an MTG" << endl;
  cerr << "\t-s : gives a brief output statistics of an MTG" << endl;
  cerr << "ex   : " << name << " +10 -px  mtg1 mtg2" << endl;
  return(0);
}

static void processItem(char* file, char* options) {

  MTG* the_mtg = 0;
  int optlen = 0;

  if (options) optlen = strlen(options);

  assert(file);

  the_mtg = new MTG(file); 
  assert(the_mtg);

  if (the_mtg->isValid()) {

    cerr << "MTG built ..." << endl;

    for(int i=0; i<optlen; i++) {

      switch(options[i]) {

      case 'p': // print the graph contents on the stdoutput
	printMTG(the_mtg);
	break;

      case 'g': // create a linetree
	createLineTree(the_mtg);
	break;

      case 'x': // create a xtree
	createXTree(the_mtg);
	break;

      case 'e': // create a xtree
	createEdgeTree(the_mtg);
	break;

      case 'c': // create a xtree
	createCodeFile(the_mtg);
	break;

      case 'l': // give different scans on an MTG
	printMTGScans(the_mtg);
	break;

      case 's': // 
	printMTGStats(the_mtg);
	break;

      default:
	break;

      }

    }

    delete the_mtg;

  }

}

int main(int argc, char** argv) {

  int loop = 1;
  char* options = 0;

  /* process arguments */
  char* exec_name = *argv;

  if (argc == 1) return main_usage(exec_name);

  argc--;
  argv++;

  if (**argv == '+') {

    loop = atoi(*(argv)+1); // on recupere l'entier
    if (loop <= 0) return main_usage(exec_name);

  }
  else {
    argc++;
    argv--;
  }
  
  argc--;
  argv++;

  if (**argv == '-') {

    options = new char[strlen(*argv)];

    strcpy(options, (*argv)+1);

  }
  else {
    argc++;
    argv--;
  }

  for(int i=0; i<loop; i++) {

    int nbfile = argc;
    char** filept = argv;

    while (--nbfile > 0) {

      ++filept;

      processItem(*filept, options);

    }

  }

  delete [] options;

  return 1;
}

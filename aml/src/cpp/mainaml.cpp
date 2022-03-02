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
 *       $Id: mainaml.cpp 16113 2014-03-18 16:59:20Z pradal $
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




#include <iostream>
#include <stdlib.h>
#include <string>
#include <assert.h>
#ifndef __GNUC__
#include <new.h>
#else
#include <new>
#endif
#include <signal.h>
#include <setjmp.h>

#include "aml/date.h"
#include "tool/util_enviro.h"
#include "tool/dirnames.h"

#ifdef _WIN32
#include "aml/guicon.h"
#endif

#include "aml/readline.h"
#include "aml/fnode.h"
#include "aml/amobj.h"
#include "aml/parseraml.h"
#include "aml/global.h"
#include "aml/gnuplot_pipe.h"

#include "aml/install.h"

#include "aml/release.h"

VPTOOLS_USING_NAMESPACE
using namespace std;

static const char* INIT_FILE = ".aml";

static jmp_buf jump_stack_env;


static void interrupt_handler(int);

static void install_signal_handlers() {
  if(signal(SIGINT, interrupt_handler) == SIG_ERR) // for ctrl-c
          cerr << "Warning ! Ctrl-C not controled" << endl;
}

static void interrupt_handler(int) {
        install_signal_handlers();  // need to be reinstalled every time
  //cout << "Interruption (to exit, type \"bye\") ... " << endl;
  longjmp(jump_stack_env, 1); // to get back to a well know state (1 will be the value returned by setjmp)
}


static int main_usage(const char* name) {

  cerr << "usage: " << name << " [-i [file]] [+i file [files]] [-b file] [-l]" << endl << endl;
  cerr << "By default, " << name << " is set up in interactive mode" << endl;
  cerr << "\t-h        : gives this command line help" << endl;
  cerr << "\t-b   file : batch mode on a file" << endl;
  cerr << "\t-i  [file]: default initialization file to load instead of .aml (none is loaded if file is missing)" << endl;
  cerr << "\t+i   files: load other initialization files at startup in addition to the default initialization file" << endl;
  cerr << "\t-l        : loop test on free store management (checked with top) by looping on initfiles" << endl;
  cerr << endl;
  cerr << "Examples:" << endl;
  cerr << "\t> " << name << " +i \"myinit1\" \"myinit2\"" << endl;
  cerr << "\t   --> load files myinit1 and myinit2 after " << INIT_FILE << " at initialization" << endl;
  cerr << "\t> " << name << " -i +i \"myinit1\" \"myinit2\"" << endl;
  cerr << "\t   --> load initialization file myinit1 and myinit2 instead of default " << INIT_FILE << endl;
  cerr << "\t> " << name << " -i myinit" << endl;
  cerr << "\t   --> load initialization file myinit instead of " << INIT_FILE << endl;

  return(0);
}

static void initAml() {

  createAMObjTable();

  installLocale();

  installAMLModules();

}

static void cleanAml() {

  deleteAMObjTable();

  removeLocale();

}

static int loadInitFile(const char* init_file) {

  RWCString name(init_file);

  if (!file_init_read_line(name.data())) {

    if(name == INIT_FILE){
      string home = getHome();

      name.prepend("/");
      name.prepend((char*)(!home.empty()?home.c_str():""));

      if (!file_init_read_line(name.data())) return UNDEF;
    }
    else {
      cerr << " ... Cannot load initialization file : \"" << name.data() << "\"" << endl;
      return UNDEF;
    }

  }

  cerr << " ... Loading initialization file : \"" << name.data() << "\"" << endl;

  initGetNextLineFunc(readline_file);

  initParser();
  int res = amlparse();
  cleanParser();

  return res;

}

static void testMemAllocAml(const StringList& init_files) {

  amlEchoOff();

  do {

    initAml();

    amlEchoOff();
    for ( size_t j=0; j < init_files.entries(); j++) {

      //while(1) {
        //amobj_table = new AMObjTable(hashAMObj);
        //installAMLModules();
        //amlEchoOff();
        loadInitFile(init_files[j].data());
        //delete amobj_table;
      //}

    }
    amlEchoOn();

    cleanAml();

  } while (TRUE);

}

static int aml(const char* file, const StringList& init_files) {

#ifdef _WIN32
  if (file != NULL) {
      string f(file);
      if(f[0]>= 'A' && f[0] <= 'Z' && f[1] == ':')
          chg_dir(get_dirname(f));
  }
  else {
      if(!init_files.empty()){
          string f (init_files[init_files.entries()-1].data());
          if(f!=INIT_FILE && f != getAMAPmodDir() + '\\' + string("init.aml"))
              chg_dir(get_dirname(f));
      }
  }
#endif

  initAml();

  // First parse init_files

  amlEchoOff();
  for (size_t j=0; j<init_files.entries(); j++) {
    loadInitFile(init_files[j].data());
  }

  amlEchoOn();

  if (file == NULL) {     // Interactive mode
#if defined(_WIN32) || defined(__APPLE__)
#else
    gnu_init_readline();
#endif
    initGetNextLineFunc(readline_interactive);
  }
  else {                // batch mode

    if (!file_init_read_line(file)) return 0;
    initGetNextLineFunc(readline_file);

  }

  initParser();

  if (setjmp(jump_stack_env) != 0) {
    cerr << "Interruption ..." << endl;
  }
  int res = amlparse();

  cleanParser();

  if (file) {

    if (res == 0) cerr << "parsing ... Ok!" << endl;
    else cerr << "parsing ... error!" << endl;

  }
  else cerr << "Bye ..." << endl;

  cleanAml();

  return res;

}

#ifndef _WIN32

static void amlFreeStoreException() {
  cerr << "Aml : free store exhausted. Process Aborted ..." << endl;
  exit(0);

}
#else
#ifdef __MINGW32__
static void amlFreeStoreException() {
#else
static int amlFreeStoreException(size_t t) {
#endif
  cerr << "Aml : free store exhausted. Process Aborted ..." << endl;
  cerr << "Aml : Press any key to finish" << endl;
  char c;
  cin.getline(&c,1);
  exit(0);

}
#ifndef __MINGW32__
#define set_new_handler _set_new_handler
#endif

#endif // _WIN32


int main(int argc, char** argv) {

#ifdef _WIN32
#ifndef _CONSOLE
  RedirectIOToConsole();
#endif
#endif

  StringList init_files;
  const char *batch_file = 0;

  const char* exec_name = *argv;

  set_new_handler(amlFreeStoreException); // handler in case of free storage exception
  install_signal_handlers();


  string initfile;
  string adir = getAMAPmodDir();
  if(!adir.empty()){
      initfile = std::string(adir) + '\\' + string("init.aml");
      if(exists(initfile))init_files.insert(initfile);
  }

  if(exists(INIT_FILE) || exists(getHome()+'/'+INIT_FILE))
  init_files.insert(INIT_FILE);

  argv++; // positionned on first argument
  argc--; // nb of remaining arguments

  string fdir;
  while(argc) {

    switch (*argv[0]) {

    case '-':

      if (strcmp(*argv, "-help")== 0 || strcmp(*argv, "-h") == 0) {
        return main_usage(exec_name);
      }
      else if (strcmp(*argv, "-init") == 0 || strcmp(*argv, "-i") == 0) {
        ++argv;
        --argc;
        if(!init_files.empty())init_files.remove(INIT_FILE);
        if(!init_files.empty())init_files.remove(initfile);
        if (argc) {
          if (*argv[0] != '-' && *argv[0] != '+') {
            init_files.insert(*argv);
          }
          else {
            argc++;
            argv--;
          }
        }
        else {
          argc++;
          argv--;
        }
      }
      else if (strcmp(*argv, "-batch")== 0 || strcmp(*argv, "-b") == 0) {
        if (!--argc) return main_usage(exec_name);
        cerr << "Aml - Batch Mode on File : " << *(++argv) << endl;
        batch_file = *argv;
        break;
      }
      else if (strcmp(*argv, "-freestorelooptest") == 0 || strcmp(*argv, "-l") == 0) {
        if (!--argc) {
          cerr << "Aml - Memory Allocation test on initialization file(s): " << endl;
          testMemAllocAml(init_files);
        }
        else return main_usage(exec_name);
      }
      else return main_usage(exec_name);

      break;

    case '+':

      if (strcmp(*argv , "+init") == 0 || strcmp(*argv, "+i") == 0) {
        ++argv;
        --argc;
        while(argc) {
          if (*argv[0] != '-' && *argv[0] != '+') init_files.insert(*argv);
          else break;
          ++argv;
          --argc;
        }
        --argv;
        ++argc;
      }
      else return main_usage(exec_name);

      break;
    default:
      return main_usage(exec_name);
    }

    ++argv;
    --argc;

  }


  cerr << endl;
  cerr << endl;
  cerr << "\tAMAPmod : Exploring and Modeling Plant Architecture" << endl;
  cerr << "\t" << getOSFamily().c_str() << " version " << release_number() << "\t" << current_release_date() << endl;
  cerr << endl;
  cerr << "\tCopyright(C) 1995-2014    " << endl << endl;
  cerr << "\tChristophe Godin,  Yann Guedon,  Frederic Boudon,  Christophe Pradal" << endl << endl;
  cerr << "\tCIRAD/INRA/INRIA - EPI VirtualPlants" << endl;
  cerr << endl;

  cerr << "\twith contribution of: " << endl;
  cerr << "\tSamir Bellouti,    Pascal Ferraro," << endl;
  cerr << "\tNicolas Dones,    Christophe Nouguier," << endl;
  cerr << "\tBoris Adam."  << endl;
  cerr << "\tOpen Software used: gnuplot v4.6" ;
#ifdef __GNUC__
  cerr << ", readline v6.2 (GNU)" ;
#endif
  cerr << "." << endl << endl << "\tForum for AMAPmod users         : amapmod@cirad.fr" << endl;
  cerr << "\tSend reports on bugs or comments: aml@cirad.fr" << endl;
  cerr << endl;

  cerr << "\tForum archive: https://gforge.inria.fr/forum/forum.php?forum_id=1735&group_id=79" << endl;
  cerr << "\tOnline doc   :http://amap.cirad.fr/amapmod/refermanual18/couverture.html" << endl;
  cerr << "\tE-learning   :http://amap-e-learning.cirad.fr" << endl;

  cerr << endl;
  cerr << endl;

  aml(batch_file, init_files);

  return 1;

}


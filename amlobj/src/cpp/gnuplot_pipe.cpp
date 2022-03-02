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
 *       $Id: gnuplot_pipe.cpp 15669 2014-02-04 16:05:56Z gbaty $
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




#include<iostream>
#include <stdlib.h>      // AML2: for compilation on Linux

#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <fcntl.h>

#ifndef _WIN32

#include <unistd.h>
#include <termios.h>

#else

// #include <windows.h>
#include <io.h>
#include <process.h>
#define pipe(a) _pipe(a,256,_O_TEXT)
#define execlp _execlp
#define sleep Sleep
#define getchar getch
#define pclose _pclose
#define popen _popen

#endif

#include <signal.h>
#include <assert.h>

#include "tool/config.h"

#ifdef STL_EXTENSION
#include <sstream>
#else
#include <strstream>
#endif

#include "gnuplot_pipe.h"

#ifdef NEW
#include <fstream>
#include <string>
#endif

#include "tool/util_enviro.h"
#include "tool/dirnames.h"

using namespace std;

VPTOOLS_USING_NAMESPACE

/// Gnuplot port pb

/*--------------------------------------------------------------*
 *
 *  Sortie des erreurs systemes.
 *
 *  arguments : stream, nom de la fonction systeme.
 *
 *--------------------------------------------------------------*/

void aml_system_error(std::ostream &os , char *function)

{
  os << function <<": "<< strerror(errno) << std::endl;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un objet GnuplotWindow.
 *
 *--------------------------------------------------------------*/

void GnuplotWindow::init()

{
  son_id = DEFAULT_ID;

  ptoc[0] = 0;
  ptoc[1] = 0;


  ctop[0] = 0;
  ctop[1] = 0;

  fWrite= 0;
  fRead= 0;
  end_seq= 0;

}


/*--------------------------------------------------------------*
 *
 *  Destructeur de la classe GnuplotWindow.
 *
 *--------------------------------------------------------------*/

GnuplotWindow::~GnuplotWindow()

{
  end_seq= 0;
#ifdef _WIN32
  if( fWrite != NULL ) {
#else
  if (son_id != DEFAULT_ID) {
#endif
    send("quit");
#ifdef _WIN32
    pclose(fWrite);
#else
    fclose(fRead);
    fclose(fWrite);
#endif
    init();
  }
}


/*--------------------------------------------------------------*
 *
 *  Initialisation de la communication par pipe et du processus GNUPLOT.
 *
 *  argument : stream.
 *
 *--------------------------------------------------------------*/

int GnuplotWindow::open(ostream &os)

{
  int status = TRUE;
#ifdef _WIN32
  if( fWrite )
    close(os);
  
  if( fWrite == NULL )
    {
#if AMAPMOD
      std::string command =  getAMAPmodDir() + "\\Gnuplot\\bin\\pgnuplot.exe";
      if(!exists(command)){
	status = FALSE;
	cerr << "Gnuplot Executable not found at '" << command << '\'' << endl;
	close(os);
      }
      else {
	fWrite =  popen(command.c_str(),"wt");
	if( fWrite == NULL )
	  {
	    status = FALSE;
	    cerr << "Command : '" << command << '\'' << endl;
	    aml_system_error(os , "*** Error on command popen");
	    close(os);
	  }
	else if( ferror(fWrite) ){
	  fWrite = NULL;
	  status = FALSE;
	  cerr << "Command : '" << command << '\'' << endl;
	  aml_system_error(os , "*** Ferror on command popen");
	  close(os);
	}
      }
#else
      std::string command =  "pgnuplot.exe";
      fWrite =  popen(command.c_str(),"wt");
      if( fWrite == NULL )
        {
          status = FALSE;
          cerr << "Command : '" << command << '\'' << endl;
          aml_system_error(os , "*** Error on command popen");
          close(os);
        }
      else if( ferror(fWrite) )
        {
          fWrite = NULL;
          status = FALSE;
          cerr << "Command : '" << command << '\'' << endl;
          aml_system_error(os , "*** Ferror on command popen");
          close(os);
        }
#endif //AMAPMOD
    }
  
#else

  if (son_id == DEFAULT_ID) {

    // creation de deux pipes

    if ((pipe(ptoc) == -1) || (pipe(ctop) == -1)) {
      status = FALSE;
      aml_system_error(os , "pipe");
    }

    son_id = vfork();

    switch (son_id) {

    case -1 : {
      status = FALSE;
      aml_system_error(os , "fork");
      break;
    }

    // processus fils

    case 0 : {

      // la sortie du pipe ptoc est redirigee sur l'entree standard de Gnuplot

      if (::close(0) == -1) {
        status = FALSE;
        aml_system_error(os , "close");
      }
      if (dup(ptoc[0]) != 0) {
        status = FALSE;
        aml_system_error(os , "dup");
      }

      // la sortie erreur de Gnuplot est redirigee sur l'entree du pipe ctop

      if (::close(2) == -1) {
        status = FALSE;
        aml_system_error(os , "close");
      }
      if (dup(ctop[1]) != 2) {
        status = FALSE;
        aml_system_error(os , "dup");
      }

      if ((::close(ptoc[0]) == -1) || (::close(ptoc[1]) == -1) ||
          (::close(ctop[0]) == -1) || (::close(ctop[1]) == -1)) {
        status = FALSE;
        aml_system_error(os , "close");
      }

      // recouvrement du processus fils par Gnuplot

      if (execlp("gnuplot" , "gnuplot" , 0) == -1) {
        status = FALSE;
        aml_system_error(os , "execlp");
      }
      break;
    }
    }

    // processus pere

    if ((::close(ptoc[0]) == -1) || (::close(ctop[1]) == -1)) {
      status = FALSE;
      aml_system_error(os , "close");
    }

    fWrite = (FILE *) fdopen(ptoc[1],"w");
    fRead = (FILE *) fdopen(ctop[0],"r");
  }

#endif // _WIN32

  return status;
}


/*--------------------------------------------------------------*
 *
 *  Fermeture des pipes et reinitialisation de l'objet GnuplotWindow.
 *
 *  argument : stream.
 *
 *--------------------------------------------------------------*/

int GnuplotWindow::close(ostream &os)

{
  int status = TRUE;

#ifdef _WIN32
    if(fWrite != NULL) status = pclose(fWrite);
        else status = FALSE;
#else
    fclose(fRead);
    fclose(fWrite);
#endif

  init();
  end_seq= 1;

  return status;
}


/*--------------------------------------------------------------*
 *
 *  Envoi d'une commande Gnuplot.
 *
 *  argument : commande.
 *
 *--------------------------------------------------------------*/

void GnuplotWindow::send(const char *command) const

{
  if(fWrite != NULL){
    fprintf( fWrite, command );
    fprintf( fWrite, "\n" );
    fflush(fWrite);
  }
}


/*--------------------------------------------------------------*
 *
 *  Lecture de la sortie erreur de Gnuplot.
 *
 *  argument : stream.
 *
 *--------------------------------------------------------------*/

int GnuplotWindow::echo(ostream &os) const

{
#ifndef WIN32
  char buff[2] , echo[BUFFER_SIZE];
  register int i = 0;
  int status= TRUE, plot_end= FALSE;

  for (;;) {
    status = read(ctop[0] , buff , 1);

    if (status > 0)
      {
      if ((buff[0] != EOF) && (buff[0] != '\n') &&
          (buff[0] != '.') && (i < BUFFER_SIZE - 1))
        {
        echo[i++] = buff[0];
        }

      else
        {
        if (i > 0)
          {
          echo[i] = '\0';
          if (strcmp(echo , "End") == 0)
            {
            plot_end = TRUE;
            }

          else
            {
            if (strcmp(echo , "<Return>: continue") == 0)
              {
              plot_end = FALSE;
              }
            else
              plot_end = GNUPLOT_KILL;
            }
          break;
          }
        }
      }
  }

  return plot_end;
#else
  return TRUE;
#endif // _WIN32
}


/*--------------------------------------------------------------*
 *
 *  Session Gnuplot.
 *
 *  arguments : prefixe des fichiers Gnuplot, stream,
 *              flag sortie bloquante ou non-bloquante, temps d'affichage.
 *
 *--------------------------------------------------------------*/

int GnuplotWindow::session(const char *prefix , ostream &os , int output , unsigned int time)

{
  char *command;
  int command_size = strlen(prefix) + 20;
  int status = open(os);

#ifdef _WIN32

  if(status){
    command = new char[command_size];

    load(prefix, command , command_size);
    delete [] command;
  }
  return status;

#else

  int start = TRUE , key= 0 , read= 0 , nb_message= 1 , end= 0;

  struct termios itty , tty;

  if (status)
    {
    if (tcgetattr(STDIN_FILENO , &itty) == -1)
      {
      status = FALSE;
      aml_system_error(os , "tcgetattr");
      }
    }

  if (status)
    {
    tty = itty;

    tty.c_lflag &= ~ECHO;
    tty.c_lflag &= ~ICANON;
    tty.c_cc[VMIN] = 1;
    tty.c_cc[VTIME] = 0;

    if (tcsetattr(STDIN_FILENO , TCSANOW , &tty) == -1)
      {
      status = FALSE;
      aml_system_error(os , "tcsetattr");
      }

    if (status)
      {

#ifndef STL_EXTENSION
	command = new char[command_size];
#endif
	
    switch (output)
      {

      case FALSE :
        {
        read = FALSE;
        key = '\n';

        // gnuplot load plot instructions
        load(prefix, command , command_size);

        end = echo(os);

        // user receive key instructions
        if( ! end )
          {
          os << "<Return>: continue, <p>: print, <s>: suspend, <q>: quit" << flush;

          do
            {
            key = getchar();
            }
          while ((key != '\n') && (key != 'p') && (key != 's') && (key != 'q'));
          }
        else
        if( end == GNUPLOT_KILL )
          {
          kill_process(os);
          }
        else
          {
          os << "<p>: print, <s>: suspend, <q>: quit" << flush;

          do
            {
            key = getchar();
            }
          while ( (key != 'p') && (key != 's') && (key != 'q'));
          }

        // flag to exit the loop.
        int exit= 0;
        for(;;)
          {
          switch (key)
            {
            case '\n' :
              {

              if( end )
                {
                load(prefix, command , command_size);
                end= echo(os);
                }
              else
                {
                send("");
                end= echo(os);
                }

              do
                {
                key = getchar();
                }
              while ((key != '\n') && (key != 'p') && (key != 's') && (key != 'q'));

              break;
              }
            case 'p' :
              {
              // print with lpr
              print(prefix, os, command, command_size, 1);
              exit= 1;
              break;
              }
            case 'P' :
              {
              // print with lp
              print(prefix, os, command, command_size, 2);
              exit= 1;
              break;
              }
            case 's' :
              {
              exit= 1;
              end_seq= end;
              break;
              }
            case 'q' :
              {
              exit= 1;
              send("quit");
              close(os);
              break;
              }
            }

          if(exit)
            break;
          }
        break;
        }  // fin case FALSE

      case TRUE :
        {
        // gnuplot load plot instructions
        load(prefix, command , command_size);

        for (;;)
          {
          end = echo(os);

          if (end)
            break;

          sleep(time);
          send("");
          }

        if (end == GNUPLOT_KILL)
          kill_process(os);

        break;
        }
      } // fin switch(output)

      if (tcsetattr(STDIN_FILENO , TCSANOW , &itty) == -1)
        {
        status = FALSE;
        aml_system_error(os , "tcsetattr");
        }
#ifndef STL_EXTENSION
      delete [] command;
#endif      
      }
    }
#endif
  return status;
}

/*--------------------------------------------------------------*
 *
 *  End current gnuplot session.
 *  Used to initiate an other one.
 *
 *--------------------------------------------------------------*/

int GnuplotWindow::end_old_session()
{
  if( end_seq )
    return 1;
  if (son_id != DEFAULT_ID)
    {
    int end= 0, i= 0;
    do
      {
      send("");
      end= echo(cout);
      i++;
      }
    while( !end && i<100 );

    if ( i >= 100 )
      return 1;
    }

  return 1;
}

/*--------------------------------------------------------------*/

void GnuplotWindow::load( const char *prefix,
                          char *command,
                          int command_size )
{
#ifndef STL_EXTENSION  
  ostrstream(command, command_size) << "load \"" << prefix << ".plot\"" << std::ends << std::flush;
  send(command);
#else
  ostringstream os;
  os <<"load \"" << prefix << ".plot\"" << std::ends << std::flush;
  send(os.str().c_str());
#endif  
}

/*--------------------------------------------------------------*/

void GnuplotWindow::print( const char *prefix,
                          ostream &os,
                          char *command,
                          int command_size,
                          int print_mode )
{
#ifndef STL_EXTENSION  
  ostrstream(command , command_size) << "load \"" << prefix << ".print\"" << std::ends;
  send(command);
#else
  ostringstream o;
  o << "load \"" << prefix << ".print\"" << std::ends;
  const char* cmd= o.str().c_str();
  send(cmd);
  o.str("");
#endif
  
  int end= 0;
  do { end = echo(os); } while (!end);

#ifndef _WIN32
#ifndef STL_EXTENSION  
  ostrstream(command , command_size) << "chmod 666 " << prefix << ".eps" << ends;
  if (system(command) == -1)
    aml_system_error(os , "chmod");
#else
  o << "chmod 666 " << prefix << ".eps" << ends;
  cmd= o.str().c_str();
  if (system(cmd) == -1)
    aml_system_error(os , "chmod");
  o.str("");
#endif  

#endif

  if( print_mode == 2 )
    {
#ifndef STL_EXTENSION  
    ostrstream(command , command_size) << "lp -c " << prefix << ".eps" << ends;
    if (system(command) == -1)
      aml_system_error(os , "lp");
#else
    o << "lp -c " << prefix << ".eps" << ends;
    cmd= o.str().c_str();
    if (system(cmd) == -1)
      aml_system_error(os , "lp");
    o.str("");
#endif    
    }
  else
    {
#ifndef STL_EXTENSION  
    ostrstream(command , command_size) << "lpr -c " << prefix << ".eps" << ends;
    if (system(command) == -1)
      aml_system_error(os , "lpr");
#else
    o << "lpr -c " << prefix << ".eps" << ends;
    cmd= o.str().c_str();
    if (system(cmd) == -1)
      aml_system_error(os , "lpr");
    o.str("");
#endif
    
    }
}

/*--------------------------------------------------------------*/

void GnuplotWindow::kill_process(ostream &os)
{
#ifdef CESTPASEAUJEPENSE
    if (kill(son_id , SIGKILL) == -1)
    {
    aml_system_error(os , "kill");
    }
#endif
  send("quit");
  close(os);

  os << "GNUPLOT error: Please, Plot again." << endl;
}

/*--------------------------------------------------------------*/
/*
bool GnuplotWindow::getNbFigures( const char *prefix ,
                                  ostream &os,
                                  char *command,
                                  int command_size )
{
#ifdef NEW
  ostrstream(command , command_size) << prefix << ".plot" << ends;
  std::ifstream file;
  file.open(command);
  if( ! file.good() )
    {
    aml_system_error(os , "open gnuplot file");
    return FALSE;
    }

  nb_fig= 0;
  char line[1024];
  int comp= 0;
  while( file.getline( line, 1024) )
    {
    comp++;
    std::string l(line);
    if( l.find("pause") != -1)
      nb_fig++;
    }

  if( nb_fig )
    return TRUE;
  else
    {
    aml_system_error(os , "no data to plot");
    return FALSE;
    }
#endif
}
*/

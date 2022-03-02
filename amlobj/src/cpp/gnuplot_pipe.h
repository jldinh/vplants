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
 *       $Id: gnuplot_pipe.h 3259 2007-06-06 13:40:30Z dufourko $
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




#ifndef GNUPLOT_PIPE_H
#define GNUPLOT_PIPE_H

#include <sys/types.h>

#ifdef STL_EXTENSION
  #include <ostream>
#else
  #include <iostream>
#endif


#ifdef _WIN32
#define pid_t int
#endif


/****************************************************************
 *
 *  Constantes :
 */


#ifndef FALSE
enum{FALSE , TRUE};
#endif

static const int DEFAULT_ID = -2;             // identificateur par defaut
static const int DEFAULT_PLOT_TIME = 2;       // temps d'affichage par defaut
static const int BUFFER_SIZE = 100;           // taille du buffer de lecture
static const int GNUPLOT_KILL = -1;           // signal GNUPLOT interrompu



/****************************************************************
 *
 *  Definition des classes :
 */


class GnuplotWindow {   // processus Gnuplot

  friend void entry(void*);

protected :

    pid_t son_id;           // identificateur du processus fils
    int ptoc[2];            // pipe pere->fils
    int ctop[2];            // pipe fils->pere

    FILE* fWrite;           // ptoc[1]
    FILE* fRead;            // ctop[0]

    void init();
    int open(std::ostream &os);
    int close(std::ostream &os);

    void send(const char *command) const;
    int echo(std::ostream &os) const;

public :

    GnuplotWindow() { init(); }
    ~GnuplotWindow();

    int session(const char *prefix , std::ostream &os , int output = FALSE ,
                unsigned int time = DEFAULT_PLOT_TIME);

    // acces membres de la classe

    pid_t get_son_id() const { return son_id; }
    int get_ptoc(int i) const { return ptoc[i]; }
    int get_ctop(int i) const { return ctop[i]; }

    // cpl in case of suspend case
    int end_old_session();

private :
  void load( const char *prefix, char *command, int command_size );

  // print_mode == 1: cmd lpr
  // print_mode == 2: cmd lp
  void print( const char *prefix, std::ostream &os, char *command, int command_size, int print_mode );

  void kill_process(std::ostream &os);

//  bool getNbFigures( const char *prefix, ostream &os, char *command, int command_size );
  int end_seq;
//  int cur_fig, nb_fig;


};



#endif

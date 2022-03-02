/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 *
 *       $Source$
 *       $Id: octree.cpp 3268 2007-06-06 16:44:27Z dufourko $
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

#include "plantgl/algo/grid/octree.h"
#include "plangl/gui/viewer/pglapplication.h"

#include "../Tools/dirnames.h"
#include <getopt.h>

GEOM_USING_NAMESPACE
PGL_USING_NAMESPACE

using namespace std;

/* ----------------------------------------------------------------------- */

static bool quarter = false;

struct conditionPlane
{
        bool operator()(const OctreeNode * a) const {
          if(a->getType() == Tile::Empty || a->getType() == Tile::Undetermined) return false;
          if(quarter &&
             a->getLowerLeftCorner().x() >= 0 &&
             a->getLowerLeftCorner().y() >= 0 &&
             a->getLowerLeftCorner().z() >= 0
             )return false;
          return true;
        }
};

struct conditionPlane2
{
        bool operator()(const OctreeNode * a) const {
          if(a->getType() == Tile::Empty ) return false;
          if(a->isDecomposed() ) return false;
          if(quarter &&
             a->getLowerLeftCorner().x() >= 0 &&
             a->getLowerLeftCorner().y() >= 0 &&
             a->getLowerLeftCorner().z() >= 0
             )return false;
          return true;
        }
};

struct conditionPlane3
{
        bool operator()(const OctreeNode * a) const {
          if(a->isDecomposed() ) return false;
          if(quarter &&
             a->getLowerLeftCorner().x() >= 0 &&
             a->getLowerLeftCorner().y() >= 0 &&
             a->getLowerLeftCorner().z() >= 0
             )return false;
          return true;
        }
};

/* ----------------------------------------------------------------------- */

int main( int argc, char **argv )
{
    string output_filename ;
    string input_filename ;

    bool out = false;
    bool in = false;
    bool include = false;
    int deep = 5;
    int mode = 1;

    if( argc != 0 ){
        /// Read of calling options
        char * optstring = "hdiqm";

        struct option longopts [] = {
            /* name      has_arg   flag        val */
            { "help",       0,      NULL,       'h' },
            { "deep",       1,      NULL,       'd' },
            { "include",    0,      NULL,       'i' },
            { "quarter",    0,      NULL,       'q' },
            { "mode",       1,      NULL,       'm' },
            // { "output",     1,      NULL,       'o' },
            /* The last arg must be null */
            { NULL,         0,      NULL,        0 },
        };

        int longindex;
        int option;

        while ((option = getopt_long (argc, argv, optstring, longopts, & longindex)) != -1 ){
            switch (option) {
                case 'q' :
                    quarter = true;
                    break;
                case 'i' :
                    include = true;
                    break;
                case 'd' :
                    if (optind != argc) {
                        deep = atoi(argv[optind++]);
                        if( deep <= 0 && deep > 20) deep = 5;
                        }
                    else {
                        cerr << "Must specifie a valid deep." << endl;
                        exit(-1);
                    }
                    break;
                case 'm' :
                    if (optind != argc) {
                        mode = atoi(argv[optind++]);
                        if( mode < 1 || mode > 3 ) mode = 1;
                        }
                    else {
                        cerr << "Must specifie a valid mode." << endl;
                        exit(-1);
                    }
                    break;
                case '?':
                case 'h' :
                  cout << "./" << get_notdirname(string(argv[0])) << " : Compute and Represent an Octree from  GEOM objects." << endl;
                    cout << "Compiled the " << __DATE__ << ".";
                    cout << "Usage: ./" << get_notdirname(string(argv[0])) <<" [ -h | --help | -i | --include  | -d | --deep ] [ filename ]" << endl;
                    cout << "\t -h --help     : display this help." << endl;
                    cout << "\t -i --include  : display GEOM object. [default="<< (include?"True":"False") << "]" << endl;
                    cout << "\t -d --deep     : maximum deep of the octree. [default="<< deep << "]" << endl;
                    cout << "\t -m --mode     : mode of display of the octree. [default="<< mode << "]" << endl;
                    cout << "\t -q --quarter  : do not display a quarter of the octree. [default="<< mode << "]" << endl;
                    exit(0);
                    break;
            }

        }
        if (optind != argc) {
            input_filename = string(argv[optind++]);
            in = true;
        }
    }
    if(in)
        input_filename = expand_dirname(input_filename);

    if(out)output_filename = cat_dir_file(get_cwd(),output_filename);
/*    else {
      if(in)
        output_filename =  change_extension(input_filename,string("wrl"));
      else
        output_filename = string("out.wrl");
    }*/

    ScenePtr _scene(0);

    if(!in){
      _scene = ScenePtr(new Scene(cin,cerr,10));
    }
    else {
        if(!input_filename.empty())
          _scene = ScenePtr(new Scene(input_filename,cerr,10));
        else {
            cerr << "Not valid input filename" << endl;
            exit(-1);
        }
    }

    if(!_scene->isEmpty()){
#ifdef GEOM_DEBUG
      cerr << *_scene << endl;
#endif
        OctreePtr _octree(new Octree(_scene,
                                     deep));
        ScenePtr scene2;
        if(mode == 1){
          conditionPlane a;
          scene2 = ScenePtr(getCondRepresentation(*_octree,a));
        }
        else if(mode == 2){
          conditionPlane2 a;
          scene2 = ScenePtr(getCondRepresentation(*_octree,a));
        }
        else {
          conditionPlane3 a;
          scene2 = ScenePtr(getCondRepresentation(*_octree,a));
        }
        ViewerApplication app;
        bool b = app.useThread(false);
        if(include){
            _scene->merge(scene2);
            app.display(_scene);
        }
        else app.display(scene2);
        if(!b)app.wait();
    }
    else {
      cerr << "No valid geometry found." << endl;
      exit(-1);
    }
}

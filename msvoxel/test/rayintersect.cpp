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
 *       $Id: rayintersect.cpp 3268 2007-06-06 16:44:27Z dufourko $
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

#include "plantgl/math/util_vector.h"
#include "plantgl/algo/raycasting/rayintersection.h"
#include "plantgl/scenegraph/scene/scene.h"
#include "plantgl/scenegraph/appearance/material.h"
#include "plantgl/scenegraph/geometry/pointset.h"
#include "plantgl/scenegraph/geometry/polyline.h"
#include "plantgl/gui/viewer/pglapplication.h"
#include "plantgl/scenegraph/container/pointarray.h"
#include "plantgl/scenegraph/scene/shape.h"

#include "../Tools/dirnames.h"
#include <getopt.h>


using namespace std;
PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
/* ----------------------------------------------------------------------- */

int main( int argc, char **argv )
{
    string output_filename ;
    string input_filename ;
    AppearancePtr blue(new Material(Color3::BLUE));
    AppearancePtr red(new Material(Color3::RED));

    bool out = false;
    bool in = false;
    Vector3 origin(0,0,0);
    Vector3 direction(0,0,1);

    if( argc != 0 ){
	/// Read of calling options 
	char * optstring = "hod";

	struct option longopts [] = {
	    /* name      has_arg   flag        val */
	    { "help",       0,      NULL,       'h' },
	    { "origin",     3,      NULL,       'o' },
	    { "direction",  3,      NULL,       'd' },
            // { "output",     1,      NULL,       'o' },
	    /* The last arg must be null */
            { NULL,         0,      NULL,        0 },
	};
  
	int longindex;
	int option;
	
	while ((option = getopt_long (argc, argv, optstring, longopts, & longindex)) != -1 ){
	  switch (option) {
	  case 'o' : 
	    if(optind <= argc-3){
	      real_t a = atof(argv[optind++]);
	      real_t b = atof(argv[optind++]);
	      real_t c = atof(argv[optind++]);
	      origin = Vector3(a,b,c);
	    }
	    else {
	      cerr << "Not Enougth arg for origin" << endl;
	      exit(-1);
	    }
	    break;
	  case 'd' : 
	    if(optind <= argc-3){
	      real_t a = atof(argv[optind++]);
	      real_t b = atof(argv[optind++]);
	      real_t c = atof(argv[optind++]);
	      direction = Vector3(a,b,c);
	    }
	    else {
	      cerr << "Not Enougth arg for direction" << endl;
	      exit(-1);
	    }
	    break;
	  case '?':
	  case 'h' :
	    cout << "./" << get_notdirname(string(argv[0])) << " : Compute the intersection of a ray and a scene." << endl;
	    cout << "Compiled the " << __DATE__ << ".";
	    cout << "Usage: ./" << get_notdirname(string(argv[0])) <<" [ -h | --help ] [ filename ]" << endl;
	    cout << "\t -h --help     : display this help." << endl;
	    cout << "\t -o --origin r1 r2 r3  : Origin vector of the ray is <r1,r2,r3>." << endl;
	    cout << "\t -d --direction r1 r2 r3  : Direction vector of the ray is <r1,r2,r3>." << endl;
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
    cerr << "Origin : " << origin << endl;
    cerr << "Direction : " << direction << endl;
	
    if(!_scene->isEmpty()){
      Discretizer dis;
      RayIntersection in(dis);
      Ray a(origin,direction);
      in.setRay(a);
      Point3ArrayPtr pint(new Point3Array(0));
      for(Scene::iterator _it = _scene->getBegin();
	  _it != _scene->getEnd();_it++){
	if((*_it)->apply(in)){
	  pint->insert(pint->getEnd(),in.getIntersection()->getBegin(),in.getIntersection()->getEnd());
	  cout << "Intersection :" << *in.getIntersection() << endl;
	}
      }
      if(pint->getSize() > 0)_scene->add(Shape(GeometryPtr(new PointSet(pint)),blue));
      else cout << "No intersection" << endl;
      Point3ArrayPtr pl(new Point3Array(2));
      pl->setAt(0,origin);
      pl->setAt(1,(origin+direction*10));
      _scene->add(Shape(GeometryPtr(new GeomPolyline(pl)),red));
      PGLViewerApplication app;
      app.useThread(false);
      app.display(_scene);      
    }
    else {
      cerr << "No valid geometry found." << endl;
      exit(-1);
    }
}

/* ----------------------------------------------------------------------- */

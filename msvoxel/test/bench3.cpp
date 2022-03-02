
#include "plantgl/pgl_geometry.h"
#include "plantgl/pgl_algo.h"

#include "plantgl/gui/base/guicon.h"
#include "plantgl/scenegraph/appearance/material.h"

#include "beam_grid.h"
#include "mvs_msvoxel.h"

#include "plantgl/scenegraph/scene/shape.h"
#include "plantgl/gui/viewer/pglapplication.h"

#include <stdlib.h>

//#define NBTEST 100

PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace std;

int main(void)
{
  RedirectIOToConsole();
  Point3ArrayPtr points(new Point3Array(3));
 /*
  points->setAt(0,Vector3(-1 ,-2,0));
  points->setAt(1,Vector3(2,1,1));
  points->setAt(2,Vector3(-1,1,-1));


points->setAt(0,Vector3(0 ,-2,0));
  points->setAt(1,Vector3(0.1,1,1));
  points->setAt(2,Vector3(0.1,1,-1));
 */
 /*
  points->setAt(2,Vector3(0.1 , 0.1, 5));
  points->setAt(1,Vector3(-0.1 ,-0.1,6));
  points->setAt(0,Vector3(-0.1,0.1,7));
*/
  points->setAt(2,Vector3(20,13 ,13));
  points->setAt(1,Vector3(0,-7,10));
  points->setAt(0,Vector3(0,0,-10));
  Index3ArrayPtr index(new Index3Array(1));
  index->setAt(0,Tuple3<unsigned long>(0,1,2));


  TriangleSetPtr tri(new TriangleSet( points,
                                       index,
                                       0,
                                       0,
                                       NULL));



  uchar slices= 5;
  uchar stacks= 5;
  AsymmetricHullPtr hull( new
    AsymmetricHull( 2,2,2,2,2,2,2,2,Vector3::ORIGIN,Vector3(0,0,3),
                    AsymmetricHull::DEFAULT_BOTTOM_SHAPE,
                    AsymmetricHull::DEFAULT_TOP_SHAPE,
                    slices,stacks));

  ScenePtr scene(new Scene());
  //  scene->add(Shape( GeometryPtr::Cast(hull), AppearancePtr(new Material()) ));
  scene->add(Shape( GeometryPtr::Cast(tri),  AppearancePtr(new Material()) ));
  Vector3 center(0,0,0);
  Vector3 size(3,3,3);
  int deep = 1 ;
  vector<int> radius;
  radius.push_back(2);
  vector<int> splittingList;
  splittingList.push_back(6);
  MSVoxel _MSVoxel(scene, splittingList, deep, 1);
  int i;
  printf ("Representation...\n");
  scene->merge(_MSVoxel.getRepresentation());
  printf ("InterceptedVoxel...\n");
  vector<int> IV = _MSVoxel.getInterceptedVoxels(deep);
  // unsigned real_t *QSr  = _MSVoxel.getS(radius);
  vector<real_t> L = _MSVoxel.getLacunarity(radius);
  printf("i / InterceptedVoxel / Fractal dimension : ");
  for(i = 0 ; i < deep ; i++)
          printf (" <%d : %d : %f> ",i,IV[i], log(IV[i])/log(pow(3,i+1)));
  //printf("\nQSr : ");
  /*for(i = 0 ; i <= radius * radius * radius ; i++)
          printf (" <%d : %f> ",i,QSr[i]);*/

  printf("\nLacunarity = %f\n", L[0]);
  PGLViewerApplication app;
  bool b = app.useThread(false);
  app.display(scene);


  return 1;
}

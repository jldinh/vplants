#define TEST1



#include "plantgl/pgl_geometry.h"
#include "plantgl/scenegraph/container/pointarray.h"
#include "plantgl/scenegraph/appearance/material.h"
#include "plantgl/scenegraph/scene/shape.h"
#include "plantgl/gui/viewer/pglapplication.h"

#include "plantgl/algo/raycasting/ray.h"
#include "plantgl/algo/raycasting/rayintersection.h"
#include "plantgl/algo/grid/octree.h"



#include <stdlib.h>

//#define NBTEST 100

GEOM_USING_NAMESPACE
TOOLS_USING_NAMESPACE

int main(void)
{
#ifdef TEST1
  Point4ArrayPtr ctrlpoints(new Point4Array(4));
  ctrlpoints->setAt(0,Vector4(0,0,0,1));
  ctrlpoints->setAt(1,Vector4(0,1,1,1));
  ctrlpoints->setAt(2,Vector4(0,-3,2,1));
  ctrlpoints->setAt(3,Vector4(0,0,3,1));
  BezierCurve bcurve(ctrlpoints);

  srand( (unsigned)time( NULL ) );

// ouvrir un fichier et ecrire dedans
  int i= 1;
  for(i= 1; i < 4; i++)
  {
cout<<endl;
cout<<"Deep;Density;Rays;triangles;time octree;time rays;total1;total old;Gain;"<<endl;


  int deep= 5, max_tri=10;
  int NBTEST= 100;

  uchar slices= AsymmetricHull::DEFAULT_SLICES * i;
  uchar stacks= AsymmetricHull::DEFAULT_STACKS * i;
  AsymmetricHullPtr hull( new
    AsymmetricHull( 2,2,2,2,2,2,2,2,Vector3::ORIGIN,Vector3(0,0,3),
                    AsymmetricHull::DEFAULT_BOTTOM_SHAPE,
                    AsymmetricHull::DEFAULT_TOP_SHAPE,
                    slices,stacks));

  Timer t;
//old
  t.start();
  AsymmetricHullPtr hull2( new
    AsymmetricHull( 2,2,2,2,2,2,2,2,
                    Vector3::ORIGIN,Vector3(0,0,3),
                    AsymmetricHull::DEFAULT_BOTTOM_SHAPE,
                    AsymmetricHull::DEFAULT_TOP_SHAPE,
                    slices,stacks));

  Discretizer discretizer;
  RayIntersection actionRay(discretizer);
  int n= 0;
  for( int u = 0; u < NBTEST; u++ )
    {
    real_t x = (real_t)rand()/ (real_t)RAND_MAX;
    real_t y = (real_t)rand()/ (real_t)RAND_MAX;
    real_t z = (real_t)rand()/ (real_t)RAND_MAX;
    Vector3 dir(x,y,z);
    dir.normalize();

    Vector3 origin = bcurve.getPointAt(u/real_t(NBTEST));
    GeomRay ray(origin,dir);
    /// Calcul de l'intersection entre ray et hull
    actionRay.setRay(ray);
    bool ok= actionRay.process(hull2);
    Vector3 pt;
    if(ok)
      {
      n++;
      real_t dist= REAL_MAX;
      Point3ArrayPtr pts= actionRay.getIntersection();
      assert(!pts->isEmpty());
      Point3Array::const_iterator it= pts->getBegin();
      for( ; it != pts->getEnd(); it++ )
        {
        real_t d_cur= normSquared(origin-(*it));
        if( d_cur < dist )
          {
          pt= *it;
          dist= d_cur;
          }
        }
      }
    }
  t.stop();
  real_t old_time= t.elapsedTime();

//new
  ScenePtr scene(new Scene());
  scene->add(Shape( GeometryPtr::Cast(hull), AppearancePtr(new Material()) ));

  for( deep= 1; deep<10; deep++)
  {
//  for( max_tri= 2; max_tri<=10; max_tri+=2 )

  t.start();

  OctreePtr _octree(new Octree(scene, deep, max_tri));

  t.stop();
  real_t octree_time= t.elapsedTime();

  t.start();
  int n= 0;
  for( int u = 0; u < NBTEST; u++ )
    {
    real_t x = (real_t)rand()/ (real_t)RAND_MAX;
    real_t y = (real_t)rand()/ (real_t)RAND_MAX;
    real_t z = (real_t)rand()/ (real_t)RAND_MAX;
    Vector3 dir(x,y,z);
//cout<<" dir "<<dir<<endl;
    dir.normalize();
    Vector3 origin = bcurve.getPointAt(u/real_t(NBTEST));
//cout<<"origin "<<origin<<endl;
    GeomRay ray(origin,dir);
    /// Calcul de l'intersection entre ray et hull
    Vector3 pt;
    bool ok= _octree->intersect( ray, pt );
    if(ok)
      {
      n++;
      real_t v= normL1(cross( pt-origin, dir ));
      if(v>GEOM_EPSILON)
        cout<<"Attention!!! v= "<<v<<endl;
      }
//    if(ok) cout<< normSquared(pt-origin)<<endl;

    }
  t.stop();
  real_t ray_time= t.elapsedTime();

cout<<deep<<";"<<max_tri<<";"<<NBTEST<<";"<<slices*stacks*16<<";";
cout<<octree_time<<";"<<ray_time<<";"<<octree_time+ray_time<<";"<<old_time;
cout<<";"<<old_time/(octree_time+ray_time)<<";"<<endl;
cout<<"nb intersections: "<<n<<endl;
//  cout << " *********** Octree ************* " <<endl;
/*
  cout<<" Deep "<<deep<<endl;
  cout<<" Density  "<<max_tri<<endl;
  cout<<" Nb rays  "<<NBTEST<<endl;
  cout<<" Nb triangles  "<<slices*stacks*16<<endl;
  cout<< "Octree build in  "<< time1 << " sec. " << endl;
  cout<< "Rays send in "<< time2 << " sec. " << endl;
  cout<< "Total in "<< time1+time2 << " sec. " << endl;

  cout<<"nb intersections: "<<n<<endl;

  cout<<"Old method takes "<<time3<< " sec. " << endl;

  cout<<" Gain * "<< time3/(time1+time2)<<endl;
*/
  }
  }
  /*
  scene->add(Shape( GeometryPtr::Cast(BezierCurvePtr(new BezierCurve(ctrlpoints))), AppearancePtr(new Material()) ));
  PGLViewerApplication app;
  bool b = app.useThread(false);
  app.display(scene);
  */
#else
//      AsymmetricHull Name="Hull_137356448"
real_t PosXRadius= 0.273638;
real_t PosYRadius= 0.614581;
real_t NegXRadius= 0.245208;
real_t NegYRadius= 0.614581;
real_t PosXHeight= 0.511739;
real_t PosYHeight= 0.727005;
real_t NegXHeight= 0.508185;
real_t NegYHeight= 0.554622;
Vector3 Bottom(0,0,0.479673);
Vector3 Top(-0.00525017,-0.0214168, 1.58913);
real_t BottomShape= 1;
real_t TopShape= 2.25;
int Slices= 2;
int Stacks= 6;

Vector3 origin(0.00502148,-0.0123014,0.521211);
Vector3 dir(0.00152146,-0.985905,0.167302);
  AsymmetricHullPtr hull(
    new AsymmetricHull( PosXRadius,
                        PosYRadius,
                        NegXRadius,
                        NegYRadius,
                        PosXHeight,
                        PosYHeight,
                        NegXHeight,
                        NegYHeight,
                        Bottom,
                        Top,
                        BottomShape,
                        TopShape,
                        Slices,
                        Stacks ));

    GeomRay ray(origin,dir);
    ScenePtr scene(new Scene());
    scene->add(Shape( GeometryPtr::Cast(hull), AppearancePtr(new Material()) ));

    OctreePtr _octree(new Octree(scene, 4, 10));
    Vector3 pt;
    bool ok= _octree->intersect( ray, pt );
    cout<<"ca marche";
    if(ok) cout<<pt<<endl;
    else cout<<"pas"<<endl;

#endif
}




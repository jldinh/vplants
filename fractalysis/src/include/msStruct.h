#ifndef msStruct_h
#define msStruct_h

#ifdef _WIN32
#ifdef LGT_MAKEDLL  /* create a DLL library */
#define LGT_API  __declspec(dllexport)
#else               /* use a  DLL library */
#define LGT_API  __declspec(dllimport)
#endif
#else
#define LGT_API  
#endif


#include <string>
#include <vector>
#include <map>
#include <tool/util_hashmap.h>
#include <plantgl/math/util_vector.h>
#include <plantgl/tool/util_array.h>
//#include <hash_map.h>
#include <plantgl/scenegraph/scene/scene.h>
#include <plantgl/scenegraph/scene/shape.h>
//#include <plantgl/gui/viewer/pglapplication.h>
#include <plantgl/gui3/viewer/pglapplication.h>
#include <plantgl/algo/base/bboxcomputer.h>
#include <plantgl/scenegraph/geometry/boundingbox.h>
//#include <plantgl/gui/base/zbuffer.h>
#include <plantgl/gui3/base/zbuffer.h>


PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE
using namespace std;
using namespace STDEXT;


struct LGT_API iBeam //to ease the lenght retrival it was an dict{<x,y>:length}
{
int id_x;
int id_y;
float length;
};

enum LGT_API distrib {Turbid, Real};

typedef vector<distrib> DistribVect;
typedef map<Vector3, map< DistribVect, float> > DirectionalDistribPMap;
typedef map<Vector3,float> DirectionalFloatMap;
typedef map<Vector3, vector<iBeam> > DirectionalHitBeamsMap;

class LGT_API msNode
{
private:
  int id;
  int scale;
  int cplx;
  vector<int>  components;
  float surface;
  float volume;
  ShapePtr shape;
  float globalOpacity;

//directional datas should be stored in map or hashtable with direction as key

  DirectionalHitBeamsMap interceptedBeams;
  DirectionalFloatMap projSurface;
  DirectionalDistribPMap pOmega;

public:


  msNode(int);
  ~msNode();

  void setId( int );
  void setCplx( int );
  void addComponent(int );
  void setComponents( const vector<int>& );
  void setSurface( float );
  void setVolume( float );
  void setShape( ShapePtr sh );
  void setGlobalOpacity(float);
  void addInterBeam( Vector3, iBeam );
  void setProjSurface( Vector3, float );
  void setPOmega( Vector3, DistribVect, float );

  int getId();
  int getScale();
  int getCplx();
  vector<int> getComponents();
  float getSurface();
  float getVolume();
  ShapePtr getShape();
  float getGlobalOpacity();
  float getBeamLength( Vector3, int, int );
  vector<iBeam> * getIBeams(Vector3);
  float getProjSurface( Vector3 );
  float getPOmega( Vector3, DistribVect );

  float computeSurface();
  float computeVolume();
  void afficheInfo();
  void cleanMaps();

};

/******************* scaledStruct *********************************/

class LGT_API scaledStruct
{
private:
  string plantName;
  vector<msNode *> nodeList;
  hash_map<int, int> scales;

public:
  scaledStruct(string);
  ~scaledStruct();
  
  string getName();
  void setName(string);
  int depth();

  void addNode( msNode * );
  void setNodeList( const vector<msNode *>& );
  msNode * getNode( int );
  vector<int> getAtoms(int);

  vector<int> get1Scale( int );
  int countScale();
  void sonOf( int, int );
  void cleanNodes();

  ScenePtr genNodeScene(int);
  ScenePtr genSelectScene() ;
  ScenePtr genScaleScene( int );
  float totalLA( int );
  vector< pair<uint32_t,double> >   computeProjections( Vector3 );
  void sprojToNodes(Vector3, vector< pair<uint32_t,double> > );

  void beamsToNodes( Vector3, ViewRayPointHitBuffer3 * );
  float probaClassic(int, Vector3);
  Array2<float> probaImage( int, Vector3, vector<distrib>, uint32_t, uint32_t );
  float probaIntercept( int, Vector3, vector<distrib> );
  float probaBeamIntercept( int, Vector3, vector<distrib>, int, int );
  float starClassic( int, Vector3);
  float star( int, Vector3, vector<distrib>);
};

typedef hash_map< int, vector<int> > decompoMap;
typedef vector<decompoMap> dicoTable ;

LGT_API ScenePtr centerShapes( const ScenePtr& );
LGT_API BoundingBoxPtr getBBox( const ShapePtr& );
LGT_API BoundingBoxPtr getBBox( const ScenePtr& );
LGT_API scaledStruct * ssFromDict( string, ScenePtr&, const dicoTable& );

#endif

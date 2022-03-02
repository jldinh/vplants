// -*-c++-*- 
/*
#define EXPORT_DLL(NAME) 
#ifdef WIN32 \
#ifdef NAME##_DLL \
#define NAME##_EXPORT __declspec(dllexport) \
#else \
#define NAME##_EXPORT __declspec(dllimport) \
#endif \
#else \
#define  NAME##_EXPORT \
#endif \

EXPORT_DLL(SCENEOBJ)
EXPORT_DLL(SCENECONT)
*/

#ifdef WIN32
#ifdef CPHYSICS_DLL 
#define CPHYSICS_EXPORT __declspec(dllexport) 
#else 
#define CPHYSICS_EXPORT __declspec(dllimport) 
#endif
#else 
#define  CPHYSICS_EXPORT 
#endif 


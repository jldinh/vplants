#ifndef __MAPPING_H__
#define __MAPPING_H__

#ifdef WIN32
    #ifdef lineage_EXPORTS
        #define LINEAGE_EXPORT __declspec(dllexport)
    #else
        #define LINEAGE_EXPORT __declspec(dllimport)
    #endif
#else
    #define LINEAGE_EXPORT
#endif



#ifdef __cplusplus
extern "C"
{
#endif

  LINEAGE_EXPORT void compute_candidates(const double distance,
                                         const unsigned int nbCells1,
                                         const unsigned int nbCells2,
                                         const unsigned int sx_im1,
                                         const unsigned int sy_im1,
                                         const unsigned int sz_im1,
                                         const unsigned short * data_im1,
                                         const unsigned int sx_im2,
                                         const unsigned int sy_im2,
                                         const unsigned int sz_im2,
                                         const unsigned short * data_im2,
                                         const double vx, const double vy, const double vz,
                                         unsigned int ** moms,
                                         unsigned int ** kids,
                                         double       ** scores,
                                         unsigned int *  nPairs);

  LINEAGE_EXPORT void compute_lineage_mapping(unsigned int nCellsT0,
                                              unsigned int nCellsT1,
                                              unsigned int mapLen,
                                              const unsigned int * mothers,
                                              const unsigned int * children,
                                              const double * scores,
                                              char * rezChildren);


#ifdef __cplusplus
}
#endif

#endif//__MAPPING_H__

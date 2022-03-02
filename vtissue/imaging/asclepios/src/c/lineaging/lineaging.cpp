#include <iostream>
#include <limits>
#include <cstdlib>

#include "lineaging.h"
#include "lineaging_p.h"
#include "candidates_p.h"


//#define USE_UGLY_FIND_CANDIDATES

#ifdef __cplusplus
extern "C"
{
#endif


  typedef std::numeric_limits<unsigned int> IntLimits;


  void compute_candidates(const double distance,
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
			  unsigned int ** ret_moms,
			  unsigned int ** ret_kids,
			  double       ** ret_scores,
			  unsigned int *  ret_nPairs) {

    MotherListType   moms;
    ChildrenListType kids;
    ScoreListType    scores;

#ifdef USE_UGLY_FIND_CANDIDATES
    find_candidates_ugly
#else
      find_candidates
#endif
      (distance, nbCells1, nbCells2,
       sx_im1, sy_im1, sz_im1, data_im1,
       sx_im2, sy_im2, sz_im2, data_im2,
       vx, vy, vz,
       moms, kids, scores);

    // use calloc instead of new since this memory is meant to be deleted
    // by ctypes and ctypes doesn't know anything about new, but does have
    // means to use free(void *)
    MotherListType::size_type size = moms.size();
    *ret_moms = (unsigned int*)std::calloc(size, sizeof(unsigned int));
    *ret_kids = (unsigned int*)std::calloc(size, sizeof(unsigned int));
    *ret_scores = (double*)std::calloc(size, sizeof(double));

    *ret_nPairs = size;
    for(unsigned int i = 0; i<size; ++i) {
      (*ret_moms)[i] = moms[i];
      (*ret_kids)[i] = kids[i];
      (*ret_scores)[i] = scores[i];
    }
  }


  void compute_lineage_mapping(unsigned int nCellsT0,
			       unsigned int nCellsT1,
			       unsigned int mapLen,
			       const unsigned int * mothers,
			       const unsigned int * children,
			       const double * scores,
			       char * rezChildren
			       ) {

    unsigned int *rez = reinterpret_cast<unsigned int*>(rezChildren);

    DestinyListType destinies(nCellsT1, DestinyListType::value_type(0,IntLimits::quiet_NaN()) );
    // std::cout << "mommies" << nCellsT0 << std::endl;
    // std::cout << "kiddies" << nCellsT1 << std::endl;
    //GrapheDeFlot graph(nCellsT0, nCellsT1, mapLen, 1);
    FlowGraph graph(nCellsT0, nCellsT1, mapLen, 1);
    for (unsigned int i=0; i< mapLen; ++i){
      // std::cout << "adding " << i << std::endl;
      //graph.ajouterCoupleDuMapping(mothers[i], children[i], scores[i]);
      graph.defineMapping(mothers[i], children[i], 1.-scores[i]);
    }

    // - compute the flow -
    graph.ajouterLesStructuresSupplementaires();
    graph.unAlgoDeFlot();

    // TODO!!!!!!!!!!!!!!!!! TODO!!!!!!!!!!!!!!!!!!!! DO THIS!
    // ///Calcul des destinees completes
    for(unsigned int i=1;i<nCellsT1;i++){
      destinies[graph.noterLaMaman(i)].push_back(i);
    }

    for( unsigned int i = 1; i<nCellsT1; ++i){
      int mom = graph.noterLaMaman(i);
      if (mom>=0) {
	rez[i]  = static_cast<unsigned int>(mom);
      }
      else {
	rez[i]  = IntLimits::quiet_NaN();
      }
    }

    return;
  }

#ifdef __cplusplus
}
#endif

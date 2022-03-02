#ifndef __CANDIDATES_P_H__
#define __CANDIDATES_P_H__

#include <vector>

typedef std::vector < int >    MotherListType;
typedef std::vector < int >    ChildrenListType;
typedef std::vector < double > ScoreListType;

int find_candidates(const double distance, const unsigned int nbCells1, const unsigned int nbCells2,
		    const unsigned int sx_im1, const unsigned int sy_im1, const unsigned int sz_im1,
		    const unsigned short * data_im1,
		    const unsigned int sx_im2, const unsigned int sy_im2, const unsigned int sz_im2,
		    const unsigned short * data_im2,
		    const double vx, const double vy, const double vz,
		    MotherListType & mothers,
		    ChildrenListType & children,
		    ScoreListType & scores);

int find_candidates_ugly(const double distance, const unsigned int nbCells1, const unsigned int nbCells2,
			 const unsigned int sx_im1, const unsigned int sy_im1, const unsigned int sz_im1,
			 const unsigned short * data_im1,
			 const unsigned int sx_im2, const unsigned int sy_im2, const unsigned int sz_im2,
			 const unsigned short * data_im2,
			 const double vx, const double vy, const double vz,
			 MotherListType & mothers,
			 ChildrenListType & children,
			 ScoreListType & scores);

#endif//__CANDIDATES_P_H__

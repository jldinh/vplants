#ifndef MINCIO_H
#define MINCIO_H

#ifdef MINC_FILES

#include <imageio/ImageIO.h>
#include <minc.h>

#ifdef __cplusplus
extern "C" {
#endif

/** read an image from a minc file
    @param im image structure
    @param name image file name
    @param startx returned X coordinate of origin vertor
    @param starty returned Y coordinate of origin vertor
    @param startz returned Z coordinate of origin vertor
    @param stepx returned X coordinate of step vertor
    @param stepy returned Y coordinate of step vertor
    @param stepz returned Z coordinate of step vertor
    @param Xcosine 3 dimensional array containing X axis cosine directions
    @param Ycosine 3 dimensional array containing Y axis cosine directions
    @param Zcosine 3 dimensional array containing Z axis cosine directions
    @return a negative value in case of failure */
int readMincHeader(_image *im, const char* name,
		   double *startx, double *starty, double *startz,
		   double *stepx, double *stepy, double *stepz,
		   double *Xcosine, double *Ycosine, double *Zcosine);

/** write an image in a minc file
    @param im image structure
    @param name image file name
    @param sourceName original minc file name
    @param startx origin X coordinate
    @param starty origin Y coordinate
    @param startz origin Z coordinate
    @param stepx returned X coordinate of step vertor
    @param stepy returned Y coordinate of step vertor
    @param stepz returned Z coordinate of step vertor
    @param Xcosine 3 dimensional array containing X axis cosine directions
    @param Ycosine 3 dimensional array containing Y axis cosine directions
    @param Zcosine 3 dimensional array containing Z axis cosine directions
    @param range 2 dimensional array containing min an max image intensity
    @return a negative value in case of failure */
int writeMincFile( const _image* im, const char *name, const char *sourceName,
		   double startx, double starty, double startz,
		   double stepx, double stepy, double stepz,
		   const double *Xcosine, const double *Ycosine,
		   const double *Zcosine, const double *range );

#ifdef __cplusplus
}
#endif

#endif

#endif

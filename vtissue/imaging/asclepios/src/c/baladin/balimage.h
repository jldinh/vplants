
#ifndef BALIMAGE_H
#define BALIMAGE_H

#include <recline.h>

typedef enum {
  VT_UNSIGNED_CHAR,  /* Unsigned 8 bits */
  VT_UNSIGNED_SHORT, /* Unsigned 16 bits */
  VT_SIGNED_SHORT,   /* Signed 16 bits */
  VT_UNSIGNED_INT,   /* Unsigned 32 bits */
  VT_SIGNED_INT,     /* Signed 32 bits */
  VT_UNSIGNED_LONG,  /* Unsigned 64 bits */
  VT_SIGNED_LONG,    /* Signed 64 bits */
  VT_FLOAT,          /* Float 32 bits */
  VT_DOUBLE,         /* Float 64 bits */
} VOXELTYPE;
/* The different size of words for a 3D image */

   
typedef struct {
  int ncols;         /* Number of columns (X dimension) */
  int nrows;         /* Number of rows (Y dimension) */
  int nplanes;       /* Number of planes (Z dimension) */
  int vdim;          /* Vector size */
  VOXELTYPE type;
  void *data;        /* Generic pointer on image data buffer.
		        This pointer has to be casted in proper data type
			depending on the type field */
  void ***array;     /* Generic 3D array pointing on each image element.
		        This pointer has to be casted in proper data type
			depending on the type field */
  double vx;          /* real voxel size in X dimension */
  double vy;          /* real voxel size in Y dimension */
  double vz;          /* real voxel size in Z dimension */

  char *name;
} bal_image;





int  BAL_InitImage    ( bal_image *image, char *name,
			int dimx, int dimy, int dimz, int dimv, VOXELTYPE type );
void BAL_FreeImage    ( bal_image *image );
int  BAL_AllocImage   ( bal_image *image );
int BAL_AllocImageArray( bal_image *image );
int BAL_BuildImageArray( bal_image *image );
int BAL_InitAllocImage( bal_image *image, char *name,
			int dimx, int dimy, int dimz, int dimv, VOXELTYPE type );
int BAL_CopyImage( bal_image *theIm, bal_image *resIm );
int  BAL_ImageDataSize( bal_image *image );



int BAL_ReadImage ( bal_image *image, char *name );
int BAL_WriteImage( bal_image *image, char *name );



int BAL_Reech3DTriLin4x4( bal_image *theIm, bal_image *resIm,
			  double *m );
int BAL_SmoothImage( bal_image *theIm,
		     recursiveFilterType theFilter, double sigma );
int BAL_SmoothImageIntoImage( bal_image *theIm, bal_image *resIm,
			      recursiveFilterType theFilter, double sigma );

#endif

#ifndef IMAGE_H
#define IMAGE_H

#include <balimage.h>
#include <baladin.h>
#include <matrix.h>
#include <estimateur.h>


int Pyramidal_Block_Matching( bal_image *theInrimage_ref,
			      bal_image *theInrimage_flo,
			      _MATRIX *theMat_init, /* initial matrix
						       (P_ref = M_init * P_flo),
						       after inversion, allow 
						       to resample the floating
						       image in the geometry of
						       the reference image.
						       NULL if none */
			      _MATRIX *theMat_result,
			      PARAM *theParam );

int Block_Matching( bal_image *theInrimage_ref, /* reference image 
						   (may be subsampled) */
		    bal_image *theInrimage_flo, /* floating image
						   (in its original geometry,
						   may be filtered) */
		    VOXELTYPE theType_flo, /* original floating image type */   
		    _MATRIX *theMat_subsample, /* allow to compute a (subsampled)
						  reference image from the
						  original one 
						  R_sub = MAT_sub * R_orig
					       */
		    _MATRIX *theMat_result, /* allow to compute a floating
					       image from the original
					       reference one
					       R_orig = MAT_res * F_orig
					    */
		    PARAM *param,
		    int level );



/* BLOCKS and FIELDS management */
void Sort_Blocks_WRT_Variance( BLOCS * blocks, PARAM *param );

int Allocate_Field_Blocs_Mesures( FIELD *field, 
				  BLOCS *blocs_flo, BLOCS *blocs_ref, 
				  bal_image *image_flo, bal_image *image_ref, 
				  PARAM *param );

void Free_Field_Blocs_Mesures( FIELD *field, BLOCS *blocs_flo, BLOCS *blocs_ref );



/* MISC */

void  WriteImageVoxelsActifs( PARAM *param, int nb_blocs, BLOCS *blocs, 
			      bal_image *Inrimage_sub, char *nom_image,
			      int seuil_bas, int seuil_haut);
#endif

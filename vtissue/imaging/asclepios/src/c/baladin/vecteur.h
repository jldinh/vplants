#ifndef VECTEUR_H
#define VECTEUR_H

#include <baladin.h>
#include <balimage.h>
#include <estimateur.h>


void CalculChampVecteurs (FIELD *field, 
			  bal_image *inrimage_flo, BLOCS *blocs_flo,
			  bal_image *inrimage_ref, BLOCS *blocs_ref,
			  PARAM *param );

int CalculAttributsBlocs (bal_image *inrimage, BLOCS *blocs,
			  int seuil_bas, int seuil_haut, float seuil_pourcent, 
			  PARAM *param );



#endif

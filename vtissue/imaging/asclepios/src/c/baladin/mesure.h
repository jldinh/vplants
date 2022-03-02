#ifndef MESURE_H
#define MESURE_H



#include <baladin.h>
#include <balimage.h> 

double SimilarityErrorValue( enumTypeMesure m );

/* Calcul de la mesure de similarité entre B(a,b,c) et B(u,v,w), 
   origines des blocs */
double Similarite3D( BLOC *bloc_flo, 
		     BLOC *bloc_ref,
		     bal_image *image_flo, 
		     bal_image *image_ref,
		     PARAM *param );

/* Calcul de la mesure de similarité entre B(a,b) et B(u,v), 
   origines des blocs */
double Similarite2D( BLOC *bloc_flo, 
		     BLOC *bloc_ref,
		     bal_image *image_flo, 
		     bal_image *image_ref,
		     PARAM *param );

#endif

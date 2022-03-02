#ifndef INITIALISATION_H
#define INITIALISATION_H

#include <baladin.h>
#include <matrix.h>


void BAL_SetParametersToDefault( PARAM *p );
void BAL_SetParametersToAuto( PARAM *p );


int Initialize_Matrice_Initiale (char *filename, _MATRIX *m);

int Param_MiseAJour( PARAM *param  );
void BAL_PrintParameters( FILE* f, PARAM *param );

#endif

#ifndef ESTIMATEUR_H
#define ESTIMATEUR_H

#include <baladin.h>
#include <matrix.h>

typedef struct {
  int dim;           /* 2 ou 3 selon les cas 2D ou 3D */
  int npoints;       /* nombre de vecteurs */

  /* distances entre les noeuds extrêmes + 1
  int Dx;            
  int Dy;        
  int Dz;
  */

  float ** x;       /* position    */
  float ** u;       /* déplacement */
  float * rho;      /* similarite  */
} OLDFIELD;       





typedef struct {
  double x;     /* position    */
  double y;
  double u;     /* déplacement */
  double v;
  double rho;   /* similarite  */
} typeScalarWeighted2DDisplacement;

typedef struct {
  double x;     /* position    */
  double y;
  double z;
  double u;     /* déplacement */
  double v;
  double w;
  double rho;   /* similarite  */
} typeScalarWeighted3DDisplacement;

typedef enum {
  _UnknownField_,
  _ScalarWeighted2DDisplacement_,
  _ScalarWeighted3DDisplacement_
} enumFieldType;


typedef struct {
  int n_pairs;       /* nombre de vecteurs */
  int n_allocated_pairs;
  enumFieldType type;
  void *pairs;
} FIELD;






double LS_Trsf_Estimation ( _MATRIX *T, FIELD *field, 
			    enumTypeTransfo transfo );
double LSSW_Trsf_Estimation ( _MATRIX *T, FIELD *field, 
			    enumTypeTransfo transfo );
double Trsf_Estimation ( _MATRIX *T, FIELD *field, 
			 enumTypeTransfo transfo, 
			 enumTypeEstimator estimator );
double Trsf_Trimmed_Estimation ( _MATRIX *T, FIELD * field, 
				 enumTypeTransfo transfo, 
				 PARAM *param, 
				 int do_some_writing );


double Estimate_Transformation( _MATRIX *T, FIELD * field, 
				PARAM *param, 
				int do_some_writing );

/* FIELD management */

int Allocate_Field ( FIELD * field, enumFieldType type, int npoints );

void Free_Field ( FIELD * field );

/* MISC */

void CreateFileDef(FIELD *field, 
		   char *nom_image, char *nom_champ );


#endif

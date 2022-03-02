#ifndef _MATRIX_H
#define _MATRIX_H


/* On definit une matrice comme un tableau de taille ligne x colonne */
typedef struct {
  int l,c;
  double *m;
} _MATRIX;


/*--------------------------------------------------
 *
 * some procedures on transformation matrices
 *
 --------------------------------------------------*/

void ChangeGeometry ( _MATRIX *matrice_res,
		      int dx_ref, int dy_ref, int dz_ref, 
		      double vx_ref, double vy_ref, double vz_ref,
		      int dx_flo, int dy_flo, int dz_flo, 
		      double vx_flo, double vy_flo, double vz_flo );

/* passage du repère voxel au repère reel */
void VoxelMatrix2RealMatrix( _MATRIX *mat_vox, /* input = transformation matrix
						  from voxel grid to voxel grid */
			     _MATRIX *mat_reel, /* output = transformation matrix
						   for real coordinates */
			     double vx_ref, double vy_ref, double vz_ref,
			     double vx_flo, double vy_flo, double vz_flo );



/* passage du repère reel au repère voxel */
void MatriceReel2MatriceVoxel (_MATRIX *mat_reel, _MATRIX *mat_vox,
				  float vx_ref, float vy_ref, float vz_ref,
				  float vx_flo, float vy_flo, float vz_flo );

/* liberation matrix */
void _free_mat (_MATRIX *m);
int _alloc_mat (_MATRIX *m, int l, int c );

/* multiply two matrices:    m1 * m2 = res    */
void _mult_mat ( _MATRIX *m1, _MATRIX *m2, _MATRIX *res );
/* substract two matrices:    m1 - m2  = res   */
void _sub_mat( _MATRIX *m1, _MATRIX *m2, _MATRIX *res );

/* copy matrix */
void _copy_mat( _MATRIX *m, _MATRIX *res );

int _write_mat( char *name, _MATRIX *m );

/* affiche la matrice */
void _print_mat ( FILE *f, _MATRIX *m, char *desc );







/* substract two matrix */
_MATRIX sub_mat(_MATRIX m1, _MATRIX m2);

/* transpose matrix */
_MATRIX transpose(_MATRIX m);

/* det matrix */
double det(_MATRIX mat);

/* inverse matrix */
_MATRIX inv_mat(_MATRIX m);




void Compose_Tmatrix ( _MATRIX T1, _MATRIX T2, _MATRIX T );


void Norms_Tmatrix ( _MATRIX T, double * dr, double * dt );

void Norms_SimilTmatrix ( _MATRIX T, double * dr, double * dt, double echelle );

void Inverse_RigidTmatrix ( _MATRIX T, _MATRIX Tinv);

void Inverse_SimilTmatrix ( _MATRIX T, _MATRIX Tinv, double echelle);


int InverseMat4x4( double *matrice, double *inv );
int InverseMat3x3( double *matrice, double *inv );

void E_DMMatTrans( double *a, double *aT, int dim );

void E_DMMatMul( double *a, double *b, double *ab, int dim );

void E_DMMatMulVect( double *a, double *b, double *c, int dim );

int E_DMVVpropresMatSym( double *m, double *val, double *vec, int dim );

void E_QMatRotFromQuat( double qr[4], double rot[9] );

void Test_Rotation( _MATRIX matrice_reel );

#endif

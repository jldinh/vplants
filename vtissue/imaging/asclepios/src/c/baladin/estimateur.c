#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#include <estimateur.h>



static int _verbose_ = 1;
#define _OLD_BEHAVIOR_ 1



typedef struct{
  double x;
  int rank; 
} ORDERED_DOUBLE;

typedef struct{
  double median;
  double sigma; 
} MAD;


/* --------------------------------------------------------------------
           Comparaison de deux variables de type double
   -------------------------------------------------------------------- */

int Compare_D ( const void * a, const void * b )
{
  double *ad = (double *) a;
  double *bd = (double *) b;

  if ( *ad  >  *bd )
    return (1);
  if ( *ad  <  *bd )
    return (-1);
  return (0);
}

/* --------------------------------------------------------------------
           Comparaison de deux variables de type ORDERED_DOUBLE 
   -------------------------------------------------------------------- */

int Compare_OD ( const void * a, const void * b )
{
  ORDERED_DOUBLE *aod = (ORDERED_DOUBLE *) a;
  ORDERED_DOUBLE *bod = (ORDERED_DOUBLE *) b;

  if ( aod->x  >  bod->x )
    return (1);
  if ( aod->x  <  bod->x )
    return (-1);
  return (0);
}

/* ---------------------------------------------------------------------
                  Médiane d'un tableau de valeurs.
   --------------------------------------------------------------------- */

double Median ( double *tab, int dim ) 
{
  int i, i_left, i_right;
  double med, center;
  double *tab_aux;

  /* ARG, mais ce'st faux ce truc !!!
     - ca trie un tableau de double ne le considerant comme un tableau de float
       (corrige, GM, Tue Jul 15 14:45:02 MEST 2003)
     - de plus, on peut mieux faire ...
     GM
  */

  /* Allocation du tableau auxiliaire où l'on recopie
     les valeurs. On évitera ainsi que le tableau initial
     soit modifié par le tri   */
  tab_aux = (double *) calloc ( dim, sizeof(double) );
  for ( i = 0; i < dim; i ++ ) 
    tab_aux [i] = tab [i];  

  /* On réordonne le tableau selon les valeurs de x */
  qsort ( tab_aux, dim, sizeof(float), & Compare_D );   
  
  /* Le centre des indices vaut (dim-1)/2 */
  center = 0.5 * (dim - 1);
  
  /* Indices a gauche et a droite */
  i_left  = (int) floor ( center );
  i_right = (int) ceil  ( center );
  
  /* Calcul de la médiane */
  med = 0.5 * ( tab_aux [i_left] + tab_aux [i_right] );
  
  /* Libération du tableau auxiliaire */
  free ( tab_aux );
  
  return med;
}


/* ---------------------------------------------------------------------
                 MAD (median of absolute deviations) 
		 d'un tableau de valeurs.
   --------------------------------------------------------------------- */

MAD MADn ( double *tab, int dim) 
{
  int i;
  double * abs_dev;
  MAD mad;

  /* Calcul de la médiane */
  mad.median = Median ( tab, dim );

  /* Allocation du tableau contenant les residus en || */
  abs_dev = (double *) calloc ( dim, sizeof(double) );
  
  /* On stocke les déviations |X-med(X)| */
  for ( i = 0 ; i < dim ; i ++ ) {
   abs_dev [i] = fabs ( tab [i] - (mad.median) ) ; 
  }

  /* Calcul de l'estimateur (avec facteur correctif) */
  mad.sigma  = 1.4826 * Median ( abs_dev, dim );

  free(abs_dev);

  return mad;
}










/* --------------------------------------------------------------------- */
/* Calcul d'une transformation rigide/similitude/affine aux moindres     */
/*   carrés par la  formule explicite utilisant les quaternions.         */
/*   Valable uniquement pour des champs 3D.                              */
/*   Adapté de Grégoire Malandain et Xavier Pennec (these p. 170)        */
/* --------------------------------------------------------------------- */

double LS_Trsf_Estimation ( _MATRIX *T, FIELD *field, enumTypeTransfo transfo )
{
  char *proc = "LS_Trsf_Estimation";
  int N;
  int i, j;
  double barx_x, barx_y, barx_z; 
  double bary_x, bary_y, bary_z; 

  double xb0, xb1, xb2, yb0, yb1, yb2;
  double a[16], aT[16], aTa[16], som[16], r[4], q[4];
  double rog[3], mr[9];
  double varX, varY, CritereRigide, xb[3], yb[3];
  double echelle = 1.0;

  double A[9], Cyx[9], Vx[9], invVx[9];



  /* Nombre d'appariements considérés */
  N = field -> n_pairs;

  /* set return matrix to identity
   */
  T->m [0] = 1.0;    T->m [1] = 0.0;    T->m [2] = 0.0;    T->m [3] = 0.0;
  T->m [4] = 0.0;    T->m [5] = 1.0;    T->m [6] = 0.0;    T->m [7] = 0.0;
  T->m [8] = 0.0;    T->m [9] = 0.0;    T->m [10] = 1.0;   T->m [11] = 0.0;
  T->m [12] = 0.0;   T->m [13] = 0.0;   T->m [14] = 0.0;   T->m [15] = 1.0;
  
  if ( N < 1 ) {
    if ( _verbose_ )
      fprintf (stderr, "%s: empty field\n", proc );
    return( -1.0 );
  }
  else if ( N < 4 ) {
    if ( _verbose_ )
      fprintf (stderr, "%s: not enough pairs for the estimation\n", proc );
    return( -1.0 );
  }

  /* barycenter
   */
  barx_x = barx_y = barx_z = 0.0;
  bary_x = bary_y = bary_z = 0.0;

  switch( field -> type ) {
  default :
    if ( _verbose_ )
      fprintf (stderr, "%s: such field type not handled in switch\n", proc );
    return( -1.0 );
  case _ScalarWeighted2DDisplacement_ :
    {
      typeScalarWeighted2DDisplacement *thePairs = 
	(typeScalarWeighted2DDisplacement *)field->pairs;
      for ( i = 0; i < N; i ++ ) {
	barx_x += thePairs[i].x;
	barx_y += thePairs[i].y;
	bary_x += thePairs[i].u;
	bary_y += thePairs[i].v;
      }
      barx_x /= (double)N;
      barx_y /= (double)N;
      bary_x = barx_x + bary_x / (double)N;
      bary_y = barx_y + bary_y / (double)N;
    }
    break;
  case _ScalarWeighted3DDisplacement_ :
    {
      typeScalarWeighted3DDisplacement *thePairs = 
	(typeScalarWeighted3DDisplacement *)field->pairs;
      for ( i = 0; i < N; i ++ ) {
	barx_x += thePairs[i].x;
	barx_y += thePairs[i].y;
	barx_z += thePairs[i].z;
	bary_x += thePairs[i].u;
	bary_y += thePairs[i].v;
	bary_z += thePairs[i].w;
      }
      barx_x /= (double)N;
      barx_y /= (double)N;
      barx_z /= (double)N;
      bary_x = barx_x + bary_x / (double)N;
      bary_y = barx_y + bary_y / (double)N;
      bary_z = barx_z + bary_z / (double)N;
    }
    break;
  }



  /* transformation computation
   */
  switch( transfo ) {
  default :
    if ( _verbose_ )
      fprintf (stderr, "%s: such transformation type not handled in switch\n", proc );
    return( -1.0 );

  case RIGIDE :
  case SIMILITUDE :
    /* for scale computation (similarity only)
     */
    varX = 0.0; varY = 0.0;
    /* for rotation computation
     */
    for ( i = 0 ; i < 16 ; i ++ )
      a[i] = som [i] = 0.0;

    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      return( -1.0 );
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)field->pairs;

	if ( transfo == RIGIDE ) {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1;
	    a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];
	    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += aTa[j];
	  }
	}
	else {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    varX += ( xb0*xb0 + xb1*xb1 );
	    varY += ( yb0*yb0 + yb1*yb1 );
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1;
	    a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];
	    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += aTa[j];
	  }
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field->pairs;

	if ( transfo == RIGIDE ) {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    xb2 = thePairs[i].z - barx_z;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    yb2 = thePairs[i].z + thePairs[i].w - bary_z;
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1; a[3]   = xb2 - yb2;
	    a[6]   = - ( xb2 + yb2 );  a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];    a[9]   = - a[6];
	    a[12]  = - a[3];    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += aTa[j];
	  }
	}
	else {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    xb2 = thePairs[i].z - barx_z;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    yb2 = thePairs[i].z + thePairs[i].w - bary_z;
	    varX += ( xb0*xb0 + xb1*xb1 + xb2*xb2 );
	    varY += ( yb0*yb0 + yb1*yb1 + yb2*yb2 );
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1; a[3]   = xb2 - yb2;
	    a[6]   = - ( xb2 + yb2 );  a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];    a[9]   = - a[6];
	    a[12]  = - a[3];    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += aTa[j];
	  }
	}
      }
      break;
    } /* switch ( field->type ) */
    
    /* Calcul du vecteur propre associé à la plus petite valeur propre */
    if ( !E_DMVVpropresMatSym( som, r, a, 4 ) ) {
      if ( _verbose_ )
	fprintf( stderr, "%s: unable to compute rotation\n", proc );
      return( -1.0 );
    }
    /* L'erreur sur la rotation est dans r [0] (valeur propre) */
    for ( i = 0 ; i < 4; i ++ )
      q [i] = a [ i*4 ];
  
    /* Calcul de la matrice de rotation */
    E_QMatRotFromQuat ( q, mr );

    if ( transfo == SIMILITUDE ) {
      /*** Calcul du parametre d'echelle - ERIC ***/
      /* calcul du critere au minimum pour les moindres carres rigides */
      CritereRigide = 0.0;
      switch( field -> type ) {
      default :
	if ( _verbose_ )
	  fprintf (stderr, "%s: such field type not handled in switch\n", proc );
	return( -1.0 );
      case _ScalarWeighted2DDisplacement_ :
	{
	  typeScalarWeighted2DDisplacement *thePairs = 
	    (typeScalarWeighted2DDisplacement *)field->pairs;
	  xb[2] = 0.0;
	  for ( i = 0; i < N; i ++ ) {
	    /* Coordonnées barycentriques de l'appariemment courant */
	    xb[0] = thePairs[i].x - barx_x;
	    xb[1] = thePairs[i].y - barx_y;
	    yb[0] = thePairs[i].x + thePairs[i].u - bary_x;
	    yb[1] = thePairs[i].y + thePairs[i].v - bary_y;
	    
	    E_DMMatMulVect ( mr, xb, rog, 3 );
	    
	    CritereRigide += 
	      (yb[0] - rog[0]) * (yb[0] - rog[0]) + 
	      (yb[1] - rog[1]) * (yb[1] - rog[1]);
	  }
	}
	break;
      case _ScalarWeighted3DDisplacement_ :
	{
	  typeScalarWeighted3DDisplacement *thePairs = 
	    (typeScalarWeighted3DDisplacement *)field->pairs;
	  for ( i = 0; i < N; i ++ ) {
	    /* Coordonnées barycentriques de l'appariemment courant */
	    xb[0] = thePairs[i].x - barx_x;
	    xb[1] = thePairs[i].y - barx_y;
	    xb[2] = thePairs[i].z - barx_z;
	    yb[0] = thePairs[i].x + thePairs[i].u - bary_x;
	    yb[1] = thePairs[i].y + thePairs[i].v - bary_y;
	    yb[2] = thePairs[i].z + thePairs[i].w - bary_z;
	    
	    E_DMMatMulVect ( mr, xb, rog, 3 );
	    
	    CritereRigide += 
	      (yb[0] - rog[0]) * (yb[0] - rog[0]) + 
	      (yb[1] - rog[1]) * (yb[1] - rog[1]) + 
	      (yb[2] - rog[2]) * (yb[2] - rog[2]);
	  }
	}
	break;
      }
      /* calcul de l'echelle */
      echelle = (varX + varY - CritereRigide) / ( 2 * varX );
    }
    
    xb[0] = barx_x;    xb[1] = barx_y;    xb[2] = barx_z;
    E_DMMatMulVect ( mr, xb, rog, 3 );

    /* Calcul de la matrice de transformation */
    T->m[0] = echelle*mr[0]; T->m[1] = echelle*mr[1]; T->m[2] = echelle*mr[2]; 
    T->m[3] = bary_x - echelle*rog[0];
    
    T->m[4] = echelle*mr[3]; T->m[5] = echelle*mr[4]; T->m[6] = echelle*mr[5]; 
    T->m[7] = bary_y - echelle*rog[1];
    
    T->m[8] = echelle*mr[6]; T->m[9] = echelle*mr[7]; T->m[10] =  echelle*mr[8]; 
    T->m[11] = bary_z - echelle*rog[2];
    
    T->m[12] = 0.0; T->m[13] = 0.0; T->m[14] = 0.0; T->m[15] = 1.0;
    
    /* end of case RIGIDE, SIMILITUDE
     */
    break;
    
  case AFFINE :
    
    for ( i = 0 ; i < 9 ; i ++ )
      Cyx[i] = Vx[i] = 0.0;
    
    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      return( -1.0 );
    case _ScalarWeighted2DDisplacement_ :
    {
      typeScalarWeighted2DDisplacement *thePairs = 
	(typeScalarWeighted2DDisplacement *)field->pairs;
      for ( i = 0; i < N; i ++ ) {
	  /* barycentric coordinates
	   */
	  xb0 = thePairs[i].x - barx_x;
	  xb1 = thePairs[i].y - barx_y;
	  yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	  yb1 = thePairs[i].y + thePairs[i].v - bary_y;

	  /* Incrémentation des matrices */
	  Cyx [0] += yb0 * xb0;    Cyx [1] += yb0 * xb1;    
	  Cyx [3] += yb1 * xb0;    Cyx [4] += yb1 * xb1;    
	  
	  Vx [0] += xb0 * xb0;    Vx [1] += xb0 * xb1;    
	  Vx [4] += xb1 * xb1;    
      }
    }
    break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field->pairs;
	for ( i = 0; i < N; i ++ ) {
	  /* barycentric coordinates
	   */
	  xb0 = thePairs[i].x - barx_x;
	  xb1 = thePairs[i].y - barx_y;
	  xb2 = thePairs[i].z - barx_z;
	  yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	  yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	  yb2 = thePairs[i].z + thePairs[i].w - bary_z;

	  /* Incrémentation des matrices */
	  Cyx [0] += yb0 * xb0;    Cyx [1] += yb0 * xb1;    Cyx [2] += yb0 * xb2;
	  Cyx [3] += yb1 * xb0;    Cyx [4] += yb1 * xb1;    Cyx [5] += yb1 * xb2;
	  Cyx [6] += yb2 * xb0;    Cyx [7] += yb2 * xb1;    Cyx [8] += yb2 * xb2;
	  
	  Vx [0] += xb0 * xb0;    Vx [1] += xb0 * xb1;    Vx [2] += xb0 * xb2;
	  Vx [4] += xb1 * xb1;    Vx [5] += xb1 * xb2;    Vx [8] += xb2 * xb2;
	}
      }
      break;
    }

    Vx [3]  = Vx [1];  Vx [6]  = Vx [2];  Vx [7]  = Vx [5];
 
    /* Normalisation pour stabilité numérique (peut-être superflu) 
       for ( i = 0 ; i < 3 ; i ++ )
       for ( j = 0 ; j < 3 ; j ++ )       {
       Cyx.m[j + 3*i] = Cyx.m[j + 3*i] / (double) N;
       Vx.m[j + 3*i] = Vx.m[j + 3*i] / (double) N;
       }*/

    /* Gestion ad hoc du cas 2D */
    switch( field -> type ) {
    default :
      break;
    case _ScalarWeighted2DDisplacement_ :
      Cyx [2] = 0;     Cyx [5] = 0;     Cyx [8] = 1; 
      Vx [6]  = Vx  [2] = 0;     
      Vx [7]  = Vx  [5] = 0;     
      Vx  [8] = 1; 
    }

    /* Inversion de la matrice de variance (3x3) 
       invVx = inv_mat (Vx);*/
    /* Pas confiance dans inv_mat -> on utilise InverseMat4x4 */
    if ( InverseMat3x3( Vx, invVx ) != 3 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to invert matrix Vx\n", proc );
      return( -1.0 );
    }

    /* Calcul de la matrice A */
    E_DMMatMul ( Cyx, invVx, A, 3 );
    
    /* Calcul de la transformation affine */
    T->m [0] = A [0];  T->m [1] = A [1];  T->m [2] = A [2];
    T->m [3] = bary_x - A[0]*barx_x - A[1]*barx_y - A[2]*barx_z;
    
    T->m [4] = A [3];  T->m [5] = A [4];  T->m [6] = A [5];
    T->m [7] = bary_y - A[3]*barx_x - A[4]*barx_y - A[5]*barx_z;
    
    T->m [8]  = A [6];  T->m [9]  = A [7];  T->m [10] = A [8];
    T->m [11] = bary_z - A[6]*barx_x - A[7]*barx_y - A[8]*barx_z;
    
    T->m [12] = 0.0;  T->m [13] = 0.0;  T->m [14] = 0.0;  T->m [15] = 1.0;

    break;
    /* end of case AFFINE
     */
    
  } /* switch( transfo ) */
  
  return ( echelle );
}










/* --------------------------------------------------------------------- */
/* Calcul d'une transformation rigide/similitude/affine aux moindres     */
/* carrés par la  formule explicite utilisant les quaternions.           */
/* avec ponderation par la  mesure locale de correlation.                */
/*   Valable uniquement pour des champs 3D.                              */
/*   Adapté de Grégoire Malandain et Xavier Pennec (these p. 170)        */
/* --------------------------------------------------------------------- */

double LSSW_Trsf_Estimation ( _MATRIX *T, FIELD *field, enumTypeTransfo transfo )
{
  char *proc = "LSSW_Trsf_Estimation";
  int N;
  int i, j;
  double barx_x, barx_y, barx_z; 
  double bary_x, bary_y, bary_z; 

  double xb0, xb1, xb2, yb0, yb1, yb2;
  double a[16], aT[16], aTa[16], som[16], r[4], q[4];
  double rog[3], mr[9];
  double varX, varY, CritereRigide, xb[3], yb[3];
  double echelle = 1.0;

  double A[9], Cyx[9], Vx[9], invVx[9];

  double rho_total = 0.0;



  /* Nombre d'appariements considérés */
  N = field -> n_pairs;

  /* set return matrix to identity
   */
  T->m [0] = 1.0;    T->m [1] = 0.0;    T->m [2] = 0.0;    T->m [3] = 0.0;
  T->m [4] = 0.0;    T->m [5] = 1.0;    T->m [6] = 0.0;    T->m [7] = 0.0;
  T->m [8] = 0.0;    T->m [9] = 0.0;    T->m [10] = 1.0;   T->m [11] = 0.0;
  T->m [12] = 0.0;   T->m [13] = 0.0;   T->m [14] = 0.0;   T->m [15] = 1.0;
  
  if ( N < 1 ) {
    if ( _verbose_ )
      fprintf (stderr, "%s: empty field\n", proc );
    return( -1.0 );
  }
  else if ( N < 4 ) {
    if ( _verbose_ )
      fprintf (stderr, "%s: not enough pairs for the estimation\n", proc );
    return( -1.0 );
  }

  /* barycenter
   */
  barx_x = barx_y = barx_z = 0.0;
  bary_x = bary_y = bary_z = 0.0;

  switch( field -> type ) {
  default :
    if ( _verbose_ )
      fprintf (stderr, "%s: such field type not handled in switch\n", proc );
    return( -1.0 );
  case _ScalarWeighted2DDisplacement_ :
    {
      typeScalarWeighted2DDisplacement *thePairs = 
	(typeScalarWeighted2DDisplacement *)field->pairs;
      for ( i = 0; i < N; i ++ ) {
	barx_x += thePairs[i].rho * thePairs[i].x;
	barx_y += thePairs[i].rho * thePairs[i].y;
	bary_x += thePairs[i].rho * thePairs[i].u;
	bary_y += thePairs[i].rho * thePairs[i].v;
	rho_total += thePairs[i].rho;
      }
      barx_x /= rho_total;
      barx_y /= rho_total;
      bary_x = barx_x + bary_x / rho_total;
      bary_y = barx_y + bary_y / rho_total;
    }
    break;
  case _ScalarWeighted3DDisplacement_ :
    {
      typeScalarWeighted3DDisplacement *thePairs = 
	(typeScalarWeighted3DDisplacement *)field->pairs;
      for ( i = 0; i < N; i ++ ) {
	barx_x += thePairs[i].rho * thePairs[i].x;
	barx_y += thePairs[i].rho * thePairs[i].y;
	barx_z += thePairs[i].rho * thePairs[i].z;
	bary_x += thePairs[i].rho * thePairs[i].u;
	bary_y += thePairs[i].rho * thePairs[i].v;
	bary_z += thePairs[i].rho * thePairs[i].w;
	rho_total += thePairs[i].rho;
      }
      barx_x /= rho_total;
      barx_y /= rho_total;
      barx_z /= rho_total;
      bary_x = barx_x + bary_x / rho_total;
      bary_y = barx_y + bary_y / rho_total;
      bary_z = barx_z + bary_z / rho_total;
    }
    break;
  }



  /* transformation computation
   */
  switch( transfo ) {
  default :
    if ( _verbose_ )
      fprintf (stderr, "%s: such transformation type not handled in switch\n", proc );
    return( -1.0 );

  case RIGIDE :
  case SIMILITUDE :
    /* for scale computation (similarity only)
     */
    varX = 0.0; varY = 0.0;
    /* for rotation computation
     */
    for ( i = 0 ; i < 16 ; i ++ )
      a[i] = som [i] = 0.0;

    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      return( -1.0 );
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)field->pairs;

	if ( transfo == RIGIDE ) {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1;
	    a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];
	    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += thePairs[i].rho * aTa[j];
	  }
	}
	else {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    varX += thePairs[i].rho * ( xb0*xb0 + xb1*xb1 );
	    varY += thePairs[i].rho * ( yb0*yb0 + yb1*yb1 );
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1;
	    a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];
	    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += thePairs[i].rho * aTa[j];
	  }
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field->pairs;

	if ( transfo == RIGIDE ) {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    xb2 = thePairs[i].z - barx_z;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    yb2 = thePairs[i].z + thePairs[i].w - bary_z;
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1; a[3]   = xb2 - yb2;
	    a[6]   = - ( xb2 + yb2 );  a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];    a[9]   = - a[6];
	    a[12]  = - a[3];    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += thePairs[i].rho * aTa[j];
	  }
	}
	else {
	  for ( i = 0; i < N; i ++ ) {
	    /* barycentric coordinates
	     */
	    xb0 = thePairs[i].x - barx_x;
	    xb1 = thePairs[i].y - barx_y;
	    xb2 = thePairs[i].z - barx_z;
	    yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	    yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	    yb2 = thePairs[i].z + thePairs[i].w - bary_z;
	    varX += thePairs[i].rho * ( xb0*xb0 + xb1*xb1 + xb2*xb2 );
	    varY += thePairs[i].rho * ( yb0*yb0 + yb1*yb1 + yb2*yb2 );
	    /* Calcul de la matrice som telle que
	       SSD = q^T * A * q ,
	       q étant le quaternion recherché
	    */
	    a[1]   = xb0 - yb0;  a[2]   = xb1 - yb1; a[3]   = xb2 - yb2;
	    a[6]   = - ( xb2 + yb2 );  a[7]   = xb1 + yb1;  a[11]  = - ( xb0 + yb0 );
	    a[4]   = - a[1];    a[8]   = - a[2];    a[9]   = - a[6];
	    a[12]  = - a[3];    a[13]  = - a[7];    a[14]  = - a[11];
	    E_DMMatTrans ( a, aT, 4 );
	    E_DMMatMul ( aT, a, aTa, 4);
	    for ( j = 0; j < 16; j ++ ) som[j] += thePairs[i].rho * aTa[j];
	  }
	}
      }
      break;
    } /* switch ( field->type ) */
    
    /* Calcul du vecteur propre associé à la plus petite valeur propre */
    if ( !E_DMVVpropresMatSym( som, r, a, 4 ) ) {
      if ( _verbose_ )
	fprintf( stderr, "%s: unable to compute rotation\n", proc );
      return( -1.0 );
    }
    /* L'erreur sur la rotation est dans r [0] (valeur propre) */
    for ( i = 0 ; i < 4; i ++ )
      q [i] = a [ i*4 ];
  
    /* Calcul de la matrice de rotation */
    E_QMatRotFromQuat ( q, mr );

    if ( transfo == SIMILITUDE ) {
      /*** Calcul du parametre d'echelle - ERIC ***/
      /* calcul du critere au minimum pour les moindres carres rigides */
      CritereRigide = 0.0;
      switch( field -> type ) {
      default :
	if ( _verbose_ )
	  fprintf (stderr, "%s: such field type not handled in switch\n", proc );
	return( -1.0 );
      case _ScalarWeighted2DDisplacement_ :
	{
	  typeScalarWeighted2DDisplacement *thePairs = 
	    (typeScalarWeighted2DDisplacement *)field->pairs;
	  xb[2] = 0.0;
	  for ( i = 0; i < N; i ++ ) {
	    /* Coordonnées barycentriques de l'appariemment courant */
	    xb[0] = thePairs[i].x - barx_x;
	    xb[1] = thePairs[i].y - barx_y;
	    yb[0] = thePairs[i].x + thePairs[i].u - bary_x;
	    yb[1] = thePairs[i].y + thePairs[i].v - bary_y;
	    
	    E_DMMatMulVect ( mr, xb, rog, 3 );
	    
	    CritereRigide += 
	      thePairs[i].rho * ( (yb[0] - rog[0]) * (yb[0] - rog[0]) + 
				  (yb[1] - rog[1]) * (yb[1] - rog[1]) );
	  }
	}
	break;
      case _ScalarWeighted3DDisplacement_ :
	{
	  typeScalarWeighted3DDisplacement *thePairs = 
	    (typeScalarWeighted3DDisplacement *)field->pairs;
	  for ( i = 0; i < N; i ++ ) {
	    /* Coordonnées barycentriques de l'appariemment courant */
	    xb[0] = thePairs[i].x - barx_x;
	    xb[1] = thePairs[i].y - barx_y;
	    xb[2] = thePairs[i].z - barx_z;
	    yb[0] = thePairs[i].x + thePairs[i].u - bary_x;
	    yb[1] = thePairs[i].y + thePairs[i].v - bary_y;
	    yb[2] = thePairs[i].z + thePairs[i].w - bary_z;
	    
	    E_DMMatMulVect ( mr, xb, rog, 3 );
	    
	    CritereRigide += 
	      thePairs[i].rho * ( (yb[0] - rog[0]) * (yb[0] - rog[0]) + 
				  (yb[1] - rog[1]) * (yb[1] - rog[1]) + 
				  (yb[2] - rog[2]) * (yb[2] - rog[2]) );
	  }
	}
	break;
      }
      /* calcul de l'echelle */
      echelle = (varX + varY - CritereRigide) / ( 2 * varX );
    }
    
    xb[0] = barx_x;    xb[1] = barx_y;    xb[2] = barx_z;
    E_DMMatMulVect ( mr, xb, rog, 3 );

    /* Calcul de la matrice de transformation */
    T->m[0] = echelle*mr[0]; T->m[1] = echelle*mr[1]; T->m[2] = echelle*mr[2]; 
    T->m[3] = bary_x - echelle*rog[0];
    
    T->m[4] = echelle*mr[3]; T->m[5] = echelle*mr[4]; T->m[6] = echelle*mr[5]; 
    T->m[7] = bary_y - echelle*rog[1];
    
    T->m[8] = echelle*mr[6]; T->m[9] = echelle*mr[7]; T->m[10] =  echelle*mr[8]; 
    T->m[11] = bary_z - echelle*rog[2];
    
    T->m[12] = 0.0; T->m[13] = 0.0; T->m[14] = 0.0; T->m[15] = 1.0;
    
    /* end of case RIGIDE, SIMILITUDE
     */
    break;
    
  case AFFINE :
    
    for ( i = 0 ; i < 9 ; i ++ )
      Cyx[i] = Vx[i] = 0.0;
    
    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      return( -1.0 );
    case _ScalarWeighted2DDisplacement_ :
    {
      typeScalarWeighted2DDisplacement *thePairs = 
	(typeScalarWeighted2DDisplacement *)field->pairs;
      for ( i = 0; i < N; i ++ ) {
	  /* barycentric coordinates
	   */
	  xb0 = thePairs[i].x - barx_x;
	  xb1 = thePairs[i].y - barx_y;
	  yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	  yb1 = thePairs[i].y + thePairs[i].v - bary_y;

	  /* Incrémentation des matrices */
	  Cyx [0] += thePairs[i].rho * yb0 * xb0;    
	  Cyx [1] += thePairs[i].rho * yb0 * xb1;    
	  Cyx [3] += thePairs[i].rho * yb1 * xb0;    
	  Cyx [4] += thePairs[i].rho * yb1 * xb1;    
	  
	  Vx [0] += thePairs[i].rho * xb0 * xb0;    
	  Vx [1] += thePairs[i].rho * xb0 * xb1;    
	  Vx [4] += thePairs[i].rho * xb1 * xb1;    
      }
    }
    break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field->pairs;
	for ( i = 0; i < N; i ++ ) {
	  /* barycentric coordinates
	   */
	  xb0 = thePairs[i].x - barx_x;
	  xb1 = thePairs[i].y - barx_y;
	  xb2 = thePairs[i].z - barx_z;
	  yb0 = thePairs[i].x + thePairs[i].u - bary_x;
	  yb1 = thePairs[i].y + thePairs[i].v - bary_y;
	  yb2 = thePairs[i].z + thePairs[i].w - bary_z;

	  /* Incrémentation des matrices */
	  Cyx [0] += thePairs[i].rho * yb0 * xb0;    
	  Cyx [1] += thePairs[i].rho * yb0 * xb1;    
	  Cyx [2] += thePairs[i].rho * yb0 * xb2;
	  Cyx [3] += thePairs[i].rho * yb1 * xb0;    
	  Cyx [4] += thePairs[i].rho * yb1 * xb1;    
	  Cyx [5] += thePairs[i].rho * yb1 * xb2;
	  Cyx [6] += thePairs[i].rho * yb2 * xb0;    
	  Cyx [7] += thePairs[i].rho * yb2 * xb1;    
	  Cyx [8] += thePairs[i].rho * yb2 * xb2;
	  
	  Vx [0] += thePairs[i].rho * xb0 * xb0;    
	  Vx [1] += thePairs[i].rho * xb0 * xb1;    
	  Vx [2] += thePairs[i].rho * xb0 * xb2;
	  Vx [4] += thePairs[i].rho * xb1 * xb1;    
	  Vx [5] += thePairs[i].rho * xb1 * xb2;    
	  Vx [8] += thePairs[i].rho * xb2 * xb2;
	}
      }
      break;
    }

    Vx [3]  = Vx [1];  Vx [6]  = Vx [2];  Vx [7]  = Vx [5];
 
    /* Normalisation pour stabilité numérique (peut-être superflu) 
       (n'est pas faite dans le cas non weighted)
     */
    for ( i = 0 ; i < 3 ; i ++ )
      for ( j = 0 ; j < 3 ; j ++ )  {
	Cyx[j + 3*i] = Cyx[j + 3*i] / rho_total;
	Vx[j + 3*i] = Vx[j + 3*i] / rho_total;
      }
    /* Normalisation pour stabilité numérique (peut-être superflu) 
       for ( i = 0 ; i < 3 ; i ++ )
       for ( j = 0 ; j < 3 ; j ++ )       {
       Cyx.m[j + 3*i] = Cyx.m[j + 3*i] / (double) N;
       Vx.m[j + 3*i] = Vx.m[j + 3*i] / (double) N;
       }*/

    /* Gestion ad hoc du cas 2D */
    switch( field -> type ) {
    default :
      break;
    case _ScalarWeighted2DDisplacement_ :
      Cyx [2] = 0;     Cyx [5] = 0;     Cyx [8] = 1; 
      Vx [6]  = Vx  [2] = 0;     
      Vx [7]  = Vx  [5] = 0;     
      Vx  [8] = 1; 
    }

    /* Inversion de la matrice de variance (3x3) 
       invVx = inv_mat (Vx);*/
    /* Pas confiance dans inv_mat -> on utilise InverseMat4x4 */
    if ( InverseMat3x3( Vx, invVx ) != 3 ) {
      if ( _verbose_ ) 
	fprintf( stderr, "%s: unable to invert matrix Vx\n", proc );
      return( -1.0 );
    }

    /* Calcul de la matrice A */
    E_DMMatMul ( Cyx, invVx, A, 3 );
    
    /* Calcul de la transformation affine */
    T->m [0] = A [0];  T->m [1] = A [1];  T->m [2] = A [2];
    T->m [3] = bary_x - A[0]*barx_x - A[1]*barx_y - A[2]*barx_z;
    
    T->m [4] = A [3];  T->m [5] = A [4];  T->m [6] = A [5];
    T->m [7] = bary_y - A[3]*barx_x - A[4]*barx_y - A[5]*barx_z;
    
    T->m [8]  = A [6];  T->m [9]  = A [7];  T->m [10] = A [8];
    T->m [11] = bary_z - A[6]*barx_x - A[7]*barx_y - A[8]*barx_z;
    
    T->m [12] = 0.0;  T->m [13] = 0.0;  T->m [14] = 0.0;  T->m [15] = 1.0;

    break;
    /* end of case AFFINE
     */
    
  } /* switch( transfo ) */
  
  return ( echelle );
}




double Trsf_Estimation ( _MATRIX *T, FIELD *field, 
			 enumTypeTransfo transfo, enumTypeEstimator estimator )
{
  switch( estimator ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "Trsf_Estimation: estimator type not handled in switch" );
    return( -1.0 );
  case TYPE_LS :
    return( LS_Trsf_Estimation( T, field, transfo ) );
  case TYPE_LSSW :
    return( LSSW_Trsf_Estimation( T, field, transfo ) );
  }
  return( -1.0 );
}





  
/* ---------------------------------------------------------------------
   Calcul d'une transformation rigide/similitude/affine par LTS. 
   Intérêt: robustesse. 
   Le critère du LTS est : sum_{i<h} r_{o(i)}^2
   Principe de l'algorithme:
      1. Initialiser (A, t) 
      2. Calculer les résidus r_i = || y_i - A x_i - t ||
      3. Considérer une liste d'appariemments correspondant 
         aux h plus faibles r_i 
      4. Sur cette liste, calculer la transformation (A, t)
         aux moindres carrés
      5. Reprendre en 2 si la transformation a peu évolué.
--------------------------------------------------------------------- */

double Trsf_Trimmed_Estimation ( _MATRIX *T, FIELD * field, 
				 enumTypeTransfo transfo, 
				 PARAM *param, 
				 int do_some_writing )
{
  char * proc = "Trsf_Trimmed_Estimation";
  int N, h;
  FIELD sub_field;
  ORDERED_DOUBLE * sqerror;

  int iter;
  const int ITER_MAX_LTS = 100;
  double eps_r;
  const double tol_r = 1e-4;
  double eps_t;
  const double tol_t = 1e-4;

  double echelle0, echelle = 1.0;

  _MATRIX T0, dT, Taux;
  double *mat;
  double x0, x1, x2;
  double res0, res1, res2;

  int i, j;


  char image_name[SIZE_NAME];
  char field_name[SIZE_NAME];

  int refine = 0;

  if ( param->use_lts == 0 )
    return( Trsf_Estimation( T, field, transfo, param->estimateur ) );



  /* --- Calcul du nombre total d'appariements --- */
  N = field -> n_pairs;

  /* --- Calcul du cut-off --- */
  if ( ( param->lts_cut <= 0 ) || ( param->lts_cut > 1) ) {
    fprintf ( stderr, "%s: bad cut-off fraction (%f), shoud be in ]0,1]\n", proc, param->lts_cut );
    return( -1.0 );
  }
  h = (int) ( param->lts_cut * (double) N );
  


  /* set return matrix to identity
   */
  T->m [0] = 1.0;    T->m [1] = 0.0;    T->m [2] = 0.0;    T->m [3] = 0.0;
  T->m [4] = 0.0;    T->m [5] = 1.0;    T->m [6] = 0.0;    T->m [7] = 0.0;
  T->m [8] = 0.0;    T->m [9] = 0.0;    T->m [10] = 1.0;   T->m [11] = 0.0;
  T->m [12] = 0.0;   T->m [13] = 0.0;   T->m [14] = 0.0;   T->m [15] = 1.0;

  /* initial transformation estimation
   */
  echelle = Trsf_Estimation( T, field, transfo, param->estimateur );

  if ( echelle <= 0.0 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: something goes wrong in the initial transformation estimation\n", proc );
    return( echelle );
  }

  /* --- Allocation mémoire pour le sous-champ --- */
  if ( Allocate_Field ( &sub_field, field->type, h ) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate sub field\n", proc );
    return( echelle );
  }

  sqerror = ( ORDERED_DOUBLE * ) calloc ( N, sizeof (ORDERED_DOUBLE) );
  if ( sqerror == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate array of residuals\n", proc );
    Free_Field( &sub_field );
    return( echelle );
  }

  if ( _alloc_mat( &T0, 4, 4 ) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #1\n", proc );
    free( sqerror );
    Free_Field( &sub_field );
    return( echelle );
  }
  if ( _alloc_mat( &Taux, 4, 4 ) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #2\n", proc );
    _free_mat( &T0 );
    free( sqerror );
    Free_Field( &sub_field );
    return( echelle );
  }
  if ( _alloc_mat( &dT, 4, 4 ) != 1 ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate matrix #3\n", proc );
    _free_mat( &Taux );
    _free_mat( &T0 );
    free( sqerror );
    Free_Field( &sub_field );
    return( echelle );
  }

  /* loop initialisation
   */
  iter = 0;

  do {

    _copy_mat( T, &T0 );
    echelle0 = echelle;

    mat = T->m;

    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      _free_mat( &dT );
      _free_mat( &Taux );
      _free_mat( &T0 );
      free( sqerror );
      Free_Field( &sub_field );
      return( echelle );
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)field->pairs;
	for ( i = 0; i < N; i ++ ) {
	  x0 = thePairs[i].x;
	  x1 = thePairs[i].y;
	  res0 = ( x0 + thePairs[i].u - (mat[0]*x0 + mat[1]*x1 + mat[3]) );   
	  res1 = ( x1 + thePairs[i].v - (mat[4]*x0 + mat[5]*x1 + mat[7]) );   
	  sqerror [i].x = res0*res0 + res1*res1;
	  sqerror [i].rank = i;
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field->pairs;
	for ( i = 0; i < N; i ++ ) {
	  x0 = thePairs[i].x;
	  x1 = thePairs[i].y;
	  x2 = thePairs[i].z;
	  res0 = ( x0 + thePairs[i].u - (mat[0]*x0 + mat[1]*x1 + mat[2]*x2  + mat[3]) );   
	  res1 = ( x1 + thePairs[i].v - (mat[4]*x0 + mat[5]*x1 + mat[6]*x2  + mat[7]) );   
	  res2 = ( x2 + thePairs[i].w - (mat[8]*x0 + mat[9]*x1 + mat[10]*x2 + mat[11]) );
	  sqerror [i].x = res0*res0 + res1*res1 + res2*res2;
	  sqerror [i].rank = i;
	}
      }
      break;
    }

    /* --- Tri des résidus par ordre croissant --- */
    if ( 0 ) {
      qsort ( sqerror, N, sizeof (ORDERED_DOUBLE), & Compare_OD );
    }
    else {
      int last, left = 0; 
      int right = N-1;
      int k;
      ORDERED_DOUBLE tmp;
      do {
	/* swap left et (left+right)/2 */
	j = (left+right)/2;
	tmp = sqerror[left]; sqerror[left] = sqerror[j]; sqerror[j] = tmp;
	last = left;
        for ( k = left+1; k <= right; k++ ) {
          if ( sqerror[k].x < sqerror[left].x ) {
	    last ++;
            tmp = sqerror[k]; sqerror[k] = sqerror[last]; sqerror[last] = tmp;
          }
        }
	tmp = sqerror[left]; sqerror[left] = sqerror[last]; sqerror[last] = tmp;
        if ( last >  h ) right = last - 1;
        if ( last <  h ) left  = last + 1;
      } while ( last != h );                         
    }

    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      _free_mat( &dT );
      _free_mat( &Taux );
      _free_mat( &T0 );
      free( sqerror );
      Free_Field( &sub_field );
      return( echelle );
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)field->pairs;
	typeScalarWeighted2DDisplacement *subPairs = 
	  (typeScalarWeighted2DDisplacement *)sub_field.pairs;
	for ( i = 0; i < h; i ++ ) {
	  j = sqerror [i].rank; 
	  subPairs[i] = thePairs[j];
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)field->pairs;
	typeScalarWeighted3DDisplacement *subPairs = 
	  (typeScalarWeighted3DDisplacement *)sub_field.pairs;
	for ( i = 0; i < h; i ++ ) {
	  j = sqerror [i].rank; 
	  subPairs[i] = thePairs[j];
	}
      }
      break;
    }

    sub_field.n_pairs = h;


    /* Si -vischeck, ecrit sur le disque le sub_field apres LTS a la premiere iteration,
       i.e. les appariements correspondant aux plus petits residus */
    if ( (iter == 0 ) && ( param->vischeck == 1 ) && (param->write_def == 1) 
	 && ( do_some_writing ) ) {
      /* Ecriture sur le disque */
      sprintf( image_name, "blocs_actifs_flo_py_%d.inr.gz", param->sub);
      sprintf( field_name, "def_lts_%d.m", param->sub);
      CreateFileDef( & sub_field, image_name, field_name );
    }


    /* --- Estimation de la transformation pour le sous-champ --- */

    echelle = Trsf_Estimation( T, &sub_field, transfo, param->estimateur );

    if ( echelle <= 0.0 ) {
      if ( _verbose_ ) {
	fprintf( stderr, "%s: something goes wrong in the transformation estimation\n", proc );
	fprintf( stderr, "\t iteration #%d of the iterated (trimmed) estimation\n", iter );
      }
      _copy_mat( &T0, T );
      _free_mat( &dT );
      _free_mat( &Taux );
      _free_mat( &T0 );
      free( sqerror );
      Free_Field( &sub_field );
      return( echelle0 );
    }


    /* --- Comparaison de T et T0 --- */
    switch ( transfo ) {
    default :
      if ( _verbose_ )
	fprintf( stderr, "%s: transformation type not handled yet\n", proc );
      _copy_mat( &T0, T );      
       _free_mat( &dT );
      _free_mat( &Taux );
      _free_mat( &T0 );
      free( sqerror );
      Free_Field( &sub_field );     
      return( echelle0 );
    case RIGIDE :
      Inverse_RigidTmatrix ( T0, Taux ); 
      Compose_Tmatrix ( Taux, *T, dT ); 
      Norms_Tmatrix ( dT, & eps_r, & eps_t ); 
      break;
    case SIMILITUDE :
    case AFFINE :
      eps_r = 0;
      for ( i = 0; i < 3; i ++ )
	for ( j = 0; j < 3; j ++ )
	  eps_r += ( T0.m[j+i*T0.c] - T->m[j+i*T->c] ) * ( T0.m[j+i*T0.c] - T->m[j+i*T->c] );
      eps_r = sqrt (eps_r);
      eps_t = (T0.m[3] - T->m[3])*(T0.m[3] - T->m[3]) +
	(T0.m[7] - T->m[7])*(T0.m[7] - T->m[7]) + (T0.m[11] - T->m[11])*(T0.m[11] - T->m[11]);
      eps_t = sqrt (eps_t);
    }

    iter ++;
    
    if ( param->verbose > 0 && param->verbosef != NULL ) {
#ifdef _OLD_BEHAVIOR_
      fprintf(stderr, "LTS: Iteration n. %2d \r", iter); 
#else
      if ( param->verbosef == stderr ) {
	fprintf( param->verbosef, "LTS: iteration #%2d \r", iter ); 
      }
      else {
	fprintf( param->verbosef, "LTS: iteration #%2d \n", iter ); 
      }
#endif
    }

  } while ( ((eps_r > tol_r) || (eps_t > tol_t)) && (iter < ITER_MAX_LTS) );



  _free_mat( &dT );
  _free_mat( &Taux );
  _free_mat( &T0 );
  free( sqerror );



  if ( refine == 1 ) {

    double *residual_0;
    double *residual_1;
    double *residual_2;

    double med_0, med_1, med_2 = 0.0;
    double sigma_0, sigma_1, sigma_2 = 0.0;
    double Decision;
    MAD mad_0, mad_1, mad_2 = {0.0, 0.0};

    /* NOTE : refine initialise a 0 et pas accessible comme parametre...
              DONC ne passe jamais par la ! A REVOIR 
       Sat Jun 21 18:04:43 MEST 2003
              Ca vaut mieux, la fonction MADn doit renvoyer
	      n'importe quoi, car la fonction Median renvoie
	      n'importe quoi
    */
    if ( param->verbose > 0 && param->verbosef != NULL )
      fprintf( param->verbosef, "\n\nLTS: Robust analysis of matching errors...\n");

    residual_0 = (double*)malloc( 3*h*sizeof(double) );
    if ( residual_0 == NULL ) {
     if ( _verbose_ ) 
       fprintf( stderr, "%s: unable to allocate residuals array\n", proc );
     return( echelle );
    }
    residual_1 = residual_0;   residual_1 += h;
    residual_2 = residual_1;   residual_2 += h;
    

    /* Calcul des résidus r_i = || y_i - R x_i - t || */
    
    switch( field -> type ) {
    default :
      if ( _verbose_ )
	fprintf (stderr, "%s: such field type not handled in switch\n", proc );
      free (residual_0);
      Free_Field( &sub_field );
      return( echelle );
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)sub_field.pairs;
	for ( i = 0; i < h; i ++ ) {
	  x0 = thePairs[i].x;
	  x1 = thePairs[i].y;
	  residual_0 [i] = ( x0 + thePairs[i].u - (mat[0]*x0 + mat[1]*x1 + mat[3]) );   
	  residual_1 [i] = ( x1 + thePairs[i].v - (mat[4]*x0 + mat[5]*x1 + mat[7]) );   
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)sub_field.pairs;
	for ( i = 0; i < h; i ++ ) {
	  x0 = thePairs[i].x;
	  x1 = thePairs[i].y;
	  x2 = thePairs[i].z;
	  residual_0 [i] = ( x0 + thePairs[i].u 
			     - (mat[0]*x0 + mat[1]*x1 + mat[2]*x2  + mat[3]) );   
	  residual_1 [i] = ( x1 + thePairs[i].v 
			     - (mat[4]*x0 + mat[5]*x1 + mat[6]*x2  + mat[7]) );   
	  residual_2 [i] = ( x2 + thePairs[i].w 
			     - (mat[8]*x0 + mat[9]*x1 + mat[10]*x2 + mat[11]) );
	}
      }
      break;
    }
      
  
    /* --- Estimation de la variance des résidus. 
       On suppose implicitement que les erreurs sont isotropes
       et que leurs composantes x, y, z sont décorrelées.
       
       On a alors:
       
       r^2 = sigma^2 chi_2 (3)
       
       Un estimateur d'échelle robuste, et naturel dans le cas du 
       LTS, est:
       
       1/h sum_i r_i^2
       
       
       Il faut lui appliquer un facteur correctif de manière à 
       ce que 
       
       int_0^alpha x chi_2(3)(x) dx = K frac = K h/n
       
       ou alpha est le fractile d'ordre h/n, i.e.
       F (alpha) = h/n. 
       
       Pour h=0.5*n, on a alpha = 2.3660
       
       
       --- */
      
    switch( field -> type ) {
    case _ScalarWeighted3DDisplacement_ :
      mad_2 = MADn ( residual_2, h);
      med_2 = mad_2.median;
      sigma_2 = mad_2.sigma;
    default :
    case _ScalarWeighted2DDisplacement_ :
      mad_0 = MADn ( residual_0, h);
      mad_1 = MADn ( residual_1, h);
      
      med_0 = mad_0.median;
      med_1 = mad_1.median;
      
      sigma_0 = mad_0.sigma;
      sigma_1 = mad_1.sigma;
    }

    if ( param->verbose > 0 && param->verbosef != NULL ) {
      switch( field -> type ) {
      default :
      case _ScalarWeighted2DDisplacement_ :
	fprintf( param->verbosef, 
		 "LTS refined: estimated error location  : %6.3f  %6.3f\n",  
		 med_0, med_1 );
	fprintf( param->verbosef, 
		 "LTS refined: estimated error scale     : %6.3f  %6.3f\n",  
		 sigma_0, sigma_1 );
	break;
      case _ScalarWeighted3DDisplacement_ :
	fprintf( param->verbosef, 
		 "LTS refined: estimated error location  : %6.3f  %6.3f  %6.3f\n",  
		 med_0, med_1, med_2);
	fprintf( param->verbosef, 
		 "LTS refined: estimated error scale     : %6.3f  %6.3f  %6.3f\n",  
		 sigma_0, sigma_1, sigma_2);
	break;
      }
    }
    
    /* ---
	 
       Diagnostic des outliers. 
       
       On utilise des tests du CHI2 pour décider si le résidu r_i est acceptable
       ou non. Si on suppose les erreurs gaussiennes, centrées, 
       avec une matrice de variance diagonale diag [sigma_0, sigma_1, sigma_2], 
       la quantité:
       
       D_i^2 =  r_i,0^2/sigma_0^2 + r_i,0^2/sigma_1^2 + r_i,2^2/sigma_2^2
       
       suit une loi du Chi2 à 3 degrés de liberté. On rejette l'hypothèse avec un
       risque de première espèce de 0.1.
       
       D_i^2 > d^2
       
       avec int_{d^2}^{infty} Chi2 (3) = 0.1 => d^2 =  6.2514 ( d ~ 2.5 ). 
       
       --- */

    if ( param->verbose > 0 && param->verbosef != NULL ) {
      fprintf(param->verbosef, "\nOutlier diagnostics using CHI2 tests...\n");  
    }
    
    /* Magouille provisoire */
    if ( sigma_0 < 1e-5 ) sigma_0 = 1e-5;
    if ( sigma_1 < 1e-5 ) sigma_1 = 1e-5;
    if ( sigma_2 < 1e-5 ) sigma_2 = 1e-5;
    
    j = 0;
      
    switch( field -> type ) {
    default :
    case _ScalarWeighted2DDisplacement_ :
      {
	typeScalarWeighted2DDisplacement *thePairs = 
	  (typeScalarWeighted2DDisplacement *)sub_field.pairs;
	for ( i = 0; i < h; i ++ ) {
	  Decision = 
	    ( residual_0 [i]*residual_0 [i] ) / ( sigma_0*sigma_0 )
	    + ( residual_1 [i]*residual_1 [i] ) / ( sigma_1*sigma_1 ) ;
	  if ( Decision >=  6.2514 ) continue;
	  /* le point est accepté... */
	  if ( i > j ) {
	    thePairs[j] = thePairs[i];
	    j ++;
	  }
	}
      }
      break;
    case _ScalarWeighted3DDisplacement_ :
      {
	typeScalarWeighted3DDisplacement *thePairs = 
	  (typeScalarWeighted3DDisplacement *)sub_field.pairs;
	for ( i = 0; i < h; i ++ ) {
	  Decision = 
	    ( residual_0 [i]*residual_0 [i] ) / ( sigma_0*sigma_0 )
	    + ( residual_1 [i]*residual_1 [i] ) / ( sigma_1*sigma_1 )
	    + ( residual_2 [i]*residual_2 [i] ) / ( sigma_2*sigma_2 ) ;
	  if ( Decision >=  6.2514 ) continue;
	  /* le point est accepté... */
	  if ( i > j ) {
	    thePairs[j] = thePairs[i];
	    j ++;
	  }
	}
      }
      break;
    }
    
    sub_field.n_pairs = j;

    if ( param->verbose > 0 && param->verbosef != NULL ) {
      fprintf ( param->verbosef, "  Detected outliers: %d (%3.1f%%)\n", 
		h - j, 100 * ( (double)(h-j) / (double) h ) );
      fprintf ( param->verbosef, "\nRefining estimation...\n" );
    }
    
    echelle = Trsf_Estimation( T, &sub_field, transfo, param->estimateur );

    free (residual_0);
  }
    
  Free_Field( &sub_field );
    
  return (echelle);
}








  
/*--------------------------------------------------*
 *
 * FIELD MANAGEMENT
 *
 *--------------------------------------------------*/

void Init_Field( FIELD *field )
{
  field->n_pairs = 0;
  field->n_allocated_pairs = 0;
  field->type = _UnknownField_;
  field->pairs = NULL;
}

/*---------------------------------------------------------
          Allocation d'un champ 3D de type double
----------------------------------------------------------*/

int Allocate_Field ( FIELD *field, enumFieldType type, int npairs )
{
  char *proc = "Allocate_Field";

  Init_Field( field );

  if ( npairs <= 0 ) return( -1 );
  
  switch( type ) {
  default :
    if ( _verbose_ )
      fprintf( stderr, "%s: field type not handled in switch\n", proc );
    return( -1 );
  case _ScalarWeighted2DDisplacement_ :
    field->pairs = calloc( npairs, sizeof(typeScalarWeighted2DDisplacement) );
    break;
  case _ScalarWeighted3DDisplacement_ :
    field->pairs = calloc( npairs, sizeof(typeScalarWeighted3DDisplacement) );
    break;
  }
  if ( field->pairs == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "%s: unable to allocate field\n", proc );
    return( -1 );
  }

  field->type = type;
  field->n_allocated_pairs = npairs;

  return( 1 );
}

/*----------------------------------------------------
         Désallocation d'un champ 3D de type double
-----------------------------------------------------*/

void Free_Field ( FIELD * field )
{
  if ( field->pairs != NULL ) free( field->pairs );
  Init_Field( field );
}










/*--------------------------------------------------*
 *
 * MISC
 *
 *--------------------------------------------------*/

void CreateFileDef( FIELD *field,
		    char *nom_image, char *nom_champ )
{
  int i;
  FILE *def;
  
  def = fopen( nom_champ, "w");
  if ( def == NULL ) {
    if ( _verbose_ )
      fprintf( stderr, "CreateFileDef: unable to open '%s' for writing\n", nom_champ );
    return;
  }
  
  switch( field -> type ) {
  default :
    if ( _verbose_ )
      fprintf (stderr, "CreateFileDef: such field type not handled in switch\n" );
  case _ScalarWeighted2DDisplacement_ :
    {
      typeScalarWeighted2DDisplacement *thePairs = 
	(typeScalarWeighted2DDisplacement *)field->pairs;
      fprintf(def, "DEF=[\n");
      for(i = 0; i < field->n_pairs; i++)
	fprintf(def, "%f %f %f %f %f\n", 
		thePairs[i].x, thePairs[i].y,
		thePairs[i].u, thePairs[i].v,
		thePairs[i].rho );
      fprintf(def, "];\n");
      fprintf(def, "X=DEF(:,1);\n");
      fprintf(def, "Y=DEF(:,2);\n");
      fprintf(def, "U=DEF(:,3);\n");
      fprintf(def, "V=DEF(:,4);\n");
      fprintf(def, "RHO=DEF(:,5);\n");
      fprintf(def, "image_name = '%s';\n", nom_image );
    }
    break;
  case _ScalarWeighted3DDisplacement_ :
    {
      typeScalarWeighted3DDisplacement *thePairs = 
	(typeScalarWeighted3DDisplacement *)field->pairs;
      fprintf(def, "DEF=[\n");
      for(i = 0; i < field->n_pairs; i++)
	fprintf(def, "%f %f %f %f %f %f %f\n", 
		thePairs[i].x, thePairs[i].y, thePairs[i].z,
		thePairs[i].u, thePairs[i].v, thePairs[i].w,
		thePairs[i].rho );
      fprintf(def, "];\n");
      fprintf(def, "X=DEF(:,1);\n");
      fprintf(def, "Y=DEF(:,2);\n");
      fprintf(def, "Z=DEF(:,3);\n");
      fprintf(def, "U=DEF(:,4);\n");
      fprintf(def, "V=DEF(:,5);\n");
      fprintf(def, "W=DEF(:,6);\n");
      fprintf(def, "RHO=DEF(:,7);\n");
      fprintf(def, "image_name = '%s';\n", nom_image );
    }
    break;
  }
  fclose(def);
}



double Estimate_Transformation( _MATRIX *T, FIELD * field, 
				PARAM *param, 
				int do_some_writing )
{
  if (  param->use_lts == 0 )
    return( Trsf_Estimation( T, field, param->transfo, param->estimateur ) );

  return( Trsf_Trimmed_Estimation( T, field, param->transfo, param, do_some_writing ) );
}

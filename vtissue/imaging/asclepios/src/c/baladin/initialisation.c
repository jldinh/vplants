#include <stdlib.h>
#include <stdio.h>

#include <initialisation.h>
#include <string.h>

#define max(a,b) ((a)>(b) ? (a) : (b))


void BAL_SetParametersToDefault( PARAM *p )
{
  
  /* this is to be kept
   */
  p->seuil_bas_flo = -100000;
  p->seuil_haut_flo = 100000;
  p->seuil_bas_ref = -100000;
  p->seuil_haut_ref = 100000;

  p->seuil_pourcent_ref = 0.500000;
  p->seuil_pourcent_flo = 0.500000;
  p->transfo = RIGIDE;
  p->estimateur = TYPE_LSSW;
  p->use_lts = 1;
  p->lts_cut = 0.500000;
  p->mesure = MESURE_CC;

  p->seuil_mesure = 0.000000;

  p->nbiter = 4;

  p->bl_dx = 4;
  p->bl_dy = 4;
  p->bl_dz = 4;
  p->bl_border_x = 0;
  p->bl_border_y = 0;
  p->bl_border_z = 0;
  p->bl_next_x = 3;
  p->bl_next_y = 3;
  p->bl_next_z = 3;
  p->bl_next_neigh_x = 1;
  p->bl_next_neigh_y = 1;
  p->bl_next_neigh_z = 1;
  p->bl_size_neigh_x = 3;
  p->bl_size_neigh_y = 3;
  p->bl_size_neigh_z = 3;
  p->bl_pourcent_var = 1.000000;
  p->bl_pourcent_var_min = 0.500000;
  p->bl_pourcent_var_dec = 0.200000;
  p->pyn = 1;
  p->pys = 0;
  p->sub = 0;
  p->verbosef = NULL;

  p->verbose = 0;
  p->write_def = 0;
  p->vischeck = 0;
  p->rms = 0;
  p->py_filt = 0;
}



void BAL_SetParametersToAuto( PARAM *p )
{
  

  /* this is to be kept
   */
  p->seuil_bas_flo = -100000;
  p->seuil_haut_flo = 100000;
  p->seuil_bas_ref = -100000;
  p->seuil_haut_ref = 100000;

  p->seuil_pourcent_ref = 0.500000;
  p->seuil_pourcent_flo = 0.500000;
  p->transfo = RIGIDE;
  p->estimateur = TYPE_LSSW;
  p->use_lts = 1;
  p->lts_cut = 0.500000;
  p->mesure = MESURE_CC;

  p->seuil_mesure = 0.000000;

  p->nbiter = 10;

  p->bl_dx = 4;
  p->bl_dy = 4;
  p->bl_dz = 4;
  p->bl_border_x = 0;
  p->bl_border_y = 0;
  p->bl_border_z = 0;
  p->bl_next_x = 3;
  p->bl_next_y = 3;
  p->bl_next_z = 3;
  p->bl_next_neigh_x = 1;
  p->bl_next_neigh_y = 1;
  p->bl_next_neigh_z = 1;
  p->bl_size_neigh_x = 3;
  p->bl_size_neigh_y = 3;
  p->bl_size_neigh_z = 3;
  p->bl_pourcent_var = 0.800000;
  p->bl_pourcent_var_min = 0.300000;
  p->bl_pourcent_var_dec = 0.200000;
  p->pyn = 5;
  p->pys = 1;
  p->sub = 0;

  p->verbose = 0;
  p->write_def = 0;
  p->vischeck = 0;
  p->rms = 1;
  p->py_filt = 0;
}



/*
  A REVOIR,
  ERREURS MAL GEREES
*/
int Initialize_Matrice_Initiale (char *filename, _MATRIX *matrix )
{
  FILE *fp;
  char line[1024];
  int ligne,i;
  double f1, f2, f3, f4;

  /* initialization */  
  ligne = 0;
  if ( matrix->l != 4 || matrix->c != 4 || matrix->m == NULL ) 
    return( 0 );

  i = 0;
  
  if ((fp = fopen (filename, "r")) == NULL){
    fprintf (stderr, "WARNING: FILE %s CANNOT OPEN \n", filename);
    exit(0);
  }
  
  fgets(line, 1024, fp);  
  while ( ( sscanf( line, "%lf %lf %lf %lf\n", &f1, &f2, &f3, &f4 ) < 4 ) && 
	  ( sscanf( line, "O8 %lf %lf %lf %lf\n", &f1, &f2, &f3, &f4 ) < 4 ) )
    fgets(line, 1024, fp);  

  matrix->m[0] = f1; matrix->m[1] = f2; matrix->m[2] = f3; matrix->m[3] = f4; 

  i = 4;
  for(ligne=0;ligne<3;ligne++){
    fgets(line,1024,fp);
    sscanf(line, "%lf %lf %lf %lf\n",
	   &(matrix->m[i]),
	   &(matrix->m[i+1]),
	   &(matrix->m[i+2]),
	   &(matrix->m[i+3])
	   );
    i=i+4;
  }
  
  fclose(fp);
  
  return( 1 );
}


/*
 * Mise a jour des parametres lors d'un changement de niveau dans la pyramide
 */
int Param_MiseAJour( PARAM *param  )
{
  int pyramide=1;

  /* On va vers un niveau de resolution plus eleve */
  param->sub++;
      
  /* Fin ? */
  if (param->sub == (param->pyn - param->pys - 1 ) )
    pyramide = 0;

  /* Nouveaux bl_d? */
  param->bl_dx =  ( (param->bl_dx / 2) > 4) ? param->bl_dx / 2 : 4;
  param->bl_dy =  ( (param->bl_dy / 2) > 4) ? param->bl_dy / 2 : 4;
  param->bl_dz =  ( (param->bl_dz / 2) > 4) ? param->bl_dz / 2 : 4;

  /* Nouveaux bl_next_? Pour le dernier niveau de la pyramide --> 1 

     METTRE CA COMME UNE OPTION -refine 

     if ( param->sub == (param->pyn - param->pys - 1) - 1 ) {
     param->bl_next_x = 1;
     param->bl_next_y = 1;
     param->bl_next_z = 1;
     }
  */

  /* Nouveaux bl_size_neigh_? et bl_next_neigh_? */
  param->bl_size_neigh_x = max ( param->bl_size_neigh_x / 2, 3);
  param->bl_size_neigh_y = max ( param->bl_size_neigh_y / 2, 3);
  if ( param->bl_size_neigh_z > 0 )
    param->bl_size_neigh_z = max ( param->bl_size_neigh_z / 2, 3);

  /* Consistance entre size_neigh_? et next_neigh_? 
     Ici on s'assure que dans le voisinage d'un bloc, au moins 3 blocs seront explores
     selon chaque axe, i.e. 27 blocs en 3D, 9 blocs en 2D */
  if ( 3 * param->bl_next_neigh_x > ( 2 * param->bl_size_neigh_x ) )
    param->bl_next_neigh_x = max ( (int) ( ( 2 * param->bl_size_neigh_x + 1 ) / 3 ) ,1 );
  if ( 3 * param->bl_next_neigh_y > ( 2 * param->bl_size_neigh_y ) )
    param->bl_next_neigh_y = max ( (int) ( ( 2 * param->bl_size_neigh_y + 1 ) / 3 ) ,1 );
  if ( 3 * param->bl_next_neigh_z > ( 2 * param->bl_size_neigh_z ) )
    param->bl_next_neigh_z = max ( (int) ( ( 2 * param->bl_size_neigh_z + 1 ) / 3 ) ,1 );
  

  /* Nouveau pourcentage pour ne considerer que les x % des blocs de plus forte variance */

  if ( param->bl_pourcent_var_dec > 0.0 ) 
    param->bl_pourcent_var =  max ( param->bl_pourcent_var_min, param->bl_pourcent_var - param->bl_pourcent_var_dec );


  if (param->verbosef != NULL) {
    fprintf(param->verbosef, "\n*** A partir du 2e passage\n");
    fprintf(param->verbosef, "\tpyramide : %d\n", pyramide);
    fprintf(param->verbosef, "\tparam->sub : %d\n", param->sub);
    fprintf(param->verbosef, "\tparam->bl_pourcent_var : %f\n", param->bl_pourcent_var);
    fprintf(param->verbosef, "\tDimensions du bloc : %d %d %d\n", 
	    param->bl_dx, param->bl_dy, param->bl_dz);
    fprintf(param->verbosef, "\tPas de progression dans le voisinage d'un bloc en x, y, z : %d %d %d\n", 
	    param->bl_next_neigh_x, param->bl_next_neigh_y, param->bl_next_neigh_z);
    fprintf(param->verbosef, "\tDimension du voisinage d'exploration autour d'un bloc : %d %d %d\n", 
	    param->bl_size_neigh_x, param->bl_size_neigh_y, param->bl_size_neigh_z);
    fflush(param->verbosef);
    
  }

  return( pyramide ); 
}




void BAL_PrintParameters( FILE* f, PARAM *param )
{
  
  
  /* seuils sur les images... */
  fprintf( f, "p->seuil_bas_flo = %d;\n", param->seuil_bas_flo );
  fprintf( f, "p->seuil_haut_flo = %d;\n", param->seuil_haut_flo );
  fprintf( f, "p->seuil_bas_ref = %d;\n", param->seuil_bas_ref );
  fprintf( f, "p->seuil_haut_ref = %d;\n", param->seuil_haut_ref );

  /* ... et pourcentages sur les seuils */
  fprintf( f, "p->seuil_pourcent_ref = %f;\n", param->seuil_pourcent_ref );
  fprintf( f, "p->seuil_pourcent_flo = %f;\n", param->seuil_pourcent_flo );


  /***
      Transformation, estimateur, mesure de similarite 
  ***/
  fprintf( f, "enumTypeTransfo transfo = ");
  switch( param->transfo ) {
  default : fprintf( f, "unknown" ); break;
  case RIGIDE : fprintf( f, "RIGIDE" ); break;
  case SIMILITUDE : fprintf( f, "SIMILITUDE" ); break;
  case AFFINE : fprintf( f, "AFFINE" ); break;
  case SPLINE : fprintf( f, "SPLINE" ); break;
  }
  fprintf( f, ";\n" );

  fprintf( f, "enumTypeEstimator estimateur = ");
  switch( param->estimateur  ) {
  default : fprintf( f, "unknown" ); break;
  case TYPE_LS : fprintf( f, "TYPE_LS" ); break;
  case TYPE_LSSW : fprintf( f, "TYPE_LSSW" ); break;
  }
  fprintf( f, ";\n" );

  fprintf( f, "p->use_lts = %d;\n", param->use_lts );
  fprintf( f, "p->lts_cut = %f;\n", param->lts_cut );

  fprintf( f, "enumTypeMesure mesure = ");
  switch( param->mesure ) {
  default : fprintf( f, "unknown" ); break;
  case MESURE_CC : fprintf( f, "MESURE_CC" ); break;
  case MESURE_CR : fprintf( f, "MESURE_CR" ); break;
  case MESURE_CC_GRAD : fprintf( f, "MESURE_CC_GRAD" ); break;
  case MESURE_CR_GRAD : fprintf( f, "MESURE_CR_GRAD" ); break;
  case MESURE_OM : fprintf( f, "MESURE_OM" ); break;
  }
  fprintf( f, ";\n" );

  /* seuil sur la mesure de similarite */
  fprintf( f, "p->seuil_mesure = %f;\n", param->seuil_mesure );

  /* nombre d'iterations par niveau */
  fprintf( f, "p->nbiter = %d;\n", param->nbiter );


  /***
      parametres lies aux blocs 
  ***/

  /* dimensions du bloc */
  fprintf( f, "p->bl_dx = %d;\n", param->bl_dx );
  fprintf( f, "p->bl_dy = %d;\n", param->bl_dy );
  fprintf( f, "p->bl_dz = %d;\n", param->bl_dz );

  /* pas de progression du bloc dans l'image "fixe" (ima_flo dans le programme) */
  fprintf( f, "p->bl_next_x = %d;\n", param->bl_next_x );
  fprintf( f, "p->bl_next_y = %d;\n", param->bl_next_y );
  fprintf( f, "p->bl_next_z = %d;\n", param->bl_next_z );

  /*** parametres pour l'exploration du voisinage d'un bloc donne ***/

  /* pas de progression du bloc lors de l'exploration du voisinage */
  fprintf( f, "p->bl_next_neigh_x = %d;\n", param->bl_next_neigh_x );
  fprintf( f, "p->bl_next_neigh_y = %d;\n", param->bl_next_neigh_y );
  fprintf( f, "p->bl_next_neigh_z = %d;\n", param->bl_next_neigh_z );

  /* dimension du voisinage d'exploration */
  fprintf( f, "p->bl_size_neigh_x = %d;\n", param->bl_size_neigh_x );
  fprintf( f, "p->bl_size_neigh_y = %d;\n", param->bl_size_neigh_y );
  fprintf( f, "p->bl_size_neigh_z = %d;\n", param->bl_size_neigh_z );

  /* pourcentage variance et variance minimale dans les blocs*/
  fprintf( f, "p->bl_pourcent_var = %f;\n", param->bl_pourcent_var );
  fprintf( f, "p->bl_pourcent_var_min = %f;\n", param->bl_pourcent_var_min );

  /***
      Parametres lies a la pyramide
  ***/

  /* nombre de niveaux de la pyramide */
  fprintf( f, "p->pyn = %d;\n", param->pyn );
  /* niveau le plus bas, i.e. 0 = resolution de ima_ref, 1, 2... on s'arrete avant */
  fprintf( f, "p->pys = %d;\n", param->pys );

  /* recalage sous-resolution */
  fprintf( f, "p->sub = %d;\n", param->sub );

  /* informations minimales lors de l'execution */
  fprintf( f, "p->verbose = %d;\n", param->verbose );

  /* save on disk the pairing fields */
  fprintf( f, "p->write_def = %d;\n", param->write_def );

  /* visually check the process with intermediate images saved on disk */
  fprintf( f, "p->vischeck = %d;\n", param->vischeck );
  
  /* root median squares pour changement de niveau */
  fprintf( f, "p->rms = %d;\n", param->rms );

  /* pyramide obtenue par filtrage gaussien */
  fprintf( f, "p->py_filt = %d;\n", param->py_filt );
}

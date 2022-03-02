
#ifndef BALADIN_H
#define BALADIN_H

#include <stdio.h>

#define SIZE_NAME 250
#define EPSILON 0.0000001
#define RMS_ERROR 100.0

typedef struct{
  int a;       /* block origin wrt x, y, z */
  int b;
  int c;

  int inclus;  /* entierement inclus dans l'image (apres seuils) */
  int valid;   /* Oui/Non : ce bloc joue-t-il un role, i.e. apres 
		  les tests sur les intensites et les variances ? */

  double moy;  /* moyenne des intensites dans le bloc */
  double var;  /* variance des intensites dans le bloc */
  double diff; /* pre-calcule sum( I - moyI )^2 pour le calcul de CC */
} BLOC;

typedef struct{

  BLOC *bloc;            /* tableau contenant tous les blocs */
  int n_valid_blocks;    /* nombre de blocs actifs */
  BLOC **p_bloc;         /* pointeurs sur les blocs : 
			    permet de retrouver les blocs 
			    apres le tri sur la variance */

  int n_blocks;     /* number of allocated blocks */

  int n_blocks_x;   /* number of blocks along each dimension */
  int n_blocks_y;
  int n_blocks_z;

  int block_size_x; /* size of blocks along each dimension */
  int block_size_y;
  int block_size_z;

  int block_step_x; /* step to reach next block along each dimension */
  int block_step_y;
  int block_step_z;

  int block_border_x; /* border to add in each direction for */
  int block_border_y; /* statistics computation */
  int block_border_z;

} BLOCS;


/***
    Different types of transformation
***/
typedef enum {
  RIGIDE,
  SIMILITUDE,
  AFFINE,
  SPLINE 
} enumTypeTransfo;


/***
    Different types of estimator
***/
typedef enum {
  TYPE_LS,
  TYPE_LSSW
} enumTypeEstimator;


/***
    Different types of mesures
***/
typedef enum {
  MESURE_CC,
  MESURE_EXT_CC,
  MESURE_CR,
  MESURE_CC_GRAD,
  MESURE_CR_GRAD,
  MESURE_OM
} enumTypeMesure;




/***
    Structure PARAM : ensemble des valeurs des parametres du programme
 ***/
typedef struct {


  /* seuils sur les images... */
  int seuil_bas_flo;
  int seuil_haut_flo;
  int seuil_bas_ref; 
  int seuil_haut_ref;

  /* ... et pourcentages sur les seuils */
  double seuil_pourcent_ref;
  double seuil_pourcent_flo;


  /***
      Transformation, estimateur, mesure de similarite 
  ***/
  enumTypeTransfo transfo;

  enumTypeEstimator estimateur;
  int use_lts;
  double lts_cut;

  enumTypeMesure mesure;

  /* seuil sur la mesure de similarite */
  double seuil_mesure;

  /* nombre d'iterations par niveau */
  int nbiter;


  /***
      parametres lies aux blocs 
  ***/

  /* dimensions du bloc */
  int bl_dx;
  int bl_dy; 
  int bl_dz;

  /* bordures du bloc a ajouter pour calculer les statistiques
     d'ordre 1 : les dimensions du bloc pour ce calcul seront 
     alors bl_d[x,y,z]+ 2 * bl_border_[x,y,z] */
  int bl_border_x;
  int bl_border_y; 
  int bl_border_z;

  /* pas de progression du bloc dans l'image "fixe" (ima_flo dans le programme) */
  int bl_next_x; 
  int bl_next_y; 
  int bl_next_z;

  /*** parametres pour l'exploration du voisinage d'un bloc donne ***/

  /* pas de progression du bloc lors de l'exploration du voisinage */
  int bl_next_neigh_x; 
  int bl_next_neigh_y; 
  int bl_next_neigh_z;

  /* dimension du voisinage d'exploration */
  int bl_size_neigh_x;
  int bl_size_neigh_y;
  int bl_size_neigh_z;

  /* pourcentage variance et variance minimale dans les blocs*/
  double bl_pourcent_var;
  double bl_pourcent_var_min;
  double bl_pourcent_var_dec;



  /***
      Parametres lies a la pyramide
  ***/

  /* nombre de niveaux de la pyramide */
  int pyn;
  /* niveau le plus bas, i.e. 0 = resolution de ima_ref, 1, 2... on s'arrete avant */
  int pys;

  /* recalage sous-resolution */
  int sub;

  /* informations lors de l'execution ? affichees, sauvees ou RAS */
  FILE *verbosef;

  /* informations minimales lors de l'execution */
  int verbose;

  /* save on disk the pairing fields */
  int write_def;

  /* visually check the process with intermediate images saved on disk */
  int vischeck;
  
  /* root median squares pour changement de niveau */
  int rms;

  /* pyramide obtenue par filtrage gaussien */
  int py_filt;

} PARAM;

#endif

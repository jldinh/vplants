#include "candidates_p.h"
#define VERBOSE
#include "macros.h"
#include "mathtools_p.h"
#include <vector>
#include <algorithm>

# define grandeValeur 10000


typedef std::vector < std::vector <unsigned int> >    BoundingBoxListType;
typedef std::vector < std::vector < double > >        BarycenterListType;
typedef std::vector < int >                           VolumeListType;
typedef std::vector < std::vector < unsigned int > >  MatchListType;

int find_candidates(const double distance, const unsigned int nbCells1, const unsigned int nbCells2,
		    const unsigned int sx_im1, const unsigned int sy_im1, const unsigned int sz_im1,
		    const unsigned short * data_im1,
		    const unsigned int sx_im2, const unsigned int sy_im2, const unsigned int sz_im2,
		    const unsigned short * data_im2,
		    const double vx, const double vy, const double vz,
		    MotherListType & mothers,
		    ChildrenListType & children,
		    ScoreListType & scores) {


  unsigned int countInter,cel1,cel2,lindex,nbInterPoss = 0;
  unsigned short valVox = 0;
  bool sortie, trouve;

  if( (sx_im1 != sx_im2) || (sy_im1 != sy_im2) || (sz_im1 != sz_im2) ){
    ERROR_MSG("Image shape mismatch");
    return -1;
  }

  DEBUG_MSG("Lecture des images d'entrees et calcul du nombre de cellules");

  //Caracteristiques des cellules
  BoundingBoxListType bBoxes1(nbCells1,BoundingBoxListType::value_type(6,0) );//x,X,y,Y,z,Z
  BoundingBoxListType bBoxes2(nbCells2,BoundingBoxListType::value_type(6,0) );//x,X,y,Y,z,Z
  BarycenterListType bary1(nbCells1,BarycenterListType::value_type(3,0) );
  BarycenterListType bary2(nbCells2,BarycenterListType::value_type(3,0) );
  VolumeListType volumes1(nbCells1,0);
  VolumeListType volumes2(nbCells2,0);

  //Informations de la matrice de recouvrement
  std::vector < std::vector < int > >  recouvrement(nbCells1,std::vector<int>  (0,0));
  MatchListType  correspondantsPoss(nbCells1, MatchListType::value_type(0,0));
  std::vector < unsigned int >         nbPoss(nbCells1,0);

  ///Structures pour le calcul des scores basés sur la distance
  std::vector < std::vector < int > > correspondantsPossDistance(nbCells1,std::vector<int>  (0,0));
  std::vector < std::vector< float > > scoresDistance(nbCells1,std::vector < float >  (0,0));
  std::vector < int > nbPossDistance(nbCells1,0);
  std::vector < int > tab1(3,0);
  std::vector < int > tab2(3,0);
  std::vector < std::vector < int >  > bresenCoords(grandeValeur,std::vector < int > (4,0));

  ///Pour les correspondances a venir
  std::vector  < std::vector < int > >  correspondance(nbCells2,std::vector < int >(2,0));
  std::vector  < std::vector < int > > destinees(nbCells1,std::vector < int > (0,0));

  ///Pour la comparaison de segmentations (optionMode=2)
  std::vector < int > resultatSegmentation(nbCells1,0);
  std::vector < float > scoreSegmentation(nbCells1,0);


  //////// Calcul des bounding boxes et des volumes des cellules //////////////////////////////////////////
  DEBUG_MSG("------------ Calcul des bounding boxes et des volumes des cellules aux deux temps-------");
  for(unsigned int i=0;i<nbCells1;i++){
    bBoxes1[i][0]=sx_im1-1;
    bBoxes1[i][2]=sy_im1-1;
    bBoxes1[i][4]=sz_im1-1;
  }
  for(unsigned int i=0;i<nbCells2;i++){
    bBoxes2[i][0]=sx_im2-1;
    bBoxes2[i][2]=sy_im2-1;
    bBoxes2[i][4]=sz_im2-1;
  }
  for(unsigned int i =0;i<sx_im1 ; i++){
    for(unsigned int j =0;j<sy_im1 ; j++){
      for(unsigned int k =0;k<sz_im1 ; k++){
	unsigned int index = sx_im1*sy_im1*k + sx_im1*j + i;
	valVox=data_im1[index];
	volumes1[valVox]++;
	BarycenterListType::value_type & baryc1 = bary1[valVox];
	BoundingBoxListType::value_type & bbox1 = bBoxes1[valVox];
	baryc1[0]+=i;baryc1[1]+=j;baryc1[2]+=k;
	if(bbox1[0] > i) bbox1[0] = i;
	if(bbox1[1] < i) bbox1[1] = i;
	if(bbox1[2] > j) bbox1[2] = j;
	if(bbox1[3] < j) bbox1[3] = j;
	if(bbox1[4] > k) bbox1[4] = k;
	if(bbox1[5] < k) bbox1[5] = k;

	valVox=data_im2[index];
	volumes2[valVox]++;
	BarycenterListType::value_type & baryc2 = bary2[valVox];
	BoundingBoxListType::value_type & bbox2 = bBoxes2[valVox];
	baryc2[0]+=i;baryc2[1]+=j;baryc2[2]+=k;
	if(bbox2[0] > i) bbox2[0] = i;
	if(bbox2[1] < i) bbox2[1] = i;
	if(bbox2[2] > j) bbox2[2] = j;
	if(bbox2[3] < j) bbox2[3] = j;
	if(bbox2[4] > k) bbox2[4] = k;
	if(bbox2[5] < k) bbox2[5] = k;
      }
    }
  }
  for(unsigned int cel1 = 1;cel1<nbCells1 ; cel1++){
    VolumeListType::value_type & volume = volumes1[cel1];
    BarycenterListType::value_type & baryc = bary1[cel1];
    if(volume>0){
      baryc[0]/=static_cast<float>(volume);
      baryc[1]/=static_cast<float>(volume);
      baryc[2]/=static_cast<float>(volume);
      ERROR_MSG("bary1 "<<" "<<cel1<<" "<<baryc[0]<<" "<<baryc[1]<<" "<<baryc[2]);
    }
    else {
      baryc[0]=0.5;baryc[1]=0.5;baryc[2]=0.5;
      ERROR_MSG("Erreur : une cellule de volume 0: " << cel1);
    }
  }
  for(unsigned int cel2 = 1;cel2<nbCells2 ; cel2++){
    VolumeListType::value_type & volume = volumes2[cel2];
    BarycenterListType::value_type & baryc = bary2[cel2];
    if(volume>0){
      baryc[0]/=static_cast<float>(volume);
      baryc[1]/=static_cast<float>(volume);
      baryc[2]/=static_cast<float>(volume);
      ERROR_MSG("bary2 "<<" "<<cel2<<" "<<baryc[0]<<" "<<baryc[1]<<" "<<baryc[2]);
    }
    else {
      baryc[0]=0.5;baryc[1]=0.5;baryc[2]=0.5;
      ERROR_MSG("Erreur : une cellule de volume 0: " << cel2);
    }
  }

  DEBUG_MSG("T1 : "<<nbCells1-1<<" cells. Mean vol = "<<((sx_im1*sy_im1*sz_im1-volumes1[1])*1.0/(nbCells1-1)));
  DEBUG_MSG("T2 : "<<nbCells2-1<<" cells. Mean vol = "<<((sx_im2*sy_im2*sz_im2-volumes2[1])*1.0/(nbCells2-1)));

  ///Calcul de la matrice de recouvrement
  DEBUG_MSG("------------ Lecture des segmentations pour le calcul de la matrice de recouvrement -------");

  for(unsigned int i =0; i<sx_im2; i++){
    for(unsigned int j =0; j<sy_im2; j++){
      for(unsigned int k =0; k<sz_im2; k++){
	unsigned int index = sx_im1*sy_im1*k + sx_im1*j + i;
	cel1 = data_im1[index];
	cel2 = data_im2[index];
	if(nbPoss[cel1]==0) {
	  nbPoss[cel1]=1;
	  correspondantsPoss[cel1].push_back(cel2);
	  recouvrement[cel1].push_back(1);
	}
	else {
	  trouve=false;
	  for(unsigned int ind=0;ind<nbPoss[cel1];ind++){
	    if(correspondantsPoss[cel1][ind]==cel2){
	      trouve=true;
	      lindex=ind;
	    }
	  }
	  if(trouve){
	    recouvrement[cel1][lindex]++;
	  }
	  else{
	    correspondantsPoss[cel1].push_back(cel2);
	    recouvrement[cel1].push_back(1);
	    nbPoss[cel1]++;
	  }
	}
      }
    }
  }


  for(unsigned int cel1 = 1; cel1<nbCells1; cel1++){
    nbInterPoss+=nbPoss[cel1];
  }
  for(unsigned int cel1=1; cel1<nbCells1; cel1++){
    for(unsigned int cel2=0;cel2<nbPoss[cel1];cel2++){
      countInter=recouvrement[cel1][cel2];
    }
  }

  DEBUG_MSG("Nb previsionnel de possibilités, en regard de l'intersection des cellules = "<<nbInterPoss);


  ////////// Ajouter les couples basés sur la distance
  nbInterPoss=0;
  DEBUG_MSG("Compute mapping candidates");

  //Pour toute cellule mere, ajouter les cellules filles dont le barycentre est a une distance inferieure a distanceSeuil
  for(unsigned int cel1 = 2;cel1<nbCells1 ; cel1++){
    BarycenterListType::value_type & baryc1 = bary1[cel1];
    MatchListType::value_type & possKids    = correspondantsPoss[cel1];
    for(unsigned int cel2 = 2; cel2<nbCells2 ; cel2++){
      BarycenterListType::value_type & baryc2 = bary2[cel2];
      //rechercher si le cas a ete detecte en superposition
      trouve = std::find(possKids.begin(), possKids.end(), cel2) != possKids.end();
      DEBUG_MSG("was CEL2 " << cel2 << " found in CEL1 " << cel1 << " : " << trouve);
      //si les cellules s'intersectent, ou que le barycentre de la cellule 2 est inclus dans la cellule 1
      //ou qu'il est situé a une distance raisonnable de la surface de la cellule 1

	// TO WHOEVER LOOKS AT THIS CODE! THE DAMN CAST IS NECESSARY TO
	// GET THE SAME RESULT AS ROMAIN. THAT DOESN'T MEAN THAT IT IS
	// A GOOD THING BUT IT'S THE SAME THING...
      unsigned int index = sx_im1*sy_im1*(unsigned int)baryc2[2] +
	                   sx_im1*(unsigned int)baryc2[1] +
	                   (unsigned int)baryc2[0];
      if( trouve ||  (data_im1[index]==cel1) ||
	  (distance > norm(baryc1[0]*vx,baryc1[1]*vy,baryc1[2]*vz,baryc2[0]*vx,baryc2[1]*vy,baryc2[2]*vz)) ){
	//Retenir
	DEBUG_MSG("Computing distance for this cel: " << cel2);
	correspondantsPossDistance[cel1].push_back(cel2);
	nbPossDistance[cel1]++;

	//Calcul de la ligne 3D (algo de Bresenham)
	for (unsigned int coor=0;coor<3;coor++){
	  tab1[coor]=baryc1[coor];
	  tab2[coor]=baryc2[coor];
	}
	bresenham_line3d(&tab1,&tab2,&bresenCoords);

	//Parcours depuis le debut jusqu'a sortir de la cellule 1
	sortie=false;

	int incr=-1;
	while( ( !sortie)  && (incr+1< bresenCoords[0][3])){
	  ++incr;
	  unsigned int index_2 = sx_im1*sy_im1*bresenCoords[incr][2] + sx_im1*bresenCoords[incr][1] + bresenCoords[incr][0];
	  if(data_im1[index_2] != cel1)sortie=true;
	}
	for (unsigned int coor=0;coor<3;coor++) {
	  tab1[coor]=bresenCoords[incr][coor];
	}

	//barycentre de la cellule 2
	for (unsigned int coor=0;coor<3;coor++) {
	  tab2[coor]=bresenCoords[bresenCoords[0][3]-1][coor];
	}

	//Calcul de la distance entre ces deux points
	//Cas d'inclusion de cel2 dans cel1 puis autres cas
	if( data_im1[index]==cel1) {
	  scoresDistance[cel1].push_back(0);
	}
	else {
	  if (distance>0.0) {
	    scoresDistance[cel1].push_back(norm(tab1[0]*vx,tab1[1]*vy,tab1[2]*vz,tab2[0]*vx,tab2[1]*vy,tab2[2]*vz)/distance);
	  }
	  else {
	    scoresDistance[cel1].push_back(0);
	  }
	}
	nbInterPoss++;
      }
    }
  }

  DEBUG_MSG("Nb previsionnel de possibilités en considerant uniquement la distance = "<<nbInterPoss);
  DEBUG_MSG("Pour moi c'est la la bonne valeur "<< scoresDistance.size());

  ///////////Insertion de toutes les autres possibilites de couples
  for(unsigned int cel1 = 1;cel1<nbCells1 ; cel1++){
    for(unsigned int j = 0; j< correspondantsPossDistance[cel1].size(); j++){
      cel2=correspondantsPossDistance[cel1][j];
      mothers.push_back(cel1);
      children.push_back(cel2);
      scores.push_back(1-scoresDistance[cel1][j]);
    }
  }


  return 0;
}



////////////////////////////////////////////////////////////////////////////
// THE CLEANED UP IMPLEMENTATION ABOVE IS GIVING PROBLEMS SO THE ORIGINAL //
// UGLY IMPLEMENTATION IS ALSO HERE FOR COMPARISON PURPOSE		  //
////////////////////////////////////////////////////////////////////////////


//Modes de suivi
#define COMPARISON_MODE 2
#define TRACKING_MODE 1

int find_candidates_ugly(const double distance, const unsigned int nbCells1, const unsigned int nbCells2,
			 const unsigned int sx_im1, const unsigned int sy_im1, const unsigned int sz_im1,
			 const unsigned short * data_im1,
			 const unsigned int sx_im2, const unsigned int sy_im2, const unsigned int sz_im2,
			 const unsigned short * data_im2,
			 const double vx, const double vy, const double vz,
			 MotherListType & mothers,
			 ChildrenListType & children,
			 ScoreListType & scores) {

  int optionMode = TRACKING_MODE;
  /////////// INITIALISATION /////////////////////////////////////////////////////////
  //  COUT<<"SUIVI TEMPOREL"<<ENDL;
  // COUT<<"Parametres choisis : mode = "<<(optionMode==COMPARISON_MODE ? "comparaison de deux segmentations" : (optionMode==TRACKING_MODE ? "suivi temporel et calcul des lignages" : "non reconnu "))<<ENDL;
  // COUT<<", cellules fixees : "<<(optionFix==NOFIX ? "aucune " : (optionFix==FIX_ALL ? optChaine : (optionFix==FIX_ONE ?"cellule du fond " : "non reconnu ")))<<" , image 1 = "<<inT1<<", image 2 = "<<inT2<<" fichiers de sortie : "<<outCorrespondances<<", "<<outScores<<ENDL;

  // if(optionMode==TRACKING_MODE)COUT<<"Calcul avec une distance de "<<distance<<ENDL;
  int incr,countInter,cel1,cel2,n1,n2,lindex,over,under,nbGood=0,nbInterPoss=0,nbAppariements,nbCells;
  int * ent1=(int *) (malloc(sizeof(int)*1));
  int * ent2=(int *) (malloc(sizeof(int)*1));
  unsigned short valVox=0;
  double scor;
  float moy=0,min=10000,max=0;
  bool sortie,trouve;

  // if( (sx_im1 != sx_im2) || (sy_im1 != sy_im2) || (sz_im1 != sz_im2) ){
  //   CERR<<"Erreur : Les dimensions des deux images ne coincident pas.\n Utilisez CROP pour les ajuster"<<ENDL;
  //   COUT<<"Erreur : Les dimensions des deux images ne coincident pas.\n Utilisez CROP pour les ajuster"<<ENDL;
  //   exit(7);
  // }
  // if( (imgIn1->getType() != yav::Inrimage::WT_UNSIGNED_SHORT) || (imgIn2->getType() != yav::Inrimage::WT_UNSIGNED_SHORT) ){
  //   CERR<<"Erreur : au moins une des deux images n'est pas du type unsigned short.\n Utilisez zpar pour reperer le probleme, puis zcopy -o 2 pour changer le type de l'image qui pose le probleme."<<ENDL;
  //   COUT<<"Erreur : au moins une des deux images n'est pas du type unsigned short.\n Utilisez zpar pour reperer le probleme, puis zcopy -o 2 pour changer le type de l'image qui pose le probleme."<<ENDL;
  //   exit(13);
  // }
  // CERR<<"Lecture des images d'entrees et calcul du nombre de cellules"<<ENDL;
  // ///Lecture des images, calcul du nombre de cellules
  // for(int i =0;i<sx_im1 ; i++){
  //   for(int j =0;j<sy_im1 ; j++){
  //     for(int k =0;k<sz_im1 ; k++){
  // 	valVox=(((unsigned short ***)tabIn1)[k][j][i]);
  // 	if(valVox==0){
  // 	  COUT<<"Erreur : L'image 1 contient des voxels a 0. Utilisez l'outil METTRE_A_VAL_LA_CELLULE "<<inT1<<" "<<inT1<<" 0 1"<<ENDL;
  // 	  CERR<<"Erreur : L'image 1 contient des voxels a 0. Utilisez l'outil METTRE_A_VAL_LA_CELLULE "<<inT1<<" "<<inT1<<" 0 1"<<ENDL;
  // 	  exit(7);
  // 	}
  // 	if(nbCells1 < valVox) nbCells1 = valVox;
  // 	valVox=(((unsigned short ***)data_im2)[k][j][i]);
  // 	if(valVox==0){
  // 	  COUT<<"Erreur : L'image 2 contient des voxels a 0. Utilisez l'outil METTRE_A_VAL_LA_CELLULE "<<inT2<<" "<<inT2<<" 0 1"<<ENDL;
  // 	  CERR<<"Erreur : L'image 2 contient des voxels a 0. Utilisez l'outil METTRE_A_VAL_LA_CELLULE "<<inT2<<" "<<inT2<<" 0 1"<<ENDL;
  // 	  exit(7);
  // 	}
  // 	if(nbCells2 < valVox) nbCells2 = valVox;
  //     }
  //   }
  // }
  // /////// INITIALISATION 2 ////////////////////////////////////////////////////////////////
  // nbCells2++;nbCells1++;//ajout des cellules 0 (exterieur de l'image) qui joueront le role de noeud lambda

  //Caracteristiques des cellules
  std::vector < std::vector<int> >bBoxes1 = std::vector < std::vector < int > > (nbCells1,std::vector<int>(6,0) );//x,X,y,Y,z,Z
  std::vector < std::vector<int> >bBoxes2 = std::vector < std::vector < int > > (nbCells2,std::vector<int>(6,0) );//x,X,y,Y,z,Z
  std::vector < std::vector < double > > bary1 = std::vector < std::vector < double > > (nbCells1,std::vector<double>(3,0) );
  std::vector < std::vector < double > > bary2 = std::vector < std::vector < double > > (nbCells2,std::vector<double>(3,0) );
  std::vector < int > volumes1=std::vector < int > (nbCells1,0);
  std::vector < int > volumes2=std::vector < int > (nbCells2,0);

  ///Verrous eventuels
  std::vector < int > occupe2=std::vector < int > (nbCells2,0);
  std::vector < int > occupe1=std::vector < int > (nbCells1,0);

  //Informations de la matrice de recouvrement
  std::vector < std::vector < int > > recouvrement = std::vector < std::vector < int > > (nbCells1,std::vector<int>  (0,0));
  std::vector < std::vector< float > > scores_ = std::vector < std::vector < float > > (nbCells1,std::vector < float >  (0,0));
  std::vector < std::vector < int > > correspondantsPoss = std::vector < std::vector < int > > (nbCells1,std::vector<int>  (0,0));
  std::vector < int > nbPoss = std::vector < int > (nbCells1,0);

  ///Structures pour le calcul des scores basés sur la distance
  std::vector < std::vector < int > > correspondantsPossDistance = std::vector < std::vector < int > > (nbCells1,std::vector<int>  (0,0));
  std::vector < std::vector< float > > scoresDistance = std::vector < std::vector < float > > (nbCells1,std::vector < float >  (0,0));
  std::vector < int > nbPossDistance = std::vector < int > (nbCells1,0);
  std::vector < int > tab1 = std::vector < int > (3,0);
  std::vector < int > tab2 = std::vector < int > (3,0);
  std::vector < std::vector < int >  > bresenCoords = std::vector < std::vector < int >  > (grandeValeur,std::vector < int > (4,0));

  //Pour la structure de graphe
  std::vector < int > & coupleCel1=mothers;//std::vector < int > (0,0);
  std::vector < int > & coupleCel2=children;//std::vector < int > (0,0);
  std::vector < double > &coupleScore=scores;//std::vector < float > (0,0);

  ///Pour les correspondances a venir
  std::vector  < std::vector < int > >  correspondance=std::vector < std::vector < int > >  (nbCells2,std::vector < int >(2,0));
  std::vector < std::vector < int >  > destinees = std::vector < std::vector < int >  > (nbCells1,std::vector < int > (0,0));

  ///Pour les correspondances de l'ancien mapping
  std::vector < std::vector < int > > arbreFilleAncienMapping = std::vector < std::vector < int > > (nbCells1,std::vector < int > (0,-1));
  std::vector  < int > arbreMereAncienMapping = std::vector < int > (nbCells2,-1);

  ///Pour la comparaison de segmentations (optionMode=2)
  std::vector < int > resultatSegmentation = std::vector < int > (nbCells1,0);
  std::vector < float > scoreSegmentation = std::vector < float > (nbCells1,0);

  // //////// Lecture du mapping precedent
  // if(optionFix == NOFIX){}
  // if(optionFix == FIX_ONE || optionMode==TRACKING_MODE){
  //   occupe1[1]=1;
  //   occupe2[1]=1;
  //   arbreFilleAncienMapping[1].push_back(1);
  //   arbreMereAncienMapping[1]=1;
  // }
  // if(optionFix == FIX_ALL){
  //   //lecture du mapping
  //   FILE * fichMap = fopen (optChaine,"r");
  //   fscanf(fichMap,"NombreDeCellules=%i\n",ent2);
  //   nbCells=*ent2;
  //   for (int cel=0;cel<nbCells;cel++){
  //     fscanf(fichMap,"%i : nbFilles=%i -> [",ent1,ent2);
  //     cel2=*ent1;
  //     COUT<<"Cellule mere fixee : "<<cel2<<"avec les filles : [";
  //     for(int fil=0;fil< (*ent2) ; fil++){
  // 	fscanf(fichMap,"%i,",ent1);
  // 	COUT<<(*ent1)<<",";
  // 	if (*ent1 ==-1)COUT<<"Probleme a la lecture du mapping precedent ligne "<<cel<<" : lecture de -1 au lieu d'un numero de cellule"<<ENDL;
  // 	if( (occupe2[*ent1]==1) || (occupe2[*ent1]==1) ){
  // 	  COUT<<"Probleme : cellule lue dans ancien mapping a deja ete lue dans ce meme mapping a une autre ligne. Probleme intervenu a la ligne "<<cel<<ENDL;exit(13);
  // 	}
  // 	arbreMereAncienMapping[*ent1]=cel2;
  // 	arbreFilleAncienMapping[cel2].push_back(*ent1);
  // 	occupe2[*ent1]=1;
  // 	occupe1[cel2]=1;
  //     }
  //     COUT<<ENDL;
  //     fscanf(fichMap,"%i,]\n",ent1);
  //     if (*ent1 != -1)COUT<<"Probleme a la lecture du mapping precedent : ligne "<<cel<<" : lecture de "<<(*ent1)<<" au lieu du -1 qui doit terminer la ligne"<<ENDL;
  //   }
  //   fclose (fichMap);
  // }
  // else{
  //   COUT<<"Probleme : mode de fixation non reconnu. Choisissez parmi -nofix, -fixOne ou -fixAll"<<ENDL;
  //   exit(7);
  // }

  //////// Calcul des bounding boxes et des volumes des cellules //////////////////////////////////////////
  // if(BLABLA)CERR<<"\n------------ Calcul des bounding boxes et des volumes des cellules aux deux temps-------"<<ENDL;
  for(int i=0;i<nbCells1;i++){
    bBoxes1[i][0]=sx_im1-1;
    bBoxes1[i][2]=sy_im1-1;
    bBoxes1[i][4]=sz_im1-1;
  }
  for(int i=0;i<nbCells2;i++){
    bBoxes2[i][0]=sx_im2-1;
    bBoxes2[i][2]=sy_im2-1;
    bBoxes2[i][4]=sz_im2-1;
  }
  for(int i =0;i<sx_im1 ; i++){
    for(int j =0;j<sy_im1 ; j++){
      for(int k =0;k<sz_im1 ; k++){
	unsigned int index = sx_im1*sy_im1*k + sx_im1*j + i;
	valVox=data_im1[index];
	volumes1[valVox]++;
	bary1[valVox][0]+=i;bary1[valVox][1]+=j;bary1[valVox][2]+=k;
	if(bBoxes1[valVox][0] > i) bBoxes1[valVox][0] = i;
	if(bBoxes1[valVox][1] < i) bBoxes1[valVox][1] = i;
	if(bBoxes1[valVox][2] > j) bBoxes1[valVox][2] = j;
	if(bBoxes1[valVox][3] < j) bBoxes1[valVox][3] = j;
	if(bBoxes1[valVox][4] > k) bBoxes1[valVox][4] = k;
	if(bBoxes1[valVox][5] < k) bBoxes1[valVox][5] = k;
	valVox=data_im2[index];
	volumes2[valVox]++;
	bary2[valVox][0]+=i;bary2[valVox][1]+=j;bary2[valVox][2]+=k;
	if(bBoxes2[valVox][0] > i) bBoxes2[valVox][0] = i;
	if(bBoxes2[valVox][1] < i) bBoxes2[valVox][1] = i;
	if(bBoxes2[valVox][2] > j) bBoxes2[valVox][2] = j;
	if(bBoxes2[valVox][3] < j) bBoxes2[valVox][3] = j;
	if(bBoxes2[valVox][4] > k) bBoxes2[valVox][4] = k;
	if(bBoxes2[valVox][5] < k) bBoxes2[valVox][5] = k;
      }
    }
  }
  for(int cel1 = 1;cel1<nbCells1 ; cel1++){
    if(volumes1[cel1]>0){
      bary1[cel1][0]/=(1.0*volumes1[cel1]);
      bary1[cel1][1]/=(1.0*volumes1[cel1]);
      bary1[cel1][2]/=(1.0*volumes1[cel1]);
      // COUT<<"bary1 "<<" "<<cel1<<" "<<bary1[cel1][0]<<" "<<bary1[cel1][1]<<" "<<bary1[cel1][2]<<ENDL;
      // COUT<<"Erreur : une cellule de volume 0";
    }
    else {
      bary1[cel1][0]=0.5;bary1[cel1][1]=0.5;bary1[cel1][2]=0.5;
    }
  }
  for(int cel2 = 1;cel2<nbCells2 ; cel2++){
    if(volumes2[cel2]>0){
      bary2[cel2][0]/=(1.0*volumes2[cel2]);
      bary2[cel2][1]/=(1.0*volumes2[cel2]);
      bary2[cel2][2]/=(1.0*volumes2[cel2]);
    }
    else {
      bary2[cel2][0]=0.5;bary2[cel2][1]=0.5;bary2[cel2][2]=0.5;
      // COUT<<"Erreur : une cellule de volume 0";
    }
  }
  // if(BLABLA)COUT<<"T1 : "<<nbCells1-1<<" cellules. Volume moyen = "<<((sx_im1*sy_im1*sz_im1-volumes1[1])*1.0/(nbCells1-1))<<ENDL;
  // if(BLABLA)COUT<<"T2 : "<<nbCells2-1<<" cellules. Volume moyen = "<<((sx_im2*sy_im2*sz_im2-volumes2[1])*1.0/(nbCells2-1))<<ENDL;

  ///Calcul de la matrice de recouvrement
  // if(BLABLA)CERR<<"\n------------ Lecture des segmentations pour le calcul de la matrice de recouvrement -------"<<ENDL;
  for(int i =0;i<sx_im2 ; i++){
    // if(BLABLA){
    //   if(i%50==0){
    // 	COUT<<(i*100.0/sx_im2)<<" %\r"<<ENDL;
    // 	CERR<<(i*100.0/sx_im2)<<" %\r"<<ENDL;
    //   }
    // }
    for(int j =0;j<sy_im2 ; j++){
      for(int k =0;k<sz_im2 ; k++){
	unsigned int index = sx_im1*sy_im1*k + sx_im1*j + i;
	cel1 = data_im1[index];
	cel2 = data_im2[index];
	if(nbPoss[cel1]==0){
	  nbPoss[cel1]=1;
	  correspondantsPoss[cel1].push_back(cel2);
	  recouvrement[cel1].push_back(1);
	}
	else{
	  trouve=false;
	  for(int ind=0;ind<nbPoss[cel1];ind++){
	    if(correspondantsPoss[cel1][ind]==cel2){
	      trouve=true;
	      lindex=ind;
	    }
	  }
	  if(trouve){
	    recouvrement[cel1][lindex]++;
	  }
	  else{
	    correspondantsPoss[cel1].push_back(cel2);
	    recouvrement[cel1].push_back(1);
	    nbPoss[cel1]++;
	  }
	}
      }
    }
  }
  for(int cel1 = 1;cel1<nbCells1 ; cel1++){
    nbInterPoss+=nbPoss[cel1];
  }
  for(int cel1=1;cel1<nbCells1;cel1++){
    for(int cel2=0;cel2<nbPoss[cel1];cel2++){
      countInter=recouvrement[cel1][cel2];
      scores_[cel1].push_back(countInter*1.0/(volumes1[cel1]+volumes2[correspondantsPoss[cel1][cel2]]-countInter));
    }
  }
  // CERR<<"Nb previsionnel de possibilités, en regard de l'intersection des cellules = "<<nbInterPoss<<ENDL;


  ////////// Ajouter les couples basés sur la distance
  nbInterPoss=0;
  if((optionMode==TRACKING_MODE)){
    // CERR<<"Calcul des possibilités supplementaires de mapping"<<ENDL;
    // COUT<<"Calcul des possibilités supplementaires de mapping"<<ENDL;
    //Pour toute cellule mere, ajouter les cellules filles dont le barycentre est a une distance inferieure a distance
    for(int cel1 = 2;cel1<nbCells1 ; cel1++){
      for(int cel2 = 2; cel2<nbCells2 ; cel2++){
	//rechercher si le cas a ete detecte en superposition
	trouve=false;
	for(int i=0;i<correspondantsPoss[cel1].size();i++){
	  if(correspondantsPoss[cel1][i]==cel2)trouve=true;
	}
	//si les cellules s'intersectent, ou que le barycentre de la cellule 2 est inclus dans la cellule 1
	//ou qu'il est situé a une distance raisonnable de la surface de la cellule 1

	// TO WHOEVER LOOKS AT THIS CODE! THE DAMN CAST IS NECESSARY TO
	// GET THE SAME RESULT AS ROMAIN. THAT DOESN'T MEAN THAT IT IS
	// A GOOD THING BUT IT'S THE SAME THING...
	unsigned int index = sx_im1*sy_im1*(unsigned int)bary2[cel2][2] +
	  sx_im1*(unsigned int)bary2[cel2][1] +
	  (unsigned int)bary2[cel2][0];
	if( trouve  ||  (data_im1[index]==cel1) || (distance > norm(bary1[cel1][0]*vx,bary1[cel1][1]*vy,bary1[cel1][2]*vz,bary2[cel2][0]*vx,bary2[cel2][1]*vy,bary2[cel2][2]*vz)) ){
	  //Retenir
	  correspondantsPossDistance[cel1].push_back(cel2);
	  nbPossDistance[cel1]++;

	  //Calcul de la ligne 3D (algo de Bresenham)
	  for (int coor=0;coor<3;coor++){
	    tab1[coor]=bary1[cel1][coor];
	    tab2[coor]=bary2[cel2][coor];
	  }
	  bresenham_line3d(&tab1,&tab2,&bresenCoords);

	  //Parcours depuis le debut jusqu'a sortir de la cellule 1
	  sortie=false;
	  incr=-1;
	  while( ( !sortie)  && (incr+1< bresenCoords[0][3])){
	    ++incr;
	    unsigned int index_2 = sx_im1*sy_im1*bresenCoords[incr][2] + sx_im1*bresenCoords[incr][1] + bresenCoords[incr][0];
	    if( (data_im1[index_2]) != cel1)sortie=true;
	  }
	  for (int coor=0;coor<3;coor++)tab1[coor]=bresenCoords[incr][coor];

	  //barycentre de la cellule 2
	  for (int coor=0;coor<3;coor++)tab2[coor]=bresenCoords[bresenCoords[0][3]-1][coor];

	  //Calcul de la distance entre ces deux points
	  //Cas d'inclusion de cel2 dans cel1 puis autres cas
	  if( data_im1[index]==cel1) scoresDistance[cel1].push_back(0);
	  else scoresDistance[cel1].push_back(norm(tab1[0]*vx,tab1[1]*vy,tab1[2]*vz,tab2[0]*vx,tab2[1]*vy,tab2[2]*vz)/distance);
	  nbInterPoss++;
	}
      }
    }
    // CERR<<"Nb previsionnel de possibilités en considerant uniquement la distance = "<<nbInterPoss<<ENDL;
  }

  // COUT<<"Pour moi c'est la la bonne valeur "<< scoresDistance.size()<<ENDL;


  //////////Listing des couples possibles
  //Ecriture des couples deja connus
  for(int cel2 = 1; cel2<nbCells2 ; cel2++){
    if(occupe2[cel2]!=0){
      coupleCel1.push_back(arbreMereAncienMapping[cel2]);
      coupleCel2.push_back(cel2);
      coupleScore.push_back(1);
    }
  }

  ///////////Insertion de toutes les autres possibilites de couples
  //Cas de comparaison : insertion des couples qui s'intersectent avec leur score de Dice inverse
  for(int cel1 = 1;cel1<nbCells1 ; cel1++){
    if(occupe1[cel1]==0){
      if(optionMode==COMPARISON_MODE){//scores basés sur la mesure de Dice
	for(unsigned int j = 0; j< correspondantsPoss[cel1].size(); j++){
	  cel2=correspondantsPoss[cel1][j];
	  if(occupe2[cel2]==0){
	    coupleCel1.push_back(cel1);
	    coupleCel2.push_back(cel2);
	    coupleScore.push_back(scores_[cel1][j]);
	  }
	}
      }
      else if(optionMode==TRACKING_MODE){//scores basés sur la distance
	for(unsigned int j = 0; j< correspondantsPossDistance[cel1].size(); j++){
	  cel2=correspondantsPossDistance[cel1][j];
	  if(occupe2[cel2]==0){
	    coupleCel1.push_back(cel1);
	    coupleCel2.push_back(cel2);
	    coupleScore.push_back(1-scoresDistance[cel1][j]);
	  }
	}
      }
    }
  }

  return 0;
}

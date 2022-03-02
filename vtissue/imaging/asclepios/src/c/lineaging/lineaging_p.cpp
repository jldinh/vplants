

#include "lineaging_p.h"

#define VERBOSE
#include "macros.h"

#include <algorithm>


//Modes de suivi : TODO make these proper enumerations!
#define COMPARISON_MODE 2
#define TRACKING_MODE 1

// ------------------------------- Node class definitions --------------------------
Vertex::Vertex():
  valMaxPot(50),
  valide(true),
  flotSortant(0),
  flotEntrant(0),
  numero(0),
  numeroEdgesSortants(),
  numeroEdgesEntrants(),
  time(0),
  potential(0),
  previous(-1){
}

Vertex::Vertex(const Vertex & other):
  valMaxPot(other.valMaxPot),
  valide(other.valide),
  flotSortant(other.flotSortant),
  flotEntrant(other.flotEntrant),
  numero(other.numero),
  numeroEdgesSortants(other.numeroEdgesSortants),
  numeroEdgesEntrants(other.numeroEdgesEntrants),
  time(other.time),
  potential(other.potential),
  previous(other.previous){
}

// -- accessors --
bool Vertex::isValid(){
	return valide;
}

int Vertex::getId(){
	return numero;
}
void Vertex::setId(int nb){
	numero = nb;
}

// - incoming -
void Vertex::addIncoming(int num){
	numeroEdgesEntrants.push_back(num);
}
int Vertex::getIncomingCount(){
  return this->numeroEdgesEntrants.size();
}
int Vertex::getIncoming(int num){
	return numeroEdgesEntrants[num];
}
void Vertex::addToIncomingFlow(int num){
	flotEntrant+=num;
	valide=(flotEntrant==flotSortant);
}

// - outgoing -
void Vertex::addOutgoing(int num){
	numeroEdgesSortants.push_back(num);
}
int Vertex::getOutgoingCount(){
  return this->numeroEdgesSortants.size();
}
int Vertex::getOutgoing(int num){
	return numeroEdgesSortants[num];
}
void Vertex::addToOutgoingFlow(int num){
	flotSortant+=num;
	valide=(flotEntrant==flotSortant);
}
// - time -
void Vertex::setTime(int nb){
	time = nb;
}
int Vertex::getTime(){
	return time;
}

// - potential -
void Vertex::setPotential(double pot){
	potential = pot;
}
double Vertex::getPotential(){
	return potential;
}

// - previous -
void Vertex::setPrevious(int prec){
	previous=prec;
}
int Vertex::getPrevious(){
	return previous;
}








// ------------------------------- Edge class definitions --------------------------
Edge::Edge(){
	valMaxFlot=50;
	valide=true;
	numero = 0;
	numDepart = 0;
	numArrivee = 0;
	typeDansStruct = 0;//0 pour l'edge retour, 1 pour edge source, 2 pour edge appariement, 3 pour edge collecteur
	flot = 0;
	cout = 0;
	capaciteMin = 0;
	capaciteMax = 0;
	typeConformite = 0;//de 1 à 7
	couleur = 0;//0=incolore, 1=noir, 2=rouge, 3=vert
}

int Edge::getId(){
	return numero;
}
int Edge::getDepart(){
	return numDepart;
}
int Edge::getArrivee(){
	return numArrivee;
}
int Edge::getTypeStruct(){
	return typeDansStruct;
}
int Edge::getFlow(){
	return flot;
}
double Edge::getCout(){
	return cout;
}
int Edge::getCapaciteMax(){
	return capaciteMax;
}
int Edge::getCapaciteMin(){
	return capaciteMin;
}
int Edge::getTypeConformite(){
	return typeConformite;
}
int Edge::getCouleur(){
	return couleur;
}
bool Edge::isValid(){
	return valide;
}

void Edge::setId(int num){
	numero = num;
}
void Edge::setDepart(int num){
	numDepart = num;
}
void Edge::setArrivee(int num){
	numArrivee = num;
}
void Edge::setTypeStruct(int num){
	typeDansStruct = num;
}
void Edge::setFlow(int num){
	if(num>valMaxFlot)num=valMaxFlot;
	if(num<0)num=0;
	flot = num;
	valide=((flot<=capaciteMax) && (flot>=capaciteMin));
}
void Edge::setCout(double num){
	cout = num;
}
void Edge::setCapaciteMax(int num){
	capaciteMax = num;
}
void Edge::setCapaciteMin(int num){
	capaciteMin = num;
}
void Edge::setTypeConformite(int num){
	typeConformite = num;
}
void Edge::setCouleur(int num){
	couleur = num;
}





// ------------------------------- Graph class definitions --------------------------

FlowGraph::FlowGraph(int nSom1,int nSom2, int nApp,int mode):
  optionMode(mode),
  nbEdges(nApp+nSom1+nSom2+1+ nSom1-1 + nSom2-1 ), //les appariements + Les sources + les collecteurs + l'ar retour + les edges fuite 1 + les edges fuite 2
  numEdgeTmp(0),
  nbAppariements(nApp),
  nbSommets(nSom1+nSom2+2),//toutes les cellules de 0 a N1 et de 0 a N2 + le sommet collecteur + le sommet retour
  edges(this->nbEdges),
  sommets(nbSommets, Vertex()),
  nbSommets1(nSom1),
  nbSommets2(nSom2),
  flagSommets(nbSommets,std::vector<int>(5,0)),
  flagEdges(nbEdges,std::vector<int>(1,0))
{
  // for(int i=0;i<nbSommets;i++){
  //   sommets.push_back(Vertex());
  // }
}

FlowGraph::~FlowGraph(){
  sommets.clear();
  edges.clear();
  flagSommets.clear();
  flagEdges.clear();
}

int FlowGraph::noterLaPresqueCorrespondance(int futur){
  int num=nbSommets1+futur;
  Vertex & som = sommets[num];
  for(int j=0;j<som.getIncomingCount();j++){
    Edge & edge = edges[som.getIncoming(j)];
    if((edge.getFlow() == 1) && ( sommets[edge.getDepart()].getId()!=0)) {
      return -1;
    }
  }
  float coutMin=100.0;
  int poss=-1;
  for(int j=0;j<som.getIncomingCount();j++){
    Edge & edge = edges[som.getIncoming(j)];
    if(edge.getCout() < coutMin ){
      poss=edge.getDepart();
      coutMin=edge.getCout();
    }
  }
  if (poss == -1) {
    ERROR_MSG("noterLaPresqueCorrespondance: poss shouldn't be -1");
  }
  return poss;
}

int FlowGraph::noterLaDestinee(int passe){
  int num=passe;
  Vertex & som = sommets[num];
  for(int j=0;j<som.getOutgoingCount();j++){
    Edge & edge = edges[som.getIncoming(j)];
    if(edge.getFlow() == 1) {
      return edge.getArrivee()-nbSommets1;
    }
  }
  ERROR_MSG("noterLaDestinee failed");
  return -1;
}

int FlowGraph::noterLaMaman(int futur){
  int num=futur+nbSommets1;
  int nb=0;
  int retour = -1;
  Vertex & som = sommets[num];
  for(int j=0;j<som.getIncomingCount();j++){
    Edge & edge = edges[som.getIncoming(j)];
    if(edge.getFlow() == 1) {
      retour=edge.getDepart();
      nb++;
    }
  }

  if(nb>1){
    ERROR_MSG("noterLaMaman failed");
    return -1;
  }
  return retour;
}


void FlowGraph::defineMapping(int cel1,int cel2,double cout){
  Edge & edge    = edges[numEdgeTmp];
  Vertex & som1 = sommets[cel1];
  Vertex & som2 = sommets[cel2+nbSommets1];

  edge.setDepart(cel1);
  edge.setArrivee(cel2+nbSommets1);
  edge.setCout(cout);
  edge.setCapaciteMax(1);
  edge.setCapaciteMin(0);
  edge.setFlow(0);
  edge.setTypeStruct(2);
  if(cel1>=nbSommets1){
    ERROR_MSG("Depassement de capacité : cellule a T0 numero "<<cel1<<" non prévue:"<<nbSommets1);
  }
  if(cel2>=nbSommets2){
    ERROR_MSG("Depassement de capacité : cellule a T1 numero "<<cel2<<" non prévue:"<<nbSommets2);
  }
  som1.setTime(1);
  som1.addOutgoing(numEdgeTmp);
  som1.setId(cel1);
  som2.setId(cel2);
  som2.setTime(2);
  som2.addIncoming(numEdgeTmp);
  numEdgeTmp++;
}

void FlowGraph::ajouterLesStructuresSupplementaires(){
  for(int i=0;i<nbSommets1;i++){
    sommets[i].setId(i);
    sommets[i].setTime(1);
  }
  for(int i=0;i<nbSommets2;i++){
    sommets[i+nbSommets1].setId(i);
    sommets[i+nbSommets1].setTime(2);
  }
  //Ajouter le sommet source et le sommet collecteur

  sommets[nbSommets1+nbSommets2+1].addOutgoing(numEdgeTmp);
  sommets[nbSommets1+nbSommets2+1].setTime(3);
  sommets[nbSommets1+nbSommets2+1].setId(nbSommets1+nbSommets2+1);
  sommets[nbSommets1+nbSommets2].setTime(0);
  sommets[nbSommets1+nbSommets2].addIncoming(numEdgeTmp);
  sommets[nbSommets1+nbSommets2].setId(nbSommets1+nbSommets2);

  //Ajouter l'edge retour
  Edge & edgeRetour = edges[numEdgeTmp];
  edgeRetour.setCout( FlowGraph::prohibitiveCost );
  edgeRetour.setTypeStruct(0);
  edgeRetour.setCapaciteMax(nbSommets2+nbSommets1);
  edgeRetour.setCapaciteMin(std::max(nbSommets2,nbSommets1));
  edgeRetour.setFlow(0);
  edgeRetour.setDepart(nbSommets1+nbSommets2+1);
  edgeRetour.setArrivee(nbSommets1+nbSommets2);
  numEdgeTmp++;

  DEBUG_MSG("Edge retour ajouté, nbEdges en tout = "<<numEdgeTmp);

  //ajouter les edges sources
  for(int i=0;i<nbSommets1;i++){
    Edge & edgeSrc = edges[numEdgeTmp];
    edgeSrc.setDepart(nbSommets1+nbSommets2);
    edgeSrc.setTypeStruct(1);
    edgeSrc.setArrivee(i);
    edgeSrc.setCout(0);
    //cas special pour la source du sommet lambda
    if(i==0){
      edgeSrc.setCapaciteMax(std::max(nbSommets1,nbSommets2));
      edgeSrc.setTypeStruct(4);
    }
    else {
      if(optionMode==COMPARISON_MODE){
	edgeSrc.setCapaciteMax(1);
      }
      else if(optionMode==TRACKING_MODE){
	edgeSrc.setCapaciteMax(FlowGraph::nDivMax);
      }
    }
    edgeSrc.setCapaciteMin(0);
    edgeSrc.setFlow(0);
    sommets[nbSommets2+nbSommets1].addOutgoing(numEdgeTmp);
    sommets[i].addIncoming(numEdgeTmp);
    numEdgeTmp++;
  }

  DEBUG_MSG("Edges sources ajoutés, nbEdges en tout = "<<numEdgeTmp);

  //ajouter les edges collecteurs
  for(int i=0;i<nbSommets2;i++){
    Edge & edgeSink = edges[numEdgeTmp];
    edgeSink.setDepart(nbSommets1+i);
    edgeSink.setTypeStruct(3);
    edgeSink.setArrivee(nbSommets2+nbSommets1+1);
    edgeSink.setCout(0);
    //cas special pour le collecteur du sommet lambda2
    if(i==0){
      edgeSink.setCapaciteMax(std::max(nbSommets1,nbSommets2));
      edgeSink.setTypeStruct(5);
    }
    else edgeSink.setCapaciteMax(1);
    edgeSink.setCapaciteMin(0);
    edgeSink.setFlow(0);
    sommets[nbSommets2+nbSommets1+1].addIncoming(numEdgeTmp);
    sommets[nbSommets1+i].addOutgoing(numEdgeTmp);
    numEdgeTmp++;
  }

  DEBUG_MSG("Edges collecteurs ajoutés, nbEdges en tout = "<<numEdgeTmp);

  //ajouter les edges fuite n1
  for(int i=1;i<nbSommets1;i++){
    Edge & edgeN1 = edges[numEdgeTmp];
    edgeN1.setDepart(i);
    edgeN1.setTypeStruct(2);
    edgeN1.setArrivee(nbSommets1+0);
    edgeN1.setCout(FlowGraph::prohibitiveCost);
    edgeN1.setCapaciteMax(1);
    edgeN1.setCapaciteMin(0);
    edgeN1.setFlow(0);
    sommets[i].addOutgoing(numEdgeTmp);
    sommets[nbSommets1+0].addIncoming(numEdgeTmp);
    numEdgeTmp++;
  }

  DEBUG_MSG("Edges fuites 1 ajoutés, nbEdges en tout = "<<numEdgeTmp);

  //ajouter les edges fuite n2
  for(int i=1;i<nbSommets2;i++){
    Edge & edgeN2 = edges[numEdgeTmp];
    edgeN2.setDepart(0);
    edgeN2.setTypeStruct(2);
    edgeN2.setArrivee(nbSommets1+i);
    edgeN2.setCout(FlowGraph::prohibitiveCost);
    edgeN2.setCapaciteMax(1);
    edgeN2.setCapaciteMin(0);
    edgeN2.setFlow(0);
    sommets[0].addOutgoing(numEdgeTmp);
    sommets[nbSommets1+i].addIncoming(numEdgeTmp);
    numEdgeTmp++;
  }

  DEBUG_MSG("Edges fuites 2 ajoutés, nbEdges en tout = "<<numEdgeTmp);
}

void FlowGraph::unAlgoDeFlot(){
  int somCur,somNext,arNext,compte1,compte3,som1,som2,numSom,nbModifIter,nbDansIter;
  bool inverse,affich,fini=false;
  int distanceInf=100000000;
  int nbModif=1;
  int iter=0;

  while(! fini){
    DEBUG_MSG("Iteration"<<(++iter)); // iter is only used for display
    nbModif=0;
    for(int som=0;som<nbSommets1+nbSommets2+2;som++){
      Vertex & sommet = sommets[som];
      sommet.setPotential(distanceInf);
      sommet.setPrevious(-1);
    }

    somCur=nbSommets1+nbSommets2;
    sommets[somCur].setPotential(0);
    for (int iSom=0;iSom<nbSommets1+nbSommets2+2;++iSom){//Faire nbSommets fois
      nbModifIter=0;
      for(int iAr=0;iAr<nbEdges;++iAr){//Pour charque edge, relaxer
	Edge    & edge     = edges[iAr];
	Vertex & sommet1 = sommets[edge.getDepart()];
	Vertex & sommet2 = sommets[edge.getArrivee()];
	som1=edge.getDepart();
	som2=edge.getArrivee();
	affich=false;
	if( (sommet2.getPotential()>sommet1.getPotential()+edge.getCout()) && (edge.getCapaciteMax()>edge.getFlow()) ){
	  nbModif++;
	  nbModifIter++;
	  sommet2.setPotential(sommet1.getPotential()+edge.getCout());
	  sommet2.setPrevious(som1);
	}
	else if( (sommet1.getPotential()>sommet2.getPotential()-edge.getCout()) && (edge.getCapaciteMin()<edge.getFlow()) ){
	  nbModif++;
	  nbModifIter++;
	  sommet1.setPotential(sommet2.getPotential()-edge.getCout());
	  sommet1.setPrevious(som2);
	}
      }
      nbDansIter=iSom;
      if(nbModifIter==0)iSom=nbSommets1+nbSommets2+2;
    }

    //Lecture du chemin le moins couteux si il existe
    somCur = nbSommets1+nbSommets2 + 1;
    if(sommets[somCur].getPrevious()==-1){
      fini=true;
    }
    else{
      numSom=0;
      while(somCur!=nbSommets1+nbSommets2){
	Vertex & pathNode = sommets[somCur];
	somNext=pathNode.getPrevious();
	arNext=-1;
	for(int iAr=0;iAr<pathNode.getIncomingCount();iAr++){
	  if(edges[pathNode.getIncoming(iAr)].getDepart()==somNext){
	    arNext=pathNode.getIncoming(iAr);
	    inverse=false;
	  }
	}
	for(int iAr=0;iAr<pathNode.getOutgoingCount();iAr++){
	  if(edges[pathNode.getOutgoing(iAr)].getArrivee()==somNext){
	    arNext=pathNode.getOutgoing(iAr);
	    inverse=true;
	  }
	}
	if(arNext==-1){
	  ERROR_MSG("Erreur, pas de sommet precedent dans le chemin calcule");
          return;
	}

	ajouterAuFlotDeAreteEtSommets(inverse ? -1 : 1,arNext,false);
	somCur=somNext;
      }
      //			COUT<<"Ok, iteration suivante ? "<<ENDL<<ENDL;
    }
    // Regarder si il reste un collecteur ou une source inutilisee
    compte1=0;
    compte3=0;
    for(int iAr=0;iAr<nbEdges;++iAr){
      if((edges[iAr].getTypeStruct()==1) || (edges[iAr].getTypeStruct()==3)){
	if((edges[iAr].getFlow()==0) && (sommets[edges[iAr].getArrivee()].getId()!=0) && (sommets[edges[iAr].getDepart()].getId()!=0)){
	  if(edges[iAr].getTypeStruct()==1)compte1++;
	  else compte3++;
	}
      }
    }
    if((compte1+compte3)==0){
      if(fini==true){
	DEBUG_MSG("En effet, c'etait deja la fin (pas de chemin augmentant, et on arrive a un compte nul");
      }
      else{
	DEBUG_MSG("Alors c'etait la derniere iteration, puisqu'on a un compte nul. A priori a la suivante, on aurait trouvé pas de chemin augmentant possible");
	fini=true;
      }
    }
  }
  DEBUG_MSG("Fini!");
}



void FlowGraph::ajouterAuFlotDeAreteEtSommets(int flotDiff,int numArete,bool img){
  Edge & edge = edges[numArete];
  int fl=edge.getFlow();
  edge.setFlow(fl+flotDiff);
  sommets[edge.getDepart()].addToOutgoingFlow(flotDiff);
  sommets[edge.getArrivee()].addToIncomingFlow(flotDiff);
}


/* Plutot du coté des comparaisons des segmentations*/
double FlowGraph::calculerLeScore(){
  double sommeErreurs=0;
  int flot;
  int nombre=0;
  /// Ajouter la somme des couts*flots du graphe biparti
  /// et ajouter un pour chaque fille en trop de chaque s_i
  for(int i=0;i<nbSommets1;i++){//ajouter les edges sources
    flot=0;
    Vertex & som = sommets[i];
    if(som.getOutgoingCount()==1){
      Edge & edge = edges[som.getOutgoing(0)];
      nombre++;
      sommeErreurs+=edge.getCout()*edge.getFlow();
    }
  }
  return (sommeErreurs/(1.0*nbSommets1));
}

/* Plutot du coté des comparaisons des segmentations*/
double FlowGraph::calculerLeScoreDuneCellule(int i,int mode){
  int nb=0;
  double total=0;
  Vertex & som = sommets[i];
  for(int j=0; j< som.getOutgoingCount() ; j++){
    Edge & edge = edges[som.getOutgoing(j)];
    if( edge.getFlow() == 1){
      nb++;
      total+=edge.getCout();
    }
  }

  if ((nb != 1) && (mode==COMPARISON_MODE)) {
    ERROR_MSG("calculerLeScoreDuneCellule failed");
  }
  return total;
}





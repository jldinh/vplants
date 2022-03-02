#ifndef __MAPPING_P_H__
#define __MAPPING_P_H__

#include <vector>


typedef std::vector< std::vector<int> > DestinyListType;


class Vertex{
 public :
  typedef std::vector<int> IncomingEdgeList;
  typedef std::vector<int> OutgoingEdgeList;

  Vertex();
  Vertex(const Vertex & other);

  bool isValid();
  int  getId();
  void setId(int num);

  void addIncoming(int num);
  int  getIncomingCount();
  int  getIncoming(int num);
  void addToIncomingFlow(int num);

  void addOutgoing(int num);
  int  getOutgoingCount();
  int  getOutgoing(int num);
  void addToOutgoingFlow(int num);

  void setTime(int nb);
  int  getTime();

  void   setPotential(double pot);
  double getPotential();

  void setPrevious(int prec);
  int  getPrevious();

 private :
  int valMaxPot;
  bool valide;
  int flotSortant;
  int flotEntrant;
  int numero;
  IncomingEdgeList  numeroEdgesSortants;
  OutgoingEdgeList  numeroEdgesEntrants;
  int time;//0 pour source, 1 pour S1, 2 pour S2, 3 pour collecteur
  double potential;
  int previous;
};


class Edge{
 public :
  Edge();

  int getId();
  int getDepart();
  int getArrivee();
  int getTypeStruct();
  int getFlow();
  double getCout();
  int getCapaciteMax();
  int getCapaciteMin();
  int getTypeConformite();
  int getCouleur();

  void setId(int num);
  void setDepart(int num);
  void setArrivee(int num);
  void setTypeStruct(int num);
  void setFlow(int num);
  void setCout(double num);
  void setCapaciteMax(int num);
  void setCapaciteMin(int num);
  void setTypeConformite(int num);
  void setCouleur(int num);
  bool isValid();

 private :
  int valMaxFlot;
  bool valide;
  int numero;
  int numDepart;
  int numArrivee;
  int typeDansStruct;//0 pour l'edge retour, 1 pour edge source, 2 pour edge appariement, 3 pour edge collecteur
  int flot;
  double cout;
  int capaciteMin;
  int capaciteMax;
  int typeConformite;//de 1 à 7
  int couleur;//0=incolore, 1=noir, 2=rouge, 3=vert
};


class FlowGraph{
 public :
  FlowGraph(int nSom1,int nSom2, int nApp,int optionMode);
  ~FlowGraph();
  void defineMapping(int cel1,int cel2,double cout);
  void ajouterLesStructuresSupplementaires();
  void unAlgoDeFlot();
  void ajouterAuFlotDeAreteEtSommets(int flotDiff,int numArete,bool img);
  int noterLaPresqueCorrespondance(int futur);
  int noterLaDestinee(int passe);
  int noterLaMaman(int futur);
  double calculerLeScore();
  double calculerLeScoreDuneCellule(int i,int mode);
 private :
  int optionMode;
  int nbEdges;
  int numEdgeTmp; //variable qui sert a la construction iterative plus tard;
  int nbAppariements;
  int nbSommets;
  std::vector <Edge>  edges;
  std::vector <Vertex>  sommets;
  int nbSommets1;
  int nbSommets2;
  std::vector < std::vector < int > > flagSommets;
  std::vector < std::vector < int > > flagEdges;

  const static int prohibitiveCost = 2;
  const static int nDivMax = 8;
};

#endif//__MAPPING_P_H__

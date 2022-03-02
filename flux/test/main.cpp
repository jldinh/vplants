#include "electrical_model.h"
using namespace std;

int main()
{
  MTG* the_mtg = new MTG("hector2.mtg");
  assert(the_mtg);
  if(the_mtg->isValid())
    {
      cout<<"MTG built ..."<<endl;

      /*
         const Feature* _feature=new Feature();
         _feature=the_mtg->si_feature(1,"TopDia");
         cout<<"topdia = "<<_feature->r<<endl;
      */

      ElectricalModel* m_electricalModel=new ElectricalModel(the_mtg,3,0);

//      cout<<"isValid = "<<m_electricalModel->isValid()<<endl;

//      cout<<"nb scale = "<< the_mtg->scaleNb()<<endl;

      m_electricalModel->computeEM();

      delete the_mtg;
      delete m_electricalModel;
      return 1;
    }
  else
    {
      delete the_mtg;
      return 0;
    }
}

/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       V-Plants: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2014 CIRAD/INRA/Inria Virtual Plants
 *
 *       File author(s): Yann Guedon (yann.guedon@cirad.fr)
 *
 *       $Source$
 *       $Id: stat_funs2.cpp 16026 2014-03-07 16:08:03Z guedon $
 *
 *       Forum for V-Plants developers:
 *
 *  ----------------------------------------------------------------------------
 *
 *                      GNU General Public Licence
 *
 *       This program is free software; you can redistribute it and/or
 *       modify it under the terms of the GNU General Public License as
 *       published by the Free Software Foundation; either version 2 of
 *       the License, or (at your option) any later version.
 *
 *       This program is distributed in the hope that it will be useful,
 *       but WITHOUT ANY WARRANTY; without even the implied warranty of
 *       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 *       GNU General Public License for more details.
 *
 *       You should have received a copy of the GNU General Public
 *       License along with this program; see the file COPYING. If not,
 *       write to the Free Software Foundation, Inc., 59
 *       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 *  ----------------------------------------------------------------------------
 */



#include <iostream>

#include "stat_tool/stat_tools.h"
#include "stat_tool/distribution.h"
#include "stat_tool/discrete_mixture.h"
#include "stat_tool/convolution.h"
#include "stat_tool/compound.h"
#include "stat_tool/curves.h"
#include "stat_tool/markovian.h"
#include "stat_tool/vectors.h"
#include "stat_tool/mixture.h"
#include "stat_tool/regression.h"
#include "stat_tool/distance_matrix.h"

#include "sequence_analysis/renewal.h"
#include "sequence_analysis/sequences.h"
#include "sequence_analysis/variable_order_markov.h"
#include "sequence_analysis/hidden_variable_order_markov.h"
#include "sequence_analysis/semi_markov.h"
#include "sequence_analysis/hidden_semi_markov.h"
#include "sequence_analysis/nonhomogeneous_markov.h"
#include "sequence_analysis/tops.h"
#include "sequence_analysis/sequence_label.h"

#include "aml/ammodel.h"
#include "aml/parseraml.h"
#include "aml/kernel_err.h"
#include "aml/amstring.h"
#include "aml/array.h"

#include "aml/stat_module.h"


#define ERR_MSG_ARRAY STAT_err_msgs_aml
#define MODULE_NAME   "Statistics"


extern const char *STAT_err_msgs_aml[];


extern int nb_required_computation(const AMObjVector &args);



/*--------------------------------------------------------------*
 *
 *  Lecture des parametres d'une loi.
 *
 *--------------------------------------------------------------*/

static int parameter_input(const AMObjVector &args , int ident , int &inf_bound ,
                           int &sup_bound , double &parameter , double &probability ,
                           const char *function , int min_inf_bound)

{
  bool status = true , lstatus;


  sup_bound = I_DEFAULT;
  parameter = D_DEFAULT;
  probability = D_DEFAULT;

  if (args[1].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , function , 2 ,
                args[1].tag.string().data() , "INT");
  }
  else {
    inf_bound = args[1].val.i;
    if ((inf_bound < min_inf_bound) || (inf_bound > MAX_INF_BOUND)) {
      status = false;
      genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , function , 2);
    }
  }

  if ((ident == BINOMIAL) || (ident == UNIFORM)) {
    if (args[2].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , function , 3 ,
                  args[2].tag.string().data() , "INT");
    }

    else {
      sup_bound = args[2].val.i;

      switch (ident) {

      case BINOMIAL : {
        if ((sup_bound <= inf_bound) || (sup_bound - inf_bound > MAX_DIFF_BOUND)) {
          status = false;
          genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , function , 3);
        }
        break;
      }

      case UNIFORM : {
        if ((sup_bound < inf_bound) || (sup_bound - inf_bound > MAX_DIFF_BOUND)) {
          status = false;
          genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , function , 3);
        }
        break;
      }
      }
    }
  }

  else {
    switch (args[2].tag()) {
    case AMObjType::INTEGER :
      parameter = args[2].val.i;
      break;
    case AMObjType::REAL :
      parameter = args[2].val.r;
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , function , 3 ,
                  args[2].tag.string().data() , "INT or REAL");
      break;
    }

    if ((parameter <= 0.) || ((ident == POISSON) && (parameter > MAX_MEAN))) {
      status = false;
      genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , function , 3);
    }
  }

  if ((ident == BINOMIAL) || (ident == NEGATIVE_BINOMIAL)) {
    switch (args[3].tag()) {
    case AMObjType::INTEGER :
      probability = args[3].val.i;
      break;
    case AMObjType::REAL :
      probability = args[3].val.r;
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , function , 4 ,
                  args[3].tag.string().data() , "INT or REAL");
      break;
    }

    lstatus = true;

    switch (ident) {

    case BINOMIAL : {
      if ((probability < 0.) || (probability > 1.)) {
        lstatus = false;
      }
      break;
    }

    case NEGATIVE_BINOMIAL : {
      if ((probability <= 0.) || (probability >= 1.)) {
        lstatus = false;
      }
      else if (parameter * (1. - probability) / probability > MAX_MEAN) {
        lstatus = false;
      }
      break;
    }
    }

    if (!lstatus) {
      status = false;
      genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , function , 4);
    }
  }

  return status;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une loi a partir d'un fichier ou a partir
 *  de son identificateur et de ses parametres.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Distribution(const AMObjVector &args)

{
  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Distribution"));
  CHECKCONDVA(args[0].tag() == AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Distribution" , 1 ,
                          args[0].tag.string().data() , "STRING"));

  if (args.length() == 1) {
    DiscreteParametricModel *dist;
    StatError error;


    dist = discrete_parametric_ascii_read(error , ((AMString*)args[0].val.p)->data());

    if (dist) {
      STAT_model* model = new STAT_model(dist);
      return AMObj(AMObjType::DISTRIBUTION , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Distribution");
      return AMObj(AMObjType::ERROR);
    }
  }

  else {
    RWCString *pstr;
    bool status = true;
    register int i;
    int ident , inf_bound , sup_bound;
    double parameter , probability;
    DiscreteParametricModel *dist;


    pstr = (AMString*)args[0].val.p;
    for (i = BINOMIAL;i <= UNIFORM;i++) {
      if ((*pstr == STAT_discrete_distribution_word[i]) ||
          (*pstr == STAT_discrete_distribution_letter[i])) {
        ident = i;
        break;
      }
    }

    if (i == UNIFORM + 1) {
      status = false;
      genAMLError(ERRORMSG(DISTRIBUTION_NAME_sds) , "Distribution" , 1 ,
                  "BINOMIAL(B) or POISSON(P) or NEGATIVE_BINOMIAL(NB) or UNIFORM(U)");
    }

    else {
      if ((ident == BINOMIAL) || (ident == NEGATIVE_BINOMIAL)) {
        if (args.length() != 4) {
          status = false;
          genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Distribution" , 4);
        }
      }
      else if ((ident == POISSON) || (ident == UNIFORM)) {
        if (args.length() != 3) {
          status = false;
          genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Distribution" , 3);
        }
      }
    }

    if (status) {
      status = parameter_input(args , ident , inf_bound , sup_bound , parameter ,
                               probability , "Distribution" , 0);
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    dist = new DiscreteParametricModel(ident , inf_bound , sup_bound , parameter , probability);

    STAT_model* model = new STAT_model(dist);
    return AMObj(AMObjType::DISTRIBUTION , model);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un melange a partir d'un fichier ou a partir
 *  de poids et de lois elementaires.
 *
 *--------------------------------------------------------------*/

AMObj STAT_DiscreteMixture(const AMObjVector &args)

{
  DiscreteMixture *mixt;
  StatError error;


  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "DiscreteMixture"));

  if (args[0].tag() == AMObjType::STRING) {
    CHECKCONDVA(args.length() == 1 ,
                genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "DiscreteMixture"));
    CHECKCONDVA(args[0].tag() == AMObjType::STRING ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "DiscreteMixture" ,
                            args[0].tag.string().data() , "STRING"));

    mixt = discrete_mixture_ascii_read(error , ((AMString*)args[0].val.p)->data());
  }

  else {
    bool status = true;
    register int i;
    int nb_component = args.length() / 2;
    double weight[DISCRETE_MIXTURE_NB_COMPONENT];
    const DiscreteParametric *component[DISCRETE_MIXTURE_NB_COMPONENT];


    CHECKCONDVA(args.length() % 2 == 0 ,
                genAMLError(ERRORMSG(UNEVEN_NB_ARG_s) , "DiscreteMixture"));
    CHECKCONDVA((nb_component >= 2) && (nb_component <= DISCRETE_MIXTURE_NB_COMPONENT) ,
                genAMLError(ERRORMSG(NB_COMPONENT_sd) , "DiscreteMixture" , DISCRETE_MIXTURE_NB_COMPONENT));

    for (i = 0;i < nb_component;i++) {
      if (args[i * 2].tag() != AMObjType::REAL) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "DiscreteMixture" , i * 2 + 1 ,
                    args[i * 2].tag.string().data() , "REAL");
      }
      else {
        weight[i] = args[i * 2].val.r;
      }

      switch (args[i * 2 + 1].tag()) {
      case AMObjType::DISTRIBUTION :
        component[i] = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[i * 2 + 1].val.p)->pt)));
        break;
      case AMObjType::DISCRETE_MIXTURE :
        component[i] = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[i * 2 + 1].val.p)->pt)));
        break;
      case AMObjType::CONVOLUTION :
        component[i] = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[i * 2 + 1].val.p)->pt)));
        break;
      case AMObjType::COMPOUND :
        component[i] = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[i * 2 + 1].val.p)->pt)));
        break;
      default :
        component[i] = NULL;
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "DiscreteMixture" , i * 2 + 2 , args[i * 2 + 1].tag.string().data() ,
                    "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
        break;
      }
    }

    if (status) {
      mixt = discrete_mixture_building(error , nb_component , weight , component);
    }

    for (i = 0;i < nb_component;i++) {
      delete component[i];
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
  }

  if (mixt) {
    STAT_model* model = new STAT_model(mixt);
    return AMObj(AMObjType::DISCRETE_MIXTURE , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "DiscreteMixture");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un produit de convolution a partir d'un fichier ou
 *  a partir de lois elementaires.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Convolution(const AMObjVector &args)

{
  Convolution *convol;
  StatError error;


  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Convolution"));

  if (args[0].tag() == AMObjType::STRING) {
    CHECKCONDVA(args.length() == 1 ,
                genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "Convolution"));
    CHECKCONDVA(args[0].tag() == AMObjType::STRING ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "Convolution" ,
                            args[0].tag.string().data() , "STRING"));

    convol = convolution_ascii_read(error , ((AMString*)args[0].val.p)->data());
  }

  else {
    bool status = true;
    register int i;
    int nb_dist = args.length();
    const DiscreteParametric *dist[CONVOLUTION_NB_DISTRIBUTION];


    CHECKCONDVA((nb_dist >= 2) && (nb_dist <= CONVOLUTION_NB_DISTRIBUTION) ,
                genAMLError(ERRORMSG(NB_DISTRIBUTION_sd) , "Convolution" , CONVOLUTION_NB_DISTRIBUTION));

    for (i = 0;i < nb_dist;i++) {
      switch (args[i].tag()) {
      case AMObjType::DISTRIBUTION :
        dist[i] = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[i].val.p)->pt)));
        break;
      case AMObjType::DISCRETE_MIXTURE :
        dist[i] = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[i].val.p)->pt)));
        break;
      case AMObjType::CONVOLUTION :
        dist[i] = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[i].val.p)->pt)));
        break;
      case AMObjType::COMPOUND :
        dist[i] = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[i].val.p)->pt)));
        break;
      default :
        dist[i] = NULL;
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Convolution" , i + 1 , args[i].tag.string().data() ,
                    "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
        break;
      }
    }

    if (status) {
      convol = convolution_building(error , nb_dist , dist);
    }

    for (i = 0;i < nb_dist;i++) {
      delete dist[i];
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
  }

  if (convol) {
    STAT_model* model = new STAT_model(convol);
    return AMObj(AMObjType::CONVOLUTION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Convolution");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une loi composee a partir d'un fichier ou
 *  d'une loi de la somme et d'une loi elementaire
 *
 *--------------------------------------------------------------*/

AMObj STAT_Compound(const AMObjVector &args)

{
  Compound *cdist;
  StatError error;


  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compound"));

  if (args[0].tag() == AMObjType::STRING) {
    CHECKCONDVA(args.length() == 1 ,
                genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "Compound"));
    CHECKCONDVA(args[0].tag() == AMObjType::STRING ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "Compound" ,
                            args[0].tag.string().data() , "STRING"));

    cdist = compound_ascii_read(error , ((AMString*)args[0].val.p)->data());
  }

  else {
    bool status = true;
    register int i;
    DiscreteParametric *dist[2];


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Compound" , 2));

    for (i = 0;i < 2;i++) {
      switch (args[i].tag()) {
      case AMObjType::DISTRIBUTION :
        dist[i] = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[i].val.p)->pt)));
        break;
      case AMObjType::DISCRETE_MIXTURE :
        dist[i] = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[i].val.p)->pt)));
        break;
      case AMObjType::CONVOLUTION :
        dist[i] = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[i].val.p)->pt)));
        break;
      case AMObjType::COMPOUND :
        dist[i] = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[i].val.p)->pt)));
        break;
      default :
        dist[i] = NULL;
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compound" , i + 1 , args[i].tag.string().data() ,
                    "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
        break;
      }
    }

    if (status) {
      cdist = new Compound(*dist[0] , *dist[1]);
    }

    for (i = 0;i < 2;i++) {
      delete dist[i];
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
  }

  if (cdist) {
    STAT_model* model = new STAT_model(cdist);
    return AMObj(AMObjType::COMPOUND , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Compound");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une loi empirique a partir d'un objet de type
 *  ARRAY(INT) ou a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_FrequencyDistribution(const AMObjVector &args)

{
  DiscreteDistributionData *histo;


  CHECKCONDVA(args.length() == 1 ,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "FrequencyDistribution"));

  switch (args[0].tag()) {

  case AMObjType::ARRAY : {
    bool status = true;
    register int i;
    int nb_element , *element;
    Array* parray = (Array*)args[0].val.p;


    CHECKCONDVA(parray->entries() > 0 ,
                genAMLError(ERRORMSG(EMPTY_ARRAY_s) , "FrequencyDistribution"));

    CHECKCONDVA(parray->surfaceType() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_sss) , "FrequencyDistribution" ,
                            (parray->surfaceType()).string().data() , "INT"));

    nb_element = parray->entries();
    element = new int[nb_element];

    ArrayIter* pnext = parray->iterator();
    ArrayIter& next = *pnext;

    i = 0;

    while (next()) {
      if ((next.key()).tag() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_2_sdss) , "FrequencyDistribution" , i + 1 ,
                    (next.key()).tag.string().data() , "INT");
      }

      else {
        if ((next.key()).val.i < 0) {
          status = false;
          genAMLError(ERRORMSG(ARRAY_ELEMENT_VALUE_sd) , "FrequencyDistribution" , i + 1);
        }
        else {
          element[i] = (next.key()).val.i;
        }
      }

      i++;
    }

    delete pnext;

    if (status) {
      histo = new DiscreteDistributionData(nb_element , element);
    }
    delete [] element;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    STAT_model* model = new STAT_model(histo);
    return AMObj(AMObjType::FREQUENCY_DISTRIBUTION , model);
  }

  case AMObjType::STRING : {
    StatError error;


    histo = frequency_distribution_ascii_read(error , ((AMString*)args[0].val.p)->data());

    if (histo) {
      STAT_model* model = new STAT_model(histo);
      return AMObj(AMObjType::FREQUENCY_DISTRIBUTION , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "FrequencyDistribution");
      return AMObj(AMObjType::ERROR);
    }
  }

  default : {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "FrequencyDistribution" ,
                args[0].tag.string().data() , "ARRAY or STRING");
    return AMObj(AMObjType::ERROR);
  }
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une loi empirique a partir d'un objet de type
 *  ARRAY(INT) ou a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Histogram(const AMObjVector &args)

{
  return STAT_FrequencyDistribution(args);
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un melange multivarie a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Mixture(const AMObjVector &args)

{
  RWCString *pstr;
  Mixture *mixt;
  StatError error;


  CHECKCONDVA(args.length() == 1 ,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "Mixture"));

  if (args[0].tag() != AMObjType::STRING) {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Mixture" , 1 ,
                args[0].tag.string().data() , "STRING");
    return AMObj(AMObjType::ERROR);
  }

  mixt = mixture_ascii_read(error , ((AMString*)args[0].val.p)->data());

  if (mixt) {
    STAT_model* model = new STAT_model(mixt);
    return AMObj(AMObjType::MIXTURE , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Mixture");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un tableau d'entiers a partir d'une objet de type ARRAY(INT).
 *
 *--------------------------------------------------------------*/

int* buildIntArray(const AMObjVector &args , int arg_index , const char *function ,
                   int output_index , int &nb_element)

{
  bool status = true;
  register int i;
  int *element = NULL;


  Array* parray = (Array*)args[arg_index].val.p;

  if (parray->surfaceType() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , function , output_index ,
                (parray->surfaceType()).string().data() , "INT");
  }

  else {
    if (nb_element == I_DEFAULT) {
      nb_element = parray->entries();
    }
    else if (parray->entries() != nb_element) {
      status = false;
      genAMLError(ERRORMSG(ARRAY_SIZE_sdd) , function , output_index , nb_element);
    }

    if (status) {
      element = new int[nb_element];

      ArrayIter* pnext = parray->iterator();
      ArrayIter& next = *pnext;

      i = 0;
      while (next()) {
        if ((next.key()).tag() != AMObjType::INTEGER) {
          status = false;
          genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_sddss) , function , output_index ,
                      i + 1 , (next.key()).tag.string().data() , "INT");
        }
        else {
          element[i] = (next.key()).val.i;
        }

        i++;
      }

      delete pnext;

      if (!status) {
        delete [] element;
        element = NULL;
      }
    }
  }

  return element;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un tableau de reels a partir d'une objet de type ARRAY(REAL).
 *
 *--------------------------------------------------------------*/

double* buildRealArray(const AMObjVector &args , int arg_index , const char *function ,
                       int output_index , int &nb_element , bool filter)

{
  register int i;
  bool status = true;
  double *element = NULL;


  Array* parray = (Array*)args[arg_index].val.p;

  switch (filter) {

  case false : {
    nb_element = parray->entries();
    element = new double[nb_element];
    break;
  }

  // allocation du filtre complet alors que seules les valeurs correspondant
  // a la demi-largeur + valeur centrale sont lues

  case true : {
    nb_element = parray->entries() - 1;
    element = new double[2 * nb_element + 1];
    break;
  }
  }

  ArrayIter* pnext = parray->iterator();
  ArrayIter& next = *pnext;

  i = 0;
  while (next()) {
    if ((next.key()).tag() != AMObjType::REAL) {
      status = false;
      genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_sddss) , function , output_index ,
                  i + 1 , (next.key()).tag.string().data() , "REAL");
    }
    else {
      element[i] = (next.key()).val.r;
    }

    i++;
  }

  delete pnext;

  if (!status) {
    delete [] element;
    element = NULL;
  }

  return element;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un ensemble de vecteurs a partir d'un objet
 *  de type ARRAY(ARRAY(INT/REAL)), a partir d'un ensemble de sequences ou
 *  a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Vectors(const AMObjVector &args)

{
  Vectors *vec;


  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Vectors"));

  if (args[0].tag() == AMObjType::ARRAY) {
    bool status = true;
    register int i , j;
    int nb_required , nb_variable = 0 , dim , nb_vector , type , *identifier = NULL ,
        **int_vector = NULL;
    double **real_vector = NULL;
    const Array* parray = (Array*)args[0].val.p , *pvector;
    StatError error;


    nb_required = 1;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Vectors"));

    CHECKCONDVA(parray->surfaceType() == AMObjType::ARRAY ,
                genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , "Vectors" , 1 ,
                            (parray->surfaceType()).string().data() , "ARRAY"));

    nb_vector = parray->entries();

    // argument obligatoire

    ArrayIter* pnext = parray->iterator();
    ArrayIter& next = *pnext;

    i = 0;

    while (next()) {
      if ((next.key()).tag() != AMObjType::ARRAY) {
        status = false;
        genAMLError(ERRORMSG(VECTOR_ARRAY_ELEMENT_TYPE_sdss) , "Vectors" , i + 1 ,
                    (next.key()).tag.string().data() , "ARRAY");
      }

      else {
        pvector = (Array*)(next.key()).val.p;
        dim = pvector->entries();

        if ((nb_variable > 0) && (dim != nb_variable)) {
          status = false;
          genAMLError(ERRORMSG(VECTOR_ARRAY_SIZE_sdd) , "Vectors" , i + 1 ,
                      nb_variable);
        }

        if (pvector->surfaceType() == AMObjType::INTEGER) {
          if (nb_variable == 0) {
            type = INT_VALUE;

            nb_variable = dim;
            int_vector = new int*[nb_vector];
            for (j = 0;j < nb_vector;j++) {
              int_vector[j] = new int[nb_variable];
            }
          }

          if ((type == INT_VALUE) && (dim == nb_variable)) {
            ArrayIter* pvector_next = pvector->iterator();
            ArrayIter& vector_next = *pvector_next;

            j = 0;

            while (vector_next()) {
              if ((vector_next.key()).tag() != AMObjType::INTEGER) {
                status = false;
                genAMLError(ERRORMSG(VECTOR_ARRAY_ELEMENT_TYPE_sddss) , "Vectors" , i + 1 ,
                            j + 1 , (vector_next.key()).tag.string().data() , "INT");
              }
              else {
                int_vector[i][j] = (vector_next.key()).val.i;
              }

              j++;
            }

            delete pvector_next;
          }

          if (type != INT_VALUE) {
            status = false;
            genAMLError(ERRORMSG(VECTOR_ARRAY_ELEMENT_TYPE_sdss) , "Vectors" , i + 1 ,
                        (pvector->surfaceType()).string().data() , "INT");
          }
        }

        else if (pvector->surfaceType() == AMObjType::REAL) {
          if (nb_variable == 0) {
            type = REAL_VALUE;

            nb_variable = dim;
            real_vector = new double*[nb_vector];
            for (j = 0;j < nb_vector;j++) {
              real_vector[j] = new double[nb_variable];
            }
          }

          if ((type == REAL_VALUE) && (dim == nb_variable)) {
            ArrayIter* pvector_next = pvector->iterator();
            ArrayIter& vector_next = *pvector_next;

            j = 0;

            while (vector_next()) {
              if ((vector_next.key()).tag() != AMObjType::REAL) {
                status = false;
                genAMLError(ERRORMSG(VECTOR_ARRAY_ELEMENT_TYPE_sddss) , "Vectors" , i + 1 ,
                            j + 1 , (vector_next.key()).tag.string().data() , "REAL");
              }
              else {
                real_vector[i][j] = (vector_next.key()).val.r;
              }

              j++;
            }

            delete pvector_next;
          }

          if (type != REAL_VALUE) {
            status = false;
            genAMLError(ERRORMSG(VECTOR_ARRAY_ELEMENT_TYPE_sdss) , "Vectors" , i + 1 ,
                        (pvector->surfaceType()).string().data() , "REAL");
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(VECTOR_ARRAY_ELEMENT_TYPE_sdss) , "Vectors" , i + 1 ,
                      (pvector->surfaceType()).string().data() , "INT or REAL");
        }
      }

      i++;
    }

    delete pnext;

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Vectors" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "Identifiers") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Vectors" , nb_required + 1 ,
                      "Identifiers");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::ARRAY) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Vectors" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "ARRAY");
      }
      else {
        identifier = buildIntArray(args , nb_required + 1 , "Vectors" ,
                                   nb_required + 1 , nb_vector);
        if (!identifier) {
          status = false;
        }
        else {
          for (i = 0;i < nb_vector;i++) {
            if (identifier[i] <= 0) {
              status = false;
              genAMLError(ERRORMSG(ARRAY_ELEMENT_VALUE_sdd) , "Vectors" ,
                          nb_required + 1 , i + 1);
            }
          }
        }
      }
    }

    if (status) {
      if (type == INT_VALUE) {
        vec = new Vectors(nb_vector , identifier , nb_variable , int_vector);
      }
      else {
        vec = new Vectors(nb_vector , identifier , nb_variable , real_vector);
      }

      status = vec->check(error);

      if (!status) {
        delete vec;
        AMLOUTPUT << "\n" << error;
        genAMLError(ERRORMSG(STAT_MODULE_s) , "Vectors");
      }
    }

    delete [] identifier;

    if (int_vector) {
      for (i = 0;i < nb_vector;i++) {
        delete [] int_vector[i];
      }
      delete [] int_vector;
    }

    if (real_vector) {
      for (i = 0;i < nb_vector;i++) {
        delete [] real_vector[i];
      }
      delete [] real_vector;
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    STAT_model* model = new STAT_model(vec);
    return AMObj(AMObjType::VECTORS , model);
  }

  if ((args[0].tag() == AMObjType::SEQUENCES) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
      (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA) || (args[0].tag() == AMObjType::TOPS)) {
    bool status = true , index_variable = false;
    int nb_required;
    Sequences *seq;


    nb_required = 1;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Vectors"));

    // argument obligatoire

    switch (args[0].tag()) {
    case AMObjType::SEQUENCES :
      seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::MARKOVIAN_SEQUENCES :
      seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
      seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::SEMI_MARKOV_DATA :
      seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
      seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::TOPS :
      seq = (Tops*)((STAT_model*)args[0].val.p)->pt;
      break;
    }

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Vectors" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "IndexVariable") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Vectors" , nb_required + 1 ,
                      "IndexVariable");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::BOOL) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Vectors" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "BOOL");
      }
      else {
        index_variable = args[nb_required + 1].val.b;
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
    }

    vec = seq->build_vectors(index_variable);

    STAT_model* model = new STAT_model(vec);
    return AMObj(AMObjType::VECTORS , model);
  }

  if (args[0].tag() == AMObjType::STRING) {
    StatError error;


    CHECKCONDVA(args.length() == 1 ,
                genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "Vectors"));

    vec = vectors_ascii_read(error , ((AMString*)args[0].val.p)->data());

    if (vec) {
      STAT_model* model = new STAT_model(vec);
      return AMObj(AMObjType::VECTORS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Vectors");
      return AMObj(AMObjType::ERROR);
    }
  }

  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "Vectors" , args[0].tag.string().data() ,
              "ARRAY or SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA or TOPS or STRING");
  return AMObj(AMObjType::ERROR);
}


/*--------------------------------------------------------------*
 *
 *  Construction des parametres de definition d'une distance entre vecteurs
 *  a partir d'un fichier ou a partir des types des variables donnes un par un.
 *
 *--------------------------------------------------------------*/

AMObj STAT_VectorDistance(const AMObjVector &args)

{
  RWCString *pstr;
  bool status;
  register int i , j;
  int nb_required , scale , nb_variable , distance_type = ABSOLUTE_VALUE ,
      variable_type[VECTOR_NB_VARIABLE];
  double *weight;
  VectorDistance *vector_dist;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "VectorDistance"));

  // arguments obligatoires

  if (args[0].tag() == AMObjType::STRING) {
    pstr = (AMString*)args[0].val.p;
    for (i = SYMBOLIC;i <= NUMERIC;i++) {
      if ((*pstr == STAT_variable_type_word[i]) || (*pstr == STAT_variable_type_letter[i])) {
        break;
      }
    }

    if (i == NUMERIC + 1) {
      CHECKCONDVA(args.length() == 1 ,
                  genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "VectorDistance"));

      vector_dist = vector_distance_ascii_read(error , ((AMString*)args[0].val.p)->data());

      if (vector_dist) {
        STAT_model* model = new STAT_model(vector_dist);
        return AMObj(AMObjType::VECTOR_DISTANCE , model);
      }
      else {
        AMLOUTPUT << "\n" << error;
        genAMLError(ERRORMSG(STAT_MODULE_s) , "VectorDistance");
        return AMObj(AMObjType::ERROR);
      }
    }

    scale = 1;
  }

  else if (args[0].tag() == AMObjType::REAL) {
    CHECKCONDVA(nb_required % 2 == 0 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "VectorDistance"));
    scale = 2;
  }

  else {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VectorDistance" , 1 ,
                args[0].tag.string().data() , "STRING or REAL");
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = nb_required / scale;

  CHECKCONDVA((nb_variable >= 1) && (nb_variable <= VECTOR_NB_VARIABLE) ,
              genAMLError(ERRORMSG(NB_VARIABLE_1_sd) , "VectorDistance" , VECTOR_NB_VARIABLE));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "VectorDistance"));

  switch (scale) {
  case 1 :
    weight = NULL;
    break;
  case 2 :
    weight = new double[nb_variable];
    break;
  }

  status = true;

  for (i = 0;i < nb_variable;i++) {
    if (weight) {
      if (args[i * scale].tag() != AMObjType::REAL) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VectorDistance" , i * scale + 1 ,
                    args[i * scale].tag.string().data() , "REAL");
      }
      else {
        weight[i] = args[i * scale].val.r;
      }
    }

    if (args[(i + 1) * scale - 1].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VectorDistance" , (i + 1) * scale ,
                  args[(i + 1) * scale - 1].tag.string().data() , "STRING");
    }

    else {
      pstr = (AMString*)args[(i + 1) * scale - 1].val.p;
      for (j = SYMBOLIC;j <= NUMERIC;j++) {
        if ((*pstr == STAT_variable_type_word[j]) || (*pstr == STAT_variable_type_letter[j])) {
          variable_type[i] = j;
          break;
        }
      }

      if (j == NUMERIC + 1) {
        status = false;
        genAMLError(ERRORMSG(VARIABLE_TYPE_sds) , "VectorDistance" , (i + 1) * scale ,
                    "SYMBOLIC(S) or ORDINAL(O) or NUMERIC(N)");
      }
    }
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VectorDistance" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Distance") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "VectorDistance" , nb_required + 1 ,
                    "Distance");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VectorDistance" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "STRING");
    }
    else {
      pstr = (AMString*)args[nb_required + 1].val.p;
      for (j = ABSOLUTE_VALUE;j <= QUADRATIC;j++) {
        if (*pstr == STAT_distance_word[j]) {
          distance_type = j;
          break;
        }
      }

      if (j == QUADRATIC + 1) {
        status = false;
        genAMLError(ERRORMSG(VARIABLE_TYPE_sds) , "VectorDistance" , nb_required + 1 ,
                    "ABSOLUTE_VALUE or QUADRATIC");
      }
    }
  }

  if (!status) {
    delete [] weight;
    return AMObj(AMObjType::ERROR);
  }

  vector_dist = new VectorDistance(nb_variable , variable_type , weight , distance_type);
  delete [] weight;

  STAT_model* model = new STAT_model(vector_dist);
  return AMObj(AMObjType::VECTOR_DISTANCE , model);
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un processus de renouvellement a partir d'un fichier,
 *  a partir de l'identificateur et des parametres de la loi inter-evenement ou
 *  a partir de la loi inter-evenement.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Renewal(const AMObjVector &args)

{
  RWCString *pstr;
  char type = 'e';
  bool status = true , type_option = false , time_option = false , scale_option = false;
  register int i;
  int nb_required , time = DEFAULT_TIME , ident , inf_bound , sup_bound;
  double parameter , probability , scaling_coeff;
  const DiscreteParametric *inter_event , *scaled_inter_event;
  Renewal *renew;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Renewal"));

  inter_event = NULL;

  // arguments obligatoires

  if (args[0].tag() == AMObjType::STRING) {
    if (nb_required > 1) {
      pstr = (AMString*)args[0].val.p;
      for (i = BINOMIAL;i <= NEGATIVE_BINOMIAL;i++) {
        if ((*pstr == STAT_discrete_distribution_word[i]) ||
            (*pstr == STAT_discrete_distribution_letter[i])) {
          ident = i;
          break;
        }
      }

      if (i == NEGATIVE_BINOMIAL + 1) {
        status = false;
        genAMLError(ERRORMSG(DISTRIBUTION_NAME_sds) , "Renewal" , 1 ,
                    "BINOMIAL(B) or POISSON(P) or NEGATIVE_BINOMIAL(NB)");
      }

      else {
        if ((ident == BINOMIAL) || (ident == NEGATIVE_BINOMIAL)) {
          if (nb_required != 4) {
            status = false;
            genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Renewal");
          }
        }
        else if (ident == POISSON) {
          if (nb_required != 3) {
            status = false;
            genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Renewal");
          }
        }
      }

      if (status) {
        status = parameter_input(args , ident , inf_bound , sup_bound , parameter ,
                                 probability , "Renewal" , 1);
      }
    }
  }

  else {
    if (nb_required != 1) {
      status = false;
      genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Renewal");
    }

    switch (args[0].tag()) {
    case AMObjType::DISTRIBUTION :
      inter_event = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt)));
      break;
    case AMObjType::DISCRETE_MIXTURE :
      inter_event = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt)));
      break;
    case AMObjType::CONVOLUTION :
      inter_event = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[0].val.p)->pt)));
      break;
    case AMObjType::COMPOUND :
      inter_event = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[0].val.p)->pt)));
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Renewal" , 1 , args[0].tag.string().data() ,
                  "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
      break;
    }

    if (inter_event->offset == 0) {
      status = false;
      genAMLError(ERRORMSG(INTER_EVENT_DISTRIBUTION_LOWER_BOUND_sd) , "Renewal" , 1);
    }
  }

  if ((args.length() != nb_required) && (args.length() != nb_required + 2) &&
      (args.length() != nb_required + 4) && (args.length() != nb_required + 6)) {
    delete inter_event;
    genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Renewal");
    return AMObj(AMObjType::ERROR);
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Renewal" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Type") {
        switch (type_option) {

        case false : {
          type_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Renewal" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }

          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Ordinary") {
              type = 'o';
            }
            else if (*pstr == "Equilibrium") {
              type = 'e';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(STOCHASTIC_PROCESS_TYPE_sds) , "Renewal" ,
                          nb_required + i + 1 , "Ordinary or Equilibrium");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Renewal" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "ObservationTime") {
        switch (time_option) {

        case false : {
          time_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Renewal" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }

          else {
            time = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Renewal" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Scale") {
        switch (scale_option) {

        case false : {
          scale_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::INTEGER :
            scaling_coeff = args[nb_required + i * 2 + 1].val.i;
            break;
          case AMObjType::REAL :
            scaling_coeff = args[nb_required + i * 2 + 1].val.r;
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Renewal" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
            break;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Renewal" , nb_required + i + 1);
          break;
         }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Renewal" ,
                    nb_required + i + 1 , "Type or ObservationTime or Scale");
      }
    }
  }

  if (!status) {
    delete inter_event;
    return AMObj(AMObjType::ERROR);
  }

  if (args[0].tag() == AMObjType::STRING) {
    if (nb_required == 1) {
      renew = renewal_ascii_read(error , ((AMString*)args[0].val.p)->data() , type , time);
    }

    else {
      inter_event = new DiscreteParametric(ident , inf_bound , sup_bound , parameter ,
                                           probability , RENEWAL_THRESHOLD);

      if (scale_option) {
        // scaled_inter_event = new DiscreteParametric(*inter_event , scaling_coeff);
        scaled_inter_event = new DiscreteParametric((Distribution&)*inter_event , scaling_coeff);
        renew = renewal_building(error , *scaled_inter_event , type , time);
        delete scaled_inter_event;
      }

      else {
        renew = renewal_building(error , *inter_event , type , time);
      }
      delete inter_event;
    }
  }

  else {
    renew = renewal_building(error , *inter_event , type , time);
    delete inter_event;
  }

  if (renew) {
    STAT_model* model = new STAT_model(renew);
    return AMObj(AMObjType::RENEWAL , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Renewal");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une structure de donnees renouvellement a partir
 *  d'un ensemble de sequences, d'une loi empirique ou d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_TimeEvents(const AMObjVector &args)

{
  TimeEvents *timev;
  StatError error;


  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TimeEvents"));

  if ((args[0].tag() == AMObjType::SEQUENCES) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
      (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) {
    RWCString *pstr;
    bool status = true , previous_date_option = false , next_date_option = false;
    register int i;
    int nb_required , nb_variable , variable , offset , begin_date , end_date ,
        previous_date = I_DEFAULT , next_date = I_DEFAULT;
    Sequences *seq;


    switch (args[0].tag()) {
    case AMObjType::SEQUENCES :
      seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::MARKOVIAN_SEQUENCES :
      seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
      seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::SEMI_MARKOV_DATA :
      seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
      seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
      break;
    }

    nb_variable = seq->get_nb_variable();
    offset = (nb_variable == 1 ? 1 : 2);

    nb_required = nb_required_computation(args);

    CHECKCONDVA(nb_required == offset + 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TimeEvents"));

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TimeEvents"));

    // arguments obligatoires

    if (nb_variable == 1) {
      variable = 1;
    }

    else {
      if (args[1].tag() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , 2 ,
                    args[1].tag.string().data() , "INT");
      }
      else {
        variable = args[1].val.i;
      }
    }

    if (args[offset].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , offset + 1 ,
                  args[offset].tag.string().data() , "INT");
    }
    else {
      begin_date = args[offset].val.i;
    }

    if (args[offset + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , offset + 2 ,
                  args[offset + 1].tag.string().data() , "INT");
    }
    else {
      end_date = args[offset + 1].val.i;
    }

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "PreviousDate") {
          switch (previous_date_option) {

          case false : {
            previous_date_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              previous_date = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "TimeEvents" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "NextDate") {
          switch (next_date_option) {

          case false : {
            next_date_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              next_date = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "TimeEvents" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "TimeEvents" ,
                      nb_required + i + 1 , "PreviousDate or NextDate");
        }
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    timev = seq->extract_time_events(error , variable , begin_date , end_date ,
                                     previous_date , next_date);

    if (timev) {
      STAT_model* model = new STAT_model(timev);
      return AMObj(AMObjType::TIME_EVENTS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "TimeEvents");
      return AMObj(AMObjType::ERROR);
    }
  }

  if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
      (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
    FrequencyDistribution *histo;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "TimeEvents" , 2));

    switch (args[0].tag()) {
    case AMObjType::FREQUENCY_DISTRIBUTION :
      histo = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
      break;
    case AMObjType::DISCRETE_MIXTURE_DATA :
      histo = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
      break;
    case AMObjType::CONVOLUTION_DATA :
      histo = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
      break;
    case AMObjType::COMPOUND_DATA :
      histo = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
      break;
    }

    CHECKCONDVA(args[1].tag() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , 2 ,
                            args[1].tag.string().data() , "INT"));

    timev = histo->build_time_events(error , args[1].val.i);

    if (timev) {
      STAT_model* model = new STAT_model(timev);
      return AMObj(AMObjType::TIME_EVENTS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "TimeEvents");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::STRING) {
    CHECKCONDVA(args.length() == 1 ,
                genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "TimeEvents"));

    timev = time_events_ascii_read(error , ((AMString*)args[0].val.p)->data());

    if (timev) {
      STAT_model* model = new STAT_model(timev);
      return AMObj(AMObjType::TIME_EVENTS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "TimeEvents");
      return AMObj(AMObjType::ERROR);
    }
  }

  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TimeEvents" , 1 , args[0].tag.string().data() ,
              "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA or FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA or STRING");
  return AMObj(AMObjType::ERROR);
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une structure de donnees renouvellement a partir
 *  d'un ensemble de sequences.
 *
 *--------------------------------------------------------------*/

AMObj STAT_RenewalData(const AMObjVector &args)

{
  bool status = true;
  int nb_variable , variable , offset , begin_index , end_index;
  const Sequences *seq;
  TimeEvents *timev;
  StatError error;


  CHECKCONDVA(args.length() >= 3 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "RenewalData"));

  switch (args[0].tag()) {
  case AMObjType::SEQUENCES :
    seq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::MARKOVIAN_SEQUENCES :
    seq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
    seq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::SEMI_MARKOV_DATA :
    seq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
    seq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  default :
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "RenewalData" , 1 , args[0].tag.string().data() ,
                "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = seq->get_nb_variable();
  offset = (nb_variable == 1 ? 1 : 2);

  CHECKCONDVA(args.length() == offset + 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "RenewalData" , offset + 2));

  if (nb_variable == 1) {
    variable = 1;
  }

  else {
    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "RenewalData" , 2 ,
                  args[1].tag.string().data() , "INT");
    }
    else {
      variable = args[1].val.i;
    }
  }

  if (args[offset].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "RenewalData" , offset + 1 ,
                args[offset].tag.string().data() , "INT");
  }
  else {
    begin_index = args[offset].val.i;
  }

  if (args[offset + 1].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "RenewalData" , offset + 2 ,
                args[offset + 1].tag.string().data() , "INT");
  }
  else {
    end_index = args[offset + 1].val.i;
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  timev = seq->extract_renewal_data(error , variable , begin_index , end_index);

  if (timev) {
    STAT_model* model = new STAT_model(timev);
    return AMObj(AMObjType::RENEWAL_DATA , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "TimeEvents");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une chaine de Markov d'ordre variable a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_VariableOrderMarkov(const AMObjVector &args)

{
  bool status = true;
  int nb_required , length = DEFAULT_LENGTH;
  VariableOrderMarkov *markov;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "VariableOrderMarkov"));

  // argument obligatoire

  if (args[0].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VariableOrderMarkov" , 1 ,
                args[0].tag.string().data() , "STRING");
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VariableOrderMarkov" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Length") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "VariableOrderMarkov" , nb_required + 1 ,
                    "Length");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VariableOrderMarkov" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "INT");
    }
    else {
      length = args[nb_required + 1].val.i;
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  markov = variable_order_markov_ascii_read(error , ((AMString*)args[0].val.p)->data() , length);

  if (markov) {
    STAT_model* model = new STAT_model(markov);
    return AMObj(AMObjType::VARIABLE_ORDER_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "VariableOrderMarkov");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une chaine de Markov d'ordre variable cachee a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_HiddenVariableOrderMarkov(const AMObjVector &args)

{
  bool status = true;
  int nb_required , length = DEFAULT_LENGTH;
  HiddenVariableOrderMarkov *hmarkov;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "HiddenVariableOrderMarkov"));

  // argument obligatoire

  if (args[0].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenVariableOrderMarkov" , 1 ,
                args[0].tag.string().data() , "STRING");
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenVariableOrderMarkov" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Length") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "HiddenVariableOrderMarkov" , nb_required + 1 ,
                    "Length");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenVariableOrderMarkov" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "INT");
    }
    else {
      length = args[nb_required + 1].val.i;
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  hmarkov = hidden_variable_order_markov_ascii_read(error , ((AMString*)args[0].val.p)->data() , length);

  if (hmarkov) {
    STAT_model* model = new STAT_model(hmarkov);
    return AMObj(AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "HiddenVariableOrderMarkov");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une semi-chaine de Markov a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_SemiMarkov(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , length_option = false , counting_option = false , counting_flag = true;
  register int i;
  int nb_required , length = DEFAULT_LENGTH;
  SemiMarkov *smarkov;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "SemiMarkov"));

  // argument obligatoire

  if (args[0].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SemiMarkov" , 1 ,
                args[0].tag.string().data() , "STRING");
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SemiMarkov" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Length") {
        switch (length_option) {

        case false : {
          length_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SemiMarkov" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            length = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "SemiMarkov" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Counting") {
        switch (counting_option) {

        case false : {
          counting_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "SemiMarkov" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            counting_flag = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "SemiMarkov" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "SemiMarkov" ,
                    nb_required + i + 1 , "Length or Counting");
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  smarkov = semi_markov_ascii_read(error , ((AMString*)args[0].val.p)->data() ,
                                   length , counting_flag);

  if (smarkov) {
    STAT_model* model = new STAT_model(smarkov);
    return AMObj(AMObjType::SEMI_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "SemiMarkov");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une semi-chaine de Markov cachee a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_HiddenSemiMarkov(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , length_option = false , counting_option = false ,
       counting_flag = true , format_option = false , old_format = false;
  register int i;
  int nb_required , length = DEFAULT_LENGTH;
  HiddenSemiMarkov *hsmarkov;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "HiddenSemiMarkov"));

  // argument obligatoire

  if (args[0].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenSemiMarkov" , 1 ,
                args[0].tag.string().data() , "STRING");
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenSemiMarkov" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Length") {
        switch (length_option) {

        case false : {
          length_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenSemiMarkov" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            length = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "HiddenSemiMarkov" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Counting") {
        switch (counting_option) {

        case false : {
          counting_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenSemiMarkov" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            counting_flag = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "HiddenSemiMarkov" , nb_required + i + 1);
          break;
        }
        }
      }


      else if (*pstr == "Format") {
        switch (format_option) {

        case false : {
          format_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "HiddenSemiMarkov" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "Current") {
              old_format = false;
            }
            else if (*pstr == "Old") {
              old_format = true;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "HiddenSemiMarkov" ,
                          nb_required + i + 1 , "Current or Old");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "HiddenSemiMarkov" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "HiddenSemiMarkov" ,
                    nb_required + i + 1 , "Length or Counting or Format");
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  hsmarkov = hidden_semi_markov_ascii_read(error , ((AMString*)args[0].val.p)->data() ,
                                           length , counting_flag , OCCUPANCY_THRESHOLD ,
                                           old_format);

  if (hsmarkov) {
    STAT_model* model = new STAT_model(hsmarkov);
    return AMObj(AMObjType::HIDDEN_SEMI_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "HiddenSemiMarkov");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une chaine de Markov non-homogene a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_NonhomogeneousMarkov(const AMObjVector &args)

{
  bool status = true;
  int nb_required , length = DEFAULT_LENGTH;
  NonhomogeneousMarkov *markov;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "NonhomogeneousMarkov"));

  // argument obligatoire

  if (args[0].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "NonhomogeneousMarkov" , 1 ,
                args[0].tag.string().data() , "STRING");
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "NonhomogeneousMarkov" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Length") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "NonhomogeneousMarkov" , nb_required + 1 ,
                    "Length");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "NonhomogeneousMarkov" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "INT");
    }
    else {
      length = args[nb_required + 1].val.i;
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  markov = nonhomogeneous_markov_ascii_read(error , ((AMString*)args[0].val.p)->data() , length);

  if (markov) {
    STAT_model* model = new STAT_model(markov);
    return AMObj(AMObjType::NONHOMOGENEOUS_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "NonhomogeneousMarkov");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une sequence entiere a partir d'un objet de type ARRAY(INT).
 *
 *--------------------------------------------------------------*/

static int** buildIntSequence(const Array *parray , int &length ,
                              int &nb_variable , int seq_index)

{
  bool status;
  register int i;
  int **int_sequence = NULL;


  if (nb_variable == 0) {
    nb_variable = 1;
  }

  length = parray->entries();

  int_sequence = new int*[nb_variable];
  int_sequence[0] = new int[length];

  ArrayIter* pnext = parray->iterator();
  ArrayIter& next = *pnext;

  status = true;
  i = 0;

  while (next()) {
    if ((next.key()).tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , "Sequences" ,
                  seq_index + 1 , i + 1 , (next.key()).tag.string().data() , "INT");
    }
    else {
      int_sequence[0][i] = (next.key()).val.i;
    }

    i++;
  }

  delete pnext;

  if (!status) {
    delete [] int_sequence[0];
    delete [] int_sequence;

    int_sequence = NULL;
  }

  return int_sequence;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une sequence reelle a partir d'un objet de type ARRAY(REAL).
 *
 *--------------------------------------------------------------*/

static double** buildRealSequence(const Array *parray , int &length ,
                                  int &nb_variable , int seq_index)

{
  bool status;
  register int i;
  double **real_sequence = NULL;


  if (nb_variable == 0) {
    nb_variable = 1;
  }

  length = parray->entries();

  real_sequence = new double*[nb_variable];
  real_sequence[0] = new double[length];

  ArrayIter* pnext = parray->iterator();
  ArrayIter& next = *pnext;

  status = true;
  i = 0;

  while (next()) {
    if ((next.key()).tag() != AMObjType::REAL) {
      status = false;
      genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , "Sequences" ,
                  seq_index + 1 , i + 1 , (next.key()).tag.string().data() , "REAL");
    }
    else {
      real_sequence[0][i] = (next.key()).val.r;
    }

    i++;
  }

  delete pnext;

  if (!status) {
    delete [] real_sequence[0];
    delete [] real_sequence;

    real_sequence = NULL;
  }

  return real_sequence;
}


/*--------------------------------------------------------------*
 *
 *  Determination du type d'une sequence multivariee.
 *
 *--------------------------------------------------------------*/

static int type_determination(const Array *parray , const char *pattern_label)

{
  int type = IMPLICIT_TYPE;
  const Array *pvector;


  ArrayIter* pnext = parray->iterator();
  ArrayIter& next = *pnext;

  next();
 
  if ((next.key()).tag() == AMObjType::ARRAY) {
    pvector = (Array*)(next.key()).val.p;

    if (pvector->surfaceType() == AMObjType::INTEGER) {
      type = INT_VALUE;
    }
    else if (pvector->surfaceType() == AMObjType::REAL) {
      type = REAL_VALUE;
    }
    else {
      genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , pattern_label , 1 ,
                  1 , (pvector->surfaceType()).string().data() , "INT or REAL");
    }
  }

  return type;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une sequence multivariee entiere a partir d'un objet de type ARRAY(ARRAY(INT)).
 *
 *--------------------------------------------------------------*/

static int** buildIntArraySequence(const Array *parray , int &length , int index_parameter_type ,
                                   int &nb_variable , int seq_index , const char *pattern_label)

{
  bool status = true;
  register int i , j;
  int dim , **int_sequence = NULL;
  const Array *pvector;


  length = parray->entries();
  if (index_parameter_type == POSITION) {
    length--;
  }

  if (nb_variable > 0) {
    int_sequence = new int*[nb_variable];
    int_sequence[0] = new int[index_parameter_type == POSITION ? length + 1 : length];
    for (i = 1;i < nb_variable;i++) {
      int_sequence[i] = new int[length];
    }
  }

  ArrayIter* pnext = parray->iterator();
  ArrayIter& next = *pnext;

  i = 0;

  while (next()) {
    if ((next.key()).tag() != AMObjType::ARRAY) {
      status = false;
      genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , pattern_label , seq_index + 1 ,
                  i + 1 , (next.key()).tag.string().data() , "ARRAY");
    }

    else {
      pvector = (Array*)(next.key()).val.p;

      if (pvector->surfaceType() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , pattern_label , seq_index + 1 ,
                    i + 1 , (pvector->surfaceType()).string().data() , "INT");
      }

      else {
        dim = pvector->entries();

        if (nb_variable == 0) {
          nb_variable = dim;

          int_sequence = new int*[nb_variable];
          int_sequence[0] = new int[index_parameter_type == POSITION ? length + 1 : length];
          for (j = 1;j < nb_variable;j++) {
            int_sequence[j] = new int[length];
          }
        }

//        if ((dim == nb_variable) || ((index_parameter_type == POSITION) &&
//             (i == length) && (dim == 1))) {
        if (dim == nb_variable) {
          ArrayIter* pvector_next = pvector->iterator();
          ArrayIter& vector_next = *pvector_next;

          j = 0;

          while (vector_next()) {
            if ((vector_next.key()).tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdddss) , pattern_label , seq_index + 1 ,
                          i + 1 , j + 1 , (vector_next.key()).tag.string().data() , "INT");
            }

            else {
              if ((j == 0) && ((index_parameter_type == POSITION) || (index_parameter_type == TIME)) &&
                  (vector_next.key()).val.i < 0) {
                status = false;
                genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_VALUE_sddd) , pattern_label ,
                            seq_index + 1 , i + 1 , j + 1);
              }
              else {
                int_sequence[j][i] = (vector_next.key()).val.i;
              }
            }

            if ((index_parameter_type == POSITION) && (i == length) && (j == 0)) {
              break;
            }

            j++;
          }

          delete pvector_next;
        }

        else {
          status = false;
          genAMLError(ERRORMSG(SEQUENCE_ARRAY_SIZE_sddd) , pattern_label , seq_index + 1 ,
                      i + 1 , nb_variable);
        }
      }
    }

    i++;
  }

  delete pnext;

  if ((!status) && (int_sequence)) {
    for (i = 0;i < nb_variable;i++) {
      delete [] int_sequence[i];
    }
    delete [] int_sequence;

    int_sequence = NULL;
  }

  return int_sequence;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'une sequence multivariee reelle a partir d'un objet de type ARRAY(ARRAY(INT)).
 *
 *--------------------------------------------------------------*/

static double** buildRealArraySequence(const Array *parray , int &length , int &nb_variable ,
                                       int seq_index , const char *pattern_label)

{
  bool status = true;
  register int i , j;
  int dim;
  double **real_sequence = NULL;
  const Array *pvector;


  length = parray->entries();

  if (nb_variable > 0) {
    real_sequence = new double*[nb_variable];
    for (i = 0;i < nb_variable;i++) {
      real_sequence[i] = new double[length];
    }
  }

  ArrayIter* pnext = parray->iterator();
  ArrayIter& next = *pnext;

  i = 0;

  while (next()) {
    if ((next.key()).tag() != AMObjType::ARRAY) {
      status = false;
      genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , pattern_label , seq_index + 1 ,
                  i + 1 , (next.key()).tag.string().data() , "ARRAY");
    }

    else {
      pvector = (Array*)(next.key()).val.p;

      if (pvector->surfaceType() != AMObjType::REAL) {
        status = false;
        genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sddss) , pattern_label , seq_index + 1 ,
                    i + 1 , (pvector->surfaceType()).string().data() , "REAL");
      }

      else {
        dim = pvector->entries();

        if (nb_variable == 0) {
          nb_variable = dim;

          real_sequence = new double*[nb_variable];
          for (j = 0;j < nb_variable;j++) {
            real_sequence[j] = new double[length];
          }
        }

        if (dim == nb_variable) {
          ArrayIter* pvector_next = pvector->iterator();
          ArrayIter& vector_next = *pvector_next;

          j = 0;

          while (vector_next()) {
            if ((vector_next.key()).tag() != AMObjType::REAL) {
              status = false;
              genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdddss) , pattern_label , seq_index + 1 ,
                          i + 1 , j + 1 , (vector_next.key()).tag.string().data() , "REAL");
            }
            else {
              real_sequence[j][i] = (vector_next.key()).val.r;
            }

            j++;
          }

          delete pvector_next;
        }

        else {
          status = false;
          genAMLError(ERRORMSG(SEQUENCE_ARRAY_SIZE_sddd) , pattern_label , seq_index + 1 ,
                      i + 1 , nb_variable);
        }
      }
    }

    i++;
  }

  delete pnext;

  if ((!status) && (real_sequence)) {
    for (i = 0;i < nb_variable;i++) {
      delete [] real_sequence[i];
    }
    delete [] real_sequence;

    real_sequence = NULL;
  }

  return real_sequence;
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un ensemble de sequences a partir d'un objet
 *  de type ARRAY(ARRAY(INT/REAL)), ARRAY(ARRAY(ARRAY(INT/REAL))) ou RENEWAL_DATA ou
 *  a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Sequences(const AMObjVector &args)

{
  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Sequences"));

  // argument obligatoire

  switch (args[0].tag()) {

  case AMObjType::ARRAY : {
    RWCString *pstr;
    bool status = true , index_parameter_option = false , identifier_option = false;
    register int i , j;
    int nb_required , nb_sequence , index_parameter_type = IMPLICIT_TYPE , *identifier = NULL;


    nb_required = 1;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Sequences"));

    nb_sequence = ((Array*)args[0].val.p)->entries();

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Sequences" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Identifiers") {
          switch (identifier_option) {

          case false : {
            identifier_option = true;

            if (args[nb_required + 1].tag() != AMObjType::ARRAY) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Sequences" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "ARRAY");
            }
            else {
              identifier = buildIntArray(args , nb_required + i * 2 + 1 , "Sequences" ,
                                         nb_required + i + 1 , nb_sequence);
              if (!identifier) {
                status = false;
              }
              else {
                for (j = 0;j < nb_sequence;j++) {
                  if (identifier[j] <= 0) {
                    status = false;
                    genAMLError(ERRORMSG(ARRAY_ELEMENT_VALUE_sdd) , "Sequences" ,
                                nb_required + i + 1 , j + 1);
                  }
                }
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Sequences" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "IndexParameter") {
          switch (index_parameter_option) {

          case false : {
            index_parameter_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Sequences" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "Position") {
                index_parameter_type = POSITION;
              }
              else if (*pstr == "Time") {
                index_parameter_type = TIME;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(VARIABLE_TYPE_sds) , "Sequences" ,
                            nb_required + i + 1 , "Position or Time");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Sequences" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Sequences" ,
                      nb_required + i + 1 , "Identifiers or IndexParameter");
        }
      }
    }

    Array* parray = (Array*)args[0].val.p;

    if (parray->surfaceType() != AMObjType::ARRAY) {
      delete [] identifier;

      genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , "Sequences" , 1 ,
                  (parray->surfaceType()).string().data() , "ARRAY");
      return AMObj(AMObjType::ERROR);
    }

    else {
      register int j;
      int nb_variable = 0 , type , *length , ***int_sequence;
      double ***real_sequence;
      const Array *seq_array;
      Sequences *seq;
      MarkovianSequences *markovian_seq;
      StatError error;


      length = new int[nb_sequence];

      int_sequence = new int**[nb_sequence];
      for (i = 0;i < nb_sequence;i++) {
        int_sequence[i] = NULL;
      }

      real_sequence = new double**[nb_sequence];
      for (i = 0;i < nb_sequence;i++) {
        real_sequence[i] = NULL;
      }

      ArrayIter* pnext = parray->iterator();
      ArrayIter& next = *pnext;

      i = 0;
      while (next()) {
        seq_array = (Array*)(next.key()).val.p;

        switch ((seq_array->surfaceType())()) {

        case AMObjType::INTEGER : {
          if (i == 0) {
            type = INT_VALUE;
          }
          if (type == INT_VALUE) {
            int_sequence[i] = buildIntSequence(seq_array, length[i] , nb_variable , i);
          }
          else {
            status = false;
            genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdss) , "Sequences" , i + 1 ,
                        (seq_array->surfaceType()).string().data() , "INT");
          }
          break;
        }

        case AMObjType::REAL : {
          if (i == 0) {
            type = REAL_VALUE;
          }
          if (type == REAL_VALUE) {
            real_sequence[i] = buildRealSequence(seq_array, length[i] , nb_variable , i);
          }
          else {
            status = false;
            genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdss) , "Sequences" , i + 1 ,
                        (seq_array->surfaceType()).string().data() , "REAL");
          }
          break;
        }

        case AMObjType::ARRAY : {
          if (i == 0) {
            type = type_determination(seq_array , "Sequences");
          }
          if (type == INT_VALUE) {
            int_sequence[i] = buildIntArraySequence(seq_array , length[i] , index_parameter_type ,
                                                    nb_variable , i , "Sequences");
          }
          else if (type == REAL_VALUE) {
            real_sequence[i] = buildRealArraySequence(seq_array , length[i] , nb_variable ,
                                                      i , "Sequences");
          }
          else {
           status = false;
           genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdss) , "Sequences" , i + 1 ,
                        (seq_array->surfaceType()).string().data() , "INT or REAL");
          }
          break;
        }

        default : {
          status = false;
          genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdss) , "Sequences" , i + 1 ,
                      (seq_array->surfaceType()).string().data() , "INT or REAL or ARRAY");
          break;
        }
        }

        if ((!int_sequence[i]) && (!real_sequence[i])) {
          status = false;
          break;
        }
        i++;
      }

      delete pnext;

      if ((index_parameter_option) && (nb_variable == 1)) {
        status = false;
        genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdss) , "Sequences" , 1 ,
                    (seq_array->surfaceType()).string().data() , "ARRAY");
      }

      if (status) {
        if (index_parameter_type != IMPLICIT_TYPE) {
          nb_variable--;
        }

        if (type == INT_VALUE) {
          seq = new Sequences(nb_sequence , identifier , length , index_parameter_type ,
                              nb_variable , INT_VALUE , int_sequence);
        }
        else {
          seq = new Sequences(nb_sequence , identifier , length ,
                              nb_variable , real_sequence);
        }

        status = seq->check(error , SEQ_label[SEQL_SEQUENCE]);

        if (!status) {
          delete seq;
          AMLOUTPUT << "\n" << error;
          genAMLError(ERRORMSG(STAT_MODULE_s) , "Sequences");
        }
      }

      delete [] identifier;

      delete [] length;

      for (i = 0;i < nb_sequence;i++) {
        if (int_sequence[i]) {
          for (j = 0;j < nb_variable;j++) {
            delete [] int_sequence[i][j];
          }
          delete [] int_sequence[i];
        }

        if (real_sequence[i]) {
          for (j = 0;j < nb_variable;j++) {
            delete [] real_sequence[i][j];
          }
          delete [] real_sequence[i];
        }
      }
      delete [] int_sequence;
      delete [] real_sequence;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }

      markovian_seq = seq->markovian_sequences(error);
      if (markovian_seq) {
        delete seq;
        STAT_model* model = new STAT_model(markovian_seq);
        return AMObj(AMObjType::MARKOVIAN_SEQUENCES , model);
      }
      else {
        AMLOUTPUT << "\n";
        error.ascii_write(AMLOUTPUT , WARNING);
        STAT_model* model = new STAT_model(seq);
        return AMObj(AMObjType::SEQUENCES , model);
      }
    }
  }

  case AMObjType::RENEWAL_DATA : {
    Sequences *seq;
    MarkovianSequences *markovian_seq;
    StatError error;


    CHECKCONDVA(args.length() == 1 ,
                genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "Sequences"));

    seq = new Sequences(*((RenewalData*)((STAT_model*)args[0].val.p)->pt));

    markovian_seq = seq->markovian_sequences(error);
    if (markovian_seq) {
      delete seq;
      STAT_model* model = new STAT_model(markovian_seq);
      return AMObj(AMObjType::MARKOVIAN_SEQUENCES , model);
    }
    else {
      AMLOUTPUT << "\n";
      error.ascii_write(AMLOUTPUT , WARNING);
      STAT_model* model = new STAT_model(seq);
      return AMObj(AMObjType::SEQUENCES , model);
    }
  }

  case AMObjType::STRING : {
    bool status = true , old_format = false;
    int nb_required;
    Sequences *seq;
    MarkovianSequences *markovian_seq;
    StatError error;


    nb_required = 1;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Sequences"));

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Sequences" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "OldFormat") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Sequences" , nb_required + 1 ,
                      "OldFormat");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::BOOL) {
       status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Sequences" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "BOOL");
      }
      else {
        old_format = args[nb_required + 1].val.b;
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
    }

    seq = sequences_ascii_read(error , ((AMString*)args[0].val.p)->data() , old_format);

    if (seq) {
      markovian_seq = seq->markovian_sequences(error);
      if (markovian_seq) {
        delete seq;
        STAT_model* model = new STAT_model(markovian_seq);
        return AMObj(AMObjType::MARKOVIAN_SEQUENCES , model);
      }
      else {
        AMLOUTPUT << "\n";
        error.ascii_write(AMLOUTPUT , WARNING);
        STAT_model* model = new STAT_model(seq);
        return AMObj(AMObjType::SEQUENCES , model);
      }
    }

    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Sequences");
      return AMObj(AMObjType::ERROR);
    }
  }

  default : {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "Sequences" ,
                args[0].tag.string().data() , "ARRAY or RENEWAL_DATA or STRING");
    return AMObj(AMObjType::ERROR);
  }
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction des parametres d'une cime a partir d'un fichier ou
 *  a partir des parametres donnes un par un.
 *
 *--------------------------------------------------------------*/

AMObj STAT_TopParameters(const AMObjVector &args)

{
  bool status = true;
  int nb_required , max_position = DEFAULT_MAX_POSITION;
  double probability , axillary_probability = D_DEFAULT , rhythm_ratio = D_DEFAULT;
  TopParameters *parameters;
  StatError error;


  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TopParameters"));

  // argument obligatoire

  if (args[0].tag() == AMObjType::STRING) {
    nb_required = 1;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TopParameters"));
  }

  else if ((args[0].tag() == AMObjType::INTEGER) || (args[0].tag() == AMObjType::REAL)) {
    nb_required = 3;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TopParameters"));

    switch (args[0].tag()) {
    case AMObjType::INTEGER :
      probability = args[0].val.i;
      break;
    case AMObjType::REAL :
      probability = args[0].val.r;
      break;
    }
    if ((probability < TOP_MIN_PROBABILITY) || (probability > 1.)) {
      status = false;
      genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , "TopParameters" , 1);
    }

    switch (args[1].tag()) {
    case AMObjType::INTEGER :
      axillary_probability = args[1].val.i;
      break;
    case AMObjType::REAL :
      axillary_probability = args[1].val.r;
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TopParameters" , 2 ,
                  args[1].tag.string().data() , "INT or REAL");
      break;
    }
    if ((axillary_probability != D_DEFAULT) &&
        ((axillary_probability < TOP_MIN_PROBABILITY) || (axillary_probability > 1.))) {
      status = false;
      genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , "TopParameters" , 2);
    }

    switch (args[2].tag()) {
    case AMObjType::INTEGER :
      rhythm_ratio = args[2].val.i;
      break;
    case AMObjType::REAL :
      rhythm_ratio = args[2].val.r;
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TopParameters" , 3 ,
                  args[2].tag.string().data() , "INT or REAL");
      break;
    }
    if ((rhythm_ratio != D_DEFAULT) &&
        ((rhythm_ratio < MIN_RHYTHM_RATIO) || (rhythm_ratio > 1. / MIN_RHYTHM_RATIO))) {
      status = false;
      genAMLError(ERRORMSG(PARAMETER_VALUE_sd) , "TopParameters" , 3);
    }
  }

  else {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TopParameters" , 1 ,
                args[0].tag.string().data() , "STRING or INT or REAL");
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TopParameters" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "MaxPosition") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "TopParameters" , nb_required + 1 ,
                    "MaxPosition");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TopParameters" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "INT");
    }
    else {
      max_position = args[nb_required + 1].val.i;
      if ((max_position < 1) || (max_position > MAX_POSITION)) {
        status = false;
        genAMLError(ERRORMSG(MAX_POSITION_sd) , "TopParameters" , nb_required + 1);
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (args[0].tag() == AMObjType::STRING) {
    parameters = top_parameters_ascii_read(error , ((AMString*)args[0].val.p)->data() , max_position);

    if (parameters) {
      STAT_model* model = new STAT_model(parameters);
      return AMObj(AMObjType::TOP_PARAMETERS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "TopParameters");
      return AMObj(AMObjType::ERROR);
    }
  }

  else {
    parameters = new TopParameters(probability , axillary_probability ,
                                   rhythm_ratio , max_position);

    STAT_model* model = new STAT_model(parameters);
    return AMObj(AMObjType::TOP_PARAMETERS , model);
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction d'un ensemble de cimes a partir d'un objet de type
 *  ARRAY(ARRAY(ARRAY(INT))) ou a partir d'un fichier.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Tops(const AMObjVector &args)

{
  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Tops"));

  switch (args[0].tag()) {

  case AMObjType::ARRAY : {
    bool status = true;
    register int i , j;
    int nb_required , nb_sequence , nb_variable = 0 , *type , *length ,
        *identifier = NULL , ***int_sequence;
    const Array *parray = (Array*)args[0].val.p , *seq_array;
    Sequences *seq;
    Tops *tops;
    StatError error;


    nb_required = 1;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Tops"));

    CHECKCONDVA(parray->surfaceType() == AMObjType::ARRAY ,
                genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , "Tops" , 1 ,
                            (parray->surfaceType()).string().data() , "ARRAY"));

    nb_sequence = parray->entries();

    // argument obligatoire

    length = new int[nb_sequence];
    int_sequence = new int**[nb_sequence];
    for (i = 0;i < nb_sequence;i++) {
      int_sequence[i] = NULL;
    }

    ArrayIter* pnext = parray->iterator();
    ArrayIter& next = *pnext;

    i = 0;
    while (next()) {
      seq_array = (Array*)(next.key()).val.p;
 
      if (seq_array->surfaceType() != AMObjType::ARRAY) {
        genAMLError(ERRORMSG(SEQUENCE_ARRAY_ELEMENT_TYPE_sdss) , "Tops" , i + 1 ,
                    (seq_array->surfaceType()).string().data() , "ARRAY");
      }
      else {
        int_sequence[i] = buildIntArraySequence(seq_array , length[i] , POSITION ,
                                                nb_variable , i , "Tops");
      }

      if (!int_sequence[i]) {
        status = false;
        break;
      }
      i++;
    }

    delete pnext;

    if (nb_variable != 2) {
      status = false;
      genAMLError(ERRORMSG(NB_VARIABLE_2_sd) , "Tops" , 2);
    }

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Tops" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "Identifiers") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Tops" , nb_required + 1 ,
                      "Identifiers");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::ARRAY) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Tops" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "ARRAY");
      }
      else {
        identifier = buildIntArray(args , nb_required + 1 , "Tops" ,
                                   nb_required + 1 , nb_sequence);
        if (!identifier) {
          status = false;
        }
        else {
          for (i = 0;i < nb_sequence;i++) {
            if (identifier[i] <= 0) {
              status = false;
              genAMLError(ERRORMSG(ARRAY_ELEMENT_VALUE_sdd) , "Tops" ,
                          nb_required + 1 , i + 1);
            }
          }
        }
      }
    }

    if (status) {
      nb_variable--;
      seq = new Sequences(nb_sequence , identifier , length , POSITION ,
                          nb_variable , NB_INTERNODE , int_sequence);

      status = seq->check(error , SEQ_label[SEQL_TOP]);

      if (!status) {
        delete seq;
        AMLOUTPUT << "\n" << error;
        genAMLError(ERRORMSG(STAT_MODULE_s) , "Tops");
      }
    }

    delete [] identifier;

    delete [] length;

    for (i = 0;i < nb_sequence;i++) {
      if (int_sequence[i]) {
        for (j = 0;j < nb_variable;j++) {
          delete [] int_sequence[i][j];
        }
        delete [] int_sequence[i];
      }
    }
    delete [] int_sequence;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    tops = seq->tops(error);
    delete seq;

    if (tops) {
      STAT_model* model = new STAT_model(tops);
      return AMObj(AMObjType::TOPS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Tops");
      return AMObj(AMObjType::ERROR);
    }
  }

  case AMObjType::STRING : {
    bool status = true , old_format = false;
    int nb_required;
    Tops *tops;
    StatError error;


    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Tops"));

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Tops" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "OldFormat") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Tops" , nb_required + 1 ,
                      "OldFormat");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::BOOL) {
       status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Tops" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "BOOL");
      }
      else {
        old_format = args[nb_required + 1].val.b;
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
    }

    tops = tops_ascii_read(error , ((AMString*)args[0].val.p)->data() , old_format);

    if (tops) {
      STAT_model* model = new STAT_model(tops);
      return AMObj(AMObjType::TOPS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Tops");
      return AMObj(AMObjType::ERROR);
    }
  }

  default : {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sss) , "Tops" ,
                args[0].tag.string().data() , "ARRAY or STRING");
    return AMObj(AMObjType::ERROR);
  }
  }
}

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
 *       $Id: stat_funs4.cpp 16095 2014-03-17 14:55:55Z guedon $
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

#include "sequence_analysis/renewal.h"
#include "sequence_analysis/sequences.h"
#include "sequence_analysis/variable_order_markov.h"
#include "sequence_analysis/hidden_variable_order_markov.h"
#include "sequence_analysis/semi_markov.h"
#include "sequence_analysis/hidden_semi_markov.h"
#include "sequence_analysis/nonhomogeneous_markov.h"
#include "sequence_analysis/tops.h"

#include "aml/ammodel.h"
#include "aml/parseraml.h"
#include "aml/kernel_err.h"
#include "aml/amstring.h"

#include "aml/stat_module.h"


#define ERR_MSG_ARRAY STAT_err_msgs_aml
#define MODULE_NAME   "Statistics"


extern const char *STAT_err_msgs_aml[];

extern int nb_required_computation(const AMObjVector &args);
extern int* buildIntArray(const AMObjVector &args , int arg_index , const char *function ,
                          int output_index , int &nb_element);


const char *STAT_model_name[] = {
  "" ,
  "DISCRETE_MIXTURE" ,
  "CONVOLUTION" ,
  "COMPOUND" ,
  "VARIABLE_ORDER_MARKOV" ,
  "SEMI-MARKOV" ,
  "HIDDEN_VARIABLE_ORDER_MARKOV" ,
  "HIDDEN_SEMI-MARKOV" ,
  "NONHOMOGENEOUS_MARKOV"
};


enum {
  STATM_DISTRIBUTION ,
  STATM_DISCRETE_MIXTURE ,
  STATM_CONVOLUTION ,
  STATM_COMPOUND ,
  STATM_VARIABLE_ORDER_MARKOV ,
  STATM_SEMI_MARKOV ,
  STATM_HIDDEN_VARIABLE_ORDER_MARKOV ,
  STATM_HIDDEN_SEMI_MARKOV ,
  STATM_NONHOMOGENEOUS_MARKOV
};



/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une loi discrete.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateDistribution(const FrequencyDistribution *histo ,
                                       int ident , const AMObjVector &args)

{
  if (ident == CATEGORICAL) {
    DiscreteParametricModel *dist;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Estimate" , 2));

    dist = new DiscreteParametricModel(*histo);

    STAT_model* model = new STAT_model(dist);
    return AMObj(AMObjType::DISTRIBUTION , model);
  }

  else {
    RWCString *pstr;
    bool status = true , min_inf_bound_option = false , inf_bound_status_option = false , flag = true;
    register int i;
    int nb_required , min_inf_bound = 0;
    DiscreteParametricModel *dist;
    StatError error;


    nb_required = 2;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "MinInfBound") {
          switch (min_inf_bound_option) {

          case false : {
            min_inf_bound_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              min_inf_bound = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "InfBoundStatus") {
          switch (inf_bound_status_option) {

          case false : {
            inf_bound_status_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Fixed") {
                flag = false;
              }
              else if (*pstr == "Free") {
                flag = true;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(INF_BOUND_STATUS_sds) , "Estimate" ,
                            nb_required + i + 1 , "Fixed or Free");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" ,
                      nb_required + i + 1 , "MinInfBound or InfBoundStatus");
        }
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    dist = histo->parametric_estimation(error , ident , min_inf_bound , flag);

    if (dist) {
      STAT_model* model = new STAT_model(dist);
      return AMObj(AMObjType::DISTRIBUTION , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
      return AMObj(AMObjType::ERROR);
    }
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'un melange de lois discretes.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateDiscreteMixture(const FrequencyDistribution *histo , const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , min_inf_bound_option = false , inf_bound_status_option = false ,
       dist_inf_bound_status_option = false , flag = true , component_flag = true ,
       nb_component_option = false , nb_component_estimation = false , penalty_option = false ,
       estimate[DISCRETE_MIXTURE_NB_COMPONENT];
  register int i , j;
  int nb_component , nb_required , min_inf_bound = 0 , penalty = BICc , ident[DISCRETE_MIXTURE_NB_COMPONENT];
  const DiscreteParametric *pcomponent[DISCRETE_MIXTURE_NB_COMPONENT];
  DiscreteMixture *imixt , *mixt;
  StatError error;


  nb_required = nb_required_computation(args);
  nb_component = nb_required - 2;

  CHECKCONDVA((nb_component >= 2) && (nb_component <= DISCRETE_MIXTURE_NB_COMPONENT) ,
              genAMLError(ERRORMSG(NB_COMPONENT_sd) , "Estimate" , DISCRETE_MIXTURE_NB_COMPONENT));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // arguments obligatoires

  for (i = 0;i < nb_component;i++) {
    estimate[i] = false;
    pcomponent[i] = NULL;

    switch (args[2 + i].tag()) {

    case AMObjType::STRING : {
      pstr = (AMString*)args[2 + i].val.p;
      for (j = BINOMIAL;j <= NEGATIVE_BINOMIAL;j++) {
        if ((*pstr == STAT_discrete_distribution_word[j]) ||
            (*pstr == STAT_discrete_distribution_letter[j])) {
          estimate[i] = true;
          ident[i] = j;
          pcomponent[i] = new DiscreteParametric(0 , j);
          break;
        }
      }

      if (j == NEGATIVE_BINOMIAL + 1) {
        status = false;
        genAMLError(ERRORMSG(DISTRIBUTION_NAME_sds) , "Estimate" , 3 + i ,
                    "BINOMIAL(B) or POISSON(P) or NEGATIVE_BINOMIAL(NB)");
      }
      break;
    }

    case AMObjType::DISTRIBUTION : {
      pcomponent[i] = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[2 + i].val.p)->pt)));
      break;
    }

    case AMObjType::DISCRETE_MIXTURE : {
      pcomponent[i] = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[2 + i].val.p)->pt)));
      break;
    }

    case AMObjType::CONVOLUTION : {
      pcomponent[i] = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[2 + i].val.p)->pt)));
      break;
    }

    case AMObjType::COMPOUND : {
      pcomponent[i] = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[2 + i].val.p)->pt)));
      break;
    }

    default : {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 + i , args[2 + i].tag.string().data() ,
                  "STRING or DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
      break;
    }
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "MinInfBound") {
        switch (min_inf_bound_option) {

        case false : {
          min_inf_bound_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            min_inf_bound = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InfBoundStatus") {
        switch (inf_bound_status_option) {

        case false : {
          inf_bound_status_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Fixed") {
              flag = false;
            }
            else if (*pstr == "Free") {
              flag = true;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(INF_BOUND_STATUS_sds) , "Estimate" ,
                          nb_required + i + 1 , "Fixed or Free");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "DistInfBoundStatus") {
        switch (dist_inf_bound_status_option) {

        case false : {
          dist_inf_bound_status_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Fixed") {
              component_flag = false;
            }
            else if (*pstr == "Free") {
              component_flag = true;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(INF_BOUND_STATUS_sds) , "Estimate" ,
                          nb_required + i + 1 , "Fixed or Free");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbComponent") {
        switch (nb_component_option) {

        case false : {
          nb_component_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Fixed") {
              nb_component_estimation = false;
            }
            else if (*pstr == "Estimated") {
              nb_component_estimation = true;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(INF_BOUND_STATUS_sds) , "Estimate" ,
                          nb_required + i + 1 , "Fixed or Estimated");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Penalty") {
        switch (penalty_option) {

        case false : {
          penalty_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            for (j = AIC;j <= BICc;j++) {
              if (*pstr == STAT_criterion_word[j]) {
                penalty = j;
                break;
              }
            }
            if (j == BICc + 1) {
              status = false;
              genAMLError(ERRORMSG(PENALTY_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "AIC or AICc or BIC or BICc");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                    "MinInfBound or InfBoundStatus or DistInfBoundStatus or NbComponent or Penalty");
      }
    }
  }

  if ((!nb_component_estimation) && (penalty_option)) {
    status = false;
    genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Penalty");
  }

  if (nb_component_estimation) {
    for (i = 0;i < nb_component;i++) {
      if (!estimate[i]) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 + i ,
                    args[2 + i].tag.string().data() , "STRING");
      }
    }
  }

  if (status) {
    if (!nb_component_estimation) {
      imixt = new DiscreteMixture(nb_component , pcomponent);

      mixt = histo->discrete_mixture_estimation(error , *imixt , estimate , min_inf_bound ,
                                                flag , component_flag);
      delete imixt;
    }

    else {
      mixt = histo->discrete_mixture_estimation(error , AMLOUTPUT , 1 , nb_component , ident ,
                                                min_inf_bound , flag , component_flag , penalty);
    }
  }

  for (i = 0;i < nb_component;i++) {
    delete pcomponent[i];
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (mixt) {
    STAT_model* model = new STAT_model(mixt);
    return AMObj(AMObjType::DISCRETE_MIXTURE , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'un produit de convolution de lois discretes.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateConvolution(const FrequencyDistribution *histo , const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , estimator_option = false , initial_distribution_option = false ,
       min_inf_bound_option = false , nb_iteration_option = false , penalty_option = false ,
       weight_option = false , outside_option = false;
  register int i;
  int nb_required , estimator = LIKELIHOOD , min_inf_bound = 0 , nb_iter = I_DEFAULT ,
      penalty = SECOND_DIFFERENCE , outside = ZERO;
  double weight = D_DEFAULT;
  const DiscreteParametric *known_dist = NULL , *unknown_dist = NULL;
  Convolution *convol;
  StatError error;


  nb_required = 3;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
              (args.length() == nb_required + 12) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // argument obligatoire

  switch (args[2].tag()) {
  case AMObjType::DISTRIBUTION :
    known_dist = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[2].val.p)->pt)));
    break;
  case AMObjType::DISCRETE_MIXTURE :
    known_dist = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[2].val.p)->pt)));
    break;
  case AMObjType::CONVOLUTION :
    known_dist = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[2].val.p)->pt)));
    break;
  case AMObjType::COMPOUND :
    known_dist = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[2].val.p)->pt)));
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 , args[2].tag.string().data() ,
                "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
    break;
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Estimator") {
        switch (estimator_option) {

        case false : {
          estimator_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Likelihood") {
              estimator = LIKELIHOOD;
            }
            else if (*pstr == "PenalizedLikelihood") {
              estimator = PENALIZED_LIKELIHOOD;
            }
            else if (*pstr == "Parametric") {
              estimator = PARAMETRIC_REGULARIZATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "Likelihood or PenalizedLikelihood or Parametric");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InitialDistribution") {
        switch (initial_distribution_option) {

        case false : {
          initial_distribution_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::DISTRIBUTION :
            unknown_dist = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::DISCRETE_MIXTURE :
            unknown_dist = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::CONVOLUTION :
            unknown_dist = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::COMPOUND :
            unknown_dist = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() ,
                        "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
            break;
          }

          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "MinInfBound") {
        switch (min_inf_bound_option) {

        case false : {
          min_inf_bound_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            min_inf_bound = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbIteration") {
        switch (nb_iteration_option) {

        case false : {
          nb_iteration_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_iter = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Penalty") {
        switch (penalty_option) {

        case false : {
          penalty_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "FirstDifference") {
              penalty = FIRST_DIFFERENCE;
            }
            else if (*pstr == "SecondDifference") {
              penalty = SECOND_DIFFERENCE;
            }
            else if (*pstr == "Entropy") {
              penalty = ENTROPY;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(PENALTY_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "FirstDifference or SecondDifference or Entropy");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Weight") {
        switch (weight_option) {

        case false : {
          weight_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::INTEGER :
            weight = args[nb_required + i * 2 + 1].val.i;
            break;
          case AMObjType::REAL :
            weight = args[nb_required + i * 2 + 1].val.r;
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
            break;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Outside") {
        switch (outside_option) {

        case false : {
          outside_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Zero") {
              outside = ZERO;
            }
            else if (*pstr == "Continuation") {
              outside = CONTINUATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(SIDE_EFFECT_MANAGEMENT_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "Zero or Continuation");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                    "Estimator or InitialDistribution or MinInfBound or NbIteration or Penalty or Weight");
      }
    }
  }

  if ((initial_distribution_option) && (min_inf_bound_option)) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Estimate" , "InitialDistribution" , "MinInfBound");
  }

  if (estimator != PENALIZED_LIKELIHOOD) {
    if (penalty_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Penalty");
    }

    if (weight_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Weight");
    }

    if (outside_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Outside");
    }
  }

  if (status) {
    if (unknown_dist) {
      convol = histo->convolution_estimation(error , AMLOUTPUT , *known_dist , *unknown_dist ,
                                             estimator , nb_iter , weight , penalty , outside);
    }
    else {
      convol = histo->convolution_estimation(error , AMLOUTPUT , *known_dist , min_inf_bound ,
                                             estimator , nb_iter , weight , penalty , outside);
    }
  }

  delete known_dist;
  delete unknown_dist;

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (convol) {
    STAT_model* model = new STAT_model(convol);
    return AMObj(AMObjType::CONVOLUTION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une loi composee.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateCompound(const FrequencyDistribution *histo , const AMObjVector &args)

{
  RWCString *pstr;
  char type = 'v';
  bool status = true , estimator_option = false , initial_distribution_option = false ,
       min_inf_bound_option = false , nb_iteration_option = false , penalty_option = false ,
       weight_option = false , outside_option = false;
  register int i;
  int nb_required , estimator = LIKELIHOOD , min_inf_bound = 0 , nb_iter = I_DEFAULT ,
      penalty = SECOND_DIFFERENCE , outside = ZERO;
  double weight = D_DEFAULT;
  const DiscreteParametric *known_dist = NULL , *unknown_dist = NULL;
  Compound *cdist;
  StatError error;


  nb_required = 4;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
              (args.length() == nb_required + 12) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // arguments obligatoires

  switch (args[2].tag()) {
  case AMObjType::DISTRIBUTION :
    known_dist = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[2].val.p)->pt)));
    break;
  case AMObjType::DISCRETE_MIXTURE :
    known_dist = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[2].val.p)->pt)));
    break;
  case AMObjType::CONVOLUTION :
    known_dist = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[2].val.p)->pt)));
    break;
  case AMObjType::COMPOUND :
    known_dist = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[2].val.p)->pt)));
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 , args[2].tag.string().data() ,
                "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
    break;
  }

  if (args[3].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 4 ,
                args[3].tag.string().data() , "STRING");
  }
  else {
    pstr = (AMString*)args[3].val.p;
    if (*pstr == "Sum") {
      type = 's';
    }
    else if (*pstr == "Elementary") {
      type = 'e';
    }
    else {
      status = false;
      genAMLError(ERRORMSG(DISTRIBUTION_NAME_sds) , "Estimate" , 4 , "Sum or Elementary");
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Estimator") {
        switch (estimator_option) {

        case false : {
          estimator_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Likelihood") {
              estimator = LIKELIHOOD;
            }
            else if (*pstr == "PenalizedLikelihood") {
              estimator = PENALIZED_LIKELIHOOD;
            }
            else if (*pstr == "Parametric") {
              estimator = PARAMETRIC_REGULARIZATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "Likelihood or PenalizedLikelihood or Parametric");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InitialDistribution") {
        switch (initial_distribution_option) {

        case false : {
          initial_distribution_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::DISTRIBUTION :
            unknown_dist = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::DISCRETE_MIXTURE :
            unknown_dist = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::CONVOLUTION :
            unknown_dist = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::COMPOUND :
            unknown_dist = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() ,
                        "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
            break;
          }

          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "MinInfBound") {
        switch (min_inf_bound_option) {

        case false : {
          min_inf_bound_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            min_inf_bound = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbIteration") {
        switch (nb_iteration_option) {

        case false : {
          nb_iteration_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_iter = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Penalty") {
        switch (penalty_option) {

        case false : {
          penalty_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "FirstDifference") {
              penalty = FIRST_DIFFERENCE;
            }
            else if (*pstr == "SecondDifference") {
              penalty = SECOND_DIFFERENCE;
            }
            else if (*pstr == "Entropy") {
              penalty = ENTROPY;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(PENALTY_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "FirstDifference or SecondDifference or Entropy");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Weight") {
        switch (weight_option) {

        case false : {
          weight_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::INTEGER :
            weight = args[nb_required + i * 2 + 1].val.i;
            break;
          case AMObjType::REAL :
            weight = args[nb_required + i * 2 + 1].val.r;
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
            break;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Outside") {
        switch (outside_option) {

        case false : {
          outside_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Zero") {
              outside = ZERO;
            }
            else if (*pstr == "Continuation") {
              outside = CONTINUATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(SIDE_EFFECT_MANAGEMENT_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "Zero or Continuation");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                    "Estimator or InitialDistribution or MinInfBound or NbIteration or Penalty or Weight");
      }
    }
  }

  if ((initial_distribution_option) && (min_inf_bound_option)) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Estimate" , "InitialDistribution" , "MinInfBound");
  }

  if (estimator != PENALIZED_LIKELIHOOD) {
    if (penalty_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Penalty");
    }

    if (weight_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Weight");
    }

    if (outside_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Outside");
    }
  }

  if (status) {
    if (unknown_dist) {
      switch (type) {
      case 's' :
        cdist = histo->compound_estimation(error , AMLOUTPUT , *unknown_dist , *known_dist , type ,
                                           estimator , nb_iter , weight , penalty , outside);
        break;
      case 'e' :
        cdist = histo->compound_estimation(error , AMLOUTPUT , *known_dist , *unknown_dist , type ,
                                           estimator , nb_iter , weight , penalty , outside);
        break;
      }
    }

    else {
      cdist = histo->compound_estimation(error , AMLOUTPUT , *known_dist , type , min_inf_bound ,
                                         estimator , nb_iter , weight , penalty , outside);
    }
  }

  delete known_dist;
  delete unknown_dist;

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (cdist) {
    STAT_model* model = new STAT_model(cdist);
    return AMObj(AMObjType::COMPOUND , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'un melange multivarie.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateMixture(const Vectors *vec , const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , algorithm_option = false , nb_iteration_option = false ,
       min_nb_assignment_option = false , max_nb_assignment_option = false , parameter_option = false ,
       assignment_option = false , assignment = true;
  register int i;
  int nb_required , algorithm = EM , nb_iter = I_DEFAULT ,
      min_nb_assignment = MIN_NB_ASSIGNMENT , max_nb_assignment = MAX_NB_ASSIGNMENT;
  double parameter = NB_ASSIGNMENT_PARAMETER;
  Mixture *mixt;
  StatError error;


  if (args[2].tag() == AMObjType::MIXTURE) {
    bool known_component_option = false , known_component = false , common_dispersion_option = false ,
         common_dispersion = false;
    Mixture *imixt = NULL;


    nb_required = 3;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    imixt = (Mixture*)((STAT_model*)args[2].val.p)->pt;

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Algorithm") {
          switch (algorithm_option) {

          case false : {
            algorithm_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "EM") {
                algorithm = EM;
              }
              else if (*pstr == "MCEM") {
                algorithm = MCEM;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "EM or MCEM");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "KnownComponent") {
          switch (known_component_option) {

          case false : {
            known_component_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              known_component = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "CommonDispersion") {
          switch (common_dispersion_option) {

          case false : {
            common_dispersion_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              common_dispersion = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "NbIteration") {
          switch (nb_iteration_option) {

          case false : {
            nb_iteration_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              nb_iter = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MinNbAssignment") {
          switch (min_nb_assignment_option) {

          case false : {
            min_nb_assignment_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              min_nb_assignment = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MaxNbAssignment") {
          switch (max_nb_assignment_option) {

          case false : {
            max_nb_assignment_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              max_nb_assignment = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
        }
        }

        else if (*pstr == "Parameter") {
          switch (parameter_option) {

          case false : {
            parameter_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              parameter = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              parameter = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Assignment") {
          switch (assignment_option) {

          case false : {
            assignment_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              assignment = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" ,
                      nb_required + i + 1 , "Algorithm or KnownComponent or CommonDispersion or NbIteration or MinNbAssignment or MaxNbAssignment or Parameter or Assignment");
        }
      }
    }

    if ((algorithm != MCEM) && (min_nb_assignment_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MinNbAssignment");
    }
    if ((algorithm != MCEM) && (max_nb_assignment_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MaxNbAssignment");
    }
    if ((algorithm != MCEM) && (parameter_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Parameter");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (algorithm) {
    case EM :
      mixt = vec->mixture_estimation(error , AMLOUTPUT , *imixt ,
                                     known_component , common_dispersion ,
                                     INDEPENDENT , assignment , nb_iter);
      break;
    case MCEM :
      mixt = vec->mixture_stochastic_estimation(error , AMLOUTPUT , *imixt ,
                                                known_component , common_dispersion ,
                                                INDEPENDENT , min_nb_assignment ,
                                                max_nb_assignment , parameter ,
                                                assignment , nb_iter);
      break;
    }
  }

  else if (args[2].tag() == AMObjType::INTEGER) {
    bool variance_factor_option = false , tied_location_option = false , tied_location = true;
    int ident , variance_factor = SCALING_FACTOR;
    double mean , standard_deviation;


    nb_required = 6;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    // arguments obligatoires

    if (args[3].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 4 ,
                  args[3].tag.string().data() , "STRING");
    }
    else {
      pstr = (AMString*)args[3].val.p;
      if ((*pstr == STAT_continuous_distribution_word[GAMMA]) ||
          (*pstr == STAT_continuous_distribution_letter[GAMMA])) {
        ident = GAMMA;
      }
      else if ((*pstr == STAT_continuous_distribution_word[GAUSSIAN]) ||
               (*pstr == STAT_continuous_distribution_letter[GAUSSIAN])) {
        ident = GAUSSIAN;
      }
      else {
        status = false;
        genAMLError(ERRORMSG(DISTRIBUTION_NAME_sds) , "Estimate" , 4 ,
                    "GAMMA(Ga) or GAUSSIAN(G)");
      }
    }

    switch (args[4].tag()) {
    case AMObjType::INTEGER :
      mean = args[4].val.i;
      break;
    case AMObjType::REAL :
      mean = args[4].val.r;
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 5 ,
                  args[4].tag.string().data() , "INT or REAL");
    }

    switch (args[5].tag()) {
    case AMObjType::INTEGER :
      standard_deviation = args[5].val.i;
      break;
    case AMObjType::REAL :
      standard_deviation = args[5].val.r;
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 6 ,
                  args[5].tag.string().data() , "INT or REAL");
    }

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Algorithm") {
          switch (algorithm_option) {

          case false : {
            algorithm_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "EM") {
                algorithm = EM;
              }
              else if (*pstr == "MCEM") {
                algorithm = MCEM;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "EM or MCEM");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "TiedLocation") {
          switch (tied_location_option) {

          case false : {
            tied_location_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              tied_location = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "VarianceFactor") {
          switch (variance_factor_option) {

          case false : {
            variance_factor_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Convolution") {
                variance_factor = CONVOLUTION_FACTOR;
              }
              else if (*pstr == "Scaling") {
                variance_factor = SCALING_FACTOR;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(VARIANCE_FACTOR_sds) , "Estimate" ,
                            nb_required + i + 1 , "Convolution or Scaling");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "NbIteration") {
          switch (nb_iteration_option) {

          case false : {
            nb_iteration_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              nb_iter = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MinNbAssignment") {
          switch (min_nb_assignment_option) {

          case false : {
            min_nb_assignment_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              min_nb_assignment = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MaxNbAssignment") {
          switch (max_nb_assignment_option) {

          case false : {
            max_nb_assignment_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              max_nb_assignment = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
        }
        }

        else if (*pstr == "Parameter") {
          switch (parameter_option) {

          case false : {
            parameter_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              parameter = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              parameter = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Assignment") {
          switch (assignment_option) {

          case false : {
            assignment_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              assignment = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" ,
                      nb_required + i + 1 , "Algorithm or TiedLocation or VarianceFactor or NbIteration or MinNbAssignment or MaxNbAssignment or Parameter or Assignment");
        }
      }
    }

    if ((algorithm != MCEM) && (min_nb_assignment_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MinNbAssignment");
    }
    if ((algorithm != MCEM) && (max_nb_assignment_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MaxNbAssignment");
    }
    if ((algorithm != MCEM) && (parameter_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Parameter");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (algorithm) {
    case EM :
      mixt = vec->mixture_estimation(error , AMLOUTPUT , args[2].val.i ,
                                     ident , mean , standard_deviation , tied_location ,
                                     variance_factor , assignment , nb_iter);
      break;
    case MCEM :
      mixt = vec->mixture_stochastic_estimation(error , AMLOUTPUT , args[2].val.i ,
                                                ident , mean , standard_deviation , tied_location ,
                                                variance_factor , min_nb_assignment ,
                                                max_nb_assignment , parameter ,
                                                assignment , nb_iter);
      break;
    }
  }

  else {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 ,
                args[2].tag.string().data() , "INT or MIXTURE");
    return AMObj(AMObjType::ERROR);
  }

  if (mixt) {
    STAT_model* model = new STAT_model(mixt);
    return AMObj(AMObjType::MIXTURE , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'un processus de renouvellement
 *  a partir de donnees d'intervalle.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateRenewalIntervalData(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , estimator_option = false , initial_inter_event_option = false ,
       nb_iteration_option = false , inter_event_mean_option = false , penalty_option = false ,
       weight_option = false , outside_option = false;
  register int i;
  int nb_required , estimator = LIKELIHOOD , nb_iter = I_DEFAULT ,
      mean_computation_method = COMPUTED , penalty = SECOND_DIFFERENCE , outside = ZERO;
  double weight = D_DEFAULT;
  const DiscreteParametric *iinter_event = NULL;
  DiscreteParametricModel *inter_event = NULL;
  Renewal *renew = NULL;
  const FrequencyDistribution *histo = NULL;
  StatError error;


  nb_required = nb_required_computation(args);

  // arguments obligatoires

  switch (args[0].tag()) {

  case AMObjType::FREQUENCY_DISTRIBUTION : {
    CHECKCONDVA((nb_required == 3) || (nb_required == 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    if (nb_required == 4) {
      if (args[3].tag() != AMObjType::FREQUENCY_DISTRIBUTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 4 ,
                    args[3].tag.string().data() , "FREQUENCY_DISTRIBUTION");
      }
      else {
        histo = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[3].val.p)->pt);
      }
    }
    break;
  }

  case AMObjType::RENEWAL_DATA : {
    CHECKCONDVA(nb_required == 1 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));
    break;
  }

  default : {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 1 ,
                args[0].tag.string().data() , "FREQUENCY_DISTRIBUTION or RENEWAL_DATA");
    break;
  }
  }

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
              (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Estimator") {
        switch (estimator_option) {

        case false : {
          estimator_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Likelihood") {
              estimator = LIKELIHOOD;
            }
            else if (*pstr == "PenalizedLikelihood") {
              estimator = PENALIZED_LIKELIHOOD;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "Likelihood or PenalizedLikelihood");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InitialInterEvent") {
        switch (initial_inter_event_option) {

        case false : {
          initial_inter_event_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::DISTRIBUTION :
            iinter_event = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::DISCRETE_MIXTURE :
            iinter_event = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::CONVOLUTION :
            iinter_event = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::COMPOUND :
            iinter_event = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() ,
                        "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
            break;
          }

          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbIteration") {
        switch (nb_iteration_option) {

        case false : {
          nb_iteration_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_iter = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InterEventMean") {
        switch (inter_event_mean_option) {

        case false : {
          inter_event_mean_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Computed") {
              mean_computation_method = COMPUTED;
            }
            else if (*pstr == "Estimated") {
              mean_computation_method = ESTIMATED;
            }
            else if (*pstr == "OneStepLate") {
              mean_computation_method = ONE_STEP_LATE;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(MEAN_COMPUTATION_METHOD_sds) , "Estimate" ,
                          nb_required + i + 1 , "Computed or Estimated or OneStepLate");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Penalty") {
        switch (penalty_option) {

        case false : {
          penalty_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "FirstDifference") {
              penalty = FIRST_DIFFERENCE;
            }
            else if (*pstr == "SecondDifference") {
              penalty = SECOND_DIFFERENCE;
            }
            else if (*pstr == "Entropy") {
              penalty = ENTROPY;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(PENALTY_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "FirstDifference or SecondDifference or Entropy");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Weight") {
        switch (weight_option) {

        case false : {
          weight_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::INTEGER :
            weight = args[nb_required + i * 2 + 1].val.i;
            break;
          case AMObjType::REAL :
            weight = args[nb_required + i * 2 + 1].val.r;
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
            break;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Outside") {
        switch (outside_option) {

        case false : {
          outside_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Zero") {
              outside = ZERO;
            }
            else if (*pstr == "Continuation") {
              outside = CONTINUATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(SIDE_EFFECT_MANAGEMENT_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "Zero or Continuation");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                    "Estimator or InitialInterEvent or NbIteration or InterEventMean or Penalty or Weight");
      }
    }
  }

  if (estimator == PENALIZED_LIKELIHOOD) {
    if (!inter_event_mean_option) {
      mean_computation_method = ONE_STEP_LATE;
    }

    else if (mean_computation_method == COMPUTED) {
      status = false;
      genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Estimate" , "Estimator" , "InterEventMean");
    }
  }

  else {
    if (penalty_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Penalty");
    }

    if (weight_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Weight");
    }

    if (outside_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Outside");
    }
  }

  if (status) {
    switch (args[0].tag()) {

    case AMObjType::FREQUENCY_DISTRIBUTION : {
      if (iinter_event) {
        inter_event = ((FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt))->estimation(error , AMLOUTPUT ,
                                                                                                              *((FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[1].val.p)->pt)) ,
                                                                                                              *((FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[2].val.p)->pt)) ,
                                                                                                              histo , *iinter_event , estimator ,
                                                                                                              nb_iter , mean_computation_method ,
                                                                                                              weight , penalty , outside);
      }
      else {
        inter_event = ((FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt))->estimation(error , AMLOUTPUT ,
                                                                                                              *((FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[1].val.p)->pt)) ,
                                                                                                              *((FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[2].val.p)->pt)) ,
                                                                                                              histo , estimator ,
                                                                                                              nb_iter , mean_computation_method ,
                                                                                                              weight , penalty , outside);
      }
      break;
    }

    case AMObjType::RENEWAL_DATA : {
      if (iinter_event) {
        renew = ((RenewalData*)((STAT_model*)args[0].val.p)->pt)->estimation(error , AMLOUTPUT ,
                                                                             *iinter_event , estimator ,
                                                                             nb_iter , mean_computation_method ,
                                                                             weight , penalty , outside);
      }
      else {
        renew = ((RenewalData*)((STAT_model*)args[0].val.p)->pt)->estimation(error , AMLOUTPUT , estimator ,
                                                                             nb_iter , mean_computation_method ,
                                                                             weight , penalty , outside);
      }
      break;
    }
    }
  }

  delete iinter_event;

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (inter_event) {
    STAT_model* model = new STAT_model(inter_event);
    return AMObj(AMObjType::DISTRIBUTION , model);
  }
  else if (renew) {
    STAT_model* model = new STAT_model(renew);
    return AMObj(AMObjType::RENEWAL , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'un processus de renouvellement
 *  a partir de donnees de comptage.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateRenewalCountData(const AMObjVector &args)

{
  RWCString *pstr;
  char type = 'v';
  bool status = true , estimator_option = false , nb_iteration_option = false ,
       initial_inter_event_option = false , equilibrium_estimator_option = false ,
       inter_event_mean_option = false , penalty_option = false , weight_option = false ,
       outside_option = false;
  register int i;
  int nb_required , estimator = LIKELIHOOD , nb_iter = I_DEFAULT , equilibrium_estimator = COMPLETE_LIKELIHOOD ,
      mean_computation_method = COMPUTED , penalty = SECOND_DIFFERENCE , outside = ZERO;
  double weight = D_DEFAULT;
  const DiscreteParametric *inter_event = NULL;
  Renewal *renew;
  const TimeEvents *timev;
  StatError error;


  nb_required = 2;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
              (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
              (args.length() == nb_required + 16) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // arguments obligatoires

  switch (args[0].tag()) {
  case AMObjType::TIME_EVENTS :
    timev = (TimeEvents*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::RENEWAL_DATA :
    timev = (RenewalData*)((STAT_model*)args[0].val.p)->pt;
    break;
  }

  if (args[1].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 2 ,
                args[1].tag.string().data() , "STRING");
  }
  else {
    pstr = (AMString*)args[1].val.p;
    if (*pstr == "Ordinary") {
      type = 'o';
    }
    else if (*pstr == "Equilibrium") {
      type = 'e';
    }
    else {
      status = false;
      genAMLError(ERRORMSG(STOCHASTIC_PROCESS_TYPE_sds) , "Estimate" , 2 ,
                  "Ordinary or Equilibrium");
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Estimator") {
        switch (estimator_option) {

        case false : {
          estimator_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Likelihood") {
              estimator = LIKELIHOOD;
            }
            else if (*pstr == "PenalizedLikelihood") {
              estimator = PENALIZED_LIKELIHOOD;
            }
            else if (*pstr == "Parametric") {
              estimator = PARAMETRIC_REGULARIZATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "Likelihood or PenalizedLikelihood or Parametric");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbIteration") {
        switch (nb_iteration_option) {

        case false : {
          nb_iteration_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_iter = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InitialInterEvent") {
        switch (initial_inter_event_option) {

        case false : {
          initial_inter_event_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::DISTRIBUTION :
            inter_event = new DiscreteParametric(*((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::DISCRETE_MIXTURE :
            inter_event = new DiscreteParametric(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::CONVOLUTION :
            inter_event = new DiscreteParametric(*((Distribution*)((Convolution*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          case AMObjType::COMPOUND :
            inter_event = new DiscreteParametric(*((Distribution*)((Compound*)((STAT_model*)args[nb_required + i * 2 + 1].val.p)->pt)));
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() ,
                        "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
            break;
          }

          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "EquilibriumEstimator") {
        switch (equilibrium_estimator_option) {

        case false : {
          equilibrium_estimator_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "CompleteLikelihood") {
              equilibrium_estimator = COMPLETE_LIKELIHOOD;
            }
            else if (*pstr == "PartialLikelihood") {
              equilibrium_estimator = PARTIAL_LIKELIHOOD;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "CompleteLikelihood or PartialLikelihood");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "InterEventMean") {
        switch (inter_event_mean_option) {

        case false : {
          inter_event_mean_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Computed") {
              mean_computation_method = COMPUTED;
            }
            else if (*pstr == "Estimated") {
              mean_computation_method = ESTIMATED;
            }
            else if (*pstr == "OneStepLate") {
              mean_computation_method = ONE_STEP_LATE;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(MEAN_COMPUTATION_METHOD_sds) , "Estimate" ,
                          nb_required + i + 1 , "Computed or Estimated or OneStepLate");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Penalty") {
        switch (penalty_option) {

        case false : {
          penalty_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "FirstDifference") {
              penalty = FIRST_DIFFERENCE;
            }
            else if (*pstr == "SecondDifference") {
              penalty = SECOND_DIFFERENCE;
            }
            else if (*pstr == "Entropy") {
              penalty = ENTROPY;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(PENALTY_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "FirstDifference or SecondDifference or Entropy");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Weight") {
        switch (weight_option) {

        case false : {
          weight_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::INTEGER :
            weight = args[nb_required + i * 2 + 1].val.i;
            break;
          case AMObjType::REAL :
            weight = args[nb_required + i * 2 + 1].val.r;
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
            break;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Outside") {
        switch (outside_option) {

        case false : {
          outside_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Zero") {
              outside = ZERO;
            }
            else if (*pstr == "Continuation") {
              outside = CONTINUATION;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(SIDE_EFFECT_MANAGEMENT_TYPE_sds) , "Estimate" ,
                          nb_required + i + 1 , "Zero or Continuation");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                    "Estimator or NbIteration or InitialInterEvent or EquilibriumEstimator or InterEventMean or Penalty or Weight");
      }
    }
  }

  if (type != 'e') {
    if (equilibrium_estimator_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Equilibrium_Estimator");
    }

    if (inter_event_mean_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "InterEventMean");
    }
  }

  if (estimator == PENALIZED_LIKELIHOOD) {
    if (!inter_event_mean_option) {
      mean_computation_method = ONE_STEP_LATE;
    }

    else if (mean_computation_method == COMPUTED) {
      status = false;
      genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Estimate" , "Estimator" , "InterEventMean");
    }
  }

  else {
    if (penalty_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Penalty");
    }

    if (weight_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Weight");
    }

    if (outside_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Outside");
    }
  }

  if (status) {
    if (inter_event) {
      renew = timev->estimation(error , AMLOUTPUT , type , *inter_event , estimator ,
                                nb_iter , equilibrium_estimator , mean_computation_method ,
                                weight , penalty , outside);
    }
    else {
      renew = timev->estimation(error , AMLOUTPUT , type , estimator , nb_iter ,
                                equilibrium_estimator , mean_computation_method , weight ,
                                penalty , outside);
    }
  }

  delete inter_event;

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (renew) {
    STAT_model* model = new STAT_model(renew);
    return AMObj(AMObjType::RENEWAL , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une chaine de Markov d'ordre variable.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateVariableOrderMarkov(const MarkovianSequences *seq , const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , counting_option = false , counting_flag = true ,
       global_initial_transition_option = false , global_initial_transition = true;
  register int i;
  int nb_required;
  VariableOrderMarkov *markov;
  StatError error;


  nb_required = 3;

  CHECKCONDVA(args.length() >= nb_required ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  switch (args[2].tag()) {

  case AMObjType::STRING : {
    char type = 'v';
    bool algorithm_option = false , estimator_option = false , global_sample_option = false ,
         global_sample = true , min_order_option = false , max_order_option = false ,
         order_estimation = true , threshold_option = false;
    int algorithm = LOCAL_BIC , estimator = LAPLACE , min_order = 0 , max_order = ORDER;
    double threshold = LOCAL_BIC_THRESHOLD;


    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    // argument obligatoire

    pstr = (AMString*)args[2].val.p;
    if (*pstr == "Ordinary") {
      type = 'o';
    }
    else if (*pstr == "Equilibrium") {
      type = 'e';
    }
    else {
      status = false;
      genAMLError(ERRORMSG(STOCHASTIC_PROCESS_TYPE_sds) , "Estimate" , 3 ,
                  "Ordinary or Equilibrium");
    }

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Algorithm") {
          switch (algorithm_option) {

          case false : {
            algorithm_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "BIC") {
                algorithm = CTM_BIC;
              }
              else if (*pstr == "KT") {
                algorithm = CTM_KT;
              }
              else if (*pstr == "LocalBIC") {
                algorithm = LOCAL_BIC;
              }
              else if (*pstr == "Context") {
                algorithm = CONTEXT;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "BIC or LocalBIC");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              counting_flag = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Estimator") {
          switch (estimator_option) {

          case false : {
            estimator_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "MaximumLikelihood") {
                estimator = MAXIMUM_LIKELIHOOD;
              }
              else if (*pstr == "Laplace") {
                estimator = LAPLACE;
              }
              else if (*pstr == "AdaptativeLaplace") {
                estimator = ADAPTATIVE_LAPLACE;
              }
              else if (*pstr == "UniformSubset") {
                estimator = UNIFORM_SUBSET;
              }
              else if (*pstr == "UniformCardinality") {
                estimator = UNIFORM_CARDINALITY;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "MaximumLikelihood or Laplace or AdaptativeLaplace or UniformSubset or UniformCardinality");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "GlobalInitialTransition") {
          switch (global_initial_transition_option) {

          case false : {
            global_initial_transition_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              global_initial_transition = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "GlobalSample") {
          switch (global_sample_option) {

          case false : {
            global_sample_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              global_sample = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MinOrder") {
          switch (min_order_option) {

          case false : {
            min_order_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              min_order = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if ((*pstr == "MaxOrder") || (*pstr == "Order")) {
          switch (max_order_option) {

          case false : {
            max_order_option = true;

            if (*pstr == "Order") {
              order_estimation = false;
            }

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              max_order = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Threshold") {
          switch (threshold_option) {

          case false : {
            threshold_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              threshold = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              threshold = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                      "Algorithm or Counting or Estimator or GlobalInitialTransition or MinOrder or MaxOrder or Order or Threshold");
        }
      }
    }

    if ((algorithm != LOCAL_BIC) && (!threshold_option)) {
      switch (algorithm) {
      case CTM_BIC :
        threshold = CTM_BIC_THRESHOLD;
        break;
      case CTM_KT :
        threshold = CTM_KT_THRESHOLD;
        break;
      case CONTEXT :
        threshold = CONTEXT_THRESHOLD;
        break;
      }
    }

    if ((algorithm == CTM_KT) && (estimator_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Estimator");
    }

    if (!order_estimation) {
      if (algorithm_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Algorithm");
      }
      if (estimator_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Estimator");
      }
      if (global_sample_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "GlobalSample");
      }
      if (min_order_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MinOrder");
      }
      if (threshold_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Threshold");
      }
    }

    if ((type == 'e') && (global_initial_transition_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "GlobalInitialTransition");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (order_estimation) {
    case false :
      markov = seq->variable_order_markov_estimation(error , type , max_order ,
                                                     global_initial_transition , counting_flag);
      break;
    case true :
      markov = seq->variable_order_markov_estimation(error , AMLOUTPUT , type , min_order ,
                                                     max_order , algorithm , threshold ,
                                                     estimator , global_initial_transition ,
                                                     global_sample , counting_flag);
      break;
    }
    break;
  }

  case AMObjType::VARIABLE_ORDER_MARKOV : {
    VariableOrderMarkov *imarkov;


    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    imarkov = (VariableOrderMarkov*)((STAT_model*)args[2].val.p)->pt;

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Counting") {
          switch (counting_option) {

          case false : {
            counting_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              counting_flag = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "GlobalInitialTransition") {
          switch (global_initial_transition_option) {

          case false : {
            global_initial_transition_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              global_initial_transition = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                      "Counting or GlobalInitialTransition");
        }
      }
    }

    if ((((Chain*)imarkov)->type == 'e') && (global_initial_transition_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "GlobalInitialTransition");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    markov = seq->variable_order_markov_estimation(error , *imarkov ,
                                                   global_initial_transition , counting_flag);
    break;
  }

  case AMObjType::ARRAY : {
    register int j;
    bool order_option = false , penalty_option = false;
    int nb_symbol = seq->get_marginal_distribution(0)->nb_value , order = 1 ,
        penalty = BIC , *symbol = NULL;


    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    // argument obligatoire

    symbol = buildIntArray(args , 2 , "Estimate" , 3 , nb_symbol);
    if (!symbol) {
      status = false;
    }

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Counting") {
          switch (counting_option) {

          case false : {
            counting_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              counting_flag = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Order") {
          switch (order_option) {

          case false : {
            order_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              order = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Penalty") {
          switch (penalty_option) {

          case false : {
            penalty_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              for (j = AIC;j <= BIC;j++) {
                if (*pstr == STAT_criterion_word[j]) {
                  penalty = j;
                  break;
                }
              }
              if (j == BIC + 1) {
                status = false;
                genAMLError(ERRORMSG(PENALTY_TYPE_sds) , "Estimate" ,
                            nb_required + i + 1 , "AIC or AICc or BIC");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" ,
                      nb_required + i + 1 , "Counting or Order or Penalty");
        }
      }
    }

    if (!status) {
      delete [] symbol;
      return AMObj(AMObjType::ERROR);
    }

    markov = seq->lumpability_estimation(error , AMLOUTPUT , symbol , penalty ,
                                         order , counting_flag);
    delete [] symbol;
    break;
  }

  default : {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 ,
                args[2].tag.string().data() , "STRING or VARIABLE_ORDER_MARKOV or ARRAY");
    return AMObj(AMObjType::ERROR);
  }
  }

  if (markov) {
    STAT_model* model = new STAT_model(markov);
    return AMObj(AMObjType::VARIABLE_ORDER_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une semi-chaine de Markov.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateSemiMarkov(const MarkovianSequences *seq , const AMObjVector &args)

{
  RWCString *pstr;
  char type = 'v';
  bool status = true , counting_option = false , counting_flag = true , estimator_option = false ,
       nb_iteration_option = false , occupancy_mean_option = false;
  register int i;
  int nb_required , estimator = COMPLETE_LIKELIHOOD , nb_iter = I_DEFAULT ,
      mean_computation_method = COMPUTED;
  SemiMarkov *smarkov;
  StatError error;


  nb_required = 3;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // argument obligatoire

  if (args[2].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 ,
                args[2].tag.string().data() , "STRING");
  }
  else {
    pstr = (AMString*)args[2].val.p;
    if (*pstr == "Ordinary") {
      type = 'o';
    }
    else if (*pstr == "Equilibrium") {
      type = 'e';
    }
    else {
      status = false;
      genAMLError(ERRORMSG(STOCHASTIC_PROCESS_TYPE_sds) , "Estimate" , 3 ,
                  "Ordinary or Equilibrium");
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Counting") {
        switch (counting_option) {

        case false : {
          counting_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            counting_flag = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Estimator") {
        switch (estimator_option) {

        case false : {
          estimator_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "CompleteLikelihood") {
              estimator = COMPLETE_LIKELIHOOD;
            }
            else if (*pstr == "PartialLikelihood") {
              estimator = PARTIAL_LIKELIHOOD;
            }
            else if (*pstr == "KaplanMeier") {
              estimator = KAPLAN_MEIER;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "CompleteLikelihood or PartialLikelihood");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbIteration") {
        switch (nb_iteration_option) {

        case false : {
          nb_iteration_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_iter = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "OccupancyMean") {
        switch (occupancy_mean_option) {

        case false : {
          occupancy_mean_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "Computed") {
              mean_computation_method = COMPUTED;
            }
            else if (*pstr == "OneStepLate") {
              mean_computation_method = ONE_STEP_LATE;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(MEAN_COMPUTATION_METHOD_sds) , "Estimate" ,
                          nb_required + i + 1 , "Computed or OneStepLate");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                    "Counting or Estimator or NbIteration or OccupancyMean");
      }
    }
  }

  if ((type != 'e') || (estimator == PARTIAL_LIKELIHOOD)) {
    if (nb_iteration_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "NbIteration");
    }

    if (occupancy_mean_option) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "OccupancyMean");
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  smarkov = seq->semi_markov_estimation(error , AMLOUTPUT , type , estimator , counting_flag ,
                                        nb_iter , mean_computation_method);

  if (smarkov) {
    STAT_model* model = new STAT_model(smarkov);
    return AMObj(AMObjType::SEMI_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une chaine de Markov d'ordre variable cachee.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateHiddenVariableOrderMarkov(const MarkovianSequences *seq ,
                                                    const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , algorithm_option = false , common_dispersion_option = false ,
       common_dispersion = false , counting_option = false , counting_flag = true ,
       global_initial_transition_option = false , global_initial_transition = true ,
       nb_iteration_option = false , min_nb_state_sequence_option = false ,
       max_nb_state_sequence_option = false , parameter_option = false ,
       state_sequences_option = false , state_sequence = true;
  register int i;
  int nb_required , algorithm = EM , nb_iter = I_DEFAULT ,
      min_nb_state_sequence = MIN_NB_STATE_SEQUENCE , max_nb_state_sequence = MAX_NB_STATE_SEQUENCE;
  double parameter = NB_STATE_SEQUENCE_PARAMETER;
  HiddenVariableOrderMarkov *ihmarkov = NULL , *hmarkov;
  StatError error;


  nb_required = 3;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
              (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
              (args.length() == nb_required + 16) || (args.length() == nb_required + 18) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // argument obligatoire  

  if (args[2].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 ,
                args[2].tag.string().data() , "HIDDEN_VARIABLE_ORDER_MARKOV");
  }
  else {
    ihmarkov = (HiddenVariableOrderMarkov*)((STAT_model*)args[2].val.p)->pt;
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Algorithm") {
        switch (algorithm_option) {

        case false : {
          algorithm_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
            if (*pstr == "EM") {
              algorithm = EM;
            }
            else if (*pstr == "MCEM") {
              algorithm = MCEM;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Estimate" ,
                          nb_required + i + 1 , "EM or MCEM");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "CommonDispersion") {
        switch (common_dispersion_option) {

        case false : {
          common_dispersion_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            common_dispersion = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
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
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            counting_flag = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "GlobalInitialTransition") {
        switch (global_initial_transition_option) {

        case false : {
          global_initial_transition_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            global_initial_transition = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "NbIteration") {
        switch (nb_iteration_option) {

        case false : {
          nb_iteration_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            nb_iter = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "MinNbStateSequence") {
        switch (min_nb_state_sequence_option) {

        case false : {
          min_nb_state_sequence_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            min_nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "MaxNbStateSequence") {
        switch (max_nb_state_sequence_option) {

        case false : {
          max_nb_state_sequence_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            max_nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Parameter") {
        switch (parameter_option) {

        case false : {
          parameter_option = true;

          switch (args[nb_required + i * 2 + 1].tag()) {
          case AMObjType::INTEGER :
            parameter = args[nb_required + i * 2 + 1].val.i;
            break;
          case AMObjType::REAL :
            parameter = args[nb_required + i * 2 + 1].val.r;
            break;
          default :
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
            break;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "StateSequences") {
        switch (state_sequences_option) {

        case false : {
          state_sequences_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            state_sequence = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" ,
                    nb_required + i + 1 , "Algorithm or CommonDispersion or Counting or GlobalInitialTransition or NbIteration or MinNbStateSequence or MaxNbStateSequence or Parameter or StateSequences");
      }
    }
  }

  if ((ihmarkov) && (((Chain*)ihmarkov)->type == 'e') && (global_initial_transition_option)) {
    status = false;
    genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "GlobalInitialTransition");
  }
  if ((algorithm != MCEM) && (min_nb_state_sequence_option)) {
    status = false;
    genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MinNbStateSequence");
  }
  if ((algorithm != MCEM) && (max_nb_state_sequence_option)) {
    status = false;
    genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MaxNbStateSequence");
  }
  if ((algorithm != MCEM) && (parameter_option)) {
    status = false;
    genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Parameter");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  switch (algorithm) {
  case EM :
    hmarkov = seq->hidden_variable_order_markov_estimation(error , AMLOUTPUT , *ihmarkov ,
                                                           global_initial_transition ,
                                                           common_dispersion , counting_flag ,
                                                           state_sequence , nb_iter);
    break;
  case MCEM :
    hmarkov = seq->hidden_variable_order_markov_stochastic_estimation(error , AMLOUTPUT , *ihmarkov ,
                                                                      global_initial_transition ,
                                                                      common_dispersion ,
                                                                      min_nb_state_sequence ,
                                                                      max_nb_state_sequence , parameter ,
                                                                      counting_flag , state_sequence , nb_iter);
    break;
  }

  if (hmarkov) {
    STAT_model* model = new STAT_model(hmarkov);
    return AMObj(AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une semi-chaine de Markov cachee.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateHiddenSemiMarkov(const MarkovianSequences *seq , const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , algorithm_option = false , common_dispersion_option = false ,
       common_dispersion = false , counting_option = false , counting_flag = true ,
       estimator_option = false , nb_iteration_option = false , min_nb_state_sequence_option = false ,
       max_nb_state_sequence_option = false , parameter_option = false , occupancy_mean_option = false ,
       state_sequences_option = false , state_sequence = true;
  register int i;
  int nb_required , algorithm = EM , estimator = COMPLETE_LIKELIHOOD , nb_iter = I_DEFAULT ,
      min_nb_state_sequence = MIN_NB_STATE_SEQUENCE , max_nb_state_sequence = MAX_NB_STATE_SEQUENCE ,
      mean_computation_method = COMPUTED;
  double parameter = NB_STATE_SEQUENCE_PARAMETER;
  HiddenSemiMarkov *hsmarkov;
  StatError error;


  CHECKCONDVA(args.length() >= 3 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  if ((args[2].tag() == AMObjType::STRING) || (args[2].tag() == AMObjType::INTEGER)) {
    char type = 'v';
    bool left_right , initial_occupancy_mean_option = false;
    int nb_state;
    double occupancy_mean = D_DEFAULT;


    nb_required = nb_required_computation(args);

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) || (args.length() == nb_required + 18) ||
                (args.length() == nb_required + 20) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Algorithm") {
          switch (algorithm_option) {

          case false : {
            algorithm_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "EM") {
                algorithm = EM;
              }
              else if (*pstr == "MCEM") {
                algorithm = MCEM;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "EM or MCEM");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "CommonDispersion") {
          switch (common_dispersion_option) {

          case false : {
            common_dispersion_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              common_dispersion = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              counting_flag = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Estimator") {
          switch (estimator_option) {

          case false : {
            estimator_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "CompleteLikelihood") {
                estimator = COMPLETE_LIKELIHOOD;
              }
              else if (*pstr == "PartialLikelihood") {
                estimator = PARTIAL_LIKELIHOOD;
              }
              else if (*pstr == "KaplanMeier") {
                estimator = KAPLAN_MEIER;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "CompleteLikelihood or PartialLikelihood");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "InitialOccupancyMean") {
          switch (initial_occupancy_mean_option) {

          case false : {
            initial_occupancy_mean_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              occupancy_mean = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              occupancy_mean = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "NbIteration") {
          switch (nb_iteration_option) {

          case false : {
            nb_iteration_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              nb_iter = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MinNbStateSequence") {
          switch (min_nb_state_sequence_option) {

          case false : {
            min_nb_state_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              min_nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MaxNbStateSequence") {
          switch (max_nb_state_sequence_option) {

          case false : {
            max_nb_state_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              max_nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Parameter") {
          switch (parameter_option) {

          case false : {
            parameter_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              parameter = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              parameter = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "OccupancyMean") {
          switch (occupancy_mean_option) {

          case false : {
            occupancy_mean_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Computed") {
                mean_computation_method = COMPUTED;
              }
              else if (*pstr == "OneStepLate") {
                mean_computation_method = ONE_STEP_LATE;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(MEAN_COMPUTATION_METHOD_sds) , "Estimate" ,
                            nb_required + i + 1 , "Computed or OneStepLate");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "StateSequences") {
          switch (state_sequences_option) {

          case false : {
            state_sequences_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              state_sequence = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                      "Algorithm or CommonDispersion or Counting or InitialOccupancyMean or Estimator or NbIteration or MinNbStateSequence or MaxNbStateSequence or Parameter or OccupancyMean or StateSequences");
        }
      }
    }

    if ((algorithm != EM) && (estimator == KAPLAN_MEIER)) {
      estimator = COMPLETE_LIKELIHOOD;
    }
    if ((algorithm != MCEM) && (min_nb_state_sequence_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MinNbStateSequence");
    }
    if ((algorithm != MCEM) && (max_nb_state_sequence_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MaxNbStateSequence");
    }
    if ((algorithm != MCEM) && (parameter_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Parameter");
    }

    CHECKCONDVA(nb_required >= 4 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    // arguments obligatoires

    if (args[2].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 ,
                  args[2].tag.string().data() , "STRING");
    }
    else {
      pstr = (AMString*)args[2].val.p;
      if (*pstr == "Ordinary") {
        type = 'o';
      }
      else if (*pstr == "Equilibrium") {
        type = 'e';
      }
      else {
        status = false;
        genAMLError(ERRORMSG(STOCHASTIC_PROCESS_TYPE_sds) , "Estimate" , 3 ,
                    "Ordinary or Equilibrium");
      }
    }

    if (args[3].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 4 ,
                  args[3].tag.string().data() , "INT");
    }
    else {
      nb_state = args[3].val.i;
    }

    CHECKCONDVA(((type == 'o') && (nb_required == 5)) ||
                ((type == 'e') && (nb_required == 4)) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    switch (type) {

    case 'o' : {
      if (args[4].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 5 ,
                    args[4].tag.string().data() , "STRING");
      }
      else {
        pstr = (AMString*)args[4].val.p;
        if (*pstr == "Irreducible") {
          left_right = false;
        }
        else if (*pstr == "LeftRight") {
          left_right = true;
        }
        else {
          status = false;
          genAMLError(ERRORMSG(MARKOV_CHAIN_TYPE_sds) , "Estimate" , 5 ,
                      "Irreducible or LeftRight");
        }
      }
      break;
    }

    case 'e' : {
      left_right = false;
      break;
    }
    }

    if (((type != 'e') || (estimator == PARTIAL_LIKELIHOOD) || (algorithm != EM)) &&
        (occupancy_mean_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "OccupancyMean");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (algorithm) {
    case EM :
      hsmarkov = seq->hidden_semi_markov_estimation(error , AMLOUTPUT , type , nb_state ,
                                                    left_right , occupancy_mean , common_dispersion ,
                                                    estimator , counting_flag , state_sequence ,
                                                    nb_iter , mean_computation_method);
      break;
    case MCEM :
      hsmarkov = seq->hidden_semi_markov_stochastic_estimation(error , AMLOUTPUT , type , nb_state ,
                                                               left_right , occupancy_mean , common_dispersion ,
                                                               min_nb_state_sequence , max_nb_state_sequence ,
                                                               parameter , estimator , counting_flag ,
                                                               state_sequence , nb_iter);
      break;
    }
  }

  else if (args[2].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
    HiddenSemiMarkov *ihsmarkov = NULL;


    nb_required = 3;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) || (args.length() == nb_required + 18) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    ihsmarkov = (HiddenSemiMarkov*)((STAT_model*)args[2].val.p)->pt;

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Algorithm") {
          switch (algorithm_option) {

          case false : {
            algorithm_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "EM") {
                algorithm = EM;
              }
              else if (*pstr == "MCEM") {
                algorithm = MCEM;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "EM or MCEM");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "CommonDispersion") {
          switch (common_dispersion_option) {

          case false : {
            common_dispersion_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              common_dispersion = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              counting_flag = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Estimator") {
          switch (estimator_option) {

          case false : {
            estimator_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "CompleteLikelihood") {
                estimator = COMPLETE_LIKELIHOOD;
              }
              else if (*pstr == "PartialLikelihood") {
                estimator = PARTIAL_LIKELIHOOD;
              }
              else if (*pstr == "KaplanMeier") {
                estimator = KAPLAN_MEIER;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "Estimate" ,
                            nb_required + i + 1 , "CompleteLikelihood or PartialLikelihood");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "NbIteration") {
          switch (nb_iteration_option) {

          case false : {
            nb_iteration_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              nb_iter = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MinNbStateSequence") {
          switch (min_nb_state_sequence_option) {

          case false : {
            min_nb_state_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              min_nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "MaxNbStateSequence") {
          switch (max_nb_state_sequence_option) {

          case false : {
            max_nb_state_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              max_nb_state_sequence = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Parameter") {
          switch (parameter_option) {

          case false : {
            parameter_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              parameter = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              parameter = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "OccupancyMean") {
          switch (occupancy_mean_option) {

          case false : {
            occupancy_mean_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Computed") {
                mean_computation_method = COMPUTED;
              }
              else if (*pstr == "OneStepLate") {
                mean_computation_method = ONE_STEP_LATE;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(MEAN_COMPUTATION_METHOD_sds) , "Estimate" ,
                            nb_required + i + 1 , "Computed or OneStepLate");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "StateSequences") {
          switch (state_sequences_option) {

          case false : {
            state_sequences_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              state_sequence = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + i + 1 ,
                      "Algorithm or CommonDispersion or Counting or Estimator or NbIteration or MinNbStateSequence or MaxNbStateSequence or Parameter or OccupancyMean or StateSequences");
        }
      }
    }

    if ((algorithm != EM) && (estimator == KAPLAN_MEIER)) {
      estimator = COMPLETE_LIKELIHOOD;
    }
    if ((algorithm != MCEM) && (min_nb_state_sequence_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MinNbStateSequence");
    }
    if ((algorithm != MCEM) && (max_nb_state_sequence_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "MaxNbStateSequence");
    }
    if ((algorithm != MCEM) && (parameter_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "Parameter");
    }
    if ((((ihsmarkov) && (((Chain*)ihsmarkov)->type == 'o')) || (estimator == PARTIAL_LIKELIHOOD) ||
         (algorithm != EM)) && (occupancy_mean_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Estimate" , "OccupancyMean");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (algorithm) {
    case EM :
      hsmarkov = seq->hidden_semi_markov_estimation(error , AMLOUTPUT , *ihsmarkov , common_dispersion ,
                                                    estimator , counting_flag , state_sequence ,
                                                    nb_iter , mean_computation_method);
      break;
    case MCEM :
      hsmarkov = seq->hidden_semi_markov_stochastic_estimation(error , AMLOUTPUT , *ihsmarkov ,
                                                               common_dispersion , min_nb_state_sequence ,
                                                               max_nb_state_sequence , parameter , estimator ,
                                                               counting_flag , state_sequence , nb_iter);
      break;
    }
  }

  else {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 ,
                args[2].tag.string().data() , "STRING or INT or HIDDEN_SEMI-MARKOV");
    return AMObj(AMObjType::ERROR);
  }

  if (hsmarkov) {
    STAT_model* model = new STAT_model(hsmarkov);
    return AMObj(AMObjType::HIDDEN_SEMI_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une chaine de Markov non-homogene.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateNonhomogeneousMarkov(const MarkovianSequences *seq , const AMObjVector &args)

{
  bool status = true , counting_flag = true;
  register int i , j;
  int nb_required , nb_state = seq->get_marginal_distribution(0)->nb_value , *ident;
  NonhomogeneousMarkov *markov;
  RWCString *pstr;
  StatError error;


  nb_required = 2 + nb_state;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // arguments obligatoires

  ident = new int[nb_state];

  for (i = 0;i < nb_state;i++) {
    if (args[2 + i].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 3 + i ,
                  args[2 + i].tag.string().data() , "STRING");
    }

    else {
      pstr = (AMString*)args[2 + i].val.p;
      if (*pstr == "VOID") {
        ident[i] = I_DEFAULT;
      }
      else {
        for (j = 1;j < 3;j++) {
          if (*pstr == STAT_function_word[j]) {
            ident[i] = j;
            break;
          }
        }

        if (j == 3) {
          status = false;
          genAMLError(ERRORMSG(FUNCTION_NAME_sds) , "Estimate" , 3 + i ,
                      "VOID or MONOMOLECULAR or LOGISTIC");
        }
      }
    }
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Counting") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" , nb_required + 1 ,
                    "Counting");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::BOOL) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "BOOL");
    }
    else {
      counting_flag = args[nb_required + 1].val.b;
    }
  }

  if (!status) {
    delete [] ident;
    return AMObj(AMObjType::ERROR);
  }

  markov = seq->nonhomogeneous_markov_estimation(error , ident , counting_flag);
  delete [] ident;

  if (markov) {
    STAT_model* model = new STAT_model(markov);
    return AMObj(AMObjType::NONHOMOGENEOUS_MARKOV , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'une cime.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_EstimateTopParameters(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , min_position_option = false , max_position_option = false ,
       neighborhood_option = false , equal_probability_option = false , equal_proba = false;
  register int i;
  int nb_required , min_position = 1 , max_position = ((Tops*)((STAT_model*)args[0].val.p)->pt)->get_max_position() ,
      neighborhood = 1;
  TopParameters *param;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "MinPosition") {
        switch (min_position_option) {

        case false : {
          min_position_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            min_position = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "MaxPosition") {
        switch (max_position_option) {

        case false : {
          max_position_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            max_position = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Neighborhood") {
        switch (neighborhood_option) {

        case false : {
          neighborhood_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            neighborhood = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "EqualProbability") {
        switch (equal_probability_option) {

        case false : {
          equal_probability_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            equal_proba = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Estimate" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Estimate" ,
                    nb_required + i + 1 , "MinPosition or MaxPosition or Neighborhood or EqualProbability");
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  param = ((Tops*)((STAT_model*)args[0].val.p)->pt)->estimation(error , min_position , max_position ,
                                                                neighborhood , equal_proba);

  if (param) {
    STAT_model* model = new STAT_model(param);
    return AMObj(AMObjType::TOP_PARAMETERS , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Estimate");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Estimation des parametres d'un modele.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Estimate(const AMObjVector &args)

{
  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

  // estimation processus de renouvellement

  if ((args[0].tag() == AMObjType::TIME_EVENTS) || (args[0].tag() == AMObjType::RENEWAL_DATA) ||
      ((args.length() >= 3) && (args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) &&
       (args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) && (args[2].tag() == AMObjType::FREQUENCY_DISTRIBUTION))) {
    if ((args.length() >= 2) && (args[0].tag() != AMObjType::FREQUENCY_DISTRIBUTION) && (args[1].tag() == AMObjType::STRING)) {
      return STAT_EstimateRenewalCountData(args);
    }

    return STAT_EstimateRenewalIntervalData(args);
  }

  // estimation loi/combinaisons de lois

  if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
      (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
    RWCString *pstr;
    register int i;
    int model = I_DEFAULT , ident;
    const FrequencyDistribution *histo;


    CHECKCONDVA(args.length() >= 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

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

    // type du modele

    CHECKCONDVA(args[1].tag() == AMObjType::STRING ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 2 ,
                            args[1].tag.string().data() , "STRING"));

    pstr = (AMString*)args[1].val.p;
    for (i = CATEGORICAL;i <= NEGATIVE_BINOMIAL;i++) {
      if ((*pstr == STAT_discrete_distribution_word[i]) ||
          (*pstr == STAT_discrete_distribution_letter[i])) {
        ident = i;
        model = STATM_DISTRIBUTION;
        break;
      }
    }

    if (i == NEGATIVE_BINOMIAL + 1) {
      if (*pstr == STAT_model_name[STATM_DISCRETE_MIXTURE]) {
        model = STATM_DISCRETE_MIXTURE;
      }
      else if (*pstr == STAT_model_name[STATM_CONVOLUTION]) {
        model = STATM_CONVOLUTION;
      }
      else if (*pstr == STAT_model_name[STATM_COMPOUND]) {
        model = STATM_COMPOUND;
      }
      else {
        genAMLError(ERRORMSG(MODEL_NAME_sd) , "Estimate" , 2);
        return AMObj(AMObjType::ERROR);
      }
    }

    switch (model) {
    case STATM_DISTRIBUTION :
      return STAT_EstimateDistribution(histo , ident , args);
    case STATM_DISCRETE_MIXTURE :
      return STAT_EstimateDiscreteMixture(histo , args);
    case STATM_CONVOLUTION :
      return STAT_EstimateConvolution(histo , args);
    case STATM_COMPOUND :
      return STAT_EstimateCompound(histo , args);
    }
  }

  // estimation melanges multivaries

  if ((args[0].tag() == AMObjType::VECTORS) ||
      (args[0].tag() == AMObjType::MIXTURE_DATA)) {
    const Vectors *vec;


    switch (args[0].tag()) {
    case AMObjType::VECTORS :
      vec = (Vectors*)((STAT_model*)args[0].val.p)->pt;
      break;
    case AMObjType::MIXTURE_DATA :
      vec = (MixtureData*)((STAT_model*)args[0].val.p)->pt;
      break;
    }

    return STAT_EstimateMixture(vec , args);
  }

  // estimation processus markoviens

  if ((args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
      (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) {
    RWCString *pstr;
    int model = I_DEFAULT;
    const MarkovianSequences *seq;


    CHECKCONDVA(args.length() >= 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Estimate"));

    switch (args[0].tag()) {
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

    // type du modele

    CHECKCONDVA(args[1].tag() == AMObjType::STRING ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Estimate" , 2 ,
                            args[1].tag.string().data() , "STRING"));

    pstr = (AMString*)args[1].val.p;
    if (*pstr == STAT_model_name[STATM_VARIABLE_ORDER_MARKOV]) {
      model = STATM_VARIABLE_ORDER_MARKOV;
    }
    else if (*pstr == STAT_model_name[STATM_SEMI_MARKOV]) {
      model = STATM_SEMI_MARKOV;
    }
    else if (*pstr == STAT_model_name[STATM_HIDDEN_VARIABLE_ORDER_MARKOV]) {
      model = STATM_HIDDEN_VARIABLE_ORDER_MARKOV;
    }
    else if (*pstr == STAT_model_name[STATM_HIDDEN_SEMI_MARKOV]) {
      model = STATM_HIDDEN_SEMI_MARKOV;
    }
    else if (*pstr == STAT_model_name[STATM_NONHOMOGENEOUS_MARKOV]) {
      model = STATM_NONHOMOGENEOUS_MARKOV;
    }
    else {
      genAMLError(ERRORMSG(MODEL_NAME_sd) , "Estimate" , 2);
      return AMObj(AMObjType::ERROR);
    }

    switch (model) {
    case STATM_VARIABLE_ORDER_MARKOV :
      return STAT_EstimateVariableOrderMarkov(seq , args);
    case STATM_SEMI_MARKOV :
      return STAT_EstimateSemiMarkov(seq , args);
    case STATM_HIDDEN_VARIABLE_ORDER_MARKOV :
      return STAT_EstimateHiddenVariableOrderMarkov(seq , args);
    case STATM_HIDDEN_SEMI_MARKOV :
      return STAT_EstimateHiddenSemiMarkov(seq , args);
    case STATM_NONHOMOGENEOUS_MARKOV :
      return STAT_EstimateNonhomogeneousMarkov(seq , args);
    }
  }

  // estimation des parametres d'une cime

  if (args[0].tag() == AMObjType::TOPS) {
    return STAT_EstimateTopParameters(args);
  }

  genAMLError(ERRORMSG(STAT_DATA_TYPE_sds) , "Estimate" , 1 , args[0].tag.string().data());
  return AMObj(AMObjType::ERROR);
}

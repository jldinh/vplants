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
 *       $Id: stat_funs5.cpp 16620 2014-05-21 09:40:46Z guedon $
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
extern int* buildIntArray(const AMObjVector &args , int arg_index , const char *function ,
                          int output_index , int &nb_element);
extern double* buildRealArray(const AMObjVector &args , int arg_index , const char *function ,
                              int output_index , int &nb_element , bool filter);

extern AMObj STAT_ThresholdingData(const AMObjVector &args);



/*--------------------------------------------------------------*
 *
 *  Simulation d'un modele.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Simulate(const AMObjVector &args)

{
  StatError error;


  CHECKCONDVA(args.length() >= 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Simulate"));

  if (args[0].tag() == AMObjType::DISTRIBUTION) {
    DiscreteDistributionData *histo;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 2));
    CHECKCONDVA(args[1].tag() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
                            args[1].tag.string().data() , "INT"));

    histo = ((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i);

    if (histo) {
      STAT_model* model = new STAT_model(histo);
      return AMObj(AMObjType::FREQUENCY_DISTRIBUTION , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::DISCRETE_MIXTURE) {
    DiscreteMixtureData *mixt_histo;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 2));
    CHECKCONDVA(args[1].tag() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
                            args[1].tag.string().data() , "INT"));

    mixt_histo = ((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i);

    if (mixt_histo) {
      STAT_model* model = new STAT_model(mixt_histo);
      return AMObj(AMObjType::DISCRETE_MIXTURE_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::CONVOLUTION) {
    ConvolutionData *convol_histo;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 2));
    CHECKCONDVA(args[1].tag() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
                            args[1].tag.string().data() , "INT"));

    convol_histo = ((Convolution*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i);

    if (convol_histo) {
      STAT_model* model = new STAT_model(convol_histo);
      return AMObj(AMObjType::CONVOLUTION_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::COMPOUND) {
    CompoundData *compound_histo;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 2));
    CHECKCONDVA(args[1].tag() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
                            args[1].tag.string().data() , "INT"));

    compound_histo = ((Compound*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i);

    if (compound_histo) {
      STAT_model* model = new STAT_model(compound_histo);
      return AMObj(AMObjType::COMPOUND_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::MIXTURE) {
    MixtureData *vec;


    CHECKCONDVA(args.length() == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 2));
    CHECKCONDVA(args[1].tag() == AMObjType::INTEGER ,
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
                            args[1].tag.string().data() , "INT"));

    vec = ((Mixture*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i);

    if (vec) {
      STAT_model* model = new STAT_model(vec);
      return AMObj(AMObjType::MIXTURE_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::RENEWAL) {
    RWCString *pstr;
    char type;
    bool status = true;
    RenewalData *timev;


    CHECKCONDVA(args.length() >= 3 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Simulate"));

    if (args[1].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
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
        genAMLError(ERRORMSG(STOCHASTIC_PROCESS_TYPE_sds) , "Simulate" , 2 ,
                    "Ordinary or Equilibrium");
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    if ((args[2].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[2].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[2].tag() == AMObjType::CONVOLUTION_DATA) || (args[2].tag() == AMObjType::COMPOUND_DATA)) {
      const FrequencyDistribution *htime;


      CHECKCONDVA(args.length() == 3 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 3));

      switch (args[2].tag()) {
      case AMObjType::FREQUENCY_DISTRIBUTION :
        htime = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[2].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE_DATA :
        htime = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[2].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION_DATA :
        htime = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[2].val.p)->pt);
        break;
      case AMObjType::COMPOUND_DATA :
        htime = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[2].val.p)->pt);
        break;
      }

      timev = ((Renewal*)((STAT_model*)args[0].val.p)->pt)->simulation(error , type , *htime);
    }

    else if (args[2].tag() == AMObjType::INTEGER) {
      CHECKCONDVA(args.length() == 4 ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Simulate" , 4));

      if (args[3].tag() == AMObjType::INTEGER) {
        timev = ((Renewal*)((STAT_model*)args[0].val.p)->pt)->simulation(error , type , args[2].val.i , args[3].val.i);
      }

      else if ((args[3].tag() == AMObjType::TIME_EVENTS) || (args[3].tag() == AMObjType::RENEWAL_DATA)) {
        const TimeEvents *itimev;


        switch (args[3].tag()) {
        case AMObjType::TIME_EVENTS :
          itimev = (TimeEvents*)((STAT_model*)args[3].val.p)->pt;
          break;
        case AMObjType::RENEWAL_DATA :
          itimev = (RenewalData*)((STAT_model*)args[3].val.p)->pt;
          break;
        }

        timev = ((Renewal*)((STAT_model*)args[0].val.p)->pt)->simulation(error , type , args[2].val.i , *itimev);
      }

      else {
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 4 ,
                    args[3].tag.string().data() , "INT or TIME_EVENTS or RENEWAL_DATA");
        return AMObj(AMObjType::ERROR);
      }
    }

    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 3 , args[2].tag.string().data() ,
                  "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA or INT");
      return AMObj(AMObjType::ERROR);
    }

    if (timev) {
      STAT_model* model = new STAT_model(timev);
      return AMObj(AMObjType::RENEWAL_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if ((args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
      (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
      (args[0].tag() == AMObjType::SEMI_MARKOV) || (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) ||
      (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV)) {
    bool status , counting_flag = true;
    int nb_required;
    VariableOrderMarkovData *variable_order_markov_seq = NULL;
    SemiMarkovData *semi_markov_seq = NULL;
    NonhomogeneousMarkovData *nonhomogeneous_markov_seq = NULL;


    if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
      nb_required = 2;
    }
    else {
      nb_required = 3;
    }

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Simulate"));

    // argument optionnel

    if (args.length() == nb_required + 2) {
      status = true;

      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "Counting") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Simulate" , nb_required + 1 ,
                      "Counting");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::BOOL) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "BOOL");
      }
      else {
        counting_flag = args[nb_required + 1].val.b;
      }

      if ((args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
          (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
          (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV)) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Simulate" , "Counting");
      }

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
    }

    if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
      const FrequencyDistribution *hlength;


      switch (args[1].tag()) {
      case AMObjType::FREQUENCY_DISTRIBUTION :
        hlength = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[1].val.p)->pt);
        break;
      case AMObjType::DISCRETE_MIXTURE_DATA :
        hlength = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[1].val.p)->pt);
        break;
      case AMObjType::CONVOLUTION_DATA :
        hlength = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[1].val.p)->pt);
        break;
      case AMObjType::COMPOUND_DATA :
        hlength = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[1].val.p)->pt);
        break;
      }

      switch (args[0].tag()) {
      case AMObjType::VARIABLE_ORDER_MARKOV :
        variable_order_markov_seq = ((VariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error ,
                                                                                                         *hlength);
        break;
      case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV :
        variable_order_markov_seq = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error ,
                                                                                                               *hlength);
        break;
      case AMObjType::SEMI_MARKOV :
        semi_markov_seq = ((SemiMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , *hlength ,
                                                                                      counting_flag);
        break;
      case AMObjType::HIDDEN_SEMI_MARKOV :
        semi_markov_seq = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , *hlength ,
                                                                                            counting_flag);
        break;
      case AMObjType::NONHOMOGENEOUS_MARKOV :
        nonhomogeneous_markov_seq = ((NonhomogeneousMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error ,
                                                                                                          *hlength);
        break;
      }
    }

    else if (args[1].tag() == AMObjType::INTEGER) {
      if (args[2].tag() == AMObjType::INTEGER) {
        switch (args[0].tag()) {
        case AMObjType::VARIABLE_ORDER_MARKOV :
          variable_order_markov_seq = ((VariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                                           args[2].val.i);
          break;
        case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV :
          variable_order_markov_seq = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                                                 args[2].val.i);
          break;
        case AMObjType::SEMI_MARKOV :
          semi_markov_seq = ((SemiMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                        args[2].val.i , counting_flag);
          break;
        case AMObjType::HIDDEN_SEMI_MARKOV :
          semi_markov_seq = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                              args[2].val.i , counting_flag);
          break;
        case AMObjType::NONHOMOGENEOUS_MARKOV :
          nonhomogeneous_markov_seq = ((NonhomogeneousMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                                            args[2].val.i);
          break;
        }
      }

      else if ((args[2].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
               (args[2].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
               (args[2].tag() == AMObjType::SEMI_MARKOV_DATA) ||
               (args[2].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) {
        const MarkovianSequences *iseq;


        switch (args[2].tag()) {
        case AMObjType::MARKOVIAN_SEQUENCES :
          iseq = (MarkovianSequences*)((STAT_model*)args[2].val.p)->pt;
          break;
        case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
          iseq = (VariableOrderMarkovData*)((STAT_model*)args[2].val.p)->pt;
          break;
        case AMObjType::SEMI_MARKOV_DATA :
          iseq = (SemiMarkovData*)((STAT_model*)args[2].val.p)->pt;
          break;
        case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
          iseq = (NonhomogeneousMarkovData*)((STAT_model*)args[2].val.p)->pt;
          break;
        }

        switch (args[0].tag()) {
        case AMObjType::VARIABLE_ORDER_MARKOV :
          variable_order_markov_seq = ((VariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                                           *iseq);
          break;
        case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV :
          variable_order_markov_seq = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                                                 *iseq);
          break;
        case AMObjType::SEMI_MARKOV :
          semi_markov_seq = ((SemiMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                        *iseq , counting_flag);
          break;
        case AMObjType::HIDDEN_SEMI_MARKOV :
          semi_markov_seq = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                              *iseq , counting_flag);
          break;
        case AMObjType::NONHOMOGENEOUS_MARKOV :
          nonhomogeneous_markov_seq = ((NonhomogeneousMarkov*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                                                            *iseq);
          break;
        }
      }

      else {
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 3 , args[2].tag.string().data() ,
                    "INT or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
        return AMObj(AMObjType::ERROR);
      }
    }

    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 , args[1].tag.string().data() ,
                  "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA or INT");
      return AMObj(AMObjType::ERROR);
    }

    if (variable_order_markov_seq) {
      STAT_model* model = new STAT_model(variable_order_markov_seq);
      return AMObj(AMObjType::VARIABLE_ORDER_MARKOV_DATA , model);
    }
    else if (semi_markov_seq) {
      STAT_model* model = new STAT_model(semi_markov_seq);
      return AMObj(AMObjType::SEMI_MARKOV_DATA , model);
    }
    else if (nonhomogeneous_markov_seq) {
      STAT_model* model = new STAT_model(nonhomogeneous_markov_seq);
      return AMObj(AMObjType::NONHOMOGENEOUS_MARKOV_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  if (args[0].tag() == AMObjType::TOP_PARAMETERS) {
    bool status = true;
    int nb_required , nb_axillary = 1;
    Tops *tops;


    nb_required = 3;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Simulate"));

    // argument obligatoire

    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 2 ,
                  args[1].tag.string().data() , "INT");
    }
    if (args[2].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , 3 ,
                  args[2].tag.string().data() , "INT");
    }

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "NbAxillary") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Simulate" , nb_required + 1 ,
                      "NbAxillary");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Simulate" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "INT");
      }
      else {
        nb_axillary = args[nb_required + 1].val.i;
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    tops = ((TopParameters*)((STAT_model*)args[0].val.p)->pt)->simulation(error , args[1].val.i ,
                                                                          args[2].val.i , nb_axillary);

    if (tops) {
      STAT_model* model = new STAT_model(tops);
      return AMObj(AMObjType::TOPS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Simulate");
      return AMObj(AMObjType::ERROR);
    }
  }

  genAMLError(ERRORMSG(STAT_MODEL_TYPE_sds) , "Simulate" , 1 , args[0].tag.string().data());
  return AMObj(AMObjType::ERROR);
}


/*--------------------------------------------------------------*
 *
 *  Comparaison de lois empiriques.
 *
 *--------------------------------------------------------------*/

AMObj STAT_CompareFrequencyDistributions(const AMObjVector &args)

{
  RWCString *pstr;
  char *file_name = NULL , format = 'a';
  bool status = true , file_name_option = false , format_option = false;
  register int i;
  int nb_required , type;
  const FrequencyDistribution **histo;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required >= 3 , genAMLError(ERRORMSG(NB_FREQUENCY_DISTRIBUTION_s) , "Compare"));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

  // arguments obligatoires

  histo = new const FrequencyDistribution*[nb_required - 1];

  switch (args[0].tag()) {
  case AMObjType::FREQUENCY_DISTRIBUTION :
    histo[0] = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[0].val.p)->pt);
    break;
  case AMObjType::DISCRETE_MIXTURE_DATA :
    histo[0] = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[0].val.p)->pt);
    break;
  case AMObjType::CONVOLUTION_DATA :
    histo[0] = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[0].val.p)->pt);
    break;
  case AMObjType::COMPOUND_DATA :
    histo[0] = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[0].val.p)->pt);
    break;
  }

  for (i = 1;i < nb_required - 1;i++) {
    switch (args[i].tag()) {
    case AMObjType::FREQUENCY_DISTRIBUTION :
      histo[i] = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[i].val.p)->pt);
      break;
    case AMObjType::DISCRETE_MIXTURE_DATA :
      histo[i] = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[i].val.p)->pt);
      break;
    case AMObjType::CONVOLUTION_DATA :
      histo[i] = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[i].val.p)->pt);
      break;
    case AMObjType::COMPOUND_DATA :
      histo[i] = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[i].val.p)->pt);
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i + 1 , args[i].tag.string().data() ,
                  "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
    }
  }

  if (args[nb_required - 1].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required ,
                args[nb_required - 1].tag.string().data() , "STRING");
  }

  else {
    pstr = (AMString*)args[nb_required - 1].val.p;
    for (i = SYMBOLIC;i <= NUMERIC;i++) {
      if ((*pstr == STAT_variable_type_word[i]) || (*pstr == STAT_variable_type_letter[i])) {
        type = i;
        break;
      }
    }

    if (i == NUMERIC + 1) {
      status = false;
      genAMLError(ERRORMSG(VARIABLE_TYPE_sds) , "Compare" , nb_required ,
                  "SYMBOLIC(S) or ORDINAL(O) or NUMERIC(N)");
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "FileName") {
        switch (file_name_option) {

        case false : {
          file_name_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
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
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "ASCII") {
              format = 'a';
            }
            else if (*pstr == "SpreadSheet") {
              format = 's';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Compare" ,
                          nb_required + i + 1 , "ASCII or SpreadSheet");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" ,
                    nb_required + i + 1 , "FileName or Format");
      }
    }
  }

  if ((format_option) && (!file_name_option)) {
    status = false;
    genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "Compare");
  }

  if (!status) {
    delete [] histo;
    return AMObj(AMObjType::ERROR);
  }

  status = histo[0]->comparison(error , AMLOUTPUT , nb_required - 2 , histo + 1 , type ,
                                file_name , format);
  delete [] histo;

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Comparaison de vecteurs.
 *
 *--------------------------------------------------------------*/

AMObj STAT_CompareVectors(const AMObjVector &args)

{
  bool status = true , standardization = true;
  int nb_required;
  DistanceMatrix *dist_matrix;
  StatError error;


  nb_required = 2;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Compare" , 2));

  // argument obligatoire

  if (args[1].tag() != AMObjType::VECTOR_DISTANCE) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 ,
                args[1].tag.string().data() , "VECTOR_DISTANCE");
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Standardization") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" , nb_required + 1 ,
                    "Standardization");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::BOOL) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "BOOL");
    }
    else {
      standardization = args[nb_required + 1].val.b;
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  dist_matrix = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->comparison(error , *((VectorDistance*)((STAT_model*)args[1].val.p)->pt) , standardization);

  if (dist_matrix) {
    STAT_model* model = new STAT_model(dist_matrix);
    return AMObj(AMObjType::DISTANCE_MATRIX , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Alignement de sequences.
 *
 *--------------------------------------------------------------*/

AMObj STAT_CompareSequences(const AMObjVector &args)

{
  RWCString *pstr;
  char *file_name = NULL , format = 'a' , *alignment_file_name = NULL , alignment_format = 'a';
  bool status = true , ref_sequence_option = false , test_sequence_option = false , begin_option = false ,
       begin_free = false , end_option = false , end_free = false , file_name_option = false ,
       format_option = false , alignment_file_name_option = false , alignment_format_option = false;
  register int i;
  int nb_required , ref_identifier = I_DEFAULT , test_identifier = I_DEFAULT;
  const Sequences *iseq;
  Sequences *seq;
  DistanceMatrix *dist_matrix;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA((nb_required == 1) || (nb_required == 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

  // argument obligatoire

  switch (args[0].tag()) {
  case AMObjType::SEQUENCES :
    iseq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::MARKOVIAN_SEQUENCES :
    iseq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
    iseq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::SEMI_MARKOV_DATA :
    iseq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::NONHOMOGENEOUS_MARKOV_DATA :
    iseq = (NonhomogeneousMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 1 , args[0].tag.string().data() ,
                "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    break;
  }

  switch (nb_required) {

  case 1 : {
    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "RefSequence") {
          switch (ref_sequence_option) {

          case false : {
            ref_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              ref_identifier = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "TestSequence") {
          switch (test_sequence_option) {

          case false : {
            test_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              test_identifier = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Begin") {
          switch (begin_option) {

          case false : {
            begin_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Aligned") {
                begin_free = false;
              }
              else if (*pstr == "Free") {
                begin_free = true;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(BEGIN_END_SPECIFICATION_sds) , "Compare" ,
                            nb_required + i + 1 , "Aligned or Free");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "End") {
          switch (end_option) {

          case false : {
            end_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Aligned") {
                end_free = false;
              }
              else if (*pstr == "Free") {
                end_free = true;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(BEGIN_END_SPECIFICATION_sds) , "Compare" ,
                            nb_required + i + 1 , "Aligned or Free");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "FileName") {
          switch (file_name_option) {

          case false : {
            file_name_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "ASCII") {
                format = 'a';
              }
              else if (*pstr == "SpreadSheet") {
                format = 's';
              }
              else {
                status = false;
                genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Compare" ,
                            nb_required + i + 1 , "ASCII or SpreadSheet");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "AlignmentFileName") {
          switch (alignment_file_name_option) {

          case false : {
            alignment_file_name_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              alignment_file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "AlignmentFormat") {
          switch (alignment_format_option) {

          case false : {
            alignment_format_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "ASCII") {
                alignment_format = 'a';
              }
/*              else if (*pstr == "Binary") {
                alignment_format = 'b';
              } */
              else {
                status = false;
                genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Compare" ,
                            nb_required + i + 1 , "ASCII");
//                            nb_required + i + 1 , "ASCII or Binary");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" , nb_required + i + 1 ,
                      "RefSequence or TestSequence or Begin or End or FileName or Format or AlignmentFileName or AlignmentFormat");
        }
      }
    }

    if ((format_option) && (!file_name_option)) {
      status = false;
      genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "Compare");
    }

    if ((alignment_format_option) && (!alignment_file_name_option)) {
      status = false;
      genAMLError(ERRORMSG(MISSING_ALIGNMENT_FILE_NAME_OPTION_s) , "Compare");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    dist_matrix = iseq->alignment(error , &AMLOUTPUT , ref_identifier , test_identifier , begin_free ,
                                  end_free , file_name , format , alignment_file_name , alignment_format);

    if (dist_matrix) {
      STAT_model* model = new STAT_model(dist_matrix);
      return AMObj(AMObjType::DISTANCE_MATRIX , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case 2 : {
    char output = 'm';
    bool output_option= false , indel_cost_option = false , indel_factor_option = false ,
         transposition_option = false , transposition = false , transposition_factor_option = false ,
         algorithm_option = false;
    int indel_cost = ADAPTATIVE , algorithm = AGGLOMERATIVE;
    double indel_factor , transposition_factor = TRANSPOSITION_FACTOR;
    MarkovianSequences *markovian_seq;


    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) || (args.length() == nb_required + 10) ||
                (args.length() == nb_required + 12) || (args.length() == nb_required + 14) ||
                (args.length() == nb_required + 16) || (args.length() == nb_required + 18) ||
                (args.length() == nb_required + 20) || (args.length() == nb_required + 22) ||
                (args.length() == nb_required + 24) || (args.length() == nb_required + 26) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

    // argument obligatoire

    if (args[1].tag() != AMObjType::VECTOR_DISTANCE) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 ,
                  args[1].tag.string().data() , "VECTOR_DISTANCE");
    }

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                    args[nb_required + i * 2].tag.string().data() , "OPTION");
      }

      else {
        pstr = (AMString*)args[nb_required + i * 2].val.p;

        if (*pstr == "Output") {
          switch (output_option) {

          case false : {
            output_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "DistanceMatrix") {
                output = 'm';
              }
              else if (*pstr == "Sequences") {
                output = 's';
              }
              else {
                status = false;
                genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Compare" ,
                            nb_required + i + 1 , "DistanceMatrix or Sequences");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "RefSequence") {
          switch (ref_sequence_option) {

          case false : {
            ref_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              ref_identifier = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "TestSequence") {
          switch (test_sequence_option) {

          case false : {
            test_sequence_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT");
            }
            else {
              test_identifier = args[nb_required + i * 2 + 1].val.i;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Begin") {
          switch (begin_option) {

          case false : {
            begin_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Aligned") {
                begin_free = false;
              }
              else if (*pstr == "Free") {
                begin_free = true;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(BEGIN_END_SPECIFICATION_sds) , "Compare" ,
                            nb_required + i + 1 , "Aligned or Free");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "End") {
          switch (end_option) {

          case false : {
            end_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Aligned") {
                end_free = false;
              }
              else if (*pstr == "Free") {
                end_free = true;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(BEGIN_END_SPECIFICATION_sds) , "Compare" ,
                            nb_required + i + 1 , "Aligned or Free");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "IndelCost") {
          switch (indel_cost_option) {

          case false : {
            indel_cost_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Adaptative") {
                indel_cost = ADAPTATIVE;
              }
              else if (*pstr == "Fixed") {
                indel_cost = FIXED;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(INDEL_COST_SPECIFICATION_sds) , "Compare" ,
                            nb_required + i + 1 , "Adaptative or Fixed");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "IndelFactor") {
          switch (indel_factor_option) {

          case false : {
            indel_factor_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              indel_factor = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              indel_factor = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Transposition") {
          switch (transposition_option) {

          case false : {
            transposition_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
            }
            else {
              transposition = args[nb_required + i * 2 + 1].val.b;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "TranspositionFactor") {
          switch (transposition_factor_option) {

          case false : {
            transposition_factor_option = true;

            switch (args[nb_required + i * 2 + 1].tag()) {
            case AMObjType::INTEGER :
              transposition_factor = args[nb_required + i * 2 + 1].val.i;
              break;
            case AMObjType::REAL :
              transposition_factor = args[nb_required + i * 2 + 1].val.r;
              break;
            default :
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "INT or REAL");
              break;
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "FileName") {
          switch (file_name_option) {

          case false : {
            file_name_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "ASCII") {
                format = 'a';
              }
              else if (*pstr == "SpreadSheet") {
                format = 's';
              }
              else {
                status = false;
                genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Compare" ,
                            nb_required + i + 1 , "ASCII or SpreadSheet");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "AlignmentFileName") {
          switch (alignment_file_name_option) {

          case false : {
            alignment_file_name_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              alignment_file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "AlignmentFormat") {
          switch (alignment_format_option) {

          case false : {
            alignment_format_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "ASCII") {
                alignment_format = 'a';
              }
/*              else if (*pstr == "Binary") {
                alignment_format = 'b';
              } */
              else {
                status = false;
                genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Compare" ,
                            nb_required + i + 1 , "ASCII");
//                            nb_required + i + 1 , "ASCII or Binary");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Algorithm") {
          switch (algorithm_option) {

          case false : {
            algorithm_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Agglomerative") {
                algorithm = AGGLOMERATIVE;
              }
              else if (*pstr == "Divisive") {
                algorithm = DIVISIVE;
              }
              else if (*pstr == "Ordering") {
                algorithm = ORDERING;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Compare" ,
                            nb_required + i + 1 , "Agglomerative or Divisive");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" , nb_required + i + 1 ,
                      "Output or RefSequence or TestSequence or Begin or End or IndelCost or IndelFactor or Transposition or FileName or Format or AlignmentFileName or AlignmentFormat");
        }
      }
    }

    switch (output) {

    case 'm' : {
      if (algorithm_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "Algorithm");
      }

      if ((!transposition_option) && (transposition_factor_option)) {
        status = false;
        genAMLError(ERRORMSG(MISSING_TRANSPOSITION_OPTION_s) , "Compare");
      }

      if ((!file_name_option) && (format_option)) {
        status = false;
        genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "Compare");
      }

      if ((!alignment_file_name_option) && (alignment_format_option)) {
        status = false;
        genAMLError(ERRORMSG(MISSING_ALIGNMENT_FILE_NAME_OPTION_s) , "Compare");
      }
      break;
    }

    case 's' : {
      if (ref_sequence_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "RefSequence");
      }

      if (test_sequence_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "TestSequence");
      }

      if (transposition_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "Transposition");
      }

      if (transposition_factor_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "TranspositionFactor");
      }

      if (format_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "Format");
      }

      if (alignment_file_name_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "AlignmentFileName");
      }

      if (alignment_format_option) {
        status = false;
        genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Compare" , "AlignmentFormat");
      }
      break;
    }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    switch (output) {

    case 'm' : {
      if (!indel_factor_option) {
        indel_factor = INDEL_FACTOR_1;
      }

      dist_matrix = iseq->alignment(error , &AMLOUTPUT , *((VectorDistance*)((STAT_model*)args[1].val.p)->pt) ,
                                    ref_identifier , test_identifier , begin_free , end_free ,
                                    indel_cost , indel_factor , transposition , transposition_factor ,
                                    file_name , format , alignment_file_name , alignment_format);

      if (dist_matrix) {
        STAT_model* model = new STAT_model(dist_matrix);
        return AMObj(AMObjType::DISTANCE_MATRIX , model);
      }
      else {
        AMLOUTPUT << "\n" << error;
        genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
        return AMObj(AMObjType::ERROR);
      }
      break;
    }

    case 's' : {
      if (!indel_factor_option) {
        indel_factor = INDEL_FACTOR_N;
      }

      seq = iseq->multiple_alignment(error , AMLOUTPUT , *((VectorDistance*)((STAT_model*)args[1].val.p)->pt) ,
                                     begin_free , end_free , indel_cost , indel_factor , algorithm , file_name);

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
        genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
        return AMObj(AMObjType::ERROR);
      }
      break;
    }
    }

    break;
  }
  }
}


/*--------------------------------------------------------------*
 *
 *  Comparaison de modeles markoviens pour un ensemble de sequences.
 *
 *--------------------------------------------------------------*/

AMObj STAT_CompareSequencesMarkovianModels(const AMObjVector &args)

{
  char *file_name = NULL;
  bool status = true;
  register int i;
  int nb_required , nb_model;
  MarkovianSequences *seq;
  StatError error;


  nb_required = nb_required_computation(args);
  nb_model = nb_required - 1;

  CHECKCONDVA(nb_model >= 2 ,
              genAMLError(ERRORMSG(NB_MODEL_s) , "Compare"));

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

  if ((args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
      (args[1].tag() == AMObjType::SEMI_MARKOV)) {
    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "FileName") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" , nb_required + 1 , "FileName");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "STRING");
      }
      else {
        file_name = (char*)((AMString*)args[nb_required + 1].val.p)->data();
      }
    }

    switch (args[1].tag()) {

    case AMObjType::VARIABLE_ORDER_MARKOV : {
      const VariableOrderMarkov **markov;


      // arguments obligatoires

      markov = new const VariableOrderMarkov*[nb_model];

      markov[0] = (VariableOrderMarkov*)((STAT_model*)args[1].val.p)->pt;
      for (i = 1;i < nb_model;i++) {
        if (args[1 + i].tag() != AMObjType::VARIABLE_ORDER_MARKOV) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 + i ,
                      args[1 + i].tag.string().data() , "VARIABLE_ORDER_MARKOV");
        }
        else {
          markov[i] = (VariableOrderMarkov*)((STAT_model*)args[1 + i].val.p)->pt;
        }
      }

      if (status) {
        status = seq->comparison(error , AMLOUTPUT , nb_model , markov , file_name);
      }

      delete [] markov;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
      break;
    }

    case AMObjType::SEMI_MARKOV : {
      const SemiMarkov **smarkov;


      // arguments obligatoires

      smarkov = new const SemiMarkov*[nb_model];

      smarkov[0] = (SemiMarkov*)((STAT_model*)args[1].val.p)->pt;
      for (i = 1;i < nb_model;i++) {
        if (args[1 + i].tag() != AMObjType::SEMI_MARKOV) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 + i ,
                      args[1 + i].tag.string().data() , "SEMI-MARKOV");
        }
        else {
          smarkov[i] = (SemiMarkov*)((STAT_model*)args[1 + i].val.p)->pt;
        }
      }

      if (status) {
        status = seq->comparison(error , AMLOUTPUT , nb_model , smarkov , file_name);
      }

      delete [] smarkov;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
      break;
    }
    }

    if (status) {
      return AMObj(AMObjType::VOID);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
      return AMObj(AMObjType::ERROR);
    }
  }

  if ((args[1].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
      (args[1].tag() == AMObjType::HIDDEN_SEMI_MARKOV)) {
    RWCString *pstr;
    bool algorithm_option = false , file_name_option = false;
    int algorithm = FORWARD;


    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Forward") {
                algorithm = FORWARD;
              }
              else if (*pstr == "Viterbi") {
                algorithm = VITERBI;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Compare" ,
                            nb_required + i + 1 , "Forward or Viterbi");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "FileName") {
          switch (file_name_option) {

          case false : {
            file_name_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Compare" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" ,
                      nb_required + i + 1 , "Algorithm or FileName");
        }
      }
    }

    switch (args[1].tag()) {

    case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV : {
      const HiddenVariableOrderMarkov **hmarkov;


      // arguments obligatoires

      hmarkov = new const HiddenVariableOrderMarkov*[nb_model];

      hmarkov[0] = (HiddenVariableOrderMarkov*)((STAT_model*)args[1].val.p)->pt;
      for (i = 1;i < nb_model;i++) {
        if (args[1 + i].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 + i ,
                      args[1 + i].tag.string().data() , "HIDDEN_VARIABLE_ORDER_MARKOV");
        }
        else {
          hmarkov[i] = (HiddenVariableOrderMarkov*)((STAT_model*)args[1 + i].val.p)->pt;
        }
      }

      if (status) {
        status = seq->comparison(error , AMLOUTPUT , nb_model , hmarkov , algorithm , file_name);
      }

      delete [] hmarkov;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
      break;
    }

    case AMObjType::HIDDEN_SEMI_MARKOV : {
      const HiddenSemiMarkov **hsmarkov;


      // arguments obligatoires

      hsmarkov = new const HiddenSemiMarkov*[nb_model];

      hsmarkov[0] = (HiddenSemiMarkov*)((STAT_model*)args[1].val.p)->pt;
      for (i = 1;i < nb_model;i++) {
        if (args[1 + i].tag() != AMObjType::HIDDEN_SEMI_MARKOV) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 + i ,
                      args[1 + i].tag.string().data() , "HIDDEN_SEMI-MARKOV");
        }
        else {
          hsmarkov[i] = (HiddenSemiMarkov*)((STAT_model*)args[1 + i].val.p)->pt;
        }
      }

      if (status) {
        status = seq->comparison(error , AMLOUTPUT , nb_model , hsmarkov , algorithm , file_name);
      }

      delete [] hsmarkov;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
      break;
    }
    }

    if (status) {
      return AMObj(AMObjType::VOID);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
      return AMObj(AMObjType::ERROR);
    }
  }

  genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 , args[1].tag.string().data() ,
              "VARIABLE_ORDER_MARKOV or SEMI-MARKOV or HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV");
  return AMObj(AMObjType::ERROR);
}


/*--------------------------------------------------------------*
 *
 *  Comparaison de modeles markoviens.
 *
 *--------------------------------------------------------------*/

AMObj STAT_CompareMarkovianModels(const AMObjVector &args)

{
  char *file_name = NULL;
  bool status = true;
  register int i;
  int nb_required , nb_model , step , nb_sequence , length;
  FrequencyDistribution **hlength = NULL;
  const MarkovianSequences **seq = NULL;
  DistanceMatrix *dist_matrix;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "FileName") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Compare" , nb_required + 1 , "FileName");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::STRING) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "STRING");
    }
    else {
      file_name = (char*)((AMString*)args[nb_required + 1].val.p)->data();
    }
  }

  CHECKCONDVA(nb_required >= 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

  if ((args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
      (args[1].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
      (args[1].tag() == AMObjType::SEMI_MARKOV) || (args[1].tag() == AMObjType::HIDDEN_SEMI_MARKOV)) {
    step = 1;
    nb_model = nb_required - 2;
  }

  else {
    if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
      nb_model = nb_required;
    }
    else if ((args[1].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[1].tag() == AMObjType::SEMI_MARKOV_DATA)) {
      nb_model = nb_required - 1;
    }
    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , 2 , args[1].tag.string().data() ,
                  "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
      return AMObj(AMObjType::ERROR);
    }

    CHECKCONDVA(nb_model % 2 == 0 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

    nb_model /= 2;
    step = 2;
  }

  CHECKCONDVA(nb_model >= 2 ,
              genAMLError(ERRORMSG(NB_MODEL_s) , "Compare"));

  if ((args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
      (args[1].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
      (args[1].tag() == AMObjType::SEMI_MARKOV) || (args[1].tag() == AMObjType::HIDDEN_SEMI_MARKOV)) {
    if (args[nb_required - 2].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required - 1 ,
                  args[nb_required - 2].tag.string().data() , "INT");
    }
    else {
      nb_sequence = args[nb_required - 2].val.i;
    }

    if (args[nb_required - 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required ,
                  args[nb_required - 1].tag.string().data() , "INT");
    }
    else {
      length = args[nb_required - 1].val.i;
    }
  }

  else {
    if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
        (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
      hlength = new FrequencyDistribution*[nb_model];

      for (i = 0;i < nb_model;i++) {
        switch (args[i * step + 1].tag()) {
        case AMObjType::FREQUENCY_DISTRIBUTION :
          hlength[i] = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[i * step + 1].val.p)->pt);
          break;
        case AMObjType::DISCRETE_MIXTURE_DATA :
          hlength[i] = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[i * step + 1].val.p)->pt);
          break;
        case AMObjType::CONVOLUTION_DATA :
          hlength[i] = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[i * step + 1].val.p)->pt);
          break;
        case AMObjType::COMPOUND_DATA :
          hlength[i] = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[i * step + 1].val.p)->pt);
          break;
        default :
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i * step + 2 ,
                      args[i * step + 1].tag.string().data() ,
                      "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
        }
      }
    }

    else if ((args[1].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
             (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[1].tag() == AMObjType::SEMI_MARKOV_DATA)) {
      seq = new const MarkovianSequences*[nb_model];

      for (i = 0;i < nb_model;i++) {
        switch (args[i * step + 1].tag()) {
        case AMObjType::MARKOVIAN_SEQUENCES :
          seq[i] = (MarkovianSequences*)((STAT_model*)args[i * step + 1].val.p)->pt;
          break;
        case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
          seq[i] = (VariableOrderMarkovData*)((STAT_model*)args[i * step + 1].val.p)->pt;
          break;
        case AMObjType::SEMI_MARKOV_DATA :
          seq[i] = (SemiMarkovData*)((STAT_model*)args[i * step + 1].val.p)->pt;
          break;
        default :
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i * step + 2 ,
                      args[i * step + 1].tag.string().data() ,
                      "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
          break;
        }
      }

      if (args[nb_required - 1].tag() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , nb_required ,
                    args[nb_required - 1].tag.string().data() , "INT");
      }
      else {
        nb_sequence = args[nb_required - 1].val.i;
      }
    }
  }

  switch (args[0].tag()) {

  case AMObjType::VARIABLE_ORDER_MARKOV : {
    const VariableOrderMarkov **markov;


    markov = new const VariableOrderMarkov*[nb_model];

    markov[0] = (VariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt;
    for (i = 1;i < nb_model;i++) {
      if (args[i * step].tag() != AMObjType::VARIABLE_ORDER_MARKOV) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i * step + 1 ,
                    args[i * step].tag.string().data() , "VARIABLE_ORDER_MARKOV");
      }
      else {
        markov[i] = (VariableOrderMarkov*)((STAT_model*)args[i * step].val.p)->pt;
      }
    }

    if (status) {
      if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
          (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
        dist_matrix = markov[0]->divergence_computation(error , AMLOUTPUT , nb_model , markov + 1 ,
                                                        hlength , file_name);
      }

      else if (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV) {
        dist_matrix = markov[0]->divergence_computation(error , AMLOUTPUT , nb_model , markov + 1 ,
                                                        nb_sequence , length , file_name);
      }

      else if ((args[1].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
               (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[1].tag() == AMObjType::SEMI_MARKOV_DATA)) {
        dist_matrix = markov[0]->divergence_computation(error , AMLOUTPUT , nb_model , markov + 1 ,
                                                        nb_sequence , seq , file_name);
      }
    }

    delete [] hlength;
    delete [] seq;
    delete [] markov;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV : {
    const HiddenVariableOrderMarkov **hmarkov;


    hmarkov = new const HiddenVariableOrderMarkov*[nb_model];

    hmarkov[0] = (HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt;
    for (i = 1;i < nb_model;i++) {
      if (args[i * step].tag() != AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i * step + 1 ,
                    args[i * step].tag.string().data() , "HIDDEN_VARIABLE_ORDER_MARKOV");
      }
      else {
        hmarkov[i] = (HiddenVariableOrderMarkov*)((STAT_model*)args[i * step].val.p)->pt;
      }
    }

    if (status) {
      if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
          (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
        dist_matrix = hmarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , hmarkov + 1 ,
                                                         hlength , file_name);
      }

      else if (args[1].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
        dist_matrix = hmarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , hmarkov + 1 ,
                                                         nb_sequence , length , file_name);
      }

      else if ((args[1].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
               (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[1].tag() == AMObjType::SEMI_MARKOV_DATA)) {
        dist_matrix = hmarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , hmarkov + 1 ,
                                                         nb_sequence , seq , file_name);
      }
    }

    delete [] hlength;
    delete [] seq;
    delete [] hmarkov;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case AMObjType::SEMI_MARKOV : {
    const SemiMarkov **smarkov;


    smarkov = new const SemiMarkov*[nb_model];

    smarkov[0] = (SemiMarkov*)((STAT_model*)args[0].val.p)->pt;
    for (i = 1;i < nb_model;i++) {
      if (args[i * step].tag() != AMObjType::SEMI_MARKOV) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i * step + 1 ,
                    args[i * step].tag.string().data() , "SEMI_MARKOV");
      }
      else {
        smarkov[i] = (SemiMarkov*)((STAT_model*)args[i * step].val.p)->pt;
      }
    }

    if (status) {
      if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
          (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
        dist_matrix = smarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , smarkov + 1 ,
                                                         hlength , file_name);
      }

      else if (args[1].tag() == AMObjType::SEMI_MARKOV) {
        dist_matrix = smarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , smarkov + 1 ,
                                                         nb_sequence , length , file_name);
      }

      else if ((args[1].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
               (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[1].tag() == AMObjType::SEMI_MARKOV_DATA)) {
        dist_matrix = smarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , smarkov + 1 ,
                                                         nb_sequence , seq , file_name);
      }
    }

    delete [] hlength;
    delete [] seq;
    delete [] smarkov;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
    break;
  }

  case AMObjType::HIDDEN_SEMI_MARKOV : {
    const HiddenSemiMarkov **hsmarkov;


    hsmarkov = new const HiddenSemiMarkov*[nb_model];

    hsmarkov[0] = (HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt;
    for (i = 1;i < nb_model;i++) {
      if (args[i * step].tag() != AMObjType::HIDDEN_SEMI_MARKOV) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Compare" , i * step + 1 ,
                    args[i * step].tag.string().data() , "HIDDEN_SEMI_MARKOV");
      }
      else {
        hsmarkov[i] = (HiddenSemiMarkov*)((STAT_model*)args[i * step].val.p)->pt;
      }
    }

    if (status) {
      if ((args[1].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[1].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
          (args[1].tag() == AMObjType::CONVOLUTION_DATA) || (args[1].tag() == AMObjType::COMPOUND_DATA)) {
        dist_matrix = hsmarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , hsmarkov + 1 ,
                                                          hlength , file_name);
      }

      else if (args[1].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
        dist_matrix = hsmarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , hsmarkov + 1 ,
                                                          nb_sequence , length , file_name);
      }

      else if ((args[1].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
               (args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) || (args[1].tag() == AMObjType::SEMI_MARKOV_DATA)) {
        dist_matrix = hsmarkov[0]->divergence_computation(error , AMLOUTPUT , nb_model , hsmarkov + 1 ,
                                                          nb_sequence , seq , file_name);
      }
    }

    delete [] hlength;
    delete [] seq;
    delete [] hsmarkov;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
    break;
  }
  }

  if (dist_matrix) {
    STAT_model* model = new STAT_model(dist_matrix);
    return AMObj(AMObjType::DISTANCE_MATRIX , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Compare");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Comparaison.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Compare(const AMObjVector &args)

{
  CHECKCONDVA(args.length() >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Compare"));

  // comparaison de lois empiriques

  if ((args[0].tag() == AMObjType::FREQUENCY_DISTRIBUTION) || (args[0].tag() == AMObjType::DISCRETE_MIXTURE_DATA) ||
      (args[0].tag() == AMObjType::CONVOLUTION_DATA) || (args[0].tag() == AMObjType::COMPOUND_DATA)) {
    return STAT_CompareFrequencyDistributions(args);
  }

  // comparaison de vecteurs

  if (args[0].tag() == AMObjType::VECTORS) {
    return STAT_CompareVectors(args);
  }

  // comparaison de modeles markoviens pour un ensemble de sequences

  if ((args.length() >= 2) && ((args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
       (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
       (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) || 
       (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) &&
      ((args[1].tag() == AMObjType::VARIABLE_ORDER_MARKOV) || (args[1].tag() == AMObjType::SEMI_MARKOV) ||
       (args[1].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
       (args[1].tag() == AMObjType::HIDDEN_SEMI_MARKOV))) {
    return STAT_CompareSequencesMarkovianModels(args);
  }

  // alignement de sequences

  if ((args[0].tag() == AMObjType::SEQUENCES) || (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
      (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) {
    return STAT_CompareSequences(args);
  }

  // comparaison de modeles markoviens

  if ((args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
      (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) ||
      (args[0].tag() == AMObjType::SEMI_MARKOV) || (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV)) {
    return STAT_CompareMarkovianModels(args);
  }

  genAMLError(ERRORMSG(ARGS_s) , "Compare");
  return AMObj(AMObjType::ERROR);
}


/*--------------------------------------------------------------*
 *
 *  Construction de groupes a partir d'une matrice des distances.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Clustering(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true;
  int nb_required;
  StatError error;


  CHECKCONDVA(args.length() >= 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Clustering"));

  // arguments obligatoires

  if (args[0].tag() != AMObjType::DISTANCE_MATRIX) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , 1 ,
                args[0].tag.string().data() , "DISTANCE_MATRIX");
  }

  CHECKCONDVA(args[1].tag() == AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , 2 ,
                          args[1].tag.string().data() , "STRING"));

  pstr = (AMString*)args[1].val.p;

  if (*pstr == "Partition") {
    Clusters *clusters;


    nb_required = 3;

    CHECKCONDVA(args.length() >= nb_required ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Clustering"));

    switch (args[2].tag()) {

    case AMObjType::INTEGER : {
      RWCString *pstr;
      bool prototypes_option = false , initialization_option = false , algorithm_option = false;
      register int i;
      int nb_cluster , *prototype = NULL , initialization = 1 , algorithm = 1;


      CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                  (args.length() == nb_required + 4) ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Clustering"));

      nb_cluster = args[2].val.i;

      // arguments optionnels

      for (i = 0;i < (args.length() - nb_required) / 2;i++) {
        if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                      args[nb_required + i * 2].tag.string().data() , "OPTION");
        }

        else {
          pstr = (AMString*)args[nb_required + i * 2].val.p;

          if (*pstr == "Prototypes") {
            switch (prototypes_option) {

            case false : {
              prototypes_option = true;

              if (args[nb_required + i * 2 + 1].tag() != AMObjType::ARRAY) {
                status = false;
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                            args[nb_required + i * 2 + 1].tag.string().data() , "ARRAY");
              }
              else {
                prototype = buildIntArray(args , nb_required + i * 2 + 1 , "Clustering" ,
                                          nb_required + i + 1 , nb_cluster);
                if (!prototype) {
                  status = false;
                }
              }
              break;
            }

            case true : {
              status = false;
              genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
              break;
            }
            }
          }

          else if (*pstr == "Initialization") {
            switch (initialization_option) {

            case false : {
              initialization_option = true;

              if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
                status = false;
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                            args[nb_required + i * 2 + 1].tag.string().data() , "INT");
              }
              else {
                initialization = args[nb_required + i * 2 + 1].val.i;
              }
              break;
            }

            case true : {
              status = false;
              genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
              break;
            }
            }
          }

          else if (*pstr == "Algorithm") {
            switch (algorithm_option) {

            case false : {
              algorithm_option = true;

              if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
                status = false;
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                            args[nb_required + i * 2 + 1].tag.string().data() , "INT");
              }
              else {
                algorithm = args[nb_required + i * 2 + 1].val.i;
              }
              break;
            }

            case true : {
              status = false;
              genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
              break;
            }
            }
          }

          else {
            status = false;
            genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Clustering" ,
                        nb_required + i + 1 , "Prototypes or Initialization or Algorithm");
          }
        }
      }

      if ((prototypes_option) && (initialization_option)) {
        status = false;
        genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_sss) , "Clustering" , "Prototypes" , "Initialization");
      }

      if (status) {
        clusters = ((DistanceMatrix*)((STAT_model*)args[0].val.p)->pt)->
        partitioning(error , AMLOUTPUT , nb_cluster , prototype , initialization , algorithm);
      }

     delete [] prototype;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
      break;
    }

    case AMObjType::ARRAY : {
      register int i , j;
      int nb_cluster , *cluster_nb_pattern = NULL , **cluster_pattern = NULL;
      const Array *parray , *pcluster;


      CHECKCONDVA(args.length() == nb_required ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Clustering" , nb_required));

      // argument obligatoire

      parray = (Array*)args[2].val.p;

      if (parray->surfaceType() != AMObjType::ARRAY) {
        status = false;
        genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , "Clustering" , 3 ,
                    (parray->surfaceType()).string().data() , "ARRAY");
      }

      else {
        nb_cluster = parray->entries();

        cluster_nb_pattern = new int[nb_cluster];
        cluster_pattern = new int*[nb_cluster];
        for (i = 0;i < nb_cluster;i++) {
          cluster_pattern[i] = NULL;
        }

        ArrayIter* pnext = parray->iterator();
        ArrayIter& next = *pnext;

        i = 0;
        while (next()) {
          if ((next.key()).tag() != AMObjType::ARRAY) {
            status = false;
            genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_sddss) , "Clustering" , 3 ,
                        i + 1 , (next.key()).tag.string().data() , "ARRAY");
          }

          else {
            pcluster = (Array*)(next.key()).val.p;

            if (pcluster->surfaceType() != AMObjType::INTEGER) {
              status = false;
              genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_sddss) , "Clustering" , 3 ,
                          i + 1 , (parray->surfaceType()).string().data() , "INT");
            }

            else {
              cluster_nb_pattern[i] = pcluster->entries();
              cluster_pattern[i] = new int[cluster_nb_pattern[i]];

              ArrayIter* pcluster_next = pcluster->iterator();
              ArrayIter& cluster_next = *pcluster_next;

              j = 0;
              while (cluster_next()) {
                if ((cluster_next.key()).tag() != AMObjType::INTEGER) {
                  status = false;
                  genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_sdddss) , "Clustering" , 3 ,
                              i + 1 , j + 1 , (cluster_next.key()).tag.string().data() , "INT");
                }
                else {
                  if ((cluster_next.key()).val.i <= 0) {
                    status = false;
                    genAMLError(ERRORMSG(ARRAY_ELEMENT_VALUE_sddd) , "Clustering" , 3 ,
                                i + 1 , j + 1);
                  }
                  else {
                    cluster_pattern[i][j] = (cluster_next.key()).val.i;
                  }
                }

                j++;
              }

              delete pcluster_next;
            }
          }

          i++;
        }

        delete pnext;
      }

      if (status) {
        clusters = ((DistanceMatrix*)((STAT_model*)args[0].val.p)->pt)->partitioning(error , AMLOUTPUT , nb_cluster ,
                                                                                     cluster_nb_pattern , cluster_pattern);
      }

      delete [] cluster_nb_pattern;
      for (i = 0;i < nb_cluster;i++) {
        delete [] cluster_pattern[i];
      }
      delete [] cluster_pattern;

      if (!status) {
        return AMObj(AMObjType::ERROR);
      }
      break;
    }

    default : {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , 3 ,
                  args[2].tag.string().data() , "INT or ARRAY");
      return AMObj(AMObjType::ERROR);
    }
    }

    if (clusters) {
      STAT_model* model = new STAT_model(clusters);
      return AMObj(AMObjType::CLUSTERS , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Clustering");
      return AMObj(AMObjType::ERROR);
    }
  }

  else if (*pstr == "Hierarchy") {
    char *file_name = NULL , format = 'a';
    bool algorithm_option = false , criterion_option = false , file_name_option = false ,
         format_option = false;
    register int i;
    int algorithm = AGGLOMERATIVE , criterion = AVERAGING;


    nb_required = 2;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
                (args.length() == nb_required + 8) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Clustering"));

    // arguments optionnels

    for (i = 0;i < (args.length() - nb_required) / 2;i++) {
      if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "Agglomerative") {
                algorithm = AGGLOMERATIVE;
              }
              else if (*pstr == "Divisive") {
                algorithm = DIVISIVE;
              }
              else if (*pstr == "Ordering") {
                algorithm = ORDERING;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(ALGORITHM_NAME_sds) , "Clustering" ,
                            nb_required + i + 1 , "Agglomerative or Divisive");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
            break;
          }
          }
        }

        else if (*pstr == "Criterion") {
          switch (criterion_option) {

          case false : {
            criterion_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
              if (*pstr == "NearestNeighbor") {
                criterion = NEAREST_NEIGHBOR;
              }
              else if (*pstr == "FarthestNeighbor") {
                criterion = FARTHEST_NEIGHBOR;
              }
              else if (*pstr == "Averaging") {
                criterion = AVERAGING;
              }
              else {
                status = false;
                genAMLError(ERRORMSG(CRITERION_NAME_sds) , "Clustering" ,
                            nb_required + i + 1 , "FarthestNeighbor or Averaging");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
            break;
          }
          }
        }

       else if (*pstr == "FileName") {
          switch (file_name_option) {

          case false : {
            file_name_option = true;

            if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
              status = false;
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
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
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Clustering" , nb_required + i + 1 ,
                          args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
            }
            else {
              pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

              if (*pstr == "ASCII") {
                format = 'a';
              }
              else if (*pstr == "SpreadSheet") {
                format = 's';
              }
              else {
                status = false;
                genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "Clustering" ,
                            nb_required + i + 1 , "ASCII or SpreadSheet");
              }
            }
            break;
          }

          case true : {
            status = false;
            genAMLError(ERRORMSG(USED_OPTION_sd) , "Clustering" , nb_required + i + 1);
            break;
          }
          }
        }

        else {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Clustering" ,
                      nb_required + i + 1 , "Algorithm or Criterion or FileName or Format");
        }
      }
    }

    if ((algorithm != AGGLOMERATIVE) && (criterion_option)) {
      status = false;
      genAMLError(ERRORMSG(FORBIDDEN_OPTION_ss) , "Clustering" , "Criterion");
    }

    if ((!file_name_option) && (format_option)) {
      status = false;
      genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "Clustering");
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    status = ((DistanceMatrix*)((STAT_model*)args[0].val.p)->pt)->hierarchical_clustering(error , AMLOUTPUT ,
                                                                                          algorithm , criterion ,
                                                                                          file_name , format);

    if (status) {
      return AMObj(AMObjType::VOID);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "Clustering");
      return AMObj(AMObjType::ERROR);
    }
  }

  else {
    genAMLError(ERRORMSG(CLUSTERING_METHOD_sds) , "Clustering" , 2 ,
                "Partition or Hierarchy");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Test de comparaison de lois empiriques.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComparisonTest(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true;
  const FrequencyDistribution *histo1 , *histo2;
  StatError error;


  CHECKCONDVA(args.length() == 3 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "ComparisonTest" , 3));

  CHECKCONDVA(args[0].tag() == AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComparisonTest" , 1 ,
                          args[0].tag.string().data() , "STRING"));

  pstr = (AMString*)args[0].val.p;
  if ((*pstr != "F") && (*pstr != "T") && (*pstr != "W")) {
    status = false;
    genAMLError(ERRORMSG(TEST_TYPE_sds) , "ComparisonTest" , 1 , "F or T or W(Wilcoxon-Mann-Whitney)");
  }

  switch (args[1].tag()) {
  case AMObjType::FREQUENCY_DISTRIBUTION :
    histo1 = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[1].val.p)->pt);
    break;
  case AMObjType::DISCRETE_MIXTURE_DATA :
    histo1 = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[1].val.p)->pt);
    break;
  case AMObjType::CONVOLUTION_DATA :
    histo1 = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[1].val.p)->pt);
    break;
  case AMObjType::COMPOUND_DATA :
    histo1 = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[1].val.p)->pt);
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComparisonTest" , 2 , args[1].tag.string().data() ,
                "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
    break;
  }

  switch (args[2].tag()) {
  case AMObjType::FREQUENCY_DISTRIBUTION :
    histo2 = (FrequencyDistribution*)((DiscreteDistributionData*)((STAT_model*)args[2].val.p)->pt);
    break;
  case AMObjType::DISCRETE_MIXTURE_DATA :
    histo2 = (FrequencyDistribution*)((DiscreteMixtureData*)((STAT_model*)args[2].val.p)->pt);
    break;
  case AMObjType::CONVOLUTION_DATA :
    histo2 = (FrequencyDistribution*)((ConvolutionData*)((STAT_model*)args[2].val.p)->pt);
    break;
  case AMObjType::COMPOUND_DATA :
    histo2 = (FrequencyDistribution*)((CompoundData*)((STAT_model*)args[2].val.p)->pt);
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComparisonTest" , 3 , args[2].tag.string().data() ,
                "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
    break;
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  if (*pstr == "F") {
    histo1->F_comparison(AMLOUTPUT , *histo2);
  }

  else if (*pstr == "T") {
    histo1->t_comparison(AMLOUTPUT , *histo2);
  }

  else if (*pstr == "W") {
    status = histo1->wilcoxon_mann_whitney_comparison(error , AMLOUTPUT , *histo2);

    if (!status) {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "ComparisonTest");
      return AMObj(AMObjType::ERROR);
    }
  }

  return AMObj(AMObjType::VOID);
}


/*--------------------------------------------------------------*
 *
 *  Ajustement d'une loi.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Fit(const AMObjVector &args)

{
  bool status = true;
  const FrequencyDistribution *histo;
  DiscreteParametricModel *dist;
  StatError error;


  CHECKCONDVA(args.length() == 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Fit" , 2));

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
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Fit" , 1 , args[0].tag.string().data() ,
                "FREQUENCY_DISTRIBUTION or DISCRETE_MIXTURE_DATA or CONVOLUTION_DATA or COMPOUND_DATA");
    break;
  }

  if (args[1].tag() != AMObjType::DISTRIBUTION) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Fit" , 2 , args[1].tag.string().data() ,
                "DISTRIBUTION");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  dist = histo->fit(error , *((DiscreteParametric*)((DiscreteParametricModel*)((STAT_model*)args[1].val.p)->pt)));

  if (dist) {
    STAT_model* model = new STAT_model(dist);
    return AMObj(AMObjType::DISTRIBUTION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Fit");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Troncature d'une loi.
 *
 *--------------------------------------------------------------*/

AMObj STAT_TruncateDistribution(const AMObjVector &args)

{
  bool status = true;
  StatError error;
  const Distribution *idist;
  DiscreteParametricModel *dist;


  CHECKCONDVA(args.length() == 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "TruncateDistribution" , 2));

  switch (args[0].tag()) {
  case AMObjType::DISTRIBUTION :
    idist = new Distribution(*((Distribution*)((DiscreteParametricModel*)((STAT_model*)args[0].val.p)->pt)));
    break;
  case AMObjType::DISCRETE_MIXTURE :
    idist = new Distribution(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[0].val.p)->pt)));
    break;
  case AMObjType::CONVOLUTION :
    idist = new Distribution(*((Distribution*)((Convolution*)((STAT_model*)args[0].val.p)->pt)));
    break;
  case AMObjType::COMPOUND :
    idist = new Distribution(*((Distribution*)((Compound*)((STAT_model*)args[0].val.p)->pt)));
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TruncateDistribution" , 1 , args[0].tag.string().data() ,
                "DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
    break;
  }

  if (args[1].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TruncateDistribution" , 2 ,
                args[1].tag.string().data() , "INT");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  dist = idist->truncate(error , args[1].val.i);

  if (dist) {
    STAT_model* model = new STAT_model(dist);
    return AMObj(AMObjType::DISTRIBUTION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "TruncateDistribution");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul de la matrice des correlations de rangs.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputeRankCorrelation(const AMObjVector &args)

{
  RWCString *pstr;
  char *file_name = NULL;
  bool status = true , type_option = false , file_name_option = false;
  register int i;
  int nb_required , type = SPEARMAN;
  StatError error;


  nb_required = 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeRankCorrelation"));

  // argument obligatoire

  if (args[0].tag() != AMObjType::VECTORS) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeRankCorrelation" , 1 ,
                args[0].tag.string().data() , "VECTORS");
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeRankCorrelation" , nb_required + i + 1 ,
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
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeRankCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "Spearman") {
              type = SPEARMAN;
            }
            else if (*pstr == "Kendall") {
              type = KENDALL;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(CORRELATION_COEFF_TYPE_sds) , "ComputeRankCorrelation" ,
                          nb_required + i + 1 , "Spearman or Kendall");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputeRankCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "FileName") {
        switch (file_name_option) {

        case false : {
          file_name_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeRankCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputeRankCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "ComputeRankCorrelation" ,
                    nb_required + i + 1 , "Type or FileName");
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  status = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->rank_correlation_computation(error , AMLOUTPUT ,
                                                                                      type , file_name);

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputeRankCorrelation");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Tableau de contingence.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ContingencyTable(const AMObjVector &args)

{
  RWCString *pstr;
  char *file_name = NULL , format = 'a';
  bool status = true , file_name_option = false , format_option = false;
  register int i;
  int nb_required;
  StatError error;


  nb_required = 3;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ContingencyTable"));

  // arguments obligatoires

  if (args[0].tag() != AMObjType::VECTORS) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ContingencyTable" , 1 ,
                args[0].tag.string().data() , "VECTORS");
  }

  if (args[1].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ContingencyTable" , 2 ,
                args[1].tag.string().data() , "INT");
  }
  if (args[2].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ContingencyTable" , 3 ,
                args[2].tag.string().data() , "INT");
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ContingencyTable" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "FileName") {
        switch (file_name_option) {

        case false : {
          file_name_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ContingencyTable" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ContingencyTable" , nb_required + i + 1);
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
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ContingencyTable" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "ASCII") {
              format = 'a';
            }
            else if (*pstr == "SpreadSheet") {
              format = 's';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "ContingencyTable" ,
                          nb_required + i + 1 , "ASCII or SpreadSheet");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ContingencyTable" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "ContingencyTable" ,
                    nb_required + i + 1 , "FileName or Format");
      }
    }
  }

  if ((!file_name_option) && (format_option)) {
    status = false;
    genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "ContingencyTable");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  status = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->contingency_table(error , AMLOUTPUT , args[1].val.i ,
                                                                           args[2].val.i , file_name , format);

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "ContingencyTable");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Analyse de variance a un facteur.
 *
 *--------------------------------------------------------------*/

AMObj STAT_VarianceAnalysis(const AMObjVector &args)

{
  RWCString *pstr;
  char *file_name = NULL , format = 'a';
  bool status = true , file_name_option = false , format_option = false;
  register int i;
  int nb_required , type;
  StatError error;


  nb_required = 4;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "VarianceAnalysis"));

  // arguments obligatoires

  if (args[0].tag() != AMObjType::VECTORS) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , 1 ,
                args[0].tag.string().data() , "VECTORS");
  }

  if (args[1].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , 2 ,
                args[1].tag.string().data() , "INT");
  }
  if (args[2].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , 3 ,
                args[2].tag.string().data() , "INT");
  }

  if (args[3].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , 4 ,
                args[3].tag.string().data() , "STRING");
  }

  else {
    pstr = (AMString*)args[3].val.p;
    for (i = ORDINAL;i <= NUMERIC;i++) {
      if ((*pstr == STAT_variable_type_word[i]) || (*pstr == STAT_variable_type_letter[i])) {
        type = i;
        break;
      }
    }

    if (i == NUMERIC + 1) {
      status = false;
      genAMLError(ERRORMSG(VARIABLE_TYPE_sds) , "VarianceAnalysis" , 4 ,
                  "ORDINAL(O) or NUMERIC(N)");
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "FileName") {
        switch (file_name_option) {

        case false : {
          file_name_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "VarianceAnalysis" , nb_required + i + 1);
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
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "VarianceAnalysis" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "ASCII") {
              format = 'a';
            }
            else if (*pstr == "SpreadSheet") {
              format = 's';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "VarianceAnalysis" ,
                          nb_required + i + 1 , "ASCII or SpreadSheet");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "VarianceAnalysis" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "VarianceAnalysis" ,
                    nb_required + i + 1 , "FileName or Format");
      }
    }
  }

  if ((!file_name_option) && (format_option)) {
    status = false;
    genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "VarianceAnalysis");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  status = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->variance_analysis(error , AMLOUTPUT , args[1].val.i ,
                                                                           args[2].val.i , type , file_name , format);

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "VarianceAnalysis");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Regression.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Regression(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true;
  StatError error;
  Regression *regression;


  CHECKCONDVA(args.length() >= 4 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Regression"));


  // arguments obligatoires

  if (args[0].tag() != AMObjType::VECTORS) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , 1 ,
                args[0].tag.string().data() , "VECTORS");
  }
  if (args[1].tag() != AMObjType::STRING) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , 2 ,
                args[1].tag.string().data() , "STRING");
  }

  if (args[2].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , 3 ,
                args[2].tag.string().data() , "INT");
  }
  if (args[3].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , 4 ,
                args[3].tag.string().data() , "INT");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  pstr = (AMString*)args[1].val.p;
  if (*pstr == "Linear") {
    CHECKCONDVA(args.length() == 4 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Regression", 4));

    regression = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->linear_regression(error , args[2].val.i , args[3].val.i);
  }

  else if (*pstr == "MovingAverage") {
    char algorithm = 'a';
    register int i;
    int nb_required , nb_point = I_DEFAULT , int_sum , *int_filter;
    double sum , *filter;
    const Distribution *dist;


    nb_required = 5;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Regression"));

    // arguments obligatoires

    filter = NULL;
    dist = NULL;

    if (args[4].tag() == AMObjType::ARRAY) {
      Array* parray = (Array*)args[4].val.p;

      if (parray->surfaceType() == AMObjType::INTEGER) {
        int_filter = buildIntArray(args , 4 , "Regression" , 5 , nb_point);
        if (!int_filter) {
          status = false;
        }

        else {
          nb_point--;

          int_sum = 0;
          for (i = 0;i < nb_point;i++) {
            int_sum += 2 * int_filter[i];
          }
          int_sum += int_filter[i];

          if (int_sum == 0) {
            status = false;
            genAMLError(ERRORMSG(FILTER_NORMALIZATION_sd) , "Regression" , 5);
          }

          else {
            filter = new double[2 * nb_point + 1];
            for (i = 0;i < nb_point;i++) {
              filter[i] = (double)int_filter[i] / (double)int_sum;
              filter[2 * nb_point - i] = filter[i];
            }
            filter[i] = (double)int_filter[i] / (double)int_sum;
          }

          delete [] int_filter;
        }
      }

      else if (parray->surfaceType() == AMObjType::REAL) {
        filter = buildRealArray(args , 4 , "Regression" , 5 , nb_point , true);
        if (!filter) {
          status = false;
        }

        else {
          sum = 0.;
          for (i = 0;i < nb_point;i++) {
            sum += 2 * filter[i];
            filter[2 * nb_point - i] = filter[i];
          }
          sum += filter[i];

          if ((sum < 1. - STAT_FILTER_ROUNDNESS) || (sum > 1. + STAT_FILTER_ROUNDNESS)) {
            status = false;
            genAMLError(ERRORMSG(FILTER_NORMALIZATION_sd) , "Regression" , 5);
          }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , "Regression" , 5 ,
                    (parray->surfaceType()).string().data() , "INT or REAL");
      }
    }

    else {
      switch (args[4].tag()) {
      case AMObjType::DISTRIBUTION :
        dist = new Distribution(*((Distribution*)((DiscreteParametricModel*)((STAT_model*)args[4].val.p)->pt)));
        break;
      case AMObjType::DISCRETE_MIXTURE :
        dist = new Distribution(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[4].val.p)->pt)));
        break;
      case AMObjType::CONVOLUTION :
        dist = new Distribution(*((Distribution*)((Convolution*)((STAT_model*)args[4].val.p)->pt)));
        break;
      case AMObjType::COMPOUND :
        dist = new Distribution(*((Distribution*)((Compound*)((STAT_model*)args[4].val.p)->pt)));
        break;
      default :
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , 5 , args[4].tag.string().data() ,
                    "ARRAY or DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
        break;
      }
    }

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "Algorithm") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Regression" , nb_required + 1 , "Algorithm");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "STRING");
      }
      else {
        pstr = (AMString*)args[nb_required + 1].val.p;
        if (*pstr == "Averaging") {
          algorithm = 'a';
        }
        else if (*pstr == "LeastSquares") {
          algorithm = 's';
        }
        else {
          status = false;
          genAMLError(ERRORMSG(ARG_sds) , "Regression" , nb_required + 1 , "Averaging or LeastSquares");
        }
      }
    }

    if (status) {
      if (!dist) {
        regression = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->moving_average(error , args[2].val.i , args[3].val.i ,
                                                                                  nb_point , filter , algorithm);
      }
      else {
        regression = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->moving_average(error , args[2].val.i , args[3].val.i ,
                                                                                  *dist , algorithm);
      }
    }

    delete [] filter;
    delete dist;

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }
  }

  else if (*pstr == "NearestNeighbors") {
    bool weighting = true;
    int nb_required;
    double span;


    nb_required = 5;

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Regression"));

    // argument obligatoire

    if (args[4].tag() != AMObjType::REAL) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , 5 ,
                  args[4].tag.string().data() , "REAL");
    }
    else {
      span = args[4].val.r;
      if ((span < STAT_MINIMUM_SPAN) || (span >= 1. - STAT_MINIMUM_SPAN)) {
        status = false;
        genAMLError(ERRORMSG(SPAN_sd) , "Regression" , 5);
      }
    }

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "Weighting") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Regression" , nb_required + 1 ,
                      "Weighting");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::BOOL) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Regression" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "BOOL");
      }
      else {
        weighting = args[nb_required + 1].val.b;
      }
    }

    if (!status) {
      return AMObj(AMObjType::ERROR);
    }

    regression = ((Vectors*)((STAT_model*)args[0].val.p)->pt)->nearest_neighbor_smoother(error , args[2].val.i , args[3].val.i ,
                                                                                         span , weighting);
  }

  else {
    genAMLError(ERRORMSG(REGRESSION_METHOD_sds) , "Regression" , 2 ,
                "Linear or MovingAverage or NearestNeighbors");
    return AMObj(AMObjType::ERROR);
  }

  if (regression) {
    STAT_model* model = new STAT_model(regression);
    return AMObj(AMObjType::REGRESSION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Regression");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul d'une fonction de correlation d'un echantillon de sequences.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputeCorrelation(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , max_lag_option = false , type_option = false , normalization_option = false ,
       individual_mean_option = false , individual_mean = false;
  register int i;
  int nb_required , nb_variable , variable1 = 0 , variable2 , max_lag = I_DEFAULT ,
      type = PEARSON , normalization = EXACT;
  const Sequences *seq;
  Correlation *correl;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeCorrelation"));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ||
              (args.length() == nb_required + 8) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeCorrelation"));

  // arguments obligatoires

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
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , 1 , args[0].tag.string().data() ,
                "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = seq->get_nb_variable();

  if (nb_variable == 1) {
    CHECKCONDVA(nb_required == 1 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeCorrelation"));

    variable1 = 1;
    variable2 = 1;
  }

  else {
    CHECKCONDVA((nb_required == 2) || (nb_required == 3) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeCorrelation"));

    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , 2 ,
                    args[1].tag.string().data() , "INT");
    }
    else {
      variable1 = args[1].val.i;
      if ((variable1 < 1) || (variable1 > nb_variable)) {
        status = false;
        genAMLError(ERRORMSG(VARIABLE_INDEX_2_sd) , "ComputeCorrelation" , 2);
      }
    }

    switch (nb_required) {

    case 2 : {
      variable2 = variable1;
      break;
    }

    case 3 : {
      if (args[2].tag() != AMObjType::INTEGER) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , 3 ,
                    args[2].tag.string().data() , "INT");
      }
      else {
        variable2 = args[2].val.i;
        if ((variable2 == variable1) || (variable2 < 1) || (variable2 > nb_variable)) {
          status = false;
          genAMLError(ERRORMSG(VARIABLE_INDEX_2_sd) , "ComputeCorrelation" , 3);
        }
      }
      break;
    }
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "MaxLag") {
        switch (max_lag_option) {

        case false : {
          max_lag_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            max_lag = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputeCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Type") {
        switch (type_option) {

        case false : {
          type_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "Pearson") {
              type = PEARSON;
            }
            else if (*pstr == "Spearman") {
              type = SPEARMAN;
            }
            else if (*pstr == "Kendall") {
              type = KENDALL;
            }
            else if (*pstr == "Spearman2") {
              type = SPEARMAN2;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(CORRELATION_COEFF_TYPE_sds) , "ComputeCorrelation" ,
                          nb_required + i + 1 , "Pearson or Spearman or Kendall");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputeCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Normalization") {
        switch (normalization_option) {

        case false : {
          normalization_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "Approximated") {
              normalization = APPROXIMATED;
            }
            else if (*pstr == "Exact") {
              normalization = EXACT;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(NORMALIZATION_sds) , "ComputeCorrelation" ,
                          nb_required + i + 1 , "Approximated or Exact");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputeCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "IndividualMean") {
        switch (individual_mean_option) {

        case false : {
          individual_mean_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            individual_mean = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputeCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "ComputeCorrelation" ,
                    nb_required + i + 1 , "MaxLag or Type or Normalization or IndividualMean");
      }
    }
  }

  if ((normalization_option) && ((type == SPEARMAN2) || (type == KENDALL))) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "ComputeCorrelation");
  }
  if ((individual_mean_option) && (type != PEARSON)) {
    status = false;
    genAMLError(ERRORMSG(INCOMPATIBLE_OPTIONS_s) , "ComputeCorrelation");
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  correl = seq->correlation_computation(error , variable1 , variable2 , type ,
                                        max_lag , normalization , individual_mean);

  if (correl) {
    STAT_model* model = new STAT_model(correl);
    return AMObj(AMObjType::CORRELATION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputeCorrelation");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul de la fonction de correlation theorique d'un bruit blanc
 *  pour une filtre donne.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputeWhiteNoiseCorrelation(const AMObjVector &args)

{
  register int i;
  bool status = true;
  int nb_point = I_DEFAULT , int_sum , *int_filter;
  double sum , *filter;
  const Distribution *dist;
  StatError error;


  CHECKCONDVA(args.length() == 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "ComputeWhiteNoiseCorrelation" , 2));

  if (args[0].tag() != AMObjType::CORRELATION) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeWhiteNoiseCorrelation" , 1 ,
                args[0].tag.string().data() , "CORRELATION");
  }

  filter = NULL;
  dist = NULL;

  if (args[1].tag() == AMObjType::ARRAY) {
    Array* parray = (Array*)args[1].val.p;

    if (parray->surfaceType() == AMObjType::INTEGER) {
      int_filter = buildIntArray(args , 1 , "ComputeWhiteNoiseCorrelation" , 2 , nb_point);
      if (!int_filter) {
        status = false;
      }

      else {
        nb_point--;

        int_sum = 0;
        for (i = 0;i < nb_point;i++) {
          int_sum += 2 * int_filter[i];
        }
        int_sum += int_filter[i];

        if (int_sum == 0) {
          status = false;
          genAMLError(ERRORMSG(FILTER_NORMALIZATION_sd) , "ComputeWhiteNoiseCorrelation" , 2);
        }

        else {
          filter = new double[2 * nb_point + 1];
          for (i = 0;i < nb_point;i++) {
            filter[i] = (double)int_filter[i] / (double)int_sum;
            filter[2 * nb_point - i] = filter[i];
          }
          filter[i] = (double)int_filter[i] / (double)int_sum;
        }

        delete [] int_filter;
      }
    }

    else if (parray->surfaceType() == AMObjType::REAL) {
      filter = buildRealArray(args , 1 , "ComputeWhiteNoiseCorrelation" , 2 , nb_point , true);
      if (!filter) {
        status = false;
      }

      else {
        sum = 0.;
        for (i = 0;i < nb_point;i++) {
          sum += 2 * filter[i];
          filter[2 * nb_point - i] = filter[i];
        }
        sum += filter[i];

        if ((sum < 1. - STAT_FILTER_ROUNDNESS) || (sum > 1. + STAT_FILTER_ROUNDNESS)) {
          status = false;
          genAMLError(ERRORMSG(FILTER_NORMALIZATION_sd) , "ComputeWhiteNoiseCorrelation" , 2);
        }
      }
    }

    else {
      status = false;
      genAMLError(ERRORMSG(ARRAY_ELEMENT_TYPE_1_sdss) , "ComputeWhiteNoiseCorrelation" , 2 ,
                  (parray->surfaceType()).string().data() , "INT or REAL");
    }
  }

  else if (args[1].tag() != AMObjType::INTEGER) {
    switch (args[1].tag()) {
    case AMObjType::DISTRIBUTION :
      dist = new Distribution(*((Distribution*)((DiscreteParametricModel*)((STAT_model*)args[1].val.p)->pt)));
      break;
    case AMObjType::DISCRETE_MIXTURE :
      dist = new Distribution(*((Distribution*)((DiscreteMixture*)((STAT_model*)args[1].val.p)->pt)));
      break;
    case AMObjType::CONVOLUTION :
      dist = new Distribution(*((Distribution*)((Convolution*)((STAT_model*)args[1].val.p)->pt)));
      break;
    case AMObjType::COMPOUND :
      dist = new Distribution(*((Distribution*)((Compound*)((STAT_model*)args[1].val.p)->pt)));
      break;
    default :
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeWhiteNoiseCorrelation" , 2 , args[1].tag.string().data() ,
                  "INT or ARRAY or DISTRIBUTION or DISCRETE_MIXTURE or CONVOLUTION or COMPOUND");
      break;
    }
  }

  if (!status) {
    delete [] filter;
    delete dist;

    return AMObj(AMObjType::ERROR);
  }

  if (!dist) {
    if (args[1].tag() == AMObjType::INTEGER) {
      status = ((Correlation*)((STAT_model*)args[0].val.p)->pt)->white_noise_correlation(error , args[1].val.i);
    }
    else {
      status = ((Correlation*)((STAT_model*)args[0].val.p)->pt)->white_noise_correlation(error , 2 * nb_point + 1 , filter);
    }
  }
  else {
    status = ((Correlation*)((STAT_model*)args[0].val.p)->pt)->white_noise_correlation(error , *dist);
  }

  delete [] filter;
  delete dist;

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputeWhiteNoiseCorrelation");
    return AMObj(AMObjType::ERROR);
  }    
}


/*--------------------------------------------------------------*
 *
 *  Calcul d'une fonction d'autocorrelation partielle.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputePartialAutoCorrelation(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , max_lag_option = false , type_option = false;
  register int i;
  int nb_required , nb_variable , variable , max_lag = I_DEFAULT , type = PEARSON;
  const Sequences *seq;
  Correlation *correl;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required >= 1 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputePartialAutoCorrelation"));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputePartialAutoCorrelation"));

  // arguments obligatoires

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
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputePartialAutoCorrelation" , 1 , args[0].tag.string().data() ,
                "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = seq->get_nb_variable();

  if (nb_variable == 1) {
    CHECKCONDVA(nb_required == 1 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputePartialAutoCorrelation"));

    variable = 1;
  }

  else {
    CHECKCONDVA(nb_required == 2 ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputePartialAutoCorrelation"));

    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputePartialAutoCorrelation" , 2 ,
                  args[1].tag.string().data() , "INT");
    }
    else {
      variable = args[1].val.i;
    }
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputePartialAutoCorrelation" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "MaxLag") {
        switch (max_lag_option) {

        case false : {
          max_lag_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputePartialAutoCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            max_lag = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputePartialAutoCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "Type") {
        switch (type_option) {

        case false : {
          type_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputePartialAutoCorrelation" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "Pearson") {
              type = PEARSON;
            }
            else if (*pstr == "Kendall") {
              type = KENDALL;
            }
            else {
              status = false;
              genAMLError(ERRORMSG(CORRELATION_COEFF_TYPE_sds) , "ComputePartialAutoCorrelation" ,
                          nb_required + i + 1 , "Pearson or Kendall");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "ComputePartialAutoCorrelation" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "ComputePartialAutoCorrelation" ,
                    nb_required + i + 1 , "MaxLag or Type");
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  correl = seq->partial_autocorrelation_computation(error , variable , type , max_lag);

  if (correl) {
    STAT_model* model = new STAT_model(correl);
    return AMObj(AMObjType::CORRELATION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputePartialAutoCorrelation");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Segmentation optimale de sequences.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Segmentation(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , sequence_option = false , output_option = false;
  register int i , j;
  int nb_required , nb_sequence , nb_variable , identifier = I_DEFAULT , output ,
      *model_type , *nb_segment;
  const Sequences *iseq;
  Sequences *seq;
  MarkovianSequences *markovian_seq;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required >= 3 , genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));

  // arguments obligatoires

  switch (args[0].tag()) {
  case AMObjType::SEQUENCES :
    iseq = (Sequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::MARKOVIAN_SEQUENCES :
    iseq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
    iseq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::SEMI_MARKOV_DATA :
    iseq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  default :
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , 1 , args[0].tag.string().data() ,
                "SEQUENCES or MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = iseq->get_nb_variable();

  if (args[1].tag() == AMObjType::ARRAY) {

    // arguments obligatoires

    nb_sequence = iseq->get_nb_sequence();
    nb_segment = buildIntArray(args , 1 , "Segmentation" , 2 , nb_sequence);
    if (!nb_segment) {
      status = false;
    }

    model_type = new int[nb_variable];

    for (i = 0;i < nb_variable;i++) {
      if (args[i + 2].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , i + 3 ,
                    args[i + 2].tag.string().data() , "STRING");
      }

      else {
        pstr = (AMString*)args[i + 2].val.p;

        if (i == 0) {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "MultivariateCategorical") {
            model_type[i] = MULTIVARIATE_CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "MultivariatePoisson") {
            model_type[i] = MULTIVARIATE_POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "MultivariateGeometric") {
            model_type[i] = MULTIVARIATE_GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Mean") {
            model_type[i] = MEAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "MeanVariance") {
            model_type[i] = MEAN_VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else if (*pstr == "BayesianPoisson") {
            model_type[i] = BAYESIAN_POISSON_CHANGE;
          }
          else if (*pstr == "BayesianGaussian") {
            model_type[i] = BAYESIAN_GAUSSIAN_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Segmentation" , i + 3 ,
                        "Categorical or Poisson or MultivariatePoisson or Geometric or ShiftedGeometric or MultivariateGeometric or Ordinal or Gaussian or Mean or Variance or MeanVariance or LinearModel or InterceptSlope");
          }

          if ((model_type[i] == MULTIVARIATE_CATEGORICAL_CHANGE) || (model_type[i] == MULTIVARIATE_POISSON_CHANGE) ||
              (model_type[i] == MULTIVARIATE_GEOMETRIC_0_CHANGE) || (model_type[i] == MEAN_CHANGE) ||
              (model_type[i] == MEAN_VARIANCE_CHANGE) || (model_type[i] == INTERCEPT_SLOPE_CHANGE)) {
            CHECKCONDVA(nb_required == 3 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));

            for (j = 1;j < nb_variable;j++) {
              model_type[j] = model_type[i];
            }
            break;
          }

          else {
            CHECKCONDVA(nb_required == nb_variable + 2 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));
          }
        }

        else {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Segmentation" , i + 3 ,
                        "Categorical or Poisson or Geometric or ShiftedGeometric or Ordinal or Gaussian or Variance or LinearModel or InterceptSlope");
          }
        }
      }
    }

    CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));

    output = SEQUENCE;

    // argument optionnel

    if (args.length() == nb_required + 2) {
      if (args[nb_required].tag() != AMObjType::OPTION) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + 1 ,
                    args[nb_required].tag.string().data() , "OPTION");
      }
      else {
        if (*((AMString*)args[nb_required].val.p) != "Output") {
          status = false;
          genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Segmentation" , nb_required + 1 ,
                      "Output");
        }
      }

      if (args[nb_required + 1].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + 1 ,
                    args[nb_required + 1].tag.string().data() , "STRING");
      }
      else {
        pstr = (AMString*)args[nb_required + 1].val.p;
        if (*pstr == "Sequence") {
          output = SEQUENCE;
        }
        else if ((*pstr == "SubtractionResidual") || (*pstr == "Residual")) {
          output = SUBTRACTION_RESIDUAL;
        }
        else if (*pstr == "DivisionResidual") {
          output = DIVISION_RESIDUAL;
        }
        else {
          status = false;
          genAMLError(ERRORMSG(SEGMENTATION_OUTPUT_sds) , "Segmentation" , nb_required + 1 ,
                      "Sequence or Residual");
        }
      }
    }

    if (!status) {
      delete [] nb_segment;
      delete [] model_type;
      return AMObj(AMObjType::ERROR);
    }

    seq = iseq->segmentation(error , AMLOUTPUT , nb_segment , model_type ,
                             identifier , output);
    delete [] nb_segment;
    delete [] model_type;
  }

  else if (args[1].tag() == AMObjType::INTEGER) {
    CHECKCONDVA(nb_required >= 4 , genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));

    // argument obligatoire

    model_type = new int[nb_variable];

    for (i = 0;i < nb_variable;i++) {
      if (args[i + 3].tag() != AMObjType::STRING) {
        status = false;
        genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , i + 4 ,
                    args[i + 3].tag.string().data() , "STRING");
      }

      else {
        pstr = (AMString*)args[i + 3].val.p;

        if (i == 0) {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "MultivariateCategorical") {
            model_type[i] = MULTIVARIATE_CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "MultivariatePoisson") {
            model_type[i] = MULTIVARIATE_POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "MultivariateGeometric") {
            model_type[i] = MULTIVARIATE_GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Mean") {
             model_type[i] = MEAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "MeanVariance") {
            model_type[i] = MEAN_VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else if (*pstr == "BayesianPoisson") {
            model_type[i] = BAYESIAN_POISSON_CHANGE;
          }
          else if (*pstr == "BayesianGaussian") {
            model_type[i] = BAYESIAN_GAUSSIAN_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Segmentation" , i + 4 ,
                        "Categorical or Poisson or MultivariatePoisson or Geometric or ShiftedGeometric or MultivariateGeometric or Ordinal or Gaussian or Mean or Variance or MeanVariance or LinearModel or InterceptSlope");
          }

          if ((model_type[i] == MULTIVARIATE_CATEGORICAL_CHANGE) || (model_type[i] == MULTIVARIATE_POISSON_CHANGE) ||
              (model_type[i] == MULTIVARIATE_GEOMETRIC_0_CHANGE) || (model_type[i] == MEAN_CHANGE) ||
              (model_type[i] == MEAN_VARIANCE_CHANGE) || (model_type[i] == INTERCEPT_SLOPE_CHANGE)) {
            CHECKCONDVA(nb_required == 4 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));

            for (j = 1;j < nb_variable;j++) {
              model_type[j] = model_type[i];
            }
            break;
          }

          else {
            CHECKCONDVA(nb_required == nb_variable + 3 ,
                        genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Segmentation"));
          }
        }

        else {
          if (*pstr == "Categorical") {
            model_type[i] = CATEGORICAL_CHANGE;
          }
          else if (*pstr == "Poisson") {
            model_type[i] = POISSON_CHANGE;
          }
          else if (*pstr == "Geometric") {
            model_type[i] = GEOMETRIC_0_CHANGE;
          }
          else if (*pstr == "ShiftedGeometric") {
            model_type[i] = GEOMETRIC_1_CHANGE;
          }
          else if (*pstr == "Ordinal") {
            model_type[i] = ORDINAL_GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Gaussian") {
            model_type[i] = GAUSSIAN_CHANGE;
          }
          else if (*pstr == "Variance") {
            model_type[i] = VARIANCE_CHANGE;
          }
          else if (*pstr == "LinearModel") {
            model_type[i] = LINEAR_MODEL_CHANGE;
          }
          else if (*pstr == "InterceptSlope") {
            model_type[i] = INTERCEPT_SLOPE_CHANGE;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(CHANGE_POINT_MODEL_sds) , "Segmentation" , i + 4 ,
                        "Categorical or Poisson or Geometric or ShiftedGeometric or Ordinal or Gaussian or Variance or LinearModel or InterceptSlope");
          }
        }
      }
    }

    if (args[2].tag() == AMObjType::INTEGER) {
      int nb_segment_option = false , nb_segment_estimation = true;


      CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
                  (args.length() == nb_required + 4) ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Segmentation" , nb_required));

      output = SEQUENCE;

      // arguments optionnels

      for (i = 0;i < (args.length() - nb_required) / 2;i++) {
        if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + i + 1 ,
                      args[nb_required + i * 2].tag.string().data() , "OPTION");
        }

        else {
          pstr = (AMString*)args[nb_required + i * 2].val.p;

          if (*pstr == "NbSegment") {
            switch (nb_segment_option) {

            case false : {
              nb_segment_option = true;

              if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
                status = false;
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + i + 1 ,
                            args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
              }
              else {
                pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
                if (*pstr == "Fixed") {
                  nb_segment_estimation = false;
                }
                else if (*pstr == "Estimated") {
                  nb_segment_estimation = true;
                }
                else {
                  status = false;
                  genAMLError(ERRORMSG(NB_SEGMENT_ESTIMATION_sds) , "Segmentation" ,
                              nb_required + i + 1 , "Fixed or Estimated");
                }
              }
              break;
            }

            case true : {
              status = false;
              genAMLError(ERRORMSG(USED_OPTION_sd) , "Segmentation" , nb_required + i + 1);
              break;
            }
            }
          }

          else if (*pstr == "Output") {
            switch (output_option) {

            case false : {
              output_option = true;

              if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
                status = false;
                genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + i + 1 ,
                            args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
              }
              else {
                pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;
                if (*pstr == "Sequence") {
                  output = SEQUENCE;
                }
                else if ((*pstr == "SubtractionResidual") || (*pstr == "Residual")) {
                  output = SUBTRACTION_RESIDUAL;
                }
                else if (*pstr == "DivisionResidual") {
                  output = DIVISION_RESIDUAL;
                }
                else if (*pstr == "Entropy") {
                  output = SEGMENTATION_ENTROPY;
                }
                else if (*pstr == "Divergence") {
                  output = SEGMENTATION_DIVERGENCE;
                }
                else {
                  status = false;
                  genAMLError(ERRORMSG(SEGMENTATION_OUTPUT_sds) , "Segmentation" , nb_required + i + 1 ,
                              "Sequence or Residual or Entropy or Divergence");
                }
              }
              break;
            }

            case true : {
              status = false;
              genAMLError(ERRORMSG(USED_OPTION_sd) , "Segmentation" , nb_required + i + 1);
              break;
            }
            }
          }

          else {
            status = false;
            genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Segmentation" , nb_required + i + 1 ,
                        "NbSegment or Output");
          }
        }
      }

      if (output_option) {
        switch (nb_segment_estimation) {

        case false : {
          if ((output == SEGMENTATION_ENTROPY) || (output == SEGMENTATION_DIVERGENCE)) {
            status = false;
            genAMLError(ERRORMSG(SEGMENTATION_OUTPUT_ss) , "Segmentation" ,
                        "Sequence or Residual");
          }
          break;
        }

        case true : {
          if ((output == SUBTRACTION_RESIDUAL) || (output == DIVISION_RESIDUAL)) {
            status = false;
            genAMLError(ERRORMSG(SEGMENTATION_OUTPUT_ss) , "Segmentation" ,
                        "Sequence or Entropy or Divergence");
          }
          break;
        }
        }
      }

      if (!status) {
        delete [] model_type;
        return AMObj(AMObjType::ERROR);
      }

      switch (nb_segment_estimation) {

      case false : {
        if (args[2].val.i == 1) {
          seq = iseq->segmentation(error , AMLOUTPUT , args[1].val.i , args[2].val.i ,
                                   0 , model_type , output);
        }

        else {
          nb_sequence = iseq->get_nb_sequence();
          nb_segment = new int[nb_sequence];

          for (i = 0;i < nb_sequence;i++) {
            nb_segment[i] = args[2].val.i;
          }

          seq = iseq->segmentation(error , AMLOUTPUT , nb_segment , model_type ,
                                   args[1].val.i , output);
          delete [] nb_segment;
        }
        break;
      }

      case true : {
        seq = iseq->segmentation(error , AMLOUTPUT , args[1].val.i , args[2].val.i ,
                                 model_type , output);
        break;
      }
      }

      delete [] model_type;
    }

    else if (args[2].tag() == AMObjType::ARRAY) {
      int nb_segment = I_DEFAULT , *change_point;


      CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
                  genAMLError(ERRORMSG(K_NB_ARG_ERR_sd) , "Segmentation" , nb_required));

      // argument obligaoire

      change_point = buildIntArray(args , 2 , "Segmentation" , 3 , nb_segment);
      if (!change_point) {
        status = false;
      }
      else {
        nb_segment++;
      }

      // argument optionnel

      output = SEQUENCE;

      if (args.length() == nb_required + 2) {
        if (args[nb_required].tag() != AMObjType::OPTION) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + 1 ,
                      args[nb_required].tag.string().data() , "OPTION");
        }
        else {
          if (*((AMString*)args[nb_required].val.p) != "Output") {
            status = false;
            genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Segmentation" , nb_required + 1 ,
                        "Output");
          }
        }

        if (args[nb_required + 1].tag() != AMObjType::STRING) {
          status = false;
          genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , nb_required + 1 ,
                      args[nb_required + 1].tag.string().data() , "STRING");
        }
        else {
          pstr = (AMString*)args[nb_required + 1].val.p;
          if (*pstr == "Sequence") {
            output = SEQUENCE;
          }
          else if ((*pstr == "SubtractionResidual") || (*pstr == "Residual")) {
            output = SUBTRACTION_RESIDUAL;
          }
          else if (*pstr == "DivisionResidual") {
            output = DIVISION_RESIDUAL;
          }
          else {
            status = false;
            genAMLError(ERRORMSG(SEGMENTATION_OUTPUT_sds) , "Segmentation" , nb_required + 1 ,
                        "Sequence or Residual");
          }
        }
      }

      if (!status) {
        delete [] change_point;
        delete [] model_type;
        return AMObj(AMObjType::ERROR);
      }

      seq = iseq->segmentation(error , AMLOUTPUT , args[1].val.i , nb_segment ,
                               change_point , model_type , output);
      delete [] change_point;
      delete [] model_type;
    }

    else {
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , 3 ,
                  args[2].tag.string().data() , "INT or ARRAY");
      return AMObj(AMObjType::ERROR);
    }
  }

  else {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Segmentation" , 2 ,
                args[1].tag.string().data() , "INT or ARRAY");
    return AMObj(AMObjType::ERROR);
  }

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
    genAMLError(ERRORMSG(STAT_MODULE_s) , "Segmentation");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul des echantillons correspondant a l'evolution des probabilites
 *  de rester dans un etat donne d'une chaine de Markov.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputeSelfTransition(const AMObjVector &args)

{
  MarkovianSequences *seq;


  CHECKCONDVA(args.length() == 1 ,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "ComputeSelfTransition"));

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
  default :
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeSelfTransition" , 1 , args[0].tag.string().data() ,
                "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  seq->self_transition_computation();

  return AMObj(AMObjType::VOID);
}


/*--------------------------------------------------------------*
 *
 *  Comptage des transitions pour differents ordres.
 *
 *--------------------------------------------------------------*/

AMObj STAT_TransitionCount(const AMObjVector &args)

{
  RWCString *pstr;
  char *file_name = NULL , format = 'a';
  bool status = true , begin_option = false , begin = false , estimator_option = false ,
       file_name_option = false , format_option = false;
  register int i;
  int nb_required , estimator = MAXIMUM_LIKELIHOOD;
  const MarkovianSequences *seq;
  StatError error;


  nb_required = 2;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "TransitionCount"));

  // arguments obligatoires

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
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , 1 , args[0].tag.string().data() ,
                "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    break;
  }

  if (args[1].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , 2 ,
                args[1].tag.string().data() , "INT");
  }

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "Begin") {
        switch (begin_option) {

        case false : {
          begin_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::BOOL) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "BOOL");
          }
          else {
            begin = args[nb_required + i * 2 + 1].val.b;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "TransitionCount" , nb_required + i + 1);
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
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , nb_required + i + 1 ,
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
              genAMLError(ERRORMSG(ESTIMATOR_NAME_sds) , "TransitionCount" ,
                          nb_required + i + 1 , "MaximumLikelihood or Laplace or AdaptativeLaplace or UniformSubset or UniformCardinality");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "TransitionCount" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "FileName") {
        switch (file_name_option) {

        case false : {
          file_name_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            file_name = (char*)((AMString*)args[nb_required + i * 2 + 1].val.p)->data();
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "TransitionCount" , nb_required + i + 1);
          break;
        }
        }
      }

/*      else if (*pstr == "Format") {
        switch (format_option) {

        case false : {
          format_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::STRING) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "TransitionCount" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "STRING");
          }
          else {
            pstr = (AMString*)args[nb_required + i * 2 + 1].val.p;

            if (*pstr == "ASCII") {
              format = 'a';
            }
            else if (*pstr == "SpreadSheet") {
              format = 's';
            }
            else {
              status = false;
              genAMLError(ERRORMSG(K_FILE_FORMAT_ERR_sds) , "TransitionCount" ,
                          nb_required + i + 1 , "ASCII or SpreadSheet");
            }
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "TransitionCount" , nb_required + i + 1);
          break;
        }
        }
      } */

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "TransitionCount" ,
                    nb_required + i + 1 , "Begin or Estimator or FileName");
//                    nb_required + i + 1 , "Begin or FileName or Format");
      }
    }
  }

/*  if ((!file_name_option) && (format_option)) {
    status = false;
    genAMLError(ERRORMSG(MISSING_FILE_NAME_OPTION_s) , "TransitionCount");
  } */

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  status = seq->transition_count(error , AMLOUTPUT , args[1].val.i , begin , estimator , file_name);
//  status = seq->transition_count_0(error , AMLOUTPUT , args[1].val.i , begin , file_name , format);

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "TransitionCount");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Comptage des frequences des mots de longueur donnee.
 *
 *--------------------------------------------------------------*/

AMObj STAT_WordCount(const AMObjVector &args)

{
  RWCString *pstr;
  bool status = true , begin_state_option = false , end_state_option = false ,
       min_frequency_option = false;
  register int i;
  int nb_required , nb_variable , variable , offset , begin_state = I_DEFAULT ,
      end_state = I_DEFAULT , min_frequency = 1;
  MarkovianSequences *seq;
  StatError error;


  CHECKCONDVA(args.length() >= 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "WordCount"));

  // arguments obligatoires

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
  default :
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , 1 , args[0].tag.string().data() ,
                "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  nb_variable = seq->get_nb_variable();

  if (nb_variable == 1) {
    offset = 1;
    variable = 1;
  }

  else {
    offset = 2;

    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , 2 ,
                  args[1].tag.string().data() , "INT");
    }
    else {
      variable = args[1].val.i;
    }
  }

  if (args[offset].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , offset + 1 ,
                args[offset].tag.string().data() , "INT");
  }

  nb_required = offset + 1;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ||
              (args.length() == nb_required + 4) || (args.length() == nb_required + 6) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "WordCount"));

  // arguments optionnels

  for (i = 0;i < (args.length() - nb_required) / 2;i++) {
    if (args[nb_required + i * 2].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , nb_required + i + 1 ,
                  args[nb_required + i * 2].tag.string().data() , "OPTION");
    }

    else {
      pstr = (AMString*)args[nb_required + i * 2].val.p;

      if (*pstr == "BeginState") {
        switch (begin_state_option) {

        case false : {
          begin_state_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            begin_state = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "WordCount" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "EndState") {
        switch (end_state_option) {

        case false : {
          end_state_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            end_state = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "WordCount" , nb_required + i + 1);
          break;
        }
        }
      }

      else if (*pstr == "MinFrequency") {
        switch (min_frequency_option) {

        case false : {
          min_frequency_option = true;

          if (args[nb_required + i * 2 + 1].tag() != AMObjType::INTEGER) {
            status = false;
            genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "WordCount" , nb_required + i + 1 ,
                        args[nb_required + i * 2 + 1].tag.string().data() , "INT");
          }
          else {
            min_frequency = args[nb_required + i * 2 + 1].val.i;
          }
          break;
        }

        case true : {
          status = false;
          genAMLError(ERRORMSG(USED_OPTION_sd) , "WordCount" , nb_required + i + 1);
          break;
        }
        }
      }

      else {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "WordCount" , nb_required + i + 1 ,
                    "BeginState or EndState or MinFrequency");
      }
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  status = seq->word_count(error , AMLOUTPUT , variable , args[offset].val.i ,
                           begin_state , end_state , min_frequency);

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "WordCount");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Test de l'aggregation des etats d'une chaine de Markov.
 *
 *--------------------------------------------------------------*/

AMObj STAT_LumpabilityTest(const AMObjVector &args)

{
  bool status = true;
  int nb_required , order = 1 , nb_symbol , *symbol = NULL;
  const MarkovianSequences *seq;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA(nb_required == 2 ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "LumpabilityTest"));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "LumpabilityTest"));

    // argument obligatoire

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
  default :
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "LumpabilityTest" , 1 , args[0].tag.string().data() ,
                "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA or NONHOMOGENEOUS_MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  nb_symbol = seq->get_marginal_distribution(0)->nb_value;

  if (args[1].tag() != AMObjType::ARRAY) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "LumpabilityTest" , 2 ,
                args[1].tag.string().data() , "ARRAY");
  }
  else {
    symbol = buildIntArray(args , 1 , "LumpabilityTest" , 2 , nb_symbol);
    if (!symbol) {
      status = false;
    }
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "LumpabilityTest" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Order") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "LumpabilityTest" , nb_required + 1 ,
                    "Order");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "LumpabilityTest" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "INT");
    }
    else {
      order = args[nb_required + 1].val.i;
    }
  }

  if (!status) {
    delete [] symbol;
    return AMObj(AMObjType::ERROR);
  }

  status = seq->lumpability_test(error , AMLOUTPUT , symbol , order);
  delete [] symbol;

  if (status) {
    return AMObj(AMObjType::VOID);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "LumpabilityTest");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Application d'un seuil sur les parametres d'un modele markovien.
 *
 *--------------------------------------------------------------*/

static AMObj STAT_ThresholdingProbability(const AMObjVector &args)

{
  bool status = true;
  int nb_required = 1;
  double min_probability = MIN_PROBABILITY;


  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "Thresholding"));

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Thresholding" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "MinProbability") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "Thresholding" , nb_required + 1 ,
                    "MinProbability");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::REAL) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Thresholding" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "REAL");
    }
    else {
      min_probability = args[nb_required + 1].val.r;
    }
  }

  if (status) {
    if (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) {
      VariableOrderMarkov *markov;

      markov = ((VariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->thresholding(min_probability);

      STAT_model* model = new STAT_model(markov);
      return AMObj(AMObjType::VARIABLE_ORDER_MARKOV , model);
    }

    if (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV) {
      HiddenVariableOrderMarkov *hmarkov;

      hmarkov = ((HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt)->thresholding(min_probability);

      STAT_model* model = new STAT_model(hmarkov);
      return AMObj(AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV , model);
    }

    if (args[0].tag() == AMObjType::SEMI_MARKOV) {
      SemiMarkov *smarkov;

      smarkov = ((SemiMarkov*)((STAT_model*)args[0].val.p)->pt)->thresholding(min_probability);

      STAT_model* model = new STAT_model(smarkov);
      return AMObj(AMObjType::SEMI_MARKOV , model);
    }

    if (args[0].tag() == AMObjType::HIDDEN_SEMI_MARKOV) {
      HiddenSemiMarkov *hsmarkov;

      hsmarkov = ((HiddenSemiMarkov*)((STAT_model*)args[0].val.p)->pt)->thresholding(min_probability);

      STAT_model* model = new STAT_model(hsmarkov);
      return AMObj(AMObjType::HIDDEN_SEMI_MARKOV , model);
    }

    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "Thresholding" ,
                1 , args[0].tag.string().data() ,
                "VARIABLE_ORDER_MARKOV or HIDDEN_VARIABLE_ORDER_MARKOV or SEMI-MARKOV or HIDDEN_SEMI-MARKOV");
  }

  return AMObj(AMObjType::ERROR);
}


/*--------------------------------------------------------------*
 *
 *  Application d'un seuil.
 *
 *--------------------------------------------------------------*/

AMObj STAT_Thresholding(const AMObjVector &args)

{
  if ((args[0].tag() == AMObjType::VECTORS) || (args[0].tag() == AMObjType::SEQUENCES) ||
      (args[0].tag() == AMObjType::MARKOVIAN_SEQUENCES) ||
      (args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::SEMI_MARKOV_DATA) ||
      (args[0].tag() == AMObjType::NONHOMOGENEOUS_MARKOV_DATA)) {
    return STAT_ThresholdingData(args);
  }

  else {
    return STAT_ThresholdingProbability(args);
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul de la fonction d'autocorrelation correspondant a un etat
 *  pour une chaine de Markov d'ordre variable / a une observation
 *  pour une chaine de Markov d'ordre variable cachee.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputeAutoCorrelation(const AMObjVector &args)

{
  bool status = true;
  int nb_required , variable , offset , value , max_lag = MAX_LAG;
  const VariableOrderMarkov *markov;
  Correlation *correl;
  StatError error;


  nb_required = nb_required_computation(args);

  CHECKCONDVA((nb_required == 2) || (nb_required == 3) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeAutoCorrelation"));

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeAutoCorrelation"));

  // arguments obligatoires

  switch (args[0].tag()) {

  case AMObjType::VARIABLE_ORDER_MARKOV : {
    markov = (VariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt;
    break;
  }

  case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV : {
    markov = (HiddenVariableOrderMarkov*)((STAT_model*)args[0].val.p)->pt;
    break;
  }

  default : {
    if (args[0].tag() != AMObjType::VARIABLE_ORDER_MARKOV_DATA) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeAutoCorrelation" , 1 , args[0].tag.string().data() ,
                  "VARIABLE_ORDER_MARKOV or HIDDEN_VARIABLE_ORDER_MARKOV or VARIABLE_ORDER_MARKOV_DATA");
    }
    break;
  }
  }

  switch (nb_required) {

  case 2 : {
    offset = 1;
    break;
  }

  case 3 : {
    offset = 2;
    if (args[1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeAutoCorrelation" , 2 ,
                  args[1].tag.string().data() , "INT");
    }
    else {
      variable = args[1].val.i;
    }
    break;
  }
  }

  if (args[offset].tag() != AMObjType::INTEGER) {
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeAutoCorrelation" , offset + 1 ,
                args[offset].tag.string().data() , "INT");
  }
  else {
    value = args[offset].val.i;
  }

  // arguments optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeAutoCorrelation" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "MaxLag") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "ComputeAutoCorrelation" , nb_required + 1 ,
                    "MaxLag");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::INTEGER) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeAutoCorrelation" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "INT");
    }
    else {
      max_lag = args[nb_required + 1].val.i;
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  switch (nb_required) {

  case 2 : {
    if ((args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
        (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV)) {
      correl = markov->state_autocorrelation_computation(error , value , max_lag);
    }
    else {
      correl = ((VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt)->state_autocorrelation_computation(error , value , max_lag);
    }
    break;
  }

  case 3 : {
    if ((args[0].tag() == AMObjType::VARIABLE_ORDER_MARKOV) ||
        (args[0].tag() == AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV)) {
      correl = markov->output_autocorrelation_computation(error , variable , value , max_lag);
    }
    else {
      correl = ((VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt)->output_autocorrelation_computation(error , variable , value , max_lag);
    }
    break;
  }
  }

  if (correl) {
    STAT_model* model = new STAT_model(correl);
    return AMObj(AMObjType::CORRELATION , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputeAutoCorrelation");
    return AMObj(AMObjType::ERROR);
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul des sequences d'etats les plus probables.
 *
 *--------------------------------------------------------------*/

AMObj STAT_ComputeStateSequences(const AMObjVector &args)

{
  bool status = true , characteristic_flag = true;
  int nb_required;
  const MarkovianSequences *iseq;
  StatError error;


  nb_required = 2;

  CHECKCONDVA((args.length() == nb_required) || (args.length() == nb_required + 2) ,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_s) , "ComputeStateSequences"));

  // argument obligatoire

  switch (args[0].tag()) {
  case AMObjType::MARKOVIAN_SEQUENCES :
    iseq = (MarkovianSequences*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
    iseq = (VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  case AMObjType::SEMI_MARKOV_DATA :
    iseq = (SemiMarkovData*)((STAT_model*)args[0].val.p)->pt;
    break;
  default :
    status = false;
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeStateSequences" , 1 , args[0].tag.string().data() ,
                "MARKOVIAN_SEQUENCES or VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
    break;
  }

  // argument optionnel

  if (args.length() == nb_required + 2) {
    if (args[nb_required].tag() != AMObjType::OPTION) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeStateSequences" , nb_required + 1 ,
                  args[nb_required].tag.string().data() , "OPTION");
    }
    else {
      if (*((AMString*)args[nb_required].val.p) != "Characteristics") {
        status = false;
        genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sds) , "ComputeStateSequences" , nb_required + 1 ,
                    "Characteristics");
      }
    }

    if (args[nb_required + 1].tag() != AMObjType::BOOL) {
      status = false;
      genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeStateSequences" , nb_required + 1 ,
                  args[nb_required + 1].tag.string().data() , "BOOL");
    }
    else {
      characteristic_flag = args[nb_required + 1].val.b;
    }
  }

  if (!status) {
    return AMObj(AMObjType::ERROR);
  }

  switch (args[1].tag()) {

  case AMObjType::HIDDEN_VARIABLE_ORDER_MARKOV : {
    VariableOrderMarkovData *seq;


    seq = ((HiddenVariableOrderMarkov*)((STAT_model*)args[1].val.p)->pt)->state_sequence_computation(error , *iseq ,
                                                                                                     characteristic_flag);

    if (seq) {
      STAT_model* model = new STAT_model(seq);
      return AMObj(AMObjType::VARIABLE_ORDER_MARKOV_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputeStateSequences");
      return AMObj(AMObjType::ERROR);
    }
  }

  case AMObjType::HIDDEN_SEMI_MARKOV : {
    SemiMarkovData *seq;


    seq = ((HiddenSemiMarkov*)((STAT_model*)args[1].val.p)->pt)->state_sequence_computation(error , AMLOUTPUT , *iseq ,
                                                                                            characteristic_flag);

    if (seq) {
      STAT_model* model = new STAT_model(seq);
      return AMObj(AMObjType::SEMI_MARKOV_DATA , model);
    }
    else {
      AMLOUTPUT << "\n" << error;
      genAMLError(ERRORMSG(STAT_MODULE_s) , "ComputeStateSequences");
      return AMObj(AMObjType::ERROR);
    }
  }

  default : {
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "ComputeStateSequences" , 2 , args[1].tag.string().data() ,
                "HIDDEN_VARIABLE_ORDER_MARKOV or HIDDEN_SEMI-MARKOV");
    return AMObj(AMObjType::ERROR);
  }
  }
}


/*--------------------------------------------------------------*
 *
 *  Construction des variables auxilliaires correspondant a la restauration
 *  des sequences d'etats optimales pour des modeles markoviens caches.
 *
 *--------------------------------------------------------------*/

AMObj STAT_BuildAuxiliaryVariable(const AMObjVector &args)

{
  MarkovianSequences *seq;
  StatError error;


  CHECKCONDVA(args.length() == 1 ,
              genAMLError(ERRORMSG(K_SINGLE_ARG_ERR_s) , "BuildAuxiliaryVariable"));

  switch (args[0].tag()) {

  case AMObjType::VARIABLE_ORDER_MARKOV_DATA :
    seq = ((VariableOrderMarkovData*)((STAT_model*)args[0].val.p)->pt)->build_auxiliary_variable(error);
    break;
  case AMObjType::SEMI_MARKOV_DATA :
    seq = ((SemiMarkovData*)((STAT_model*)args[0].val.p)->pt)->build_auxiliary_variable(error);
    break;
  default :
    genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss) , "BuildAuxiliaryVariable" , 1 , args[0].tag.string().data() ,
                "VARIABLE_ORDER_MARKOV_DATA or SEMI-MARKOV_DATA");
    return AMObj(AMObjType::ERROR);
  }

  if (seq) {
    STAT_model* model = new STAT_model(seq);
    return AMObj(AMObjType::MARKOVIAN_SEQUENCES , model);
  }
  else {
    AMLOUTPUT << "\n" << error;
    genAMLError(ERRORMSG(STAT_MODULE_s) , "BuildAuxiliaryVariable");
    return AMObj(AMObjType::ERROR);
  }
}

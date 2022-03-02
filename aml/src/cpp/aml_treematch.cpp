/* -*-c++-*-
 *  ----------------------------------------------------------------------------
 *
 *       AMAPmod: Exploring and Modeling Plant Architecture
 *
 *       Copyright 1995-2000 UMR Cirad/Inra Modelisation des Plantes
 *
 *       File author(s): P. Ferraro (pascal.ferraro@cirad.fr)
 *
 *       $Source$
 *       $Id: aml_treematch.cpp 3573 2007-09-05 16:59:56Z dufourko $
 *
 *       Forum for AMAPmod developers    : amldevlp@cirad.fr
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







#include "aml/aml_treematch.h"

#define  ERR_MSG_ARRAY mtg_err_msgs_aml
#define  MODULE_NAME   "Tree Matching"
AMObj AML_TreeMatch::save(const AMObjVector& args) const
{
  assert(&args);

  int len = args.length();
  int argth = 2;
  const char *mtg_err_msgs_aml[] =
  {
    "Cannot proceed: no MTG loaded",
    "function %s: undefined feature %s"
  };

  RWCString format("ASCII");

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TreeMatching", 1));

  CHECKCONDVA(args[1].tag() ==AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TreeMatching", 1, args[0].tag.string().data(), "STRING"));
  RWCString file_name =  *(AMString*)(args[1].val.p);

  while (argth < len)
  {
    // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd),"TreeMatching",(argth+1)/2+1));

    // must contain at least two parameters : this is verified syntactically

    assert(argth + 1 < len);

    if (*(AMString*)(args[argth].val.p) == "Format")
    {
      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));

      format = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA( format == "ASCII" || format == "Binary" || format == "SpreadSheet",
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "one of ASCII, Binary, SpreadSheet"));

    }
    argth += 2;

  }

  char TAB='\t';

  if (!strcmp(format.data(),"ASCII"))
  {

    RWCString name=file_name+".txt";
    fstream out_file(name.data(),ios::out);

    out_file<<TAB;;
    int i,j,k;
    int nb_matching=getNbTree()*(getNbTree()-1)/2;
    DistanceType max_distance=MINDIST;
    DistanceType min_distance=MAXDIST;
    DistanceType average_distance=0.0;

    float ins_rate=0.0;
    float sub_rate=0.0;
    float del_rate=0.0;
    float mat_rate=0.0;


    out_file<<" MATCHING OF "<<getNbTree()<<" TREES"<<endl;
    out_file<<endl<<" DISTANCE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    out_file<<TAB;
    for (i=0; i<getNbTree();i++)
    {

      out_file<<"|"<<TAB<<"T"<<i<<TAB;
    }
    out_file<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"  T"<<i<<TAB;
      for(j=0;j<getNbTree();j++)
      {
        DistanceType D=0;
// Before Fred Correction  : if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<"|"<<TAB<<D<<TAB;
      }
          out_file<<"|"<<endl;
    }
    for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;

    out_file<<endl<<" CONSERVATION RATE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    for (i=0; i<getNbTree();i++)
    {
      out_file<<TAB<<"|"<<"T"<<i;
    }
    out_file<<TAB<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"T"<<i<<"";
      for(int j=0;j<getNbTree();j++)
          {

            if (i!=j)
            {
              float T=0;
              int nb_inp_vertex = getTree(i)->getNbVertex();

              int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :          T=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
              T=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
              out_file<<TAB<<"|"<<T;
            }
            else
            {
              out_file<<TAB<<"|   *";
            };
          }
      out_file<<TAB<<"|"<<endl;
    }
    for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;



    for (i=0; i<getNbTree()-1;i++)
    {
      int tree_size1=getTree(i)->getNbVertex();

      for(int j=i+1;j<getNbTree();j++)
      {
        Sequence* mat_seq=getSequence(i,j);
        int seq_size=mat_seq->getSize();
        int sub_number=0;
        int mat_number=0;
        mat_seq->reset();
        do
        {
          if (mat_seq->getCurrent()->getCost()==0.0)
          {
            mat_number++;
          }
          else
          {
            sub_number++;
          };
        } while(mat_seq->next());
        int tree_size2=getTree(j)->getNbVertex();

        int nb_edit_op=tree_size1+tree_size2-seq_size;
        del_rate = del_rate + ((float) tree_size1-seq_size)/((float) nb_edit_op);
        ins_rate = ins_rate + ((float) tree_size2-seq_size)/((float) nb_edit_op);
        sub_rate = sub_rate + ((float) sub_number)/((float) nb_edit_op);
        mat_rate = mat_rate + ((float) mat_number)/((float) nb_edit_op);
        DistanceType distance=getDistance(i,j);
        max_distance=I_MAX(max_distance,distance);
        min_distance=I_MIN(min_distance,distance);
        average_distance=average_distance+distance;
      }
    }
    average_distance=average_distance/((float) nb_matching);
    del_rate = del_rate/((float) nb_matching);
    sub_rate = sub_rate/((float) nb_matching);
    ins_rate = ins_rate/((float) nb_matching);
    mat_rate = mat_rate/((float) nb_matching);
    out_file<<endl;
    out_file<<"MAXIMUM DISTANCE         : "<<max_distance<<endl;
    out_file<<"MINIMUM DISTANCE         : "<<min_distance<<endl;
    out_file<<"AVERAGE DISTANCE         : "<<average_distance<<endl;
    out_file<<endl;
    out_file<<"AVERAGE INSERTION RATE   : "<<ins_rate<<endl;
    out_file<<"AVERAGE DELETION  RATE   : "<<del_rate<<endl;
    out_file<<"AVERAGE MATCHING RATE    : "<<mat_rate<<endl;
    out_file<<"AVERAGE SUBSTITUTION RATE : "<<sub_rate<<endl;
    out_file<<endl;

    out_file.close();

  }
  else if (!strcmp(format.data(),"SpreadSheet"))
  {

    int i=0;
    int j=0;
    RWCString name=file_name+".dat";
    fstream out_file(name.data(),ios::out);
    int nb_tree=getNbTree();
    for (i=0; i<nb_tree;i++)
    {
       for(j=0;j<nb_tree;j++)
      {
        DistanceType D=0;
// Before Fred Correction  :    if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<D<<TAB;
      }
      out_file<<endl;
    }

    for (i=0; i<nb_tree;i++)
    {
      for(int j=0;j<nb_tree;j++)
      {
        if (i!=j)
        {
          float R=0;
          int nb_inp_vertex=getTree(i)->getNbVertex();

          int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :      R=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
          R=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
          out_file<<R<<TAB;
        }
        else
        {
           out_file<<0<<TAB;
        }
      }
      out_file<<endl;
    }

    out_file.close();

  }
#ifndef RWOUT
  else if (!strcmp(format.data(),"Binary"))
  {
    RWCString name=file_name+".bin";
    RWFile out_file(name.data(),"w");
    if (out_file.Error()) assert(0);
    if (!out_file.Flush()) assert(0);
    saveGuts(out_file);
  }
#endif
  return(AMObj(AMObjType::VOID));
};


ostream& AML_TreeMatch::displayOneLine(ostream& out_info) const
{
  int nb_tree=getNbTree();
  int m_nb_vertex=0;
  int m_degree=0;
  for (int i=0;i<nb_tree;i++)
  {
    m_nb_vertex=m_nb_vertex+getTree(i)->getNbVertex();
    m_degree=m_degree+getTree(i)->getDegree();
  }
  //  out_info<<"NB TREE = "<<nb_tree<<" AVERAGE NB VERTEX = "<<SINLT(m_nb_vertex/nb_tree)<<" AVERAGE DEGREE = "<<SINLT(m_degree/nb_tree)<<endl;
  return out_info;
};




/////////////////////////////////////////////////////////////////////////////////////
AMObj AML_TreeMatch_U::save(const AMObjVector& args) const
{
  assert(&args);

  int len = args.length();
  int argth = 2;
  const char *mtg_err_msgs_aml[] =
  {
    "Cannot proceed: no MTG loaded",
    "function %s: undefined feature %s"
  };

  RWCString format("ASCII");

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TreeMatching", 1));

  CHECKCONDVA(args[1].tag() ==AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TreeMatching", 1, args[0].tag.string().data(), "STRING"));
  RWCString file_name =  *(AMString*)(args[1].val.p);

  while (argth < len)
  {
    // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd),"TreeMatching",(argth+1)/2+1));

    // must contain at least two parameters : this is verified syntactically

    assert(argth + 1 < len);

    if (*(AMString*)(args[argth].val.p) == "Format")
    {
      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));

      format = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA( format == "ASCII" || format == "Binary" || format == "SpreadSheet",
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "one of ASCII, Binary, SpreadSheet"));

    }
    argth += 2;

  }

  char TAB='\t';

  if (!strcmp(format.data(),"ASCII"))
  {

    RWCString name=file_name+".txt";
    fstream out_file(name.data(),ios::out);

    out_file<<TAB;;
    int i,j,k;
    int nb_matching=getNbTree()*(getNbTree()-1)/2;
    DistanceType max_distance=MINDIST;
    DistanceType min_distance=MAXDIST;
    DistanceType average_distance=0.0;

    float ins_rate=0.0;
    float sub_rate=0.0;
    float del_rate=0.0;
    float mat_rate=0.0;


    out_file<<" MATCHING OF "<<getNbTree()<<" TREES"<<endl;
    out_file<<endl<<" DISTANCE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    out_file<<TAB;
    for (i=0; i<getNbTree();i++)
    {

      out_file<<"|"<<TAB<<"T"<<i<<TAB;
    }
    out_file<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"  T"<<i<<TAB;
      for(j=0;j<getNbTree();j++)
      {
        DistanceType D=0;
// Before Fred Correction  : if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<"|"<<TAB<<D<<TAB;
      }
          out_file<<"|"<<endl;
    }
    for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;

    out_file<<endl<<" CONSERVATION RATE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    for (i=0; i<getNbTree();i++)
    {
      out_file<<TAB<<"|"<<"T"<<i;
    }
    out_file<<TAB<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"T"<<i<<"";
      for(int j=0;j<getNbTree();j++)
          {

            if (i!=j)
            {
              float T=0;
              int nb_inp_vertex = getTree(i)->getNbVertex();

              int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :          T=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
              T=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
              out_file<<TAB<<"|"<<T;
            }
            else
            {
              out_file<<TAB<<"|   *";
            };
          }
      out_file<<TAB<<"|"<<endl;
    }
    for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;



    for (i=0; i<getNbTree()-1;i++)
    {
      int tree_size1=getTree(i)->getNbVertex();

      for(int j=i+1;j<getNbTree();j++)
      {
        Sequence* mat_seq=getSequence(i,j);
        int seq_size=mat_seq->getSize();
        int sub_number=0;
        int mat_number=0;
        mat_seq->reset();
        do
        {
          if (mat_seq->getCurrent()->getCost()==0.0)
          {
            mat_number++;
          }
          else
          {
            sub_number++;
          };
        } while(mat_seq->next());
        int tree_size2=getTree(j)->getNbVertex();

        int nb_edit_op=tree_size1+tree_size2-seq_size;
        del_rate = del_rate + ((float) tree_size1-seq_size)/((float) nb_edit_op);
        ins_rate = ins_rate + ((float) tree_size2-seq_size)/((float) nb_edit_op);
        sub_rate = sub_rate + ((float) sub_number)/((float) nb_edit_op);
        mat_rate = mat_rate + ((float) mat_number)/((float) nb_edit_op);
        DistanceType distance=getDistance(i,j);
        max_distance=I_MAX(max_distance,distance);
        min_distance=I_MIN(min_distance,distance);
        average_distance=average_distance+distance;
      }
    }
    average_distance=average_distance/((float) nb_matching);
    del_rate = del_rate/((float) nb_matching);
    sub_rate = sub_rate/((float) nb_matching);
    ins_rate = ins_rate/((float) nb_matching);
    mat_rate = mat_rate/((float) nb_matching);
    out_file<<endl;
    out_file<<"MAXIMUM DISTANCE         : "<<max_distance<<endl;
    out_file<<"MINIMUM DISTANCE         : "<<min_distance<<endl;
    out_file<<"AVERAGE DISTANCE         : "<<average_distance<<endl;
    out_file<<endl;
    out_file<<"AVERAGE INSERTION RATE   : "<<ins_rate<<endl;
    out_file<<"AVERAGE DELETION  RATE   : "<<del_rate<<endl;
    out_file<<"AVERAGE MATCHING RATE    : "<<mat_rate<<endl;
    out_file<<"AVERAGE SUBSTITUTION RATE : "<<sub_rate<<endl;
    out_file<<endl;

    out_file.close();

  }
  else if (!strcmp(format.data(),"SpreadSheet"))
  {

    int i=0;
    int j=0;
    RWCString name=file_name+".dat";
    fstream out_file(name.data(),ios::out);
    int nb_tree=getNbTree();
    for (i=0; i<nb_tree;i++)
    {
       for(j=0;j<nb_tree;j++)
      {
        DistanceType D=0;
// Before Fred Correction  :    if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<D<<TAB;
      }
      out_file<<endl;
    }

    for (i=0; i<nb_tree;i++)
    {
      for(int j=0;j<nb_tree;j++)
      {
        if (i!=j)
        {
          float R=0;
          int nb_inp_vertex=getTree(i)->getNbVertex();

          int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :      R=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
          R=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
          out_file<<R<<TAB;
        }
        else
        {
           out_file<<0<<TAB;
        }
      }
      out_file<<endl;
    }

    out_file.close();

  }
#ifndef RWOUT
  else if (!strcmp(format.data(),"Binary"))
  {
    RWCString name=file_name+".bin";
    RWFile out_file(name.data(),"w");
    if (out_file.Error()) assert(0);
    if (!out_file.Flush()) assert(0);
    saveGuts(out_file);
  }
#endif
  return(AMObj(AMObjType::VOID));
};


ostream& AML_TreeMatch_U::displayOneLine(ostream& out_info) const
{
  int nb_tree=getNbTree();
  int m_nb_vertex=0;
  int m_degree=0;
  for (int i=0;i<nb_tree;i++)
  {
    m_nb_vertex=m_nb_vertex+getTree(i)->getNbVertex();
    m_degree=m_degree+getTree(i)->getDegree();
  }
  //  out_info<<"NB TREE = "<<nb_tree<<" AVERAGE NB VERTEX = "<<SINLT(m_nb_vertex/nb_tree)<<" AVERAGE DEGREE = "<<SINLT(m_degree/nb_tree)<<endl;
  return out_info;
};
/////////////////////////////////////////////////////////////////////////////////////
AMObj AML_TreeMatch_O::save(const AMObjVector& args) const
{
  assert(&args);

  int len = args.length();
  int argth = 2;
  const char *mtg_err_msgs_aml[] =
  {
    "Cannot proceed: no MTG loaded",
    "function %s: undefined feature %s"
  };

  RWCString format("ASCII");

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TreeMatching", 1));

  CHECKCONDVA(args[1].tag() ==AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TreeMatching", 1, args[0].tag.string().data(), "STRING"));
  RWCString file_name =  *(AMString*)(args[1].val.p);

  while (argth < len)
  {
    // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd),"TreeMatching",(argth+1)/2+1));

    // must contain at least two parameters : this is verified syntactically

    assert(argth + 1 < len);

    if (*(AMString*)(args[argth].val.p) == "Format")
    {
      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));

      format = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA( format == "ASCII" || format == "Binary" || format == "SpreadSheet",
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "one of ASCII, Binary, SpreadSheet"));

    }
    argth += 2;

  }

  char TAB='\t';

  if (!strcmp(format.data(),"ASCII"))
  {

    RWCString name=file_name+".txt";
    fstream out_file(name.data(),ios::out);

    out_file<<TAB;;
    int i,j,k;
    int nb_matching=getNbTree()*(getNbTree()-1)/2;
    DistanceType max_distance=MINDIST;
    DistanceType min_distance=MAXDIST;
    DistanceType average_distance=0.0;

    float ins_rate=0.0;
    float sub_rate=0.0;
    float del_rate=0.0;
    float mat_rate=0.0;


    out_file<<" MATCHING OF "<<getNbTree()<<" TREES"<<endl;
    out_file<<endl<<" DISTANCE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    out_file<<TAB;
    for (i=0; i<getNbTree();i++)
    {

      out_file<<"|"<<TAB<<"T"<<i<<TAB;
    }
    out_file<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"  T"<<i<<TAB;
      for(j=0;j<getNbTree();j++)
      {
        DistanceType D=0;
// Before Fred Correction  : if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<"|"<<TAB<<D<<TAB;
      }
          out_file<<"|"<<endl;
    }
    for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;

    out_file<<endl<<" CONSERVATION RATE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    for (i=0; i<getNbTree();i++)
    {
      out_file<<TAB<<"|"<<"T"<<i;
    }
    out_file<<TAB<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"T"<<i<<"";
      for(int j=0;j<getNbTree();j++)
          {

            if (i!=j)
            {
              float T=0;
              int nb_inp_vertex = getTree(i)->getNbVertex();

              int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :          T=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
              T=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
              out_file<<TAB<<"|"<<T;
            }
            else
            {
              out_file<<TAB<<"|   *";
            };
          }
      out_file<<TAB<<"|"<<endl;
    }
    for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;



    for (i=0; i<getNbTree()-1;i++)
    {
      int tree_size1=getTree(i)->getNbVertex();

      for(int j=i+1;j<getNbTree();j++)
      {
        Sequence* mat_seq=getSequence(i,j);
        int seq_size=mat_seq->getSize();
        int sub_number=0;
        int mat_number=0;
        mat_seq->reset();
        do
        {
          if (mat_seq->getCurrent()->getCost()==0.0)
          {
            mat_number++;
          }
          else
          {
            sub_number++;
          };
        } while(mat_seq->next());
        int tree_size2=getTree(j)->getNbVertex();

        int nb_edit_op=tree_size1+tree_size2-seq_size;
        del_rate = del_rate + ((float) tree_size1-seq_size)/((float) nb_edit_op);
        ins_rate = ins_rate + ((float) tree_size2-seq_size)/((float) nb_edit_op);
        sub_rate = sub_rate + ((float) sub_number)/((float) nb_edit_op);
        mat_rate = mat_rate + ((float) mat_number)/((float) nb_edit_op);
        DistanceType distance=getDistance(i,j);
        max_distance=I_MAX(max_distance,distance);
        min_distance=I_MIN(min_distance,distance);
        average_distance=average_distance+distance;
      }
    }
    average_distance=average_distance/((float) nb_matching);
    del_rate = del_rate/((float) nb_matching);
    sub_rate = sub_rate/((float) nb_matching);
    ins_rate = ins_rate/((float) nb_matching);
    mat_rate = mat_rate/((float) nb_matching);
    out_file<<endl;
    out_file<<"MAXIMUM DISTANCE         : "<<max_distance<<endl;
    out_file<<"MINIMUM DISTANCE         : "<<min_distance<<endl;
    out_file<<"AVERAGE DISTANCE         : "<<average_distance<<endl;
    out_file<<endl;
    out_file<<"AVERAGE INSERTION RATE   : "<<ins_rate<<endl;
    out_file<<"AVERAGE DELETION  RATE   : "<<del_rate<<endl;
    out_file<<"AVERAGE MATCHING RATE    : "<<mat_rate<<endl;
    out_file<<"AVERAGE SUBSTITUTION RATE : "<<sub_rate<<endl;
    out_file<<endl;

    out_file.close();

  }
  else if (!strcmp(format.data(),"SpreadSheet"))
  {

    int i=0;
    int j=0;
    RWCString name=file_name+".dat";
    fstream out_file(name.data(),ios::out);
    int nb_tree=getNbTree();
    for (i=0; i<nb_tree;i++)
    {
       for(j=0;j<nb_tree;j++)
      {
        DistanceType D=0;
// Before Fred Correction  :    if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<D<<TAB;
      }
      out_file<<endl;
    }

    for (i=0; i<nb_tree;i++)
    {
      for(int j=0;j<nb_tree;j++)
      {
        if (i!=j)
        {
          float R=0;
          int nb_inp_vertex=getTree(i)->getNbVertex();

          int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :      R=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
          R=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
          out_file<<R<<TAB;
        }
        else
        {
           out_file<<0<<TAB;
        }
      }
      out_file<<endl;
    }

    out_file.close();

  }
#ifndef RWOUT
  else if (!strcmp(format.data(),"Binary"))
  {
    RWCString name=file_name+".bin";
    RWFile out_file(name.data(),"w");
    if (out_file.Error()) assert(0);
    if (!out_file.Flush()) assert(0);
    saveGuts(out_file);
  }
#endif
  return(AMObj(AMObjType::VOID));
};


ostream& AML_TreeMatch_O::displayOneLine(ostream& out_info) const
{
  int nb_tree=getNbTree();
  int m_nb_vertex=0;
  int m_degree=0;
  for (int i=0;i<nb_tree;i++)
  {
    m_nb_vertex=m_nb_vertex+getTree(i)->getNbVertex();
    m_degree=m_degree+getTree(i)->getDegree();
  }
  //  out_info<<"NB TREE = "<<nb_tree<<" AVERAGE NB VERTEX = "<<SINLT(m_nb_vertex/nb_tree)<<" AVERAGE DEGREE = "<<SINLT(m_degree/nb_tree)<<endl;
  return out_info;
};
/////////////////////////////////////////////////////////////////////////////////////
AMObj AML_TreeMatch_PO::save(const AMObjVector& args) const
{
  assert(&args);

  int len = args.length();
  int argth = 2;
  const char *mtg_err_msgs_aml[] =
  {
    "Cannot proceed: no MTG loaded",
    "function %s: undefined feature %s"
  };

  RWCString format("ASCII");

  CHECKCONDVA(len > 0,
              genAMLError(ERRORMSG(K_NB_ARG_ERR_sd), "TreeMatching", 1));

  CHECKCONDVA(args[1].tag() ==AMObjType::STRING ,
              genAMLError(ERRORMSG(K_F_ARG_TYPE_ERR_sdss), "TreeMatching", 1, args[0].tag.string().data(), "STRING"));
  RWCString file_name =  *(AMString*)(args[1].val.p);

  while (argth < len)
  {
    // treatment of options

    CHECKCONDVA(args[argth].tag() == AMObjType::OPTION,
                genAMLError(ERRORMSG(K_OPTION_NAME_ERR_sd),"TreeMatching",(argth+1)/2+1));

    // must contain at least two parameters : this is verified syntactically

    assert(argth + 1 < len);

    if (*(AMString*)(args[argth].val.p) == "Format")
    {
      CHECKCONDVA(args[argth+1].tag() == AMObjType::STRING,
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "a STRING"));

      format = *(AMString*)(args[argth+1].val.p);
      CHECKCONDVA( format == "ASCII" || format == "Binary" || format == "SpreadSheet",
                  genAMLError(ERRORMSG(K_OPTION_VALUE_ERR_sds), "TreeMatching", (argth+1)/2+1, "one of ASCII, Binary, SpreadSheet"));

    }
    argth += 2;

  }

  char TAB='\t';

  if (!strcmp(format.data(),"ASCII"))
  {

    RWCString name=file_name+".txt";
    fstream out_file(name.data(),ios::out);

    out_file<<TAB;;
    int i,j,k;
    int nb_matching=getNbTree()*(getNbTree()-1)/2;
    DistanceType max_distance=MINDIST;
    DistanceType min_distance=MAXDIST;
    DistanceType average_distance=0.0;

    float ins_rate=0.0;
    float sub_rate=0.0;
    float del_rate=0.0;
    float mat_rate=0.0;


    out_file<<" MATCHING OF "<<getNbTree()<<" TREES"<<endl;
    out_file<<endl<<" DISTANCE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    out_file<<TAB;
    for (i=0; i<getNbTree();i++)
    {

      out_file<<"|"<<TAB<<"T"<<i<<TAB;
    }
    out_file<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"  T"<<i<<TAB;
      for(j=0;j<getNbTree();j++)
      {
        DistanceType D=0;
// Before Fred Correction  : if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<"|"<<TAB<<D<<TAB;
      }
          out_file<<"|"<<endl;
    }
    for (k=0;k<=2*getNbTree();k++) { out_file <<"--------"; };out_file<<endl;

    out_file<<endl<<" CONSERVATION RATE MATRIX "<<endl;
    out_file<<TAB;
    for (k=0;k<getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
    for (i=0; i<getNbTree();i++)
    {
      out_file<<TAB<<"|"<<"T"<<i;
    }
    out_file<<TAB<<"|"<<endl;

    for (i=0; i<getNbTree();i++)
    {
      for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;
      out_file<<"|"<<"T"<<i<<"";
      for(int j=0;j<getNbTree();j++)
          {

            if (i!=j)
            {
              float T=0;
              int nb_inp_vertex = getTree(i)->getNbVertex();

              int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :          T=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
              T=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
              out_file<<TAB<<"|"<<T;
            }
            else
            {
              out_file<<TAB<<"|   *";
            };
          }
      out_file<<TAB<<"|"<<endl;
    }
    for (k=0;k<=getNbTree();k++) { out_file <<"--------"; };out_file<<endl;



    for (i=0; i<getNbTree()-1;i++)
    {
      int tree_size1=getTree(i)->getNbVertex();

      for(int j=i+1;j<getNbTree();j++)
      {
        Sequence* mat_seq=getSequence(i,j);
        int seq_size=mat_seq->getSize();
        int sub_number=0;
        int mat_number=0;
        mat_seq->reset();
        do
        {
          if (mat_seq->getCurrent()->getCost()==0.0)
          {
            mat_number++;
          }
          else
          {
            sub_number++;
          };
        } while(mat_seq->next());
        int tree_size2=getTree(j)->getNbVertex();

        int nb_edit_op=tree_size1+tree_size2-seq_size;
        del_rate = del_rate + ((float) tree_size1-seq_size)/((float) nb_edit_op);
        ins_rate = ins_rate + ((float) tree_size2-seq_size)/((float) nb_edit_op);
        sub_rate = sub_rate + ((float) sub_number)/((float) nb_edit_op);
        mat_rate = mat_rate + ((float) mat_number)/((float) nb_edit_op);
        DistanceType distance=getDistance(i,j);
        max_distance=I_MAX(max_distance,distance);
        min_distance=I_MIN(min_distance,distance);
        average_distance=average_distance+distance;
      }
    }
    average_distance=average_distance/((float) nb_matching);
    del_rate = del_rate/((float) nb_matching);
    sub_rate = sub_rate/((float) nb_matching);
    ins_rate = ins_rate/((float) nb_matching);
    mat_rate = mat_rate/((float) nb_matching);
    out_file<<endl;
    out_file<<"MAXIMUM DISTANCE         : "<<max_distance<<endl;
    out_file<<"MINIMUM DISTANCE         : "<<min_distance<<endl;
    out_file<<"AVERAGE DISTANCE         : "<<average_distance<<endl;
    out_file<<endl;
    out_file<<"AVERAGE INSERTION RATE   : "<<ins_rate<<endl;
    out_file<<"AVERAGE DELETION  RATE   : "<<del_rate<<endl;
    out_file<<"AVERAGE MATCHING RATE    : "<<mat_rate<<endl;
    out_file<<"AVERAGE SUBSTITUTION RATE : "<<sub_rate<<endl;
    out_file<<endl;

    out_file.close();

  }
  else if (!strcmp(format.data(),"SpreadSheet"))
  {

    int i=0;
    int j=0;
    RWCString name=file_name+".dat";
    fstream out_file(name.data(),ios::out);
    int nb_tree=getNbTree();
    for (i=0; i<nb_tree;i++)
    {
       for(j=0;j<nb_tree;j++)
      {
        DistanceType D=0;
// Before Fred Correction  :    if (i!=j) D=0.01*((float) trunc(100.0*getDistance(i,j)));
        if (i!=j) D=0.01*((float)(100.0*getDistance(i,j)));
        out_file<<D<<TAB;
      }
      out_file<<endl;
    }

    for (i=0; i<nb_tree;i++)
    {
      for(int j=0;j<nb_tree;j++)
      {
        if (i!=j)
        {
          float R=0;
          int nb_inp_vertex=getTree(i)->getNbVertex();

          int s_size=getSequence(i,j)->getSize();
// Before Fred Correction  :      R=0.01*trunc(100.0*((float) s_size)/((float) nb_inp_vertex));
          R=0.01*(float)(100.0*((float) s_size)/((float) nb_inp_vertex));
          out_file<<R<<TAB;
        }
        else
        {
           out_file<<0<<TAB;
        }
      }
      out_file<<endl;
    }

    out_file.close();

  }
#ifndef RWOUT
  else if (!strcmp(format.data(),"Binary"))
  {
    RWCString name=file_name+".bin";
    RWFile out_file(name.data(),"w");
    if (out_file.Error()) assert(0);
    if (!out_file.Flush()) assert(0);
    saveGuts(out_file);
  }
#endif
  return(AMObj(AMObjType::VOID));
};


ostream& AML_TreeMatch_PO::displayOneLine(ostream& out_info) const
{
  int nb_tree=getNbTree();
  int m_nb_vertex=0;
  int m_degree=0;
  for (int i=0;i<nb_tree;i++)
  {
    m_nb_vertex=m_nb_vertex+getTree(i)->getNbVertex();
    m_degree=m_degree+getTree(i)->getDegree();
  }
  //  out_info<<"NB TREE = "<<nb_tree<<" AVERAGE NB VERTEX = "<<SINLT(m_nb_vertex/nb_tree)<<" AVERAGE DEGREE = "<<SINLT(m_degree/nb_tree)<<endl;
  return out_info;
};

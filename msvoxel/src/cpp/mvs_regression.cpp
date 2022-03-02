#include "mvs_regression.h"


PGL_USING_NAMESPACE
TOOLS_USING_NAMESPACE

MsvRegression::MsvRegression(int inb_vector, int **ivector)
{
    int i;
    // double **vector[nb_vector][nb_variable];
    nb_vector = inb_vector; 
    nb_variable = 2;
    vector = ivector;

    /*for( i = 0 ; i < nb_variable ; i++ )
    {
      cout<<"v"<<i<<": ";
      for( int j = 0 ; j < nb_vector ; j++ )
      {
         cout<<vector[i][j]<<"("<<getVector(j,i)<<"), ";
      }
      cout<<endl;
    }
    cout<<endl;
    */
    mean = new double[nb_variable];
    
    covariance = new double*[nb_variable];
    for( i = 0 ; i < nb_variable ; i++ )
      covariance[i] = new double[nb_variable];

    /*
    max_value = min_value = getVector(0,1);
    for( i = 1 ; i < nb_vector ; i++ ){
      if(getVector(i, 1) > max_value) max_value = getVector(i, 1);
      if(getVector(i, 1) < min_value) min_value = getVector(i, 1);
    }
    */

    point = new double[nb_vector];

    residual = new double[nb_vector];

    parameters_computation();
}

MsvRegression::~MsvRegression()
{
    int i;
    delete [] mean; delete [] point; delete [] residual;

    for( i = 0 ; i < nb_variable ; i++ )
      delete [] covariance[i];

    delete [] covariance;
}

/*--------------------------------------------------------------*
 *
 *  Calcul de la moyenne d'une variable.
 *
 *  argument : indice de la variable.
 *
 *--------------------------------------------------------------*/

void MsvRegression::mean_computation(int variable)
{
  register int i;

  mean[variable] = 0.;

  for (i = 0 ; i < nb_vector ; i++) {
    mean[variable] += getVector(i, variable);
  }

  mean[variable] /= nb_vector;
}

void MsvRegression::variance_computation(int variable)
{
    covariance[variable][variable] = 0.;

    if (nb_vector > 1) {
      register int i;
      double diff;


      for (i = 0;i < nb_vector;i++) {
        diff = getVector(i, variable) - mean[variable];
        covariance[variable][variable] += diff * diff;
      }

      covariance[variable][variable] /= (nb_vector - 1);
    }
}

/*--------------------------------------------------------------*
 *
 *  Calcul de la matrice de variance-covariance.
 *
 *  argument : indice de la variable.
 *
 *--------------------------------------------------------------*/

void MsvRegression::covariance_computation()

{
//  if (mean[0] != D_INF) {
    register int i , j , k;


    for (i = 0 ; i < nb_variable ; i++) 
    {
      for (j = i + 1 ;j < nb_variable ; j++) 
      {
        covariance[i][j] = 0.;

        for (k = 0 ; k < nb_vector ; k++) 
        {
          covariance[i][j] += (getVector(k, i) - mean[i]) * (getVector(k, j) - mean[j]);
        }
        covariance[i][j] /= (nb_vector - 1);
        covariance[j][i] = covariance[i][j];
      }
    }
 // }
}

/*--------------------------------------------------------------*
 *
 *  Calcul des valeurs d'une fonction parametrique.
 *
 *--------------------------------------------------------------*/

void MsvRegression::computation()

{
  register int i;

  for ( i = 0 ; i < nb_vector ; i++ ) {
    point[i] = b + a * getVector(i, 0);
  }
}

/*--------------------------------------------------------------*
 *
 *  Calcul des residus.
 *
 *--------------------------------------------------------------*/

void MsvRegression::residual_computation()

{
  register int i;
  
  for ( i = 0;i < nb_vector ; i++ ) {
    residual[i] = getVector(i, 1) - point[i];
  }
}


/*--------------------------------------------------------------*
 *
 *  Calcul de la moyenne des residus.
 *
 *--------------------------------------------------------------*/

double MsvRegression::residual_mean_computation() const

{
  register int i;
  double residual_mean = 0.;

  for (i = 0;i < nb_vector;i++) {
    residual_mean += residual[i];
  }
  residual_mean /= nb_vector;

  return residual_mean;
}

/*--------------------------------------------------------------*
 *
 *  Calcul de la somme des carres des residus.
 *
 *--------------------------------------------------------------*/

double MsvRegression::residual_square_sum_computation() const
{
  register int i;
  double residual_square_sum = 0. ;

  for (i = 0;i < nb_vector;i++) {
    residual_square_sum += residual[i] * residual[i];
  }

  return residual_square_sum;
}


/*  */

void MsvRegression::parameters_computation()
{
  int i = 0;

  for( i = 0 ; i < nb_variable ; i++)
  {
    mean_computation(i);
    variance_computation(i);
  }
  covariance_computation();

  a = covariance[0][1] / covariance[0][0];
  b = mean[1] - mean[0] * a;

  
  computation();
  residual_computation();

  double m = residual_mean_computation();
  double ssc = residual_square_sum_computation();
  
  r2 = 1. - ssc / ( covariance[1][1] * (nb_vector - 1) );
 
}

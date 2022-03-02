# This file has been extracted from AMAPmod documentation (refermanual 18)

"""
Plot, NewPlot
        Graphical output of an object of the STAT module using the GNUPLOT software.

    Usage
    -----
        Plot(obj1, Title="Distribution")
        w1 = NewPlot(obj1, Title="Distribution")
        Plot(Window=w1)
        w1 = NewPlot()
        
        Plot(vec1, Title="Values")
        Plot()
        Plot(vecn, variable, Title="Vectors")
        Plot(variable)
        
        Plot(obj2, type, Title="Sequences")
        Plot(type)
        Plot(obj3, type, variable, Title="Multivariate sequences")
        Plot(type, variable)
        
        Plot(dist1, dist2,..., Title="Family of distributions")
        Plot(histo1, histo2,...,
        Title="Family of frequency distributions")
        
        Plot(seq, ViewPoint="Data")
        
        Plot(dist, ViewPoint="Survival", Title="Survival rates")
        Plot(histo, ViewPoint="Survival", Title="Survival rates")
        
        Plot(hmc, identifier, ViewPoint="StateProfile",
        Title="Smoothed probabilities")
        Plot(hsmc, identifier, ViewPoint="StateProfile",
        Title="Smoothed probabilities")
        

    Parameters
    ----------
        obj1 (distribution, mixture, convolution, compound, histogram, mixture_data, convolution_data, compound_data, renewal, time_events, renewal_data, sequences, distance_matrix, top_parameters, tops),
        vec1 (vectors): values,
        vecn (vectors): vectors,
        variable (int): variable index,
        
        obj2 (markov, semi-markov, hidden_markov, hidden_semi-markov, discrete_sequences, markov_data, semi-markov_data): Markovian model for discrete univariate sequences or discrete univariate sequences,
        obj3: (markov, semi-markov, hidden_markov, hidden_semi-markov, discrete_sequences, markov_data, semi-markov_data): Markovian model for discrete multivariate sequences or discrete multivariate sequences,
        type (string): type of graphical outputs in the case of Markovian models or sequences: "SelfTransition", "Observation", "Intensity", "FirstOccurrence", "Recurrence", "Sojourn" or "Counting",
        
        dist1, dist2, ... (distribution, mixture, convolution, compound),
        histo1, histo2, ... (histogram, mixture_data, convolution_data, compound_data),
        
        seq (sequences, discrete_sequences, markov_data, semi-markov_data, tops),
        
        dist (distribution, mixture, convolution, compound),
        histo (histogram, mixture_data, convolution_data, compound_data),
        
        hmc (hidden_markov),
        hsmc (hidden_semi-markov),
        identifier (int): identifier of a sequence.
        

    Optional Parameters
    ------------------- 
        Window (window): window (the default: last used window). This optional argument cannot be used with the function NewPlot.
        ViewPoint (string): point of view on the object ("Data" or "Survival" or "StateProfile"). This optional argument can be set at "Data" only if the first mandatory argument is of type sequences, discrete_sequences, markov_data, semi-markov_data or tops, can be set at "Survival" only if the first mandatory argument is of type distribution, mixture, convolution, compound, histogram, mixture_data, convolution_data or compound_data and can be set at "StateProfile" only if the first mandatory argument is of type hidden_markov or hidden_semi-markov.
        Title (string): graphic title (the default: no title).
        

    Returns
    -------
        No object returned by the function Plot. An object of type window is returned by the function NewPlot.

    Description
    -----------
        In the case of Markovian models or sequences, the graphical outputs are grouped as follows:
         "SelfTransition": self-transition probability as a function of the index parameter (non-homogeneous Markov chain),
         "Observation": observation distributions attached to each state of the underlying (semi-)Markov chain (lumped processes or hidden Markovian processes),
         "Intensity": (empirical) probabilities of states/outputs as a function of the index parameter,
         "FirstOccurrence": (frequency) distributions of the time-up to the first occurrence of a state/output (or first-passage time in a state/output distributions),
         "Recurrence" (frequency) distributions of the recurrence time in a state/output,
         "Sojourn": (frequency) distributions of the sojourn time in a state/output (or state/output occupancy distributions). For the frequency distributions extracted from sequences, the sojourn times in the last visited states which are considered as censored are isolated.
         "Counting": counting (frequency) distributions (either distributions of the number of runs (or clumps) of a state/output per sequence or distributions of the number of occurrences of a state/output per sequence).
        

    Background
    ----------
        Graphical output of a (frequency) distribution and the associate hazard or survival rates (ViewPoint="Survival"): It is assumed that the (frequency) distribution represents lifetime and the hazard or survival rates are deduced from this lifetime distribution.
        Graphical output of the state profile given by the smoothed probabilities  as a function of the index parameter t computed from the parameters of a hidden Markovian model for the sequence  (ViewPoint="StateProfile").
        

    See Also
    --------
        Display, 
        Save.
"""

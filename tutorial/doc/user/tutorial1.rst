.. _tuto_stat_analysis:

Statistical Analysis and Simulation 
###################################

The objective is to generate using LPy repeated patterns or motifs represented by
variable-order Markov chains. In a variable-order Markov chain, the order (or memory length) is
variable and depends on the "context" within the sequence instead of being fixed.

Two applications are treated:

    * Branching of Tassili cypress second-order axes (Guédon *et al.*, 2001): 
      The data set is composed of 276 second-order axes measured at selected positions on the trunk of 35 3-year-old Tassili
      cypresses (Cupressus dupreziana A. Camus, Cupressaceae) with an opposite decussate phyllotaxis.
      The measured variable for each node is the number of offspring shoots and
      can take only three possible values: 0, 1 and 2.

    * Permutation patterns in spiral phyllotaxis of Arabidopsis thaliana (Guédon *et al.*, 2012):
      The data set is composed of 82 wild-type plants of cumulative length (in number of
      divergence angles or internodes) 2405 and 89 ahp6-1 mutant plants of cumulative
      length 2815. The seven states are the multiples of the canonical divergence angle :math:`$\alpha$`,
      :math:`$2\alpha$`, :math:`$-\alpha$`, :math:`$3\alpha$`, :math:`$-2\alpha$`, :math:`$4\alpha$` and :math:`$5\alpha$` corresponding to
      the possible divergence angles according to the formal language induced by 2- and 3-permutations.

For each example, a variable-order Markov chain was previously estimated. Branching sequences
(respectively divergence angle sequences) are generated using the estimated model and
the sequences are geometrically interpreted. The sequences are also written as ASCII files
and variable-order Markov chains are estimated on the basis of the simulated sequences.

Guédon, Y., Barthelemy, D., Caraglio, Y. & Costes, E. (2001). Pattern analysis in
branching and axillary flowering sequences. \textit{Journal of Theoretical Biology} 212(4), 481-520.
Guédon, Y., Refahi, Y., Besnard, F., Farcot, E., Godin, C. & Vernoux, T. (2012).
Identifying and characterizing permutation patterns reveal control mechanisms of
spiral phyllotaxis. Submitted to \textit{Journal of Theoretical Biology}.


L-py production rule
--------------------

L-py principle
**************

An L-system (for Lindenmayer system) is a variant of a formal grammar, famously used to model the growth processes of plant development. An L-system consists of an alphabet of symbols that can be used to make strings, a collection of production rules which expand each symbol into some larger string of symbols, an initial "axiom" string from which to begin construction, and a mechanism for translating the generated strings into geometric structures. 

L-py is an adaptation of L-systems to the Python language, a popular and powerful open-license dynamic language. 
.. The use of dynamic language properties makes it possible to enhance the development of plant growth models: (i) by keeping a simple syntax while allowing for high-level programming constructs, (ii) by making code execution easy and avoiding compilation overhead, (iii) by allowing a high-level of model reusability and the building of complex modular models, and (iv) by providing powerful solutions to integrate MTG data-structures (that are a common way to represent plants at several scales) into L-systems and thus enabling to use a wide spectrum of computer tools based on MTGs developed for plant architecture. We then illustrate the use of L-Py in real applications to build complex models or to teach plant modeling in the classroom.

`L-py web page <http://openalea.gforge.inria.fr/wiki/doku.php?id=packages:vplants:lpy:doc:lsystem>`_


Modeling of the axillary branching process using L-py
*****************************************************

The axillary branching process during shoot growth is generally represented by the iterative creation of a phytomer (and its associated branches) by the shoot apex.

At any given time, we model a shoot as a list of geometric triplet:
    * **Internode (I)**: 
        A segment between two nodes along the shoot represented geometrically by a vertical cylinder. 
        Typically its length (or radius) can be fixed or can change at each iteration. 
    * **Rotation (R)**:  
        The rotation around the shoot between two nodes. 
        The angle can be controled in order to model phyllotaxis as in an example below.  
    * **Lateral organ (L)** 
        In our model, it represents the number of organs (either leaves or branches) at a node. 
        In the cypress branching example, it can take the value 0, 1 or 2. 


The L-system process is defined by the recursive rule:
    * start with a single apex:
        :math:`$\text{axiom}: A$` 
    * at each iteration, the apex add a *phythomer* unit **IRL**:
        :math:`$A \rightarrow IRL \; A$`
                                                                                    
    Process:                                                                        
        | :math:`$\text{axiom}: A$`                                                 
        | :math:`$\text{step} \; 1: IRL \; A$`                                      
        | :math:`$\text{step} \; 2: IRL \; IRL \; A$`                               
        | :math:`$\hspace{2cm} \vdots$`                                                                    
        | :math:`$\text{step} \; n: IRL \; \ldots \; IRL \; A$`                        
                                                                                    

The stochastic process is simulated by controling the variable parameters of each element along the growth sequence. 

For the case of the branching of Tassili cypress, We have:
    | :math:`$A[s_t] \rightarrow IRL(s_{t+1}) \; A[s_{t+1}]$`
    | where :math:`$s_t$` is the number of branches at time t. 

    
In the file :download:`cypress_order1.lpy <../../src/tutorial/cypress_order1.lpy>` (see section First-order Markov chain), the iterative L-system simulation is implemented in by:

    >>> # Simulation #
    >>> ##############
    >>> s0 = draw(pi) # draw of initial state s0 from distribution pi
    >>> 
    >>> Axiom: A(s0)
    >>> 
    >>> derivation length: nbsteps  # number of simulation iteration
    >>> production:
    >>> 
    >>> # A -> I R L A
    >>> A(s) :
    >>>   new_s = transition(s)     # draw next state using the transition function above
    >>>   produce I R(90) L(new_s,length) A(new_s)


For the case of the permutation patterns in spiral phyllotaxis of Arabidopsis thaliana, we have:
    | :math:`$A[s_t] \rightarrow IR(s_{t+1})L \; A[s_{t+1}]$`
    | where :math:`$s_t$` is the random angle between two successive leaf :math:`$t$` and leaf :math:`$t+1$`. 
        
        .. | :math:`$\text{axiom}: A$`
        .. | :math:`$\text{step} \; 1: IR(s_1)L \; A$`
        .. | :math:`$\text{step} \; 2: IR(s_1)L \; IR(\theta_2)L \; A$`
        .. | :math:`$\hspace{2cm} \vdots$`
        .. | :math:`$\text{step} \; n: IR(s_1)L \; \ldots \; IR(s_n)L \; A$`
        
        
These successive random variables are simulated using different Markov models.

First-order Markov chain
------------------------

For the simulation of a first-order Markov chain :math:`$(S_t)_{t \in N}$`, the initial state is drawn according to the initial distribution: 
    | :math:`$\pi = \lbrace P(S_0 = j) \rbrace_{j = 1, \ldots, J}$`

Then the next states are successively drawn according to the transition distribution (row of the transition probability matrix) of the current state. 
    | :math:`$P = \lbrace P(S_{t+1} = j | S_t = i) \rbrace_{i,j = 1, \ldots, J}$`
    
    .. `

A Markov chain of order 1 is thus characterized by the vector :math:`$\pi$` and the transition matrix :math:`$P$`.
 
The file :download:`cypress_order1.lpy <../../src/tutorial/cypress_order1.lpy>` contains an example applied to the modeling of the branching of Tassili cypress.

In this example, the possible state (:math:`$s_t$`) are 0, 1 or 2 branches. A previous statistical analysis provided the **estimated** initial distribution :math:`$\hat{\pi}$` and transition probability :math:`$\hat{P}$`. 
    >>> pi = [0.99, 0.01, 0]    # initial probabilities
    >>> P=[[0.35, 0.56, 0.09],  # transition probability matrix
    >>>    [0.85, 0.14, 0.01],
    >>>    [0.97, 0.03, 0]]

    
At each step, the states are randomly simulated using the transition function:
    >>> # return the next state for a given state 's'
    >>> def transition(s):  
    >>>   proba = P[s]            # select the transition distribution for state 's'
    >>>   return draw(proba)
    >>>   
    >>> # draw of the next state
    >>> def draw(proba):  
    >>>   unif = random.uniform(0,1)
    >>>   if unif < proba[0]:
    >>>     return 0
    >>>   elif unif < proba[0]+proba[1]:
    >>>     return 1
    >>>   else:
    >>>     return 2

In the following lpy output image, a single branch is drawn in green and pairs in red.

.. image:: images/cypress_branching.png

Variable-order Markov chain
---------------------------

For the simulation using L-Py, the estimated variable-order Markov chain are re-parameterized 
as two  :math:`$M \times J$` matrices where $M$ is the number of memories and :math:`$J$` is the number of states:
    - a matrix of transition between memories **MT**.
    - a transition probability matrix **P**.

The file :download:`cypress_variable_order.lpy <../../src/tutorial/cypress_variable_order.lpy>` contains an example applied to the modeling of the branching of Tassili cypress. In this example , we use an **estimated** transition probability :math:`$\hat{P}$` obtained by a previous statistical analysis which are stored in file  :download:`dupreziana13.py <../../src/tutorial/dupreziana13.py>`. 
    >>> # import model parameters stored in file dupreziana13.py
    >>> import dupreziana13 as model
    >>> MT = model.memory_transition       # memory transition matrix (including the order 0 memory)
    >>> P  = model.transition_probability  # transition probability matrix (including the initial probabilities)
    
This reparameterization exploits the property that a variable-order Markov chain can be viewed
as a first-order Markov chain defined on an extended state space corresponding to the possible
memories. The possible memories which include the root vertex of the memory tree and the non-leaf vertices
are numbered. The root vertex is used to model the initial distribution which is given in the first row
of the transition probability matrix. The initial probabilities are defined for first-order memories
(i.e. states). The transition distributions - rows of the transition probability matrix - attached to
the non-leaf vertices are used to model the transient regime of the model (by opposition to
the permanent regime which is modeled by the transition distributions attached to the leaf vertices).
The transient memories can only be visited once at the beginning of the sequence while permanent memories
can be visited more than once in a sequence.

The files :download:`arabidopsis_phyllotaxis_order1.lpy <../../src/tutorial/arabidopsis_phyllotaxis_order1.lpy>` or
`arabidopsis_phyllotaxis_variable_order..lpy <../../src/tutorial/arabidopsis_phyllotaxis_variable_order.lpy>` contain another example
dealing with the modeling of the permutation patterns in spiral phyllotaxis of Arabidopsis thaliana.
In the case of variable-order Markov chains, we use an estimated transition probability matrix: math:`$\hat{P}$` obtained in a previous statistical analysis
and stored in files: download: `arabidopsis_phyllotaxis_4.py <../../src/tutorial/arabidopsis_phyllotaxis_4.py>`,
`arabidopsis_phyllotaxis_5.py <../../src/tutorial/arabidopsis_phyllotaxis_5.py>` or `arabidopsis_phyllotaxis_7.py <../../src/tutorial/arabidopsis_phyllotaxis_7.py>`. 

In this example, the possible state (:math:`$s_t$`) are :math:`$\{\alpha, 2\alpha, -\alpha, 3\alpha\}$`
where :math:`$\alpha$` is the *golden angle* of 137.5 degrees (the standard phylotaxic divergence angle between 2 sucessive lateral organs).
The first four states are respectively drawn in green, red, blue and pink.

.. image:: images/lpy_arabido_permutation.png


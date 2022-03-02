
#define NBPLANTS 1
#define PLANTSTEP 10
#define APEXDIAMETER 1
#define STEPS 10
#define REP 1

/* Transition Probabilities */
#define P1 1.0

#define IANGLE 60  /* default insertion angle for branches */
/* Transition Probabilities */
#define T1 1
#define T2 1
#define T3 0
#define T4 0
#define T5 0
#define T6 0
#define T7 0

#define IANGLE 60  /* default insertion angle for branches */

#define trans1_1(t,s,x,o) (s==1 && t<=T1 && o == 0)
#define trans1_2(t,s,x,o) (s==1 && t>T1)
#define trans2_2(t,s,x,o) (s==2 && t<=T2)
#define trans2_3(t,s,x,o) (s==2 && t>T2)
#define trans3_3(t,s,x,o) (s==3 && t<=T3)
#define trans3_4(t,s,x,o) (s==3 && t>T3)
#define trans4_4(t,s,x,o) (s==4 && t<=T4)
#define trans4_5(t,s,x,o) (s==4 && t>T4)
#define trans5_5(t,s,x,o) (s==5 && t<=T5)
#define trans5_6(t,s,x,o) (s==5 && t>T5)
#define trans6_6(t,s,x,o) (s==6 && t<=T6)
#define trans6_7(t,s,x,o) (s==6 && t>T6)
#define trans7_7(t,s,x,o) (s==7 && t<=T7)
#define trans7_8(t,s,x,o) (s==7 && t>T7)

Lsystem: 1
Seed: 0

derivation length: 30

Start: {flag=0; /* flag for making sure the string contains NBPLANTS */}

Axiom: [-(90)#(1);(255)F((NBPLANTS+1)*PLANTSTEP)]-(90)P(0,0)

P(n,x) :  n < NBPLANTS --> T[G(n,x)]P(n+1,x)
P(n,x) :  n >= NBPLANTS {flag=1;} --> *

G(n,x) : flag==1 --> +(90)S(x-STEPS*n)


/* Initialisation of plant distribution */
S(x) : x<0  --> S(x+1)
S(x) : x>=0 {printf("Step 1\n");}--> A(0,1,1,0)

/* t = time in state s, 
   s = physiological state of the apex A 
   x = not used 
   o = order */


A(t,s,x,o) : trans1_1(t,s,x,o)  --> M(t,s) [R(t,s,x)A(0,s+1,0,o+1)] A(t+1,s,x+1,o) 
A(t,s,x,o) : trans1_2(t,s,x,o)  --> A(0,s+1,x,o)


A(t,s,x,o) : trans2_2(t,s,x,o) --> M(t,s) [R(t,s,x)A(0,s+1,0,o+1)] A(t+1,s,x+1,o)
A(t,s,x,o) : trans2_3(t,s,x,o) --> A(0,s+1,x,o) 


A(t,s,x,o) : trans3_3(t,s,x,o) --> M(t,s) [R(t,s,x)A(0,s+1,0,o+1)] A(t+1,s,x+1,o)
A(t,s,x,o) : trans3_4(t,s,x,o) --> A(0,s+1,x,o) 

A(t,s,x,o) : trans4_4(t,s,x,o) --> M(t,s) [R(t,s,x)A(0,s+1,0,o+1)] A(t+1,s,x+1,o)
A(t,s,x,o) : trans4_5(t,s,x,o) --> A(0,s+1,x,o)


A(t,s,x,o) : trans5_5(t,s,x,o) --> M(t,s) [R(t,s,x)A(0,s+1,0,o+1)] A(t+1,s,x+1,o) 
A(t,s,x,o) : trans5_6(t,s,x,o) --> A(0,s+1,x,o) 

A(t,s,x,o) : trans6_6(t,s,x,o) --> M(t,s) [R(t,s,x)A(0,s+1,0,o+1)] A(t+1,s,x+1,o)
A(t,s,x,o) : trans6_7(t,s,x,o) --> A(0,s+1,x,o)


decomposition
/* what is a module at state s made of ? */

M(t,s) : s == 1 --> K(t,s,5.5,1)
M(t,s) : s == 2 --> K(t,s,4,1)
M(t,s) : s == 3 --> K(t,s,2.5,1)
M(t,s) : s == 4 --> K(t,s,2,1)
M(t,s) : s == 5 --> K(t,s,1.5,1)
M(t,s) : s != 5 --> K(t,s,1,1)


/* Phyllotaxy */

R(t,s,x) : (x%2 == 0 && s!=6) --> +(IANGLE-(IANGLE/6)*s)

R(t,s,x) : (x%2 == 1 && s!=6) --> -(IANGLE-(IANGLE/6)*s)

R(t,s,x) : (x%2 == 0) --> +(90)
R(t,s,x) : (x%2 == 1) --> -(90)



homomorphism


/* management of space between plants */
T : flag==0 --> f(PLANTSTEP);(15)@c(4)
T : flag==1 --> f(PLANTSTEP)

/* Display the internodes */

K(t,s,l,d) --> ;(s)#(d*4)F(l*(7-s))
K(t,s,l,d) : t > 0  --> ;(255)#(d*4)F(d/2);(s)#(d*4)F(l*(7-s))
/* Display the apex */

A(t,s,x,o) : s < 7 --> ;(s)@Gc(APEXDIAMETER)
/*A(t,s,x) : s ==6 --> ;(15)F(1)*/
/*A(t,s,x,o) : s == 6 --> ;(15)#(4)Gc(APEXDIAMETER)*/

endlsystem

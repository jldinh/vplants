#ifndef LSYSTEMTOMTG_PARSER_HPP
# define LSYSTEMTOMTG_PARSER_HPP

#ifndef YYSTYPE
typedef union {
  int                   integer;
  double                real;
  char                  character;
  std::list<double>* doublelist;
} yystype;
# define YYSTYPE yystype
# define YYSTYPE_IS_TRIVIAL 1
#endif
# define	TokInt	257
# define	TokReal	258
# define	TokChar	259
# define	TokQuery	260
# define	TokError	261


#endif /* not BISON_BUILD_SCONS_SRC_CPP_LSYSTEMTOMTG_PARSER_HPP */

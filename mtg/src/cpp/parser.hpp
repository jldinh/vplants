#ifndef BISON_PARSER_HPP
# define BISON_PARSER_HPP

#ifndef YYSTYPE
typedef union{
  int intval;
  char charval;
  CString stgval;
  void* symblistpt;  // should be of type SymbList*, but this is a parametrized type.
  const EType* etypeval;
  FType ftypeval;
  VName vname;
  Label label;
} yystype;
# define YYSTYPE yystype
# define YYSTYPE_IS_TRIVIAL 1
#endif
# define	TokCODE	257
# define	TokFORM_A	258
# define	TokFORM_B	259
# define	TokCLASSES	260
# define	TokSYMBOL	261
# define	TokSCALE	262
# define	TokVDECOMP	263
# define	TokINDEXATION	264
# define	TokVDEF	265
# define	TokDESCRIPTION	266
# define	TokLEFT	267
# define	TokRIGHT	268
# define	TokRELTYPE	269
# define	TokMAX	270
# define	TokFEATURES	271
# define	TokFNAME	272
# define	TokFTYPE	273
# define	TokMTG	274
# define	TokENTITYCODE	275
# define	TokReltype	276
# define	TokFType	277
# define	TokString	278
# define	TokFilename	279
# define	TokSymbol	280
# define	TokInteger	281
# define	tabc	282
# define	eol	283
# define	TokError	284


extern YYSTYPE yylval;

#endif /* not BISON_PARSER_HPP */

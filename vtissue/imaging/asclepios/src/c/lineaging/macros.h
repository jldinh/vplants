#ifndef __MACROS_H__
#define __MACROS_H__

#ifdef VERBOSE
  #include <iostream>
  #define ERROR_MSG(msg) std::cout << msg << std::endl
  #define DEBUG_MSG(msg) std::cout << msg << std::endl
#else
  #define ERROR_MSG(msg)
  #define DEBUG_MSG(msg)
#endif


#endif//__MACROS_H__

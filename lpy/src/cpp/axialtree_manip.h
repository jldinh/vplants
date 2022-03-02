/* ---------------------------------------------------------------------------
 #
 #       L-Py: L-systems in Python
 #
 #       Copyright 2003-2008 UMR Cirad/Inria/Inra Dap - Virtual Plant Team
 #
 #       File author(s): F. Boudon (frederic.boudon@cirad.fr)
 #
 # ---------------------------------------------------------------------------
 #
 #                      GNU General Public Licence
 #
 #       This program is free software; you can redistribute it and/or
 #       modify it under the terms of the GNU General Public License as
 #       published by the Free Software Foundation; either version 2 of
 #       the License, or (at your option) any later version.
 #
 #       This program is distributed in the hope that it will be useful,
 #       but WITHOUT ANY WARRANTY; without even the implied warranty of
 #       MERCHANTABILITY or FITNESS For A PARTICULAR PURPOSE. See the
 #       GNU General Public License for more details.
 #
 #       You should have received a copy of the GNU General Public
 #       License along with this program; see the file COPYING. If not,
 #       write to the Free Software Foundation, Inc., 59
 #       Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 #
 # ---------------------------------------------------------------------------
 */

#ifndef __axialtree_manip_h__
#define __axialtree_manip_h__

#include "lpy_config.h"
#include "module.h"
#include <list>

LPY_BEGIN_NAMESPACE

/*---------------------------------------------------------------------------*/

template<class Iterator>
Iterator endBracket(Iterator pos, Iterator string_end, bool startingBeforePos = false)
{ 
  if(pos == string_end)return pos;
  if(!startingBeforePos && pos->isLeftBracket())++pos;
  int bracket= 0;
  while(pos != string_end && (bracket>0 || !pos->isRightBracket())){
	if(pos->isLeftBracket()) bracket++;
	else if(pos->isRightBracket()) bracket--;
	++pos;
  }
  return pos; 
}

template<class Iterator>
Iterator beginBracket(Iterator pos, Iterator string_begin, Iterator string_end, bool startingAfterPos = false)
{ 
  if(pos != string_end && pos->isLeftBracket())return pos;
  if(pos == string_begin) return string_end;
  if(pos == string_end)--pos;
  else if(!startingAfterPos && pos->isRightBracket())--pos;
  int bracket= 0;
  while(pos != string_begin && (bracket>0 || !pos->isLeftBracket())){
	if(pos->isRightBracket()) bracket++;
	else if(pos->isLeftBracket()) bracket--;
	--pos;
  }
  if(pos == string_begin) {
	if(bracket == 0 && pos->isLeftBracket())return pos;
	else return string_end;
  }
  return pos; 
}


template<class Iterator>
Iterator parent(Iterator pos, Iterator string_begin, Iterator string_end)
{
  if( pos == string_begin ) return string_end;
  --pos;
  while((pos != string_end) && (pos != string_begin) && (pos->isBracket() || pos->isIgnored())){
	while( (pos != string_begin) && (pos->isLeftBracket() || pos->isIgnored()))--pos;
	while((pos != string_end) && (pos != string_begin) && pos->isRightBracket()){
	  pos = beginBracket(pos,string_begin,string_end);
	  if( pos != string_end ) --pos;
	}
  }
  if( pos == string_end ) return pos;
  else if( (pos == string_begin) && (pos->isLeftBracket() || pos->isIgnored())) return string_end;
  else return pos;
}

template<class Iterator>
bool wellBracketed(Iterator string_begin, Iterator string_end) 
{ 
  int bracket= 0;
  Iterator pos = string_begin;
  while((pos != string_end) && bracket>= 0){
	if(pos->isLeftBracket()) ++bracket;
	else if(pos->isRightBracket()) --bracket;
	++pos;
  }
  return (bracket == 0); 
}

template<class Iterator>
std::vector<Iterator>  children(Iterator pos, Iterator string_end)
{ 
  std::vector<Iterator> result; 
  // current pos is the end of a branch
  if( (pos == string_end) || pos->isRightBracket()) return result;
  ++pos;
  // if module after pos is the end of the branch
  if( (pos == string_end) || pos->isRightBracket()) return result;
  // looking for first modules of all branches
  while((pos != string_end) && (pos->isLeftBracket() || pos->isIgnored())){ 
	while((pos != string_end) && !pos->isBracket() && pos->isIgnored()) ++pos; // skip ignored
	while((pos != string_end) && pos->isLeftBracket()){ // find lateral branches
	  std::vector<Iterator> res = children(pos,string_end); // get children
	  if(!res.empty()) result.insert(result.end(),res.begin(),res.end());
	  pos = endBracket(pos,string_end); // go to the end of this sub branches
	  if( pos == string_end ) return result;
	  ++pos;
	}
  }
  // add direct children if any
  if( (pos != string_end) && !pos->isRightBracket()){
	result.push_back(pos);
  }
  return result;
}

template<class Iterator>
std::vector<Iterator> lateral_children(Iterator pos, Iterator string_end) {
  std::vector<Iterator> result; 
  // current pos is the end of a branch
  if( (pos == string_end) || pos->isRightBracket()) return result;
  ++pos;
  // if module after pos is the end of the branch
  if( (pos == string_end) || pos->isRightBracket()) return result;
  // looking for first modules of all branches
  while((pos != string_end) && (pos->isLeftBracket() || pos->isIgnored())){
	while((pos != string_end) && !pos->isBracket() && pos->isIgnored()) ++pos;  // skip ignored
	while((pos != string_end) && pos->isLeftBracket()){ // find lateral branches
	  std::vector<Iterator> res = children(pos,string_end);
	  if(!res.empty()) result.insert(result.end(),res.begin(),res.end());
	  pos = endBracket(pos,string_end);
	  if( pos == string_end ) return result;
	  ++pos;
	}
  }
  // do not add direct son
  return result;
}

template<class Iterator>
Iterator direct_child(Iterator pos, Iterator string_end) 
{
  if( (pos == string_end) || pos->isRightBracket()) return string_end;
  ++pos;
  return direct_child_from_previous_pos(pos,string_end);
}

template<class Iterator>
Iterator direct_child_from_previous_pos(Iterator pos, Iterator string_end) 
{
  // remove ignored modules and lateral branches
  while((pos != string_end) && (pos->isLeftBracket() || pos->isIgnored())){
	while((pos != string_end) && !pos->isLeftBracket() && pos->isIgnored())++pos;
	while((pos != string_end) && pos->isLeftBracket()){
	  pos = endBracket(pos,string_end);
	  if( pos == string_end ) return string_end;
	  ++pos;
	}
  }
  // return direct child if any
  if( (pos == string_end) || pos->isRightBracket()) return string_end;
  else return pos;
}



template<class Iterator>
std::vector<Iterator> roots(Iterator string_begin, Iterator string_end) 
{ 
  std::vector<Iterator> res;
  if (string_begin == string_end) return res;
  Iterator i = string_begin;
  if(i->isRightBracket())return res;
  else if(i->isLeftBracket()){
	while((i != string_end) && (i->isBracket() || i->isIgnored())){
	  while((i != string_end) && i->isLeftBracket()){
		std::vector<Iterator> res2 = children(i,string_end);
		if(!res2.empty())
		  res.insert(res.end(),res2.begin(),res2.end());
		i = endBracket(i,string_end);
		if( i == string_end ) return res;
		++i;
	  }
	  while((i != string_end) && !i->isBracket() && i->isIgnored())++i;
	}
	if( (i != string_end) && !i->isRightBracket()){
	  res.push_back(i);
	}
	// std::vector<const_iterator> res2 = children(i);
	// if(!res2.empty())res.insert(res.end(),res2.begin(),res2.end());
  }
  else if(i->isIgnored()){
	std::vector<Iterator> res2 = children(i,string_end);
	if(!res2.empty())res.insert(res.end(),res2.begin(),res2.end());
  }
  else res.push_back(i);
  return res;
}

template<class Iterator>
Iterator complex(Iterator pos, int scale, Iterator string_begin, Iterator string_end)
{
  if( pos == string_begin ) return string_end;
  if( !is_lower_scale(pos->scale(),scale)) return string_end;
  pos = parent(pos,string_begin, string_end);
  while(pos != string_end && is_lower_scale(pos->scale(),scale)){
	  pos = parent(pos,string_begin, string_end);
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}


template<class Iterator>
std::vector<Iterator>  components(Iterator pos, Iterator string_end)
{ 
  std::vector<Iterator> result; 
  // current pos is the end of a branch
  if( (pos == string_end) || pos->isRightBracket()) return result;
  int currentscale = pos->scale();
  std::list<Iterator> toconsider;
  std::vector<Iterator> cchildren = children(pos,string_end);
  toconsider.insert(toconsider.end(),cchildren.begin(),cchildren.end());
  while(!toconsider.empty()){
    Iterator child = toconsider.front();
    toconsider.pop_front();
    int cscale = child->scale();
    if (is_upper_scale(cscale,currentscale)){
        result.push_back(child);
        cchildren = children(child,string_end);
        toconsider.insert(toconsider.end(),cchildren.begin(),cchildren.end());
    } 
  }
  return result;
}

template<class Iterator>
std::vector<Iterator>  components_at_scale(Iterator pos, int scale, Iterator string_end)
{ 
  std::vector<Iterator> result; 
  // current pos is the end of a branch
  if( (pos == string_end) || pos->isRightBracket()) return result;
  int currentscale = pos->scale();
  std::list<Iterator> toconsider;
  std::vector<Iterator> cchildren = children(pos,string_end);
  toconsider.insert(toconsider.end(),cchildren.begin(),cchildren.end());
  while(!toconsider.empty()){
    Iterator child = toconsider.front();
    toconsider.pop_front();
    int cscale = child->scale();
    if (is_upper_scale(cscale,currentscale)){
        if (is_eq_scale(cscale,scale)) result.push_back(child);
        cchildren = children(child,string_end);
        toconsider.insert(toconsider.end(),cchildren.begin(),cchildren.end());
    } 
  }
  return result;
}

/*
template<class Iterator>
Iterator predecessor_at_scale(Iterator pos, int scale, Iterator string_begin, Iterator string_end)
{
  if( pos == string_begin ) return string_end;
  int previousscale = pos->scale();
  pos = parent(pos,string_begin, string_end); 
  if( pos == string_end ) return string_end;
  int curscale = pos->scale();
  if (!is_upper_scale(scale,previousscale)) { // mean that we look for a predecessor, not a complex
    // Go up into complex.
    while(pos != string_end && is_upper_scale(curscale,previousscale)){
      pos = parent(pos,string_begin, string_end);
      previousscale = curscale;
      curscale = pos->scale();
    }
  }
  // Skip predecessor components to go to the complex at good scale
  while(pos != string_end && is_lower_scale(pos->scale(),scale)){
      pos = parent(pos,string_begin, string_end);
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}
*/


template<class Iterator>
Iterator predecessor_at_scale(Iterator pos, int targetscale, Iterator string_begin, Iterator string_end)
{
  if( pos == string_begin ) return string_end;
  // warning : we assume here that the pos give us the current scale. In case of new left context, in theory, this information comes from somewhere else.
  int previousscale = pos->scale();

  pos = parent(pos,string_begin, string_end); 
  if( pos == string_end ) return string_end;

  int curscale = pos->scale();
  if (!is_lower_scale(targetscale,previousscale)) { // mean that we look for a predecessor, not a complex
    // Go up into complex.
    while(pos != string_end && is_lower_scale(curscale,previousscale)){
      pos = parent(pos,string_begin, string_end);
      // previousscale = curscale;
      if (pos == string_end) return string_end;
      curscale = pos->scale();
    }
  }
  // Skip predecessor components to go to the complex at good scale
  while(pos != string_end && is_upper_scale(curscale,targetscale)){
      pos = parent(pos,string_begin, string_end);
      if (pos == string_end) return string_end;
      curscale = pos->scale();
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),targetscale))  return pos;
  else return string_end;
}

/*
template<class Iterator>
Iterator successor_at_scale(Iterator pos, int scale, 
                            Iterator string_end,
                            bool fromPreviousPosition = false, 
                            int previous_scale = -1)
{
  if( pos == string_end ) return string_end;  
  if(fromPreviousPosition) pos = direct_child_from_previous_pos(pos, string_end);
  else {
    previous_scale = pos->scale();
    pos = direct_child(pos, string_end);
  }
  if (!is_lower_scale(scale,previous_scale)) { // mean that we look for a successor, not a components
    // Skip successor components
    while(pos != string_end && is_lower_scale(pos->scale(),scale)){
      pos = direct_child(pos,string_end);
    }
    if (pos == string_end) return string_end;
  }
  // If exists, we are on the child or at least one of its complex.
  int curscale = pos->scale();
  if (is_upper_scale(curscale,scale)) { // We look for a component of current module
    // Go down into components.
    do {
      pos = direct_child(pos,string_end);
      if (pos == string_end) return string_end;   
      previous_scale = curscale;
      curscale = pos->scale();
    } while(pos != string_end && is_lower_scale(curscale,previous_scale) && is_upper_scale(curscale,scale));
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}
*/


template<class Iterator>
Iterator successor_at_scale(Iterator pos, int scale, 
                            Iterator string_end,
                            bool fromPreviousPosition = false, 
                            int previous_scale = -1)
{
  if( pos == string_end ) return string_end;  
  if(fromPreviousPosition) pos = direct_child_from_previous_pos(pos, string_end);
  else {
    previous_scale = pos->scale();
    pos = direct_child(pos, string_end);
  }
  if (!is_upper_scale(scale,previous_scale)) { // mean that we look for a successor, not a components
    // Skip successor components
    while(pos != string_end && is_upper_scale(pos->scale(),scale)){
      pos = direct_child(pos,string_end);
    }
    if (pos == string_end) return string_end;
  }
  // If exists, we are on the child or at least one of its complex.
  int curscale = pos->scale();
  if (is_lower_scale(curscale,scale)) { // We look for a component of current module
    // Go down into components.
    do {
      pos = direct_child(pos,string_end);
      if (pos == string_end) return string_end;   
      previous_scale = curscale;
      curscale = pos->scale();
    } while(pos != string_end && is_upper_scale(curscale,previous_scale) && is_lower_scale(curscale,scale));
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}


template<class Iterator>
Iterator predecessor_at_level(Iterator pos, int scale, Iterator string_begin, Iterator string_end)
{
  if( pos == string_begin ) return string_end;
  pos = parent(pos,string_begin, string_end);
  // Skip predecessors at other levels
  while(pos != string_end && is_neq_scale(pos->scale(),scale)){
	  pos = parent(pos,string_begin, string_end);
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}

template<class Iterator>
Iterator successor_at_level(Iterator pos, int scale, Iterator string_end, bool fromPreviousPosition = false)
{
  if( pos == string_end ) return string_end;
  if(fromPreviousPosition) pos = direct_child_from_previous_pos(pos, string_end);
  else pos = direct_child(pos, string_end);
  // Skip successors at other levels
  while(pos != string_end && is_neq_scale(pos->scale(),scale)){
	  pos = direct_child(pos, string_end);
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}

template<class Iterator>
Iterator next_module(Iterator pos, Iterator string_end, bool fromPreviousPosition = false) 
{
	if(!fromPreviousPosition) ++pos;
	while(pos != string_end && pos->isIgnored()){ ++pos; }
	return pos;
}

template<class Iterator>
Iterator previous_module(Iterator pos, Iterator string_begin, Iterator string_end, bool fromPreviousPosition = false) 
{
	if(!fromPreviousPosition){
		if(pos == string_begin) return string_end;
		--pos;
	}
	while(pos != string_begin && pos->isIgnored()){ --pos; }
	return pos;
}



template<class Iterator>
Iterator next_module_at_scale(Iterator pos, int scale, 
							Iterator string_end,
							bool fromPreviousPosition = false, 
							int previous_scale = -1)
{
  if( pos == string_end ) return string_end;  
  if(fromPreviousPosition) pos = next_module(pos, string_end,true);
  else {
	previous_scale = pos->scale();
	pos = next_module(pos, string_end);
  }
  if (!is_upper_scale(scale,previous_scale)) { // mean that we look for a successor, not a components
	// Skip successor components
	while(pos != string_end && is_upper_scale(pos->scale(),scale)){
	  pos = next_module(pos,string_end);
	}
	if (pos == string_end) return string_end;
  }
  // If exists, we are on the successor or at least one of its complex.
  int curscale = pos->scale();
  if (is_lower_scale(curscale,scale)) { // We look for a component of current module
    // Go down into components.
	do {
	  pos = next_module(pos,string_end);
	  if (pos == string_end) return string_end;	  
	  previous_scale = curscale;
	  curscale = pos->scale();
	} while(pos != string_end && is_upper_scale(curscale,previous_scale) && is_lower_scale(curscale,scale));
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}

template<class Iterator>
Iterator next_module_at_level(Iterator pos, int scale, Iterator string_end, bool fromPreviousPosition = false)
{
  if( pos == string_end ) return string_end;
  if(fromPreviousPosition) pos = next_module(pos, string_end, true);
  else pos = next_module(pos, string_end);
  // Skip successors at other levels
  while(pos != string_end && is_neq_scale(pos->scale(),scale)){
	  pos = next_module(pos, string_end);
  }
  if (pos == string_end) return string_end;
  if (is_eq_scale(pos->scale(),scale))  return pos;
  else return string_end;
}

/*---------------------------------------------------------------------------*/

LPY_END_NAMESPACE

#endif

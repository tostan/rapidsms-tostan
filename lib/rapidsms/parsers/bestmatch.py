#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from __future__ import with_statement
import re
import threading
import sys

class MultiMatch(object):
    """ 
    Simple wrapper around multiple BestMatchers that
    let's you search through multiple target sets at once.

    E.g., take 'men_best_matcher=BestMatch(target=['bob','jim'])
    and women_best_matcher=BestMatch(target=['jen','sarah'])

    And you want to search in both at once, do:
    MultiMatch(men_best_matcher,women_best_matcher).match(aPerson)

    """
    def __init__(self, *args):
        self.matchers = [m for m in args if isinstance(m, BestMatch)]

     
    def match(self, src, **kwargs):
        """Returns uniqued list of matches for all match sets"""
        matches = set()
        for m in self.matchers:
            matches.update(m.match(src, **kwargs))
        return list(matches)

        
class BestMatch(object):
    def __init__(self, targets=None, ignore_prefixes=None):
        self.__targets = dict()
        self.__data = dict()
        self.__aliases = dict()
        self.__ignore_prefixes = list()
        self.__lock = threading.Lock()
        self.__set_targets(targets)
        self.__set_ignore_prefixes(ignore_prefixes)
        self.__ignore_prefix_pattern = ''
    
    def match(self, src, anchored=True, with_data=False, exact_match_trumps=True):
        """
        Returns a sequence of matched targets.
        The sequence may of 0,1, or more matches
        
        anchored -- means anchor source string at beginning of line.
                    E.g. matching 'foo' against 'baz bar foo' with not match
                    anchored, but will unanchored.

        with_data -- when True, return a list of tuples of 
                     (matched target, stored target data)

        exact_match_trumps -- when true and exact match will
                              return just that match.
                              e.g. with targets 'bob' and 'bobby'
                              with exact match on, matching 'bob'
                              with return ('bob'). With it off
                              the return will be ('bob','bobby')

        """
        
        # short circuit do-nothing case
        if src is None or len(self.__aliases)==0:
            return []

        src = src.strip()
        if len(src)==0:
            return []
            
        anchor = ('^' if anchored else '.*')

        # see if the source already has a prefix on it
        # in which case we strip it and don't try to match other
        # prefixes
        has_prefix=False
        for p in self.__ignore_prefixes:
            left,pref,right = src.partition(p)
            if len(left)==0 and \
                    len(pref)!=0:
                # we matched a prefix
                has_prefix=True
                break

        # now make the matching regex
        prefixes = (self.__ignore_prefix_pattern \
                      if not has_prefix \
                      else '')

        src_matcher = re.compile(ur'%s\s*%s\s*%s.*' % \
                                   ( 
                anchor,
                prefixes,
                re.escape(src),
                
                ),re.IGNORECASE)

        # now look for matches
        found = set()
        for a in self.__aliases:
            if exact_match_trumps and src==a:
                found = set([a])
                break
            if src_matcher.match(a) is not None:    
                found.add(self.__aliases[a])

        if len(found)>0 and not with_data:
            return list(found)
        else:
            return [(t,self.__data[t]) for t in found]


    #
    # A slew of convenient setters/getters
    #
    def get_aliases_for_target(self, target):
        return self.__targets[target]

    def add_alias_for_target(self, target, alias):
        self.__targets[target].add(alias)
        self.__aliases[alias] = target

    def remove_alias_for_target(self, target, alias):
        self.__targets[target].remove(alias)
        del self.__aliases[alias]

    def __get_targets(self):
        """
        reconstruct a return list equivalent to the full target setting
        list:

        [([targ, alias*], data)+]

        """
        return [([i[0]]+list(i[1]),self.__data[i[0]]) for i in self.__targets.items()]

    def __set_targets(self,val):
        # erase existing
        with self.__lock:
            self.__targets = dict()
            self.__data = dict()
            self.__aliases = dict()

        if val is None or len(val)==0:
            return
    
        for v in val:
            self.add_target(v)
    targets = property(__get_targets,__set_targets)

    def __get_ignore_prefixes(self):
        """Return ignore prefixes as a set"""
        with self.__lock:
            pres=self.__ignore_prefixes
        return pres

    def __set_ignore_prefixes(self, val):
        """Takes a sequence of prefix strings"""
        # erase existing
        with self.__lock:
            self.__ignore_prefixes = list()
          
        if val is None or len(val)==0: 
            return

        for v in val[:-1]:
            self.add_ignore_prefix(v,prep=False)
        # add the last one with sort turned on
        self.add_ignore_prefix(val[-1],prep=True)
    ignore_prefixes = property(__get_ignore_prefixes,__set_ignore_prefixes)
            
    def add_target(self, val):
        """ 
        'val' is the target to add and it may be ANY of the following:
        
        target_string
        (target_string, data) -- in which case the data will be returned with
                                 the match

        [target, alias, alias, alias] -- in which case the first element in
                                         the list is the target and others
                                         are aliases

        ([target, alias...], data) -- combo of above, target, aliases and data

        """
        if val is None:
            return

        # check for something that we interpet as (target,data)
        target,data = (val if isinstance(val, tuple) else (val, None))

        # see if it is an iterable, in which case the first is 
        # the target and the rest are aliases
        aliases=[]
        if getattr(target, '__iter__', False):
            aliases = list(target)
            target = aliases[0]
        else:
            aliases = [target]
                  

        # check for empty
        target = ('' if target is None else target.strip())
        if len(target)==0: 
            return

        with self.__lock:
            self.__data[target] = data
            for a in aliases:
                self.__aliases[a] = target
            al_set=set(aliases)
            al_set.remove(target)
            self.__targets[target] = al_set

    def add_ignore_prefix(self,val,prep=True):
        val=('' if val is None else val.strip())
        if len(val)==0:
            return

        with self.__lock:
            self.__ignore_prefixes.append(val)
            if prep:
                self.__prep_prefixes()

    def remove_ignore_prefix(self, val, prep=True):
        """Returns 'True' if removed, 'False' if not in the set"""
        with self.__lock:
            try:
                self.__ignore_prefixes.remove(val)
            except KeyError:
                return False
            if prep:
                self.__prep_prefixes()
        return True

    def __prep_prefixes(self):
        # sort longest to shortest
        self.__ignore_prefixes.sort(lambda x,y: len(y)-len(x))
        # and make the regex pattern
        ppats=[ur'(?:%s)' % re.escape(p) \
                   for p in self.__ignore_prefixes]
        self.__ignore_prefix_pattern = '(%s)' % u'|'.join(ppats)

    def remove_target(self, val):
        """Returns 'True' if removed, 'False' if not in the set"""
        targ = val.strip()
        with self.__lock:
            try:
                del self.__data[targ]
                for k in self.__aliases.keys():
                    if self.__aliases[k] == targ:
                        del self.__aliases[targ]
            except KeyError:
                return False
        return True


# cruddy manual test script

if __name__ == "__main__":
    src='mr'

    if len(sys.argv)>1:
        targ = sys.argv[1]

    src = sys.argv[1]

    targets = ['jeff','john','jimmy','mary',
             'mr. smith','mr. smuthers',
             'mrs. smith',('mr. smith-edwards*','foo'),
             'mr. jones']
#    targets=['mr. smith', 'mr. jones']
    bm = BestMatch(targets,['mr.','mrs.'])
    print "found: %s" %  bm.match(src,with_data=True)
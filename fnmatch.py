# File: f (Python 2.4)

import re
__all__ = [
    'filter',
    'fnmatch',
    'fnmatchcase',
    'translate']
_cache = { }

def fnmatch(name, pat):
    import os as os
    name = os.path.normcase(name)
    pat = os.path.normcase(pat)
    return fnmatchcase(name, pat)


def filter(names, pat):
    import os
    import posixpath as posixpath
    result = []
    pat = os.path.normcase(pat)
    if pat not in _cache:
        res = translate(pat)
        _cache[pat] = re.compile(res)
    
    match = _cache[pat].match
    if os.path is posixpath:
        for name in names:
            if match(name):
                result.append(name)
                continue
        
    else:
        for name in names:
            if match(os.path.normcase(name)):
                result.append(name)
                continue
        
    return result


def fnmatchcase(name, pat):
    if pat not in _cache:
        res = translate(pat)
        _cache[pat] = re.compile(res)
    
    return _cache[pat].match(name) is not None


def translate(pat):
    i = 0
    n = len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            res = res + '.*'
            continue
        if c == '?':
            res = res + '.'
            continue
        if c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j + 1
            
            if j < n and pat[j] == ']':
                j = j + 1
            
            while j < n and pat[j] != ']':
                j = j + 1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                
                res = '%s[%s]' % (res, stuff)
        j >= n
        res = res + re.escape(c)
    return res + '$'


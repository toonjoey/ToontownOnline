# File: p (Python 2.4)

import os
import time
import marshal
import re
__all__ = [
    'Stats']

class Stats:
    
    def __init__(self, *args):
        if not len(args):
            arg = None
        else:
            arg = args[0]
            args = args[1:]
        self.init(arg)
        self.add(*args)

    
    def init(self, arg):
        self.all_callees = None
        self.files = []
        self.fcn_list = None
        self.total_tt = 0
        self.total_calls = 0
        self.prim_calls = 0
        self.max_name_len = 0
        self.top_level = { }
        self.stats = { }
        self.sort_arg_dict = { }
        self.load_stats(arg)
        trouble = 1
        
        try:
            self.get_top_level_stats()
            trouble = 0
        finally:
            if trouble:
                print 'Invalid timing data'if self.files:
                    print self.files[-1],
                
                print 
            


    
    def load_stats(self, arg):
        if not arg:
            self.stats = { }
        elif type(arg) == type(''):
            f = open(arg, 'rb')
            self.stats = marshal.load(f)
            f.close()
            
            try:
                file_stats = os.stat(arg)
                arg = time.ctime(file_stats.st_mtime) + '    ' + arg
            except:
                pass

            self.files = [
                arg]
        elif hasattr(arg, 'create_stats'):
            arg.create_stats()
            self.stats = arg.stats
            arg.stats = { }
        
        if not self.stats:
            raise TypeError, "Cannot create or construct a %r object from '%r''" % (self.__class__, arg)
        

    
    def get_top_level_stats(self):
        for (cc, nc, tt, ct, callers) in self.stats.items():
            self.total_calls += nc
            self.prim_calls += cc
            self.total_tt += tt
            if callers.has_key(('jprofile', 0, 'profiler')):
                self.top_level[func] = None
            
            if len(func_std_string(func)) > self.max_name_len:
                self.max_name_len = len(func_std_string(func))
                continue
        

    
    def add(self, *arg_list):
        if not arg_list:
            return self
        
        if len(arg_list) > 1:
            self.add(*arg_list[1:])
        
        other = arg_list[0]
        if type(self) != type(other) or self.__class__ != other.__class__:
            other = Stats(other)
        
        self.files += other.files
        self.total_calls += other.total_calls
        self.prim_calls += other.prim_calls
        self.total_tt += other.total_tt
        for func in other.top_level:
            self.top_level[func] = None
        
        if self.max_name_len < other.max_name_len:
            self.max_name_len = other.max_name_len
        
        self.fcn_list = None
        for (func, stat) in other.stats.iteritems():
            if func in self.stats:
                old_func_stat = self.stats[func]
            else:
                old_func_stat = (0, 0, 0, 0, { })
            self.stats[func] = add_func_stats(old_func_stat, stat)
        
        return self

    
    def dump_stats(self, filename):
        f = file(filename, 'wb')
        
        try:
            marshal.dump(self.stats, f)
        finally:
            f.close()


    sort_arg_dict_default = {
        'calls': (((1, -1),), 'call count'),
        'cumulative': (((3, -1),), 'cumulative time'),
        'file': (((4, 1),), 'file name'),
        'line': (((5, 1),), 'line number'),
        'module': (((4, 1),), 'file name'),
        'name': (((6, 1),), 'function name'),
        'nfl': (((6, 1), (4, 1), (5, 1)), 'name/file/line'),
        'pcalls': (((0, -1),), 'call count'),
        'stdname': (((7, 1),), 'standard name'),
        'time': (((2, -1),), 'internal time') }
    
    def get_sort_arg_defs(self):
        if not self.sort_arg_dict:
            self.sort_arg_dict = { }
            dict = { }
            bad_list = { }
            for (word, tup) in self.sort_arg_dict_default.iteritems():
                fragment = word
                while fragment:
                    if not fragment:
                        break
                    
                    if fragment in dict:
                        bad_list[fragment] = 0
                        break
                    
                    dict[fragment] = tup
                    fragment = fragment[:-1]
            
            for word in bad_list:
                del dict[word]
            
        
        return self.sort_arg_dict

    
    def sort_stats(self, *field):
        if not field:
            self.fcn_list = 0
            return self
        
        if len(field) == 1 and type(field[0]) == type(1):
            field = [
                {
                    -1: 'stdname',
                    0: 'calls',
                    1: 'time',
                    2: 'cumulative' }[field[0]]]
        
        sort_arg_defs = self.get_sort_arg_defs()
        sort_tuple = ()
        self.sort_type = ''
        connector = ''
        for word in field:
            sort_tuple = sort_tuple + sort_arg_defs[word][0]
            self.sort_type += connector + sort_arg_defs[word][1]
            connector = ', '
        
        stats_list = []
        for (cc, nc, tt, ct, callers) in self.stats.iteritems():
            stats_list.append((cc, nc, tt, ct) + func + (func_std_string(func), func))
        
        stats_list.sort(TupleComp(sort_tuple).compare)
        self.fcn_list = []
        fcn_list = []
        for tuple in stats_list:
            fcn_list.append(tuple[-1])
        
        return self

    
    def reverse_order(self):
        if self.fcn_list:
            self.fcn_list.reverse()
        
        return self

    
    def strip_dirs(self):
        oldstats = self.stats
        self.stats = { }
        newstats = { }
        max_name_len = 0
        for (cc, nc, tt, ct, callers) in oldstats.iteritems():
            newfunc = func_strip_path(func)
            if len(func_std_string(newfunc)) > max_name_len:
                max_name_len = len(func_std_string(newfunc))
            
            newcallers = { }
            for (func2, caller) in callers.iteritems():
                newcallers[func_strip_path(func2)] = caller
            
            if newfunc in newstats:
                newstats[newfunc] = add_func_stats(newstats[newfunc], (cc, nc, tt, ct, newcallers))
                continue
            newstats[newfunc] = (cc, nc, tt, ct, newcallers)
        
        old_top = self.top_level
        self.top_level = { }
        new_top = { }
        for func in old_top:
            new_top[func_strip_path(func)] = None
        
        self.max_name_len = max_name_len
        self.fcn_list = None
        self.all_callees = None
        return self

    
    def calc_callees(self):
        if self.all_callees:
            return None
        
        self.all_callees = { }
        all_callees = { }
        for (cc, nc, tt, ct, callers) in self.stats.iteritems():
            if func not in all_callees:
                all_callees[func] = { }
            
            for (func2, caller) in callers.iteritems():
                if func2 not in all_callees:
                    all_callees[func2] = { }
                
                all_callees[func2][func] = caller
            
        

    
    def eval_print_amount(self, sel, list, msg):
        new_list = list
        if type(sel) == type(''):
            new_list = []
            for func in list:
                if re.search(sel, func_std_string(func)):
                    new_list.append(func)
                    continue
            
        else:
            count = len(list)
            if type(sel) == type(1.0):
                if 0.0 <= sel:
                    pass
                sel < 1.0
                if 1:
                    count = int(count * sel + 0.5)
                    new_list = list[:count]
                elif type(sel) == type(1):
                    if 0 <= sel:
                        pass
                    sel < count
                    if 1:
                        count = sel
                        new_list = list[:count]
                    
        if len(list) != len(new_list):
            msg = msg + '   List reduced from %r to %r due to restriction <%r>\n' % (len(list), len(new_list), sel)
        
        return (new_list, msg)

    
    def get_print_list(self, sel_list):
        width = self.max_name_len
        if self.fcn_list:
            list = self.fcn_list[:]
            msg = '   Ordered by: ' + self.sort_type + '\n'
        else:
            list = self.stats.keys()
            msg = '   Random listing order was used\n'
        for selection in sel_list:
            (list, msg) = self.eval_print_amount(selection, list, msg)
        
        count = len(list)
        if not list:
            return (0, list)
        
        print msg
        if count < len(self.stats):
            width = 0
            for func in list:
                if len(func_std_string(func)) > width:
                    width = len(func_std_string(func))
                    continue
            
        
        return (width + 2, list)

    
    def print_stats(self, *amount):
        for filename in self.files:
            print filename
        
        if self.files:
            print 
        
        indent = ' ' * 8
        for func in self.top_level:
            print indent, func_get_function_name(func)
        
        print indent, self.total_calls, 'function calls'if self.total_calls != self.prim_calls:
            print '(%d primitive calls)' % self.prim_calls,
        
        print 'in %.3f CPU seconds' % self.total_tt
        print 
        (width, list) = self.get_print_list(amount)
        if list:
            self.print_title()
            for func in list:
                self.print_line(func)
            
            print 
            print 
        
        return self

    
    def print_callees(self, *amount):
        (width, list) = self.get_print_list(amount)
        if list:
            self.calc_callees()
            self.print_call_heading(width, 'called...')
            for func in list:
                if func in self.all_callees:
                    self.print_call_line(width, func, self.all_callees[func])
                    continue
                self.print_call_line(width, func, { })
            
            print 
            print 
        
        return self

    
    def print_callers(self, *amount):
        (width, list) = self.get_print_list(amount)
        if list:
            self.print_call_heading(width, 'was called by...')
            for func in list:
                (cc, nc, tt, ct, callers) = self.stats[func]
                self.print_call_line(width, func, callers)
            
            print 
            print 
        
        return self

    
    def print_call_heading(self, name_size, column_title):
        print 'Function '.ljust(name_size) + column_title

    
    def print_call_line(self, name_size, source, call_dict):
        print func_std_string(source).ljust(name_size)if not call_dict:
            print '--'
            return None
        
        clist = call_dict.keys()
        clist.sort()
        name_size = name_size + 1
        indent = ''
        for func in clist:
            name = func_std_string(func)
            print indent * name_size + name + '(%r)' % (call_dict[func],), f8(self.stats[func][3])
            indent = ' '
        

    
    def print_title(self):
        print '   ncalls  tottime  percall  cumtime  percall', 'filename:lineno(function)'

    
    def print_line(self, func):
        (cc, nc, tt, ct, callers) = self.stats[func]
        c = str(nc)
        if nc != cc:
            c = c + '/' + str(cc)
        
        print c.rjust(9), f8(tt)if nc == 0:
            print ' ' * 8,
        else:
            print f8(tt / nc),
        print f8(ct)if cc == 0:
            print ' ' * 8,
        else:
            print f8(ct / cc),
        print func_std_string(func)

    
    def ignore(self):
        pass



class TupleComp:
    
    def __init__(self, comp_select_list):
        self.comp_select_list = comp_select_list

    
    def compare(self, left, right):
        for (index, direction) in self.comp_select_list:
            l = left[index]
            r = right[index]
            if l < r:
                return -direction
            
            if l > r:
                return direction
                continue
        
        return 0



def func_strip_path(func_name):
    (filename, line, name) = func_name
    return (os.path.basename(filename), line, name)


def func_get_function_name(func):
    return func[2]


def func_std_string(func_name):
    return '%s:%d(%s)' % func_name


def add_func_stats(target, source):
    (cc, nc, tt, ct, callers) = source
    (t_cc, t_nc, t_tt, t_ct, t_callers) = target
    return (cc + t_cc, nc + t_nc, tt + t_tt, ct + t_ct, add_callers(t_callers, callers))


def add_callers(target, source):
    new_callers = { }
    for (func, caller) in target.iteritems():
        new_callers[func] = caller
    
    for (func, caller) in source.iteritems():
        if func in new_callers:
            new_callers[func] = caller + new_callers[func]
            continue
        new_callers[func] = caller
    
    return new_callers


def count_calls(callers):
    nc = 0
    for calls in callers.itervalues():
        nc += calls
    
    return nc


def f8(x):
    return '%8.3f' % x

if __name__ == '__main__':
    import cmd
    
    try:
        import readline
    except ImportError:
        pass

    
    class ProfileBrowser(cmd.Cmd):
        
        def __init__(self, profile = None):
            cmd.Cmd.__init__(self)
            self.prompt = '% '
            if profile is not None:
                self.stats = Stats(profile)
            else:
                self.stats = None

        
        def generic(self, fn, line):
            args = line.split()
            processed = []
            for term in args:
                
                try:
                    processed.append(int(term))
                except ValueError:
                    pass

                
                try:
                    frac = float(term)
                    if frac > 1 or frac < 0:
                        print 'Fraction argument mus be in [0, 1]'
                        continue
                    
                    processed.append(frac)
                except ValueError:
                    pass

                processed.append(term)
            
            if self.stats:
                getattr(self.stats, fn)(*processed)
            else:
                print 'No statistics object is loaded.'
            return 0

        
        def generic_help(self):
            print 'Arguments may be:'
            print '* An integer maximum number of entries to print.'
            print '* A decimal fractional number between 0 and 1, controlling'
            print '  what fraction of selected entries to print.'
            print '* A regular expression; only entries with function names'
            print '  that match it are printed.'

        
        def do_add(self, line):
            self.stats.add(line)
            return 0

        
        def help_add(self):
            print 'Add profile info from given file to current statistics object.'

        
        def do_callees(self, line):
            return self.generic('print_callees', line)

        
        def help_callees(self):
            print 'Print callees statistics from the current stat object.'
            self.generic_help()

        
        def do_callers(self, line):
            return self.generic('print_callers', line)

        
        def help_callers(self):
            print 'Print callers statistics from the current stat object.'
            self.generic_help()

        
        def do_EOF(self, line):
            print ''
            return 1

        
        def help_EOF(self):
            print 'Leave the profile brower.'

        
        def do_quit(self, line):
            return 1

        
        def help_quit(self):
            print 'Leave the profile brower.'

        
        def do_read(self, line):
            if line:
                
                try:
                    self.stats = Stats(line)
                except IOError:
                    args = None
                    print args[1]
                    return None

                self.prompt = line + '% '
            elif len(self.prompt) > 2:
                line = self.prompt[-2:]
            else:
                print 'No statistics object is current -- cannot reload.'
            return 0

        
        def help_read(self):
            print 'Read in profile data from a specified file.'

        
        def do_reverse(self, line):
            self.stats.reverse_order()
            return 0

        
        def help_reverse(self):
            print 'Reverse the sort order of the profiling report.'

        
        def do_sort(self, line):
            abbrevs = self.stats.get_sort_arg_defs()
            if line and not filter(lambda x, a = abbrevs: x not in a, line.split()):
                self.stats.sort_stats(*line.split())
            else:
                print 'Valid sort keys (unique prefixes are accepted):'
                for (key, value) in Stats.sort_arg_dict_default.iteritems():
                    print '%s -- %s' % (key, value[1])
                
            return 0

        
        def help_sort(self):
            print 'Sort profile data according to specified keys.'
            print "(Typing `sort' without arguments lists valid keys.)"

        
        def complete_sort(self, text, *args):
            continue
            return _[1]

        
        def do_stats(self, line):
            return self.generic('print_stats', line)

        
        def help_stats(self):
            print 'Print statistics from the current stat object.'
            self.generic_help()

        
        def do_strip(self, line):
            self.stats.strip_dirs()
            return 0

        
        def help_strip(self):
            print 'Strip leading path information from filenames in the report.'

        
        def postcmd(self, stop, line):
            if stop:
                return stop
            


    import sys
    print 'Welcome to the profile statistics browser.'
    if len(sys.argv) > 1:
        initprofile = sys.argv[1]
    else:
        initprofile = None
    
    try:
        ProfileBrowser(initprofile).cmdloop()
        print 'Goodbye.'
    except KeyboardInterrupt:
        pass



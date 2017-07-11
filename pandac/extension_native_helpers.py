# File: p (Python 2.4)

__all__ = [
    'Dtool_ObjectToDict',
    'Dtool_funcToMethod',
    'Dtool_PreloadDLL']
import imp
import sys
import os
dll_suffix = ''
if sys.platform == 'win32':
    dll_ext = '.dll'
    dll_suffix = getattr(sys, 'dll_suffix', None)
    if dll_suffix is None:
        dll_suffix = ''
        if sys.executable.endswith('_d.exe'):
            dll_suffix = '_d'
        
    
elif sys.platform == 'darwin':
    
    try:
        from direct.extensions_native.extensions_darwin import dll_ext
    except ImportError:
        dll_ext = '.dylib'
    

dll_ext = '.so'
if sys.platform == 'win32':
    target = None
    filename = 'libpandaexpress%s%s' % (dll_suffix, dll_ext)
    for dir in sys.path + [
        sys.prefix]:
        lib = os.path.join(dir, filename)
        if os.path.exists(lib):
            target = dir
            continue
    
    if target == None:
        message = 'Cannot find %s' % filename
        raise ImportError, message
    
    path = os.environ['PATH']
    if not path.startswith(target + ';'):
        os.environ['PATH'] = target + ';' + path
    


def Dtool_PreloadDLL(module):
    if module in sys.modules:
        return None
    
    target = None
    filename = module + dll_suffix + dll_ext
    for dir in sys.path + [
        sys.prefix]:
        lib = os.path.join(dir, filename)
        if os.path.exists(lib):
            target = dir
            break
            continue
    
    if target == None:
        message = 'DLL loader cannot find %s.' % module
        raise ImportError, message
    
    pathname = os.path.join(target, filename)
    imp.load_dynamic(module, pathname)

Dtool_PreloadDLL('libpandaexpress')
from libpandaexpress import *

def Dtool_ObjectToDict(clas, name, obj):
    clas.DtoolClassDict[name] = obj


def Dtool_funcToMethod(func, clas, method_name = None):
    func.im_class = clas
    func.im_func = func
    func.im_self = None
    if not method_name:
        method_name = func.__name__
    
    clas.DtoolClassDict[method_name] = func


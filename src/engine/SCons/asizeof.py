#!/usr/bin/env python

# Copyright, license and disclaimer are at the end of this file.

# This is the latest, enhanced version of the asizeof.py recipes at
# <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/546530>
# <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/544288>

'''This module exposes 8 functions and 1 class to obtain lengths
   and sizes of Python objects (for Python 2.2 or later).

   Function  asizeof calculates the combined (approximate) size
   of one or several Python objects in bytes.  Function  asizesof
   returns a tuple containing the (approximate) size in bytes for
   each given Python object separately.

   Functions  basicsize and  itemsize return the basic resp. item
   size of the given object.

   Function  flatsize returns the flat size of a Python object in
   bytes defined as the basic size plus the item size times the
   length of the given object.

   Function  leng returns the length of an object, like standard
   len but extended for several types, e.g. the  leng of a multi-
   precision int (or long) is the number of digits**.

   Function  refs returns (a generator for) the referents of the
   given object, i.e. the objects referenced by the given object.

   Certain classes are known to be sub-classes of or behave as
   dict objects.  Function  adict can be used to install other
   class objects to be treated as dict.

   Class  Asizer can be used to accumulate the results of several
   asizeof or  asizesof calls.  After creating an  Asizer instance,
   use methods  asizeof and  asizesof to size additional objects.
   Methods  exclude_refs or  exclude_types can be used to exclude
   references to resp. instances or types of certain objects.  Use
   one of the  print_... methods to report the statistics.


   The size of an object is defined as the sum of the flat size of
   the object and the the sizes of any referents.  Referents are
   visited recursively up to a given limit.  The size of objects
   referenced multiple times is included only once.

   The flat size of an object is defined as the basic size of the
   object plus the item size times the number of items.  The flat
   size does include the items (which may contain references to
   the referents), but does not include the referents themselves.
   The flat size equals the result of the  asizeof function with
   recursion limit zero and without size alignment.

   The leng(th) and (flat) size of mutable sequence objects as
   dicts, lists, sets, etc. includes an estimate for the over-
   allocation of the items space.


   The basic and item sizes are obtained from the __basicsize__
   resp. __itemsize__ attributes of the (type of the) object.
   Where necessary (for sequence objects), a zero item size is
   replaced by the size of the C typedef of the item.

   The (byte)code size of objects as classes, functions, methods,
   modules, etc. can be included, optionally.

   Sizes can be aligned to a given alignment (power of 2).


   All class, instance and type objects, new- and old-style are
   handled uniformly such that instance objects are distinguished
   from class objects and instances of different old-style classes
   can be dealt with separately.

   Class and type objects are represented as <class ....* def>
   resp. <type ... def> where an * indicates an old-style class
   and the  def suffix marks the definition object.  Instances of
   old-style classes are shown as new-style ones but with an *
   like <class module.name*>.

   To prevent excessive sizes, several object types are ignored,
   e.g. builtin functions, builtin types and classes, function
   globals and referents modules.  However, any instances thereof
   are sized and module objects are sized if passed as arguments.

   In addition, many __...__ attributes of callable objects are
   ignored, except crucial ones, e.g. class attributes __dict__,
   __doc__, __name__.  For more details, see the type-specific
   _..._refs() and _len_...() functions below.

   Types and classes are considered builtin if the module of the
   type or class is listed in _builtin_modules below.

   These definitions and other assumptions are rather arbitrary
   and may need corrections or adjustments.

   Tested with Python 2.2.3, 2.3.4, 2.4.4, 2.5.1, 2.5.2, 2.6a1
   or 3.0a3 on RHEL 3u7, CentOS 4.6, SuSE 9.3, MacOS X Tiger
   (Intel) and Panther (PPC), Solaris 10 and Windows XP.

   The functions and classes in this module are not thread-safe.

   **) See Python source file .../Include/longinterp.h for the
       C typedef of digit used in multi-precision int (or long)
       objects.  The size of digit in bytes can be obtained in
       Python from the int (or long) __itemsize__ attribute.
       Function  leng (rather _len_int) below deterimines the
       number of digits from the int (or long) value.
'''

from __future__ import generators  # for yield in Python 2.2

from inspect    import isbuiltin, isclass, iscode, isframe, isfunction, ismethod, ismodule, stack
from math       import log
from os         import linesep
from struct     import pack  # class Struct only in Python 2.5 and 3.0
from sys        import modules, getrecursionlimit, stdout
import types    as     Types
import weakref  as     Weakref

__version__ = '3.22 (Apr 03, 2008)'
__all__     = ['adict', 'asizeof', 'asizesof', 'Asizer',
               'basicsize', 'flatsize', 'itemsize', 'leng', 'refs']

 # any classes or types in modules listed in _builtin_modules
 # are considered builtin and ignored, like builtin functions
if __name__ == '__main__':
    _builtin_modules = (int.__module__, 'types', Exception.__module__)  # , 'weakref'
else:  # treat this very module as builtin
    _builtin_modules = (int.__module__, 'types', Exception.__module__, __name__)  # , 'weakref'

 # sizes of some C types
 # XXX len(pack(T, 0)) == Struct(T).size == calcsize(T)
_sizeof_Cint   = len(pack('i', 0))  # sizeof(int)
_sizeof_Clong  = len(pack('l', 0))  # sizeof(long)
_sizeof_Cshort = len(pack('h', 0))  # sizeof(short)
_sizeof_Cssize = len(pack('P', 0))  # sizeof(ssize_t)
_sizeof_Cvoidp = len(pack('P', 0))  # sizeof(void*)
try:  # C typedef digit for multi-precision int (or long)
   _sizeof_Cdigit = long.__itemsize__
except NameError:  # no long in Python 3.0
   _sizeof_Cdigit = int.__itemsize__
if _sizeof_Cdigit < 2:
    raise ValueError('sizeof(digit) too low: %d' % _sizeof_Cdigit)

 # default values for some basic- and itemsizes
_sizeof_Chead           = _sizeof_Cvoidp + _sizeof_Cssize  # sizeof(PyObject_HEAD)
_sizeof_Cvar_head       = _sizeof_Chead  + _sizeof_Cssize  # sizeof(PyObject_VAR_HEAD)

_sizeof_CPyCodeObject   = _sizeof_Chead     + (10 * _sizeof_Cvoidp) + (5 * _sizeof_Cint)  # sizeof(PyCodeObject)
_sizeof_CPyFrameObject  = _sizeof_Cvar_head + (13 * _sizeof_Cvoidp) + (21 * 3 * _sizeof_Cint)  # sizeof(PyFrameObject)
_sizeof_CPyModuleObject = _sizeof_Chead     +       _sizeof_Cvoidp  # sizeof(PyModuleObject)

_sizeof_CPyDictEntry    = _sizeof_Cssize + (2 * _sizeof_Cvoidp)  # sizeof(PyDictEntry)
_sizeof_Csetentry       = _sizeof_Cvoidp + _sizeof_Clong         # sizeof(setentry)


 # compatibility functions for more uniform
 # behavior across Python version 2.2 thu 3.0

def _items(obj):  # dict only
    '''Return iter-/generator, preferably.
    '''
    return getattr(obj, 'iteritems', obj.items)()

def _keys(obj):  # dict only
    '''Return iter-/generator, preferably.
    '''
    return getattr(obj, 'iterkeys', obj.keys)()

def _values(obj):  # dict only
    '''Use iter-/generator, preferably.
    '''
    return getattr(obj, 'itervalues', obj.values)()

try:  # callable() builtin
    _callable = callable
except NameError:  # callable() removed in Python 3.0
    def _callable(obj):
        '''Substitute for callable().'''
        return hasattr(obj, '__call__')

def _kwds(**kwds):  # no dict(key=value, ...) in Python 2.2
    '''Return name=value pairs as keywords dict.
    '''
    return kwds

try:  # sorted() builtin
    _sorted = sorted
except NameError:  # no sorted() in Python 2.2
    def _sorted(vals, reverse=False):
        '''Partial substitute for missing sorted().'''
        vals.sort()
        if reverse:
            vals.reverse()
        return vals

 # private functions

def _basicsize(t, base=0):
    '''Get non-zero basicsize of type.
    '''
     # at the default size
    return max(getattr(t, '__basicsize__', 0), base)

def _derive_typedef(typ):
    '''Return single, existing super type typedef or None.
    '''
    v = [v for v in _values(_typedefs) if _issubclass(typ, v.type)]
    if len(v) == 1:
        return v[0]
    return None

def _dir(obj, pref='', excl=()):
    '''Return matching attribute names of an object with exclusions.
    '''
    for a in dir(obj):  # cf. inspect.getmembers()
        if a.startswith(pref) and a not in excl:
            yield a

def _infer_dict(obj):
    '''Return True for likely dict object.
    '''
    for ats in (('__len__', 'get', 'has_key',     'items',     'keys',     'values'),
                ('__len__', 'get', 'has_key', 'iteritems', 'iterkeys', 'itervalues')):
        for a in ats:  # no all(<generator_expression>) in Python 2.2
            if not _callable(getattr(obj, a, None)):
                break
        else:  # all True
            return True
    return False

def _isdictclass(obj):
    '''Return True for known dict objects.
    '''
    c = getattr(obj, '__class__', None)
    return c and c.__name__ in _dict_classes.get(c.__module__, ())

def _issubclass(sub, sup):
    '''Safe issubclass().
    '''
    if sup is not object:
        try:
            return issubclass(sub, sup)
        except TypeError:
            pass
    return False

def _itemsize(t, item=0):
    '''Get non-zero itemsize of type.
    '''
     # replace zero value with default
    return getattr(t, '__itemsize__', 0) or item

def _kwdstr(**kwds):
    '''Keyword arguments as a string.
    '''
    return ', '.join(_sorted(['%s=%r' % kv for kv in _items(kwds)]))  # [] for Python 2.2

def _lengstr(obj):
    '''Object length as a string.
    '''
    n = leng(obj)
    if n is None:  # no len
        return ''
    if n > _len(obj):  # extended
        return ' leng %d!' % n
    return ' leng %d' % n

def _prepr(obj, clip=0):
    '''Prettify and clip long repr() string.
    '''
    return _repr(obj, clip=clip).strip('<>').replace("'", '')  # remove <''>

def _printf(fmt, *args, **print3opts):
    '''Formatted print.
    '''
    if print3opts:  # like Python 3.0
        f = print3opts.get('file', stdout) or stdout
        if args:
            f.write(fmt % args)
        else:
            f.write(fmt)
        f.write(print3opts.get('end', linesep))
    elif args:
        print(fmt % args)
    else:
        print(fmt)

def _refs(obj, *ats, **kwds):
    '''Return specific attribute objects of an object.
    '''
    for a in ats:  # cf. inspect.getmembers()
        if hasattr(obj, a):
            #tmp = (a, getattr(obj, a))
            yield getattr(obj,a)
    if kwds:  # kwds are _dir() args
        for a in _dir(obj, **kwds):
            #tmp = (a, getattr(obj, a))
            yield getattr(obj,a)

def _repr(obj, clip=80):
    '''Clip long repr() string.
    '''
    try:  # safe repr()
        r = repr(obj)
    except TypeError:
        r = 'N/A'
    if 0 < clip < len(r):
        h = (clip // 2) - 2
        if h > 0:
            r = r[:h] + '....' + r[-h:]
    return r

def _SI(size, K=1024, i='i'):
    '''Return size as SI string.
    '''
    if 1 < K < size:
        f = float(size)
        for si in iter('KMGPTE'):
            f /= K
            if f < K:
                return ' or %.1f %s%sB' % (f, si, i)
    return ''

def _SI2(size, **kwds):
    '''Return size as regular plus SI string.
    '''
    return str(size) + _SI(size, **kwds)


 # type-specific referent functions

def _class_refs(obj):
    '''Return specific referents of a class object.
    '''
    return _refs(obj, '__class_', '__dict__', '__doc__', '__mro__', '__name__', '__slots__', '__weakref__')

def _co_refs(obj):
    '''Return specific referents of a code object.
    '''
    return _refs(obj, pref='co_')

def _dict_refs(obj):
    '''Return key and value objects of a dict/proxy.
    '''
     # dict.iteritems removed in Python 3.0
    for k, v in _items(obj):
        yield k
        yield v

def _enum_refs(obj):
    '''Return specific referents of an enumerate object.
    '''
    return _refs(obj, '__doc__')

def _exc_refs(obj):
    '''Return specific referents of an Exception object.
    '''
    return _refs(obj, 'args', 'filename', 'lineno', 'message', 'msg', 'text')  # mixed

def _file_refs(obj):
    '''Return specific referents of a file object.
    '''
    return _refs(obj, 'mode', 'name')

def _frame_refs(obj):
    '''Return specific referents of a frame object.
    '''
    return _refs(obj, pref='f_')

def _func_refs(obj):
    '''Return specific referents of a function or lambda object.
    '''
    return _refs(obj, '__doc__', '__name__', '__code__', pref='func_', excl=('func_globals',))

def _gi_refs(obj):
    '''Return specific referents of a generator object.
    '''
    return _refs(obj, pref='gi_')

def _im_refs(obj):
    '''Return specific referents of a method object.
    '''
    return _refs(obj, '__doc__', '__name__', '__code__', pref='im_')

def _inst_refs(obj):
    '''Return specific referents of a class instance.
    '''
    return _refs(obj, '__dict__', '__slots__', '__class__')

def _module_refs(obj):
    '''Return specific referents of a module object.
    '''
     # ignore this very module
    if obj.__name__ == __name__:
        return ()
     # module is essentially a dict
    return _dict_refs(obj.__dict__)

def _prop_refs(obj):
    '''Return specific referents of a property object.
    '''
    return _refs(obj, '__doc__', pref='f')

def _seq_refs(obj):
    '''Return specific referents of a frozen/set, list, tuple and xrange object.
    '''
    return obj  # XXX for r in obj: yield r

def _tb_refs(obj):
    '''Return specific referents of a traceback object.
    '''
    return _refs(obj, pref='tb_')

def _type_refs(obj):
    '''Return specific referents of a type object.
    '''
    return _refs(obj, '__dict__', '__doc__', '__mro__', '__name__', '__slots__', '__weakref__')

def _weak_refs(obj):
    '''Return weakly referent object.
    '''
    try:  # ignore 'key' of KeyedRef
        return (obj(),)
    except:  # XXX ReferenceError
        return ()

_all_refs = (None, _class_refs,     _co_refs, _dict_refs, _enum_refs, _exc_refs,
                    _file_refs,  _frame_refs, _func_refs,   _gi_refs,  _im_refs,
                    _inst_refs, _module_refs, _prop_refs,  _seq_refs,  _tb_refs,
                    _type_refs,   _weak_refs)


 # type-specific length functions

def _len(obj):
    '''Safe len().
    '''
    try:
        return len(obj)
    except TypeError:  # no len()
        return 0

def _len1(obj):
    '''Length of str and unicode.
    '''
    return len(obj) + 1  # XXX sentinel

def _len_array(obj):
    '''Array length in bytes.
    '''
    return len(obj) * obj.itemsize

_digit2p2 = 1 << (_sizeof_Cdigit * 8)
_digitmax = _digit2p2 - 1  # == (2 * PyLong_MASK + 1)
_digitlog = 1.0 / log(_digit2p2)

def _len_int(obj):
    '''Length of multi-precision int (aka long) in digits.
    '''
    n, i = 1, abs(obj)
    if i > _digitmax:
         # no log(x[, base]) in Python 2.2
        n += int(log(i) * _digitlog)
    return n

def _len_module(obj):
    '''Module length.
    '''
    return _len(obj.__dict__)  # _len(dir(obj))

def _len_mutable(obj):
    '''Length of mutable sequences.
    '''
    n = len(obj)
     # estimate over-allocation
    if n < 9:
        n += 4
    else:
        n += 6 + (n >> 3)
    return n

def _len_slice(obj):
    '''Slice length.
    '''
    try:
        return ((obj.stop - obj.start + 1) // obj.step)
    except AttributeError:
        return 0

def _len_struct(obj):
    '''Struct length in bytes.
    '''
    try:
        return obj.size
    except AttributeError:
        return 0

_all_lengs = (None, _len,        _len1,        _len_array, _len_int,
                    _len_module, _len_mutable, _len_slice, _len_struct)


# more private functions and classes

_old_style = '*'  # marker
_new_style = ''   # no marker

class _Claskey(object):
    '''Wrapper for class objects.
    '''
    _obj = None
    _sty = ''

    def __init__(self, obj, style):
        self._obj = obj  # XXX Weakref.ref(obj)
        self._sty = style

    def __str__(self):
        r = str(self._obj)
        if r.endswith('>'):
            return '%s%s def>' % (r[:-1], self._sty)
        elif self._sty is _old_style and not r.startswith('class '):
            return 'class %s%s def' % (r, self._sty)
        else:
            return '%s%s def' % (r, self._sty)
    __repr__ = __str__

 # For most objects, the object type is used as the key in the
 # _typedefs dict further below, except class and type objects
 # and old-style instances.  Those are wrapped with separate
 # _Claskey or _Instkey instances to be able (1) to distinguish
 # instances of different old-style classes by class, (2) to
 # distinguish class (and type) instances from class (and type)
 # definitions for new-style classes and (3) provide similar
 # results for repr() and str() of new- and old-style classes
 # and instances.

_claskeys = {}  # [id(obj)] = _Claskey()

def _claskey(obj, style):
    '''Wrap an old- or new-style class object.
    '''
    i =  id(obj)
    k = _claskeys.get(i, None)
    if not k:
        _claskeys[i] = k = _Claskey(obj, style)
    return k

_Type_type = type(type)  # type and new-style class type

try:  # no Class_ and InstanceType in Python 3.0
    _Types_ClassType    = Types.ClassType
    _Types_InstanceType = Types.InstanceType

    class _Instkey(object):
        '''Wrapper for old-style class (instances).
        '''
        _obj = None

        def __init__(self, obj):
            self._obj = obj  # XXX Weakref.ref(obj)

        def __str__(self):
            return '<class %s.%s%s>' % (self._obj.__module__, self._obj.__name__, _old_style)
        __repr__ = __str__

    _instkeys = {}  # [id(obj)] = _Instkey()

    def _instkey(obj):
        '''Wrap an old-style class (instance).
        '''
        i =  id(obj)
        k = _instkeys.get(i, None)
        if not k:
            _instkeys[i] = k = _Instkey(obj)
        return k

    def _keytuple(obj):
        '''Return class and instance keys for a class.
        '''
        t = type(obj)
        if t is _Types_InstanceType:
            t = obj.__class__
            return _claskey(t,   _old_style), _instkey(t)
        elif t is _Types_ClassType:
            return _claskey(obj, _old_style), _instkey(obj)
        elif t is _Type_type:
            return _claskey(obj, _new_style), obj
        return None, None  # not a class

    def _objkey(obj):
        '''Return the key for any object.
        '''
        k = type(obj)
        if k is _Types_InstanceType:
            return _instkey(obj.__class__)
        elif k is _Types_ClassType:
            return _claskey(obj, _old_style)
        elif k is _Type_type:
            return _claskey(obj, _new_style)
        return k

except AttributeError:  # Python 3.0

    def _keytuple(obj):  #PYCHOK expected
        '''Return class and instance keys for a class.
        '''
        if type(obj) is _Type_type:  # isclass(obj):
            return _claskey(obj, _new_style), obj
        return None, None  # not a class

    def _objkey(obj):  #PYCHOK expected
        '''Return the key for any object.
        '''
        k = type(obj)
        if k is _Type_type:  # isclass(obj):
            k = _claskey(k, _new_style)
        return k

 # kinds of _Typedefs
_all_kinds = (_kind_static, _kind_dynamic, _kind_derived, _kind_ignored, _kind_inferred) = (
                   'static',     'dynamic',     'derived',     'ignored',     'inferred')

class _Typedef(object):
    '''Internal type definition class.
    '''
    base = 0     # basic size in bytes
    item = 0     # item size in bytes
    leng = None  # or _len_() function
    refs = None  # or _refs() function
    both = None  # both data and code if True, code only if False
    kind = None  # or _kind_ value
    type = None  # original type

    def __init__(self, **kwds):
        self.reset(**kwds)

    def __lt__(self, other):  # for Python 3.0
        return True

    def __repr__(self):
        return repr(self.args())

    def __str__(self):
        if self.kind == _kind_ignored:
            t = [_kind_ignored,]
        else:
            t = [str(self.base), str(self.item)]
            for f in (self.leng, self.refs):
                if f:
                    t.append(f.__name__)
                else:
                    t.append('n/a')
        if not self.both:
            t.append('(code only)')
        return ', '.join(t)

    def args(self):  # as args tuple
        '''Return all attributes as arguments tuple.
        '''
        return (self.base, self.item, self.leng, self.refs, self.both, self.kind, self.type)

    def dup(self, other=None, **kwds):
        '''Duplicate attributes of dict or other typedef.
        '''
        if other is None:
            d = _typedefs[_dict_key].kwds()
        else:
            d =  other.kwds()
        d.update(kwds)
        self.reset(**d)

    def kwds(self):
        '''Return all attributes as keywords dict.
        '''
         # no dict(refs=self.refs, ..., kind=self.kind) in Python 2.0
        return _kwds(base=self.base, item=self.item,
                     leng=self.leng, refs=self.refs,
                     both=self.both, kind=self.kind, type=self.type)

    def set(self, safe_len=False, **kwds):
        '''Set one or more attributes.
        '''
        d = self.kwds()
        d.update(kwds)
        self.reset(**d)
        if safe_len and self.item:
            self.leng = _len

    def reset(self, base=0, item=0, leng=None, refs=None, both=True, kind=None, type=None):
        '''Reset all attributes.
        '''
        if base < 0:
            raise ValueError('asizeof basic size invalid: %r' % base)
        else:
            self.base = base
        if item < 0:
            raise ValueError('asizeof item size invalid: %r' % item)
        else:
            self.item = item
        if leng in _all_lengs:  # XXX or _callable(leng)
            self.leng = leng
        else:
            raise ValueError('asizeof _len_() invalid: %r' % leng)
        if refs in _all_refs:  # XXX or _callable(refs)
            self.refs = refs
        else:
            raise ValueError('asizeof _refs() invalid: %r' % refs)
        if both in (False, True):
            self.both = both
        else:
            raise ValueError('asizeof both invalid: %r' % both)
        if kind in _all_kinds:
            self.kind = kind
        else:
            raise ValueError('asizeof kind invalid: %r' % kind)
        self.type = type
         # zap ignored typedefs
        if self.kind == _kind_ignored:
            self.base = self.item = 0
            self.leng = self.refs = None

_typedefs = {}  # [key] = _Typedef()

def _typedef(t, base=0, item=0, leng=None, refs=None, both=True, kind=_kind_static):
    '''Add new typedef for both data and code or for code only.
    '''
    c, k = _keytuple(t)
    if k and k not in _typedefs:  # instance key
        _typedefs[k] = _Typedef(base=_basicsize(t, base), item=item,
                                refs=refs, leng=leng,
                                both=both, kind=kind, type=t)
        if c and c not in _typedefs:  # class key
            if t.__module__ not in _builtin_modules:
                _typedefs[c] = _Typedef(base=_basicsize(t),
                                        refs=_type_refs,
                                        both=False, kind=kind, type=t)
          ##else:
          ##    _typedefs[c] = _Typedef(both=False, kind=_kind_ignored, type=t)
    elif isbuiltin(t) and t not in _typedefs:  # array, range, xrange in Python 2.x
        _typedefs[t] = _Typedef(both=False, kind=_kind_ignored, type=t)
    else:
        raise KeyError('asizeof typedef %r: %r %r' % (t, (c, k), both))
    return k  # for _dict_key

def _typedef_both(t, base=0, item=0, leng=None, refs=None, kind=_kind_static):
    '''Add new typedef for both data and code.
    '''
    return _typedef(t, base=base, item=_itemsize(t, item), leng=leng, refs=refs, both=True, kind=kind)

def _typedef_code(t, refs=None, kind=_kind_static):
    '''Add new typedef for code only.
    '''
    return _typedef(t, item=0, refs=refs, both=False, kind=kind)


 # static typedefs for data and code types
_typedef_both(complex)
_typedef_both(float)
_typedef_both(list,     leng=_len_mutable, refs=_seq_refs, item=_sizeof_Cvoidp)  # sizeof(PyObject*)
_typedef_both(tuple,    leng=_len,         refs=_seq_refs, item=_sizeof_Cvoidp)  # sizeof(PyObject*)
_typedef_both(property, refs=_prop_refs)
_typedef_both(type(Ellipsis))
_typedef_both(type(None))

 # dict, dictproxy, dict_proxy and other dict-like types
_dict_key  = _typedef_both(      dict,     item=_sizeof_CPyDictEntry, leng=_len_mutable, refs=_dict_refs)
try:  # <type dictproxy> only in Python 2.x
    _typedef_both(Types.DictProxyType,     item=_sizeof_CPyDictEntry, leng=_len_mutable, refs=_dict_refs)
except AttributeError:  # XXX any class __dict__ is <type dict_proxy> in Python 3.0?
    _typedef_both(type(_Typedef.__dict__), item=_sizeof_CPyDictEntry, leng=_len_mutable, refs=_dict_refs)
 # other dict-like classes and types may be derived or inferred,
 # provided the module and class name is listed here (see functions
 # adict, _isdictclass and _infer_dict for further details)
_dict_classes = {'UserDict': ('IterableUserDict',  'UserDict'),
                 'weakref' : ('WeakKeyDictionary', 'WeakValueDictionary')}
try:  # <type module> is essentially a dict
    _typedef_both(Types.ModuleType, base=_typedefs[_dict_key].base,
                                    item=_typedefs[_dict_key].item + _sizeof_CPyModuleObject,
                                    leng=_len_module, refs=_module_refs)
except AttributeError:  # missing
    pass

 # newer or obsolete types
try:
    from array import array  # array type
    _typedef_both(array, leng=_len_array, item=1)
except ImportError:  # missing
    pass

try:
    _typedef_both(bool)
except NameError:  # missing
    pass

try:  # ignore basestring
    _typedef_both(basestring, leng=None)
except NameError:  # missing
    pass

try:
    if isbuiltin(buffer):  # Python 2.2
        _typedef_both(type(buffer('')), item=1, leng=_len)  # XXX len in bytes?
    else:
        _typedef_both(buffer,           item=1, leng=_len)  # XXX len in bytes?
except NameError:  # missing
    pass

try:
    _typedef_both(bytearray, item=1, leng=_len)  # len in bytes #PYCHOK bytearray new in 3.0
except NameError:  # missing
    pass
try:
    if type(bytes) is not type(str):  # bytes is str in 2.6 #PYCHOK bytes new in 3.0
      _typedef_both(bytes, item=1, leng=_len)  # len in bytes #PYCHOK bytes new in 3.0
except NameError:  # missing
    pass
try:  # XXX like bytes + sentinel?
    _typedef_both(str8,  item=1, leng=_len1,)  # len in bytes #PYCHOK str8 new in 3.0
except NameError:  # missing
    pass

try:
    _typedef_both(enumerate, refs=_enum_refs)
except NameError:  # missing
    pass

try:  # Exception is type in Python 3.0
    _typedef_both(Exception, refs=_exc_refs)
except:  # missing
    pass

try:
    _typedef_both(file, refs=_file_refs)
except NameError:  # missing
    pass

try:
    _typedef_both(frozenset, item=_sizeof_Csetentry, leng=_len_mutable, refs=_seq_refs)
except NameError:  # missing
    pass
try:
    _typedef_both(set,       item=_sizeof_Csetentry, leng=_len_mutable, refs=_seq_refs)
except NameError:  # missing
    pass

try:  # no len() and not callable()
    _typedef_both(Types.GeneratorType, refs=_gi_refs)
except AttributeError:  # missing
    pass

try:  # not callable()
    _typedef_both(Types.GetSetDescriptorType)
except AttributeError:  # missing
    pass

try:  # if long exists, it is multi-precision ...
    _typedef_both(long, item=_sizeof_Cdigit, leng=_len_int)
    _typedef_both(int)  # ... and int is fixed size
except NameError:  # no long, only multi-precision int in Python 3.0
    _typedef_both(int,  item=_sizeof_Cdigit, leng=_len_int)

try:  # not callable()
    _typedef_both(Types.MemberDescriptorType)
except AttributeError:  # missing
    pass

try:
    _typedef_both(type(NotImplemented))
except NameError:  # missing
    pass

try:
    _typedef_both(range)
except NameError:  # missing
    pass
try:
    _typedef_both(xrange)
except NameError:  # missing
    pass

try:
    _typedef_both(reversed, refs=_enum_refs)
except NameError:  # missing
    pass

try:
    _typedef_both(slice, item=_sizeof_Cvoidp, leng=_len_slice)  # XXX worst-case itemsize?
except NameError:  # missing
    pass

try:
    from struct import Struct  # only in Python 2.5 and 3.0
    _typedef_both(Struct, item=1, leng=_len_struct)  # len in bytes
except ImportError:  # missing
    pass

try:
    _typedef_both(Types.TracebackType, refs=_tb_refs)
except AttributeError:  # missing
    pass

try:
    _typedef_both(unicode, leng=_len1, item=_sizeof_Cshort)  # XXX sizeof(PY_UNICODE_TYPE)?
    _typedef_both(str,     leng=_len1, item=1)  # 1-byte char
except NameError:  # str is unicode
    _typedef_both(str,     leng=_len1, item=2)  # XXX 2-byte char?

try:  # <type 'KeyedRef'>
    _typedef_both(Weakref.KeyedRef, refs=_weak_refs)
except AttributeError:  # missing
    pass

try:  # <type 'weakproxy'>
    _typedef_both(Weakref.ProxyType)
except AttributeError:  # missing
    pass

try:  # <type 'weakref'>
    _typedef_both(Weakref.ReferenceType, refs=_weak_refs)
except AttributeError:  # missing
    pass

 # some other, callable types
_typedef_code(object,     kind=_kind_ignored)
_typedef_code(super,      kind=_kind_ignored)
_typedef_code(_Type_type, kind=_kind_ignored)

try:
    _typedef_code(classmethod, refs=_im_refs)
except NameError:
    pass
try:
    _typedef_code(staticmethod, refs=_im_refs)
except NameError:
    pass
try:
    _typedef_code(Types.MethodType, refs=_im_refs)
except NameError:
    pass

try:  # <type 'weakcallableproxy'>
    _typedef_code(Weakref.CallableProxyType, refs=_weak_refs)
except AttributeError:  # missing
    pass


class _Prof(object):
    '''Internal type profile class.
    '''
    total  = 0     # total size
    high   = 0     # largest size
    number = 0     # number of (unique) objects
    objref = None  # largest object (weakref)
    weak   = False # objref is weakref(object)

    def __cmp__(self, other):
        if self.total < other.total:
            return -1
        if self.total > other.total:
            return +1
        if self.number < other.number:
            return -1
        if self.number > other.number:
            return +1
        return 0

    def __lt__(self, other):  # for Python 3.0
        return self.__cmp__(other) < 0

    def format(self, clip=0):
        '''Return format dict.
        '''
        if self.number > 1:  # avg., plural
            a, p = int(self.total / self.number), 's'
        else:
            a, p = self.total, ''
        o = self.objref
        if self.weak:  # weakref'd
            o = o()
        return _kwds(avg=_SI2(a),             high=_SI2(self.high), lengstr=_lengstr(o),
                     obj=_repr(o, clip=clip), plural=p,             total=_SI2(self.total))

    def update(self, obj, size):
        '''Update this profile.
        '''
        self.number += 1
        self.total  += size
        if self.high < size:  # largest
           self.high = size
           try:  # prefer using weak ref
               self.objref, self.weak = Weakref.ref(obj), True
           except TypeError:
               self.objref, self.weak = obj, False


 # public class

class Asizer(object):
    '''Sizer state and options.
    '''
    _excl_d = {}

    def __init__(self, **opts):
        '''See method  reset for the available options.
        '''
        self.reset(**opts)

    def _clear(self):
        '''Clear state.
        '''
        self._depth   = 0   # recursion depth
        self._excl_d  = dict([(k, 0) for k in _keys(self._excl_d)])
        self._incl    = ''  # or ' (incl. code)'
        self._mask    = 0
        self._profile = False
        self._profs   = {}
        self._seen    = {}
        self._total   = 0   # total size

    def _prepr(self, obj):
        '''Like prepr().
        '''
        return _prepr(obj, clip=self._clip_)

    def _prof(self, key):
        '''Get _Prof object.
        '''
        p = self._profs.get(key, None)
        if not p:
            self._profs[key] = p = _Prof()
        return p

    def _repr(self, obj):
        '''Like repr().
        '''
        return _repr(obj, clip=self._clip_)

    def _recursive_sizer(self, obj, deep):
        '''Size an object, recursively.
        '''
        s, i = 0, id(obj)
        base = 0
        chld = []
         # skip obj if seen before
         # or if ref of a given obj
        if i in self._seen:
            self._seen[i] += 1
            if deep:
                return (s, base, chld)
        else:
            self._seen[i]  = 1
        try:
            k = _objkey(obj)
            if k in self._excl_d:
                self._excl_d[k] += 1
            else:
                v = _typedefs.get(k, None)
                if not v:  # new type
                    v = self._typedef(obj)
                    if k in _typedefs:  # and _typedefs[k] != v:  # double check
                        raise KeyError('asizeof %r conflict: %r vs %r' % (t, _typedefs[k], v))
                    _typedefs[k] = v
                  ##_printf('new typedefs [%r] %r', k, v)
                if v.both or self._code_:
                    s = v.base  # basic size
                    if v.leng and v.item > 0:  # include items
                        s += v.item * v.leng(obj)
                    if self._mask:  # aligned size
                        s = (s + self._mask) & ~self._mask
                    if self._profile:  # profile type
                        self._prof(k).update(obj, s)
                    base = s
                     # recurse, but not for nested modules
                    if v.refs and deep < self._limit_ and not (deep and ismodule(obj)):
                         # add sizes of referents
                        r, d = v.refs, deep + 1
                        for o in r(obj):  # no sum(<generator_expression>) in Python 2.2
                            #label = o
                            #if isinstance(o, tuple):
                            #    label = o[0]
                            #    o = o[1]
                            #else:
                            #    label = o
                            if deep < self._detail:
                                # TODO Associate member variable name, rather
                                # than content. Find some way to make _ref
                                # functions return the ref name, too.                                                                
                                so = self._recursive_sizer(o,d)
                                so = so + (o,)
                                chld.append(so)
                                s += so[0]
                            else:
                                s += self._sizer(o,d)
                         # recursion depth
                        if self._depth < d:
                           self._depth = d
        except RuntimeError:  # XXX RecursionLimitExceeded:
            pass
        return (s, base, chld)

    def _sizer(self, obj, deep):
        '''Size an object, recursively.
        '''
        s, i = 0, id(obj)
         # skip obj if seen before
         # or if ref of a given obj
        if i in self._seen:
            self._seen[i] += 1
            if deep:
                return s
        else:
            self._seen[i]  = 1
        try:
            k = _objkey(obj)
            if k in self._excl_d:
                self._excl_d[k] += 1
            else:
                v = _typedefs.get(k, None)
                if not v:  # new type
                    v = self._typedef(obj)
                    if k in _typedefs:  # and _typedefs[k] != v:  # double check
                        raise KeyError('asizeof %r conflict: %r vs %r' % (t, _typedefs[k], v))
                    _typedefs[k] = v
                  ##_printf('new typedefs [%r] %r', k, v)
                if v.both or self._code_:
                    s = v.base  # basic size
                    if v.leng and v.item > 0:  # include items
                        s += v.item * v.leng(obj)
                    if self._mask:  # aligned size
                        s = (s + self._mask) & ~self._mask
                    if self._profile:  # profile type
                        self._prof(k).update(obj, s)
                     # recurse, but not for nested modules
                    if v.refs and deep < self._limit_ and not (deep and ismodule(obj)):
                         # add sizes of referents
                        r, z, d = v.refs, self._sizer, deep + 1
                        for o in r(obj):  # no sum(<generator_expression>) in Python 2.2
                            s += z(o, d)
                         # recursion depth
                        if self._depth < d:
                           self._depth = d
        except RuntimeError:  # XXX RecursionLimitExceeded:
            pass
        return s

    def _typedef(self, obj):
        '''Return a new typedef for the type of an object.
        '''
        t =  type(obj)
        v = _Typedef(kind=_kind_dynamic, type=t)
      ##_printf('new %r %r/%r %s', t, _basicsize(t), _itemsize(t), self._repr(dir(obj)))
        if ismodule(obj):  # handle module like dict
            v.dup(item=_typedefs[_dict_key].item + _sizeof_CPyModuleObject,
                  leng=_len_module,
                  refs=_module_refs)
        elif isframe(obj):
            v.set(base=_basicsize(t, _sizeof_CPyFrameObject),
                  item=_itemsize(t), safe_len=True,
                  refs=_frame_refs)
        elif iscode(obj):
            v.set(base=_basicsize(t, _sizeof_CPyCodeObject),
                  refs=_co_refs,
                  both=False)  # code only
        elif _callable(obj):
            if isclass(obj):  # class or type
                if obj.__module__ in _builtin_modules:
                    v.set(both=False,  # code only
                          kind=_kind_ignored)
                else:
                    v.set(base=_basicsize(t),
                          refs=_class_refs,
                          both=False)  # code only
            elif isbuiltin(obj):  # function or method
                v.set(both=False,  # code only
                      kind=_kind_ignored)
            elif isfunction(obj):
                v.set(base=_basicsize(t),
                      refs=_func_refs,
                      both=False)  # code only
            elif ismethod(obj):
                v.set(base=_basicsize(t),
                      refs=_im_refs,
                      both=False)  # code only
            elif isclass(t):  # callable instance, e.g. SCons,
                 # handle like any other instance further below
                v.set(base=_basicsize(t),
                      item=_itemsize(t), safe_len=True,
                      refs=_inst_refs)  # not code only!
            else:
                v.set(base=_basicsize(t),
                      both=False)  # code only
        elif _issubclass(t, dict):
            v.dup(kind=_kind_derived)
        elif _isdictclass(obj) or (self._infer_ and _infer_dict(obj)):
            v.dup(kind=_kind_inferred)
        elif getattr(obj, '__module__', None) in _builtin_modules:
            v.set(kind=_kind_ignored)
        else:  # assume an instance of some class
            if self._derive_:
                p = _derive_typedef(t)
                if p:  # duplicate parent
                    v.dup(other=p, kind=_kind_derived)
                    return v
            if _issubclass(t, Exception):
                v.set(base=_basicsize(t),
                      item=_itemsize(t), safe_len=True,
                      refs=_exc_refs,
                      kind=_kind_derived)
            elif isinstance(obj, Exception):
                v.set(base=_basicsize(t),
                      item=_itemsize(t), safe_len=True,
                      refs=_exc_refs)
            else:
                v.set(base=_basicsize(t),
                      item=_itemsize(t), safe_len=True,
                      refs=_inst_refs)
        return v

    def asizeof(self, *objs, **opts):
        '''Return the combined object size (with modified options).
        '''
        self.set(**opts)
        self.exclude_refs(*objs)  # skip refs to objs
        s, z = 0, self._sizer
        for o in objs:  # no sum(<generator_expression>) in Python 2.2
            s += z(o, 0)
        self._total += s  # accumulate
        return s

    def asizeof_rec(self, obj, detail=0, **opts):
        self.set(**opts)
        self.exclude_refs(obj)
        self._detail = detail
        z = self._recursive_sizer
        s = z(obj,0)
        self._total += s[0]
        return s            

    def asizesof(self, *objs, **opts):
        '''Return the individual object sizes (with modified options).
        '''
        self.set(**opts)
        self.exclude_refs(*objs)  # skip refs to objs
        s, z = 0, self._sizer
        t = tuple([z(o, 0) for o in objs])
        for z in t:  # no sum(<generator_expression>) in Python 2.2
            s += z
        self._total += s  # accumulate
        return t

    def exclude_refs(self, *objs):
        '''Exclude any references to the specified objects from sizing.

           While any references to the given objects are excluded, the
           objects will be sized if specified as positional arguments
           in subsequent calls to methods  asizeof and  asizesof.
        '''
        if self._seen:
            for o in objs:
                i = id(o)
                if i not in self._seen:
                    self._seen[i] = 0
        else:
            self._seen = dict([(id(o), 0) for o in objs])

    def exclude_types(self, *objs):
        '''Exclude the specified object instances and types from sizing.

           All instances and types of the given objects are excluded,
           even objects specified as positional arguments in subsequent
           calls to methods  asizeof and  asizesof.
        '''
        for o in objs:
            for t in _keytuple(o):
                if t and t not in self._excl_d:
                    self._excl_d[t] = 0

    def print_profiles(self, w=0, **print3opts):
        '''Print the profiles.
        '''
         # get the profiles with non-zero size or count
        t = [(v, k) for k, v in _items(self._profs) if v.total > 0 or v.number > 1]
        if (len(self._profs) - len(t)) < 9:  # just show all
            t = [(v, k) for k, v in _items(self._profs)]
        if t:
            _printf('%s%*d profiles:  total, average, and largest flat size%s:  largest object',
                     linesep, w, len(t), self._incl, **print3opts)
            for v, k in _sorted(t, reverse=True):
                s  = 'object%(plural)s:  %(total)s, %(avg)s, %(high)s:  %(obj)s%(lengstr)s' % v.format(self._clip_)
                _printf('%*d %s %s', w, v.number, self._prepr(k), s, **print3opts)
            t = len(self._profs) - len(t)
            if t > 0:
                _printf('%+*d %r objects', w, t, 'zero', **print3opts)

    def print_stats(self, objs=(), sizes=(), stats=3, **opts):
        '''Print the statistics.
        '''
        s = min(stats, self._stats_)
        if s > 0:  # print stats
            w = 1 + len(str(self._total))
             # print header line(s)
            if sizes and objs:
                _printf('%sasizesof(..., %s) ...', linesep, _kwdstr(**opts))
                for z, o in zip(sizes, objs):
                    _printf('%*d bytes%s%s:  %s', w, z, _SI(z), self._incl, self._repr(o))
            else:
                t = c = ''  # title
                if objs:
                    t = self._repr(objs)
                    if opts:
                        c = ', '
                _printf('%sasizeof(%s%s%s) ...', linesep, t, c, _kwdstr(**opts))
             # print summary
            self.print_summary(w=w)
            if s > 1:  # print profile
                self.print_profiles(w=w)
                if s > 2:  # print typedefs
                    self.print_typedefs(w=w)

    def print_summary(self, w=0, **print3opts):
        '''Print the summary statistics.
        '''
        _printf('%*d bytes%s%s', w, self._total, _SI(self._total), self._incl, **print3opts)
        if self._mask:
            _printf('%*d byte aligned', w, self._mask + 1, **print3opts)
        _printf('%*d byte sizeof(void*)', w, _sizeof_Cvoidp, **print3opts)
        _printf('%*d objects sized', w, len(self._seen), **print3opts)
        if self._excl_d:
            t = 0  # no sum() in Python 2.2
            for v in _values(self._excl_d):
                t += v
            _printf('%*d objects excluded', w, t, **print3opts)
        t = 0  # no sum() in Python 2.2
        for v in _values(self._seen):
            t += v
        _printf('%*d objects seen', w, t, **print3opts)
        if self._depth > 0:
            _printf('%*d recursion depth', w,  self._depth, **print3opts)

    def print_typedefs(self, w=0, **print3opts):
        '''Print the types and dict tables.
        '''
        for k in _all_kinds:
             # XXX Python 3.0 doesn't sort type objects
            t = [(self._prepr(a), v) for a, v in _items(_typedefs) if v.kind == k and (v.both or self._code_)]
            if t:
                _printf('%s%*d %s types:  basicsize, itemsize, _len_(), _refs()',
                         linesep, w, len(t), k, **print3opts)
                for a, v in _sorted(t):
                    _printf('%*s %s:  %s', w, '', a, v, **print3opts)
         # dict and dict-like classes
        t = 0  # no sum() in Python 2.2
        for v in _values(_dict_classes):
            t += len(v)
        if t:
            _printf('%s%*d dict/-like classes:', linesep, w, t, **print3opts)
            for m, v in _items(_dict_classes):
                _printf('%*s %s:  %s', w, '', m, self._prepr(v), **print3opts)

    def set(self, code=None, limit=None, stats=None):
        '''Set some options.
        '''
        if code is not None:
            self._code_ = code
            if self._code_:  # incl. (byte)code
                self._incl = ' (incl. code)'
        if limit is not None:
            self._limit_ = limit
        if stats is not None:
            self._stats_ = stats
            if self._stats_ > 1:  # profile types
                self._profile = True
            else:
                self._profile = False

    def _get_total(self):
        '''Total size accumulated so far.
        '''
        return self._total
    total = property(_get_total, doc=_get_total.__doc__)

    def reset(self, align=8, all=None, clip=80, code=False, derive=False, infer=False, limit=100, stats=0):
        '''Reset options, state, etc.  The available
           options and default values are:

           .reset(align=8,      # size alignment
                  all=False,    # all current objects
                  clip=80,      # clip repr() strings
                  code=False,   # incl. (byte)code size
                  derive=False  # derive from super type
                  infer=False   # try to infer types
                  limit=100,    # recursion limit
                  stats=0)      # print statistics
        '''
         # options
        self._align_  = align
        self._all_    = all  # unused
        self._clip_   = clip
        self._code_   = code
        self._derive_ = derive
        self._infer_  = infer
        self._limit_  = limit
        self._stats_  = stats
         # clear state
        self._clear()
         # adjust
        if self._align_ > 1:
            self._mask = self._align_ - 1
            if (self._mask & self._align_) != 0:
                raise ValueError('asizeof invalid alignment: %r' % self._align_)
        self.set(code=code, stats=stats)


 # public functions

def adict(*classes):
    '''Install one or more classes to be handled as dict.
    '''
    a = True
    for c in classes:
         # if class is dict-like, add class
         # name to _dict_classes[module]
        if isclass(c) and _infer_dict(c):
            t = _dict_classes.get(c.__module__, ())
            if c.__name__ not in t:  # extend tuple
                _dict_classes[c.__module__] = t + (c.__name__,)
        else:  # not a dict-like class
            a = False
    return a  # all installed if True

_asizer = Asizer()

def asizeof(*objs, **opts):
    '''Return the combined size in bytes of all objects passed
       as positional argments using the following options.

       asizeof(obj, ..., align=8,      # size alignment
                         all=False,    # all current objects
                         clip=80,      # clip repr() strings
                         code=False,   # incl. (byte)code size
                         derive=False  # derive from super type
                         infer=False   # try to infer types
                         limit=100,    # recursion limit
                         stats=0)      # print statistics

       Set  align to a power of 2 to align sizes.  Any value less
       than 2 avoids size alignment.

       All current module, global and stack objects are sized if
       all is True and if no positional arguments are supplied.

       A positive  clip value truncates all repr() strings to at
       most  clip characters.

       The (byte)code size of callable objects like functions,
       methods, classes, etc. is included only if  code is True.

       If  derive is True, new types are handled like an existing
       (super) type provided there is one and only of those.

       If  infer is True, new types are inferred from attributes
       (only implemented for dict types on callable attributes
       as get, has_key, items, keys and values).

       Set  limit to a positive value to accumulate the sizes of
       the referents of each object, recursively up to the limit.
       Using  limit zero returns the sum of the flat** sizes of
       the given objects.

       A positive value for  stats prints up to 8 statistics, (1)
       a summary of the number of objects sized and seen, (2) a
       simple profile of the sized objects by type and (3+) up to
       6 tables showing the static, dynamic, derived, ignored,
       inferred and dict types used, found resp. installed.

       **) See this module documentation for the definition of
           flat size.
    '''
    if objs:  # size given objects
        t = objs
    elif opts.get('all', False) is True:  # size 'all' objects:
        t = (modules,                     # modules first
             globals(),                   # globals
             stack(getrecursionlimit()))  # stack
    else:
        return 0
    _asizer.reset(**opts)  # (align=8, all=False, clip=80, code=False, derive=False, infer=False, limit=100, stats=0)
    s = _asizer.asizeof(*t)
    _asizer.print_stats(objs, **opts)  # show opts as _kwdstr
    _asizer._clear()
    return s

def asizesof(*objs, **opts):
    '''Return a tuple containing the size in bytes of all objects
       passed as positional argments using the following options.

       asizesof(obj, ..., align=8,      # size alignment
                          clip=80,      # clip repr() strings
                          code=False,   # incl. (byte)code size
                          derive=False  # derive from super type
                          infer=False   # try to infer types
                          limit=100,    # recursion limit
                          stats=0)      # print statistics

       See function  asizeof() for a description of the options.

       The length of the returned tuple matches the number of
       given objects.
    '''
    if objs:
        pass
    elif opts.get('all', None):  # is not None and not False
        raise TypeError('asizesof invalid option: %s=%r' % ('all', opts['all']))
    else:
        return () # size given objects
    _asizer.reset(**opts)  # (align=8, clip=80, code=False, derive=False, infer=False, limit=100, stats=0)
    s = _asizer.asizesof(*objs)
    _asizer.print_stats(objs, sizes=s, **opts)  # show opts as _kwdstr
    _asizer._clear()
    return s

def flatsize(obj, code=False):
    '''Return the flat size of an object (in bytes).
    '''
    return asizeof(obj, align=0, code=code, limit=0, stats=0)

def _typedefof(obj, force, code=False, derive=False, infer=False):
    '''Get and install typedef for an object.
    '''
    k = _objkey(obj)
    v = _typedefs.get(k, None)
    if not v and force:
        _ = asizeof(obj, align=0, all=False, code=code, derive=derive, infer=infer, limit=0, stats=0)
        v = _typedefs.get(k, None)
    return v

def basicsize(obj, force=False, **opts):
    '''Return the basic size of an object (in bytes).

       None is returned if the object type is not defined.
       Use  force=True and possibly some other options to
       install the missing type definition.

       Valid options and default values are
           code=False    # include (byte)code size
           derive=False  # derive type from super type
           infer=False   # try to infer types
    '''
    v = _typedefof(obj, force, **opts)
    if v:
        v = v.base
    return v

def itemsize(obj, force=False, **opts):
    '''Return the item size of an object (in bytes).
       See function  basicsize for other details.
    '''
    v = _typedefof(obj, force, **opts)
    if v:
        v = v.item
    return v

def leng(obj, force=False, **opts):
    '''Return the length of an object (in items).
       See function  basicsize for other details.
    '''
    v = _typedefof(obj, force, **opts)
    if v:
        v = v.leng
        if v and _callable(v):
            v = v(obj)
    return v

def refs(obj, force=False, **opts):
    '''Return (a generator for) specific referents of an
       object.  See function  basicsize for other details.
    '''
    v = _typedefof(obj, force, **opts)
    if v:
        v = v.refs
        if v and _callable(v):
            v = v(obj)
    return v


if __name__ == '__main__':

    MAX = getrecursionlimit()

    def _print_asizeof(obj, infer=False, stats=0):
        a = [_repr(obj),]
        for d, c in ((0, False), (MAX, False), (MAX, True)):
            a.append(asizeof(obj, limit=d, code=c, infer=infer, stats=stats))
        _printf(" asizeof(%s) is %d, %d, %d", *a)

    def _print_functions(obj, name):
        _printf('%sfunctions for %s ...', linesep, name)
        _printf(' %s(): %s', 'basicsize', basicsize(obj))
        _printf(' %s(): %s', 'itemsize',  itemsize(obj))
        _printf(' %s(): %r', 'leng',      leng(obj))
        _printf(' %s(): %s', 'refs',     _repr(refs(obj)))
        _printf(' %s(): %s', 'flatsize',  flatsize(obj))

    def _bool(arg):
        a = arg.lower()
        if a in ('1', 't', 'y', 'true', 'yes', 'on'):
            return True
        elif a in ('0', 'f', 'n', 'false', 'no', 'off'):
            return False
        else:
            raise ValueError('bool option expected: %r' % arg)

    def _aopts(argv, **opts):
        '''Get argv options as typed values.
        '''
        while argv[1].startswith('-'):
            k = argv[1].lstrip('-')
            if k in opts:
                t = type(opts[k])
                if t is bool:
                    t = _bool
                opts[k] = t(argv.pop(2))
                argv.pop(1)
            else:
                raise NameError('invalid option: %s' % argv[1])
        return opts

    from sys import argv
    if len(argv) > 1:  # size modules given as args
        opts = _aopts(argv, align=8, all=False, clip=80, code=False, derive=False, limit=MAX, stats=0, type3=True)
        for m in argv[1:]:
            o = __import__(m)
            s = asizeof(o, **opts)
            _printf(" asizeof(%s) is %d", _repr(o, opts['clip']), s)

    else:
        t = [t for t in locals().items() if t[0].startswith('_sizeof_')]
        _printf('%s%d C sizes: (bytes)', linesep, len(t))
        for n, v in _sorted(t):
            _printf(' sizeof(%s): %r', n[len('_sizeof_'):], v)

        _printf('%s%d types: basic- and itemsize, kind:', linesep, len(_typedefs))
        for k, v in _sorted([(_prepr(k), v) for k, v in _items(_typedefs)]):  # [] for Python 2.2
            if v.both:
                c = ''
            else:
                c = ' (code only)'
            _printf(' %s: %d and %d, %s%s', k, v.base, v.item, v.kind, c)

        try:
            _L5d  = long(1) << 64
            _L17d = long(1) << 256
            t = '<int>/<long>'
        except NameError:
            _L5d  = 1 << 64
            _L17d = 1 << 256
            t = '<int>'

        _printf('%sasizeof(%s, align=%s, limit=%s) ...', linesep, t, 0, 0)
        for o in (1024, 1000000000,
                  MAX, 1 << 32, _L5d, -_L5d, _L17d, -_L17d):
            _printf(" asizeof(%s) is %s (%s + %s * %s)", _repr(o), asizeof(o, align=0, limit=0),
                                                         basicsize(o), leng(o), itemsize(o))

        class C: pass

        class D(dict):
            _attr1 = None
            _attr2 = None

        class E(D):
            def __init__(self, a1=1, a2=2):
                _attr1 = a1
                _attr2 = a2

        class P(object):
            _p = None
            def _get_p(self):
                return self._p
            p = property(_get_p)

        class S(object):
            __slots__ = ('a', 'b')

        class T(object):
            __slots__ = ('a', 'b')
            def __init__(self):
                self.a = self.b = 0

        _printf('%sasizeof(%s) for (limit, code) in %s ...', linesep, '<non-callable>', '((0, False), (MAX, False), (MAX, True))')
        for o in (None,
                  1.0, 1.0e100, 1024, 1000000000,
                  MAX, 1 << 32, _L5d, -_L5d, _L17d, -_L17d,
                  '', 'a', 'abcdefg',
                  {}, (), [],
                  C(), C.__dict__,
                  D(), D.__dict__,
                  E(), E.__dict__,
                  P(), P.__dict__, P.p,
                  S(), S.__dict__,
                  T(), T.__dict__,
                 _typedefs):
            _print_asizeof(o, infer=True)

        _printf('%sasizeof(%s) for (limit, code) in %s ...', linesep, '<callable>', '((0, False), (MAX, False), (MAX, True))')
        for o in (C, D, E, P, S, T,  # classes are callable
                  type,
                 _co_refs, _dict_refs, _inst_refs, _len_int, _seq_refs, lambda x: x,
                (_co_refs, _dict_refs, _inst_refs, _len_int, _seq_refs),
                 _typedefs):
            _print_asizeof(o)

        _printf('%sasizeof(%s) for (limit, code) in %s ...', linesep, '<Dicts>', '((0, False), (MAX, False), (MAX, True))')
        try:
            import UserDict  # no UserDict in 3.0
            for o in (UserDict.IterableUserDict(), UserDict.UserDict()):
                _print_asizeof(o)
        except ImportError:
            pass
        class _Dict(dict):
            pass
        for o in (dict(), _Dict(),
                  P.__dict__,  # dictproxy
                  Weakref.WeakKeyDictionary(), Weakref.WeakValueDictionary()):
            _print_asizeof(o)

        _printf('%sasizeof(%s, limit=%s, code=%s) ...', linesep, 'locals()', 'MAX', False)
        asizeof(locals(), limit=MAX, code=False, stats=1)
        _print_functions(locals(), 'locals()')

        _printf('%sasizeof(%s, limit=%s, code=%s) ...', linesep, 'globals()', 'MAX', False)
        asizeof(globals(), limit=MAX, code=False, stats=1)
        _print_functions(globals(), 'globals()')

        _printf('%sasizeof(limit=%s, code=%s, *%s) ...', linesep, 'MAX', False, 'sys.modules.values()')
        asizeof(limit=MAX, code=False, stats=1, *modules.values())
        _print_functions(modules, 'modules')

        _printf('%sasizeof(%s, limit=%s, code=%s) ...', linesep, 'stack(MAX)', 'MAX', False)
        asizeof(stack(MAX), limit=MAX, code=False, stats=1)
        _print_functions(stack(MAX), 'stack(MAX)')

        _printf('%sasizeof(limit=%s, code=%s, *%s) ...', linesep, 'MAX', False, 'gc.garbage')
        from gc import collect, garbage  # list()
        collect()
        asizeof(limit=MAX, code=False, stats=1, *garbage)

        _printf('%sasizeof(limit=%s, code=%s, %s) ...', linesep, 'MAX', True, 'all=True')
        asizeof(limit=MAX, code=True, stats=MAX, all=True)

        _printf('%sasizesof(%s, limit=%s, code=%s) ...', linesep, 'globals(), locals()', 'MAX', False)
        asizesof(globals(), locals(), limit=MAX, code=False, stats=1)


# License file from an earlier version of this source file follows:

#---------------------------------------------------------------------
#       Copyright (c) 2002-2008 -- ProphICy Semiconductor, Inc.
#                        All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
# 
# - Neither the name of ProphICy Semiconductor, Inc. nor the names
#   of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#---------------------------------------------------------------------


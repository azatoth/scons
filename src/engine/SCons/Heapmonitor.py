"""SCons.Heapmonitor

Facility to introspect memory consumption of certain classes and objects.
Tracked objects are sized recursively to provide an overview of memory
distribution between the different tracked objects.

"""

#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

#
# The meta programming techniques used to trace object construction requires
# nested scopes introduced in Python 2.2. For Python 2.1 compliance,
# nested_scopes are imported from __future__.
#
from __future__ import nested_scopes

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import sys
import time

import weakref
import new

import SCons.asizeof

# Dictionaries of TrackedObject objects associated with the actual objects that
# are tracked.
_tracked_classes = {}
_tracked_objects = {}
_footprint = []

# Keep objects alive by reference. Just for debugging purpose.
_keepalive = [] 

_constructors = {}


def _inject_constructor(klass, f, resolution_level):
    """
    Modifying Methods in Place - after the recipe 15.7 in the Python
    Cookbook by Ken Seehof. The original constructors may be restored later.
    Therefore, prevent constructor chaining by multiple calls with the same
    class.
    """
    if klass in _constructors.keys():
        return

    try:
        ki = klass.__init__
    except AttributeError:
        def ki(self, *args, **kwds):
            pass

    _constructors[klass] = ki
    klass.__init__ = new.instancemethod(
        lambda *args, **kwds: f(ki, resolution_level, *args, **kwds), None, klass)


def _restore_constructor(klass):
    """
    Restore the original constructor, lose track of class.
    """
    if _constructors.has_key(klass):
        klass.__init__ = _constructors[klass]
    else: # class is not tracked: TODO emit error
        pass


def _tracker(__init__, resolution_level, self, *args, **kwds):
    """
    Injected constructor for tracked classes.
    Call the actual constructor of the object and track the object.
    """
    __init__(self, *args, **kwds)
    track_object(self, resolution_level=resolution_level)


class TrackedObject(object):
    """
    Stores size and lifetime information of a tracked object. A weak reference is
    attached to monitor the object without preventing its deletion.
    """

    def __init__(self, instance):
        """
        Create a weak reference for 'instance' to observe an object but which
        won't prevent its deletion (which is monitored by the finalize
        callback). The size of the object is recorded in 'footprint' as 
        (timestamp, size) tuples.
        """
        self.ref = weakref.ref(instance, self.finalize)
        self.birth = time.time()
        self.death = None

        #initial_size = SCons.asizeof.basicsize(instance)
        initial_size = SCons.asizeof.basicsize(instance)
        if initial_size is None:
            initial_size = SCons.asizeof.asizeof(instance) # FIXME unbound size computation in the middle of creation

        self.footprint = [(self.birth, initial_size)]


    def track_size(self, sizer):
        """
        Store timestamp and current size for later evaluation.
        The 'sizer' is a stateful sizing facility that excludes other tracked
        objects.
        """
        obj = self.ref()
        self.footprint.append( (time.time(), sizer.asizeof(obj)) ) 


    def get_max_size(self):
        """
        Get the maximum of all sampled sizes, or return 0 if no samples were
        recorded.
        """
        try:
            return max([s for (t, s) in self.footprint])
        except ValueError:
            return 0

    
    def finalize(self, ref):
        """
        Mark the reference as dead and remember the timestamp.
        It would be great if we could measure the pre-destruction size. 
        Unfortunately, the object is gone by the time the weakref callback is called.
        However, weakref callbacks are useful to be informed when tracked objects die(d)
        without the need of destructors.
        """
        pass # TODO

        #self.death = gettime()
        #print self
        #self.mark_deletion()


def track_object(instance, name=None, resolution_level=0, keep=0):
    """
    Track object 'instance' and sample size and lifetime information.
    The 'resolution_level' is the recursion depth up to which referents are
    sized individually. Resolution level 0 (default) treats the object as an
    opaque entity, 1 sizes all direct referents individually, 2 also sizes the
    referents of the referents and so forth.
    To prevent the object's deletion a (strong) reference can be held with
    'keep'.
    """
    if resolution_level > 0:
        raise NotImplementedError

    if name is None:
        name = instance.__class__.__name__
    if not _tracked_classes.has_key(name):
        _tracked_classes[name] = []

    to = TrackedObject(instance)

    _tracked_classes[name].append(to)
    _tracked_objects[id(instance)] = to

    if keep:
        _keepalive.append(instance)


def track_class(cls, resolution_level=0):
    """
    Track all objects of the class 'cls'. Objects of that type that already
    exist are _not_ tracked.
    A constructor is injected to begin instance tracking on creation
    of the object. The constructor calls 'track_object' internally.
    """
    if resolution_level > 0:
        raise NotImplementedError

    _inject_constructor(cls, _tracker, resolution_level)


def lose_track_class(cls):
    """
    Stop tracking class 'cls'. Any new objects of that type are not tracked
    anymore. Existing objects are still tracked.
    """
    _restore_constructor(cls)
    

def create_snapshot():
    """
    Collect current per instance statistics.
    """
    #sizer = SCons.asizeof.Asizer()
    #sizer.norecurse(instance_ids=_tracked_objects.keys())
    sizer = SCons.asizeof.Asizer()
    objs = [to.ref() for to in _tracked_objects.values()]
    sizer.exclude_refs(*objs)
    for to in _tracked_objects.values():
        to.track_size(sizer)
    _footprint.append( (time.time(), sizer.total) )
    # overhead = sizer.asizeof(self) # compute actual profiling overhead


def find_garbage():
    """
    Let the garbage collector identify ref cycles and check against tracked
    objects.
    WARNING: Prototype implementation.
    """
    import gc
    gc.enable()
    gc.set_debug(gc.DEBUG_LEAK)
    gc.collect()
    for x in gc.garbage:
        # print str(x)
        if _tracked_objects.has_key(id(x)):
            print "WARNING: Tracked object is marked as garbage: %s" % repr(_tracked_objects[id(x)].ref())


def print_stats(file=sys.stdout):
    """
    Write tracked objects by class to stdout.
    """
    print "[ INFO ] Prototype: Do not take the reported values too seriously"
    pattern  = '  %-66s  %9d %s\n'
    pattern2 = '  %-34s %8d Alive  %8d Free    %9d %s\n'
    classlist = _tracked_classes.keys()
    classlist.sort()
    summary = []
    for classname in classlist:
        file.write('\n%s:\n' % classname)
        sum = 0
        dead = 0
        alive = 0
        for to in _tracked_classes[classname]:
            # size = SCons.asizeof.asizeof(obj)
            size = to.get_max_size()
            obj  = to.ref()
            sum += size
            if obj is not None:
                file.write(pattern % (repr(obj), size, 'Bytes'))
                alive += 1
            else:
                dead += 1
        #file.write(pattern2 % (classname,alive,dead,sum,'Bytes'))
        summary.append(pattern2 % (classname,alive,dead,sum,'Bytes'))
    try:
        total = max([s for (t, s) in _footprint])
    except ValueError:
        total = 0
    file.write('\n')
    for line in summary:
        file.write(line)
    file.write('\n')
    file.write(pattern % ('Total',total,'Bytes'))

    #SCons.asizeof.asizeof(all=True, stats=6)


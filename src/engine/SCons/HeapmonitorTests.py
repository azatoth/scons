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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import unittest
import TestCmd

from SCons.Heapmonitor import *

class Foo():
    def __init__(self):
        self.foo = 'foo'

class Bar(Foo):
    def __init__(self):
        Foo.__init__(self)
        self.bar = 'bar'

class FooNew(object):
    def __init__(self):
        self.foo = 'foo'

class BarNew(FooNew):
    def __init__(self):
        super(BarNew, self).__init__()


class TrackObjectTestCase(unittest.TestCase):

    def setUp(self):
        detach_all()

    def test_track_object(self):
        """Test object registration.
        """
        foo = Foo()
        bar = Bar()

        track_object(foo)
        track_object(bar)

        assert id(foo) in tracked_objects
        assert id(bar) in tracked_objects

        assert 'Foo' in tracked_index
        assert 'Bar' in tracked_index

        assert tracked_objects[id(foo)].ref() == foo
        assert tracked_objects[id(bar)].ref() == bar

    def test_track_by_name(self):
        """Test registering objects by name.
        """
        foo = Foo()

        track_object(foo, name='Foobar')

        assert 'Foobar' in tracked_index        
        assert tracked_index['Foobar'][0].ref() == foo

    def test_keep(self):
        """Test lifetime of tracked objects.
        """
        foo = Foo()
        bar = Bar()

        track_object(foo, keep=1)
        track_object(bar)
       
        idfoo = id(foo)
        idbar = id(bar)

        del foo
        del bar

        assert tracked_objects[idfoo].ref() is not None
        assert tracked_objects[idbar].ref() is None

    def future_test_recurse(self):
        """Test recursive sizing and saving of referents.
        """
        foo = Foo()
        bar = Bar()

        track_object(foo, recurse=1)

        # TODO
        

class TrackClassTestCase(unittest.TestCase):

    def setUp(self):
        detach_all()

    def test_track_class(self):
        """Test tracking objects through classes.
        """
        track_class(Foo)
        track_class(Bar)

        foo = Foo()
        bar = Bar()

        assert id(foo) in tracked_objects
        assert id(bar) in tracked_objects

    def test_track_class_new(self):
        """Test tracking new style classes.
        """
        track_class(FooNew)
        track_class(BarNew)

        foo = FooNew()
        bar = BarNew()

        assert id(foo) in tracked_objects
        assert id(bar) in tracked_objects

    def test_track_by_name(self):
        """Test registering objects by name.
        """
        track_class(Foo, name='Foobar')

        foo = Foo()

        assert 'Foobar' in tracked_index        
        assert tracked_index['Foobar'][0].ref() == foo

    def test_keep(self):
        """Test lifetime of tracked objects.
        """
        track_class(Foo, keep=1)
        track_class(Bar)

        foo = Foo()
        bar = Bar()
       
        idfoo = id(foo)
        idbar = id(bar)

        del foo
        del bar

        assert tracked_objects[idfoo].ref() is not None
        assert tracked_objects[idbar].ref() is None

    def test_detach(self):
        """Test detaching from tracked classes.
        """
        track_class(Foo)
        track_class(Bar)

        foo = Foo()
        bar = Bar()

        assert id(foo) in tracked_objects
        assert id(bar) in tracked_objects

        detach_class(Foo)
        detach_class(Bar)

        foo2 = Foo()
        bar2 = Bar()
    
        assert id(foo2) not in tracked_objects
        assert id(bar2) not in tracked_objects

        self.assertRaises(ValueError, detach_class, Foo)


if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [ TrackObjectTestCase,
                 TrackClassTestCase
                 # RecursionLevelTestCase,
               ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)

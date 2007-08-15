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

import os.path
import shutil
import sys
import unittest

from TestCmd import TestCmd

import SCons.CacheDir

class Action:
    pass

class Scanner:
    pass

class Environment:
    pass

class Builder:
    pass

class CacheDirTestCase(unittest.TestCase):
    def setUp(self):
        self.test = TestCmd(workdir='')

        import SCons.Node.FS
        self.fs = SCons.Node.FS.FS()

        self.fs.CacheDir('cache')
        self.cp = self.fs.CachePath

    def retrieve_succeed(self, target, source, env, execute=1):
        self.retrieved.append(target)
        return 0

    def retrieve_fail(self, target, source, env, execute=1):
        self.retrieved.append(target)
        return 1

    def push(self, target, source, env):
        self.pushed.append(target)
        return 0

    def test_CacheRetrieve(self):
        """Test the CacheRetrieve() function"""

        save_CacheRetrieve = SCons.CacheDir.CacheRetrieve
        self.retrieved = []

        f1 = self.fs.File("cd.f1")
        f1.builder_set(Builder())
        try:
            SCons.CacheDir.CacheRetrieve = self.retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f1.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f1], self.retrieved
            assert built_it is None, built_it

            SCons.CacheDir.CacheRetrieve = self.retrieve_fail
            self.retrieved = []
            built_it = None

            r = f1.retrieve_from_cache()
            assert not r, r
            assert self.retrieved == [f1], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.CacheDir.CacheRetrieve = save_CacheRetrieve

    def test_CacheRetrieveSilent(self):
        """Test the CacheRetrieveSilent() function"""

        save_CacheRetrieveSilent = SCons.CacheDir.CacheRetrieveSilent

        SCons.CacheDir.cache_show = 1

        f2 = self.fs.File("cd.f2")
        f2.binfo = f2.BuildInfo(f2)
        f2.binfo.ninfo.bsig = 'f2_bsig'
        f2.builder_set(Builder())
        try:
            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f2.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f2], self.retrieved
            assert built_it is None, built_it

            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_fail
            self.retrieved = []
            built_it = None

            r = f2.retrieve_from_cache()
            assert r is False, r
            assert self.retrieved == [f2], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.CacheDir.CacheRetrieveSilent = save_CacheRetrieveSilent

    def test_CachePush(self):
        """Test the CachePush() function"""

        save_CachePush = SCons.CacheDir.CachePush

        SCons.CacheDir.CachePush = self.push

        try:
            self.pushed = []

            cd_f3 = self.test.workpath("cd.f3")
            f3 = self.fs.File(cd_f3)
            f3.built()
            assert self.pushed == [], self.pushed
            self.test.write(cd_f3, "cd.f3\n")
            f3.built()
            assert self.pushed == [f3], self.pushed

            self.pushed = []

            cd_f4 = self.test.workpath("cd.f4")
            f4 = self.fs.File(cd_f4)
            f4.visited()
            assert self.pushed == [], self.pushed
            self.test.write(cd_f4, "cd.f4\n")
            f4.clear()
            f4.visited()
            assert self.pushed == [], self.pushed
            SCons.CacheDir.cache_force = 1
            f4.clear()
            f4.visited()
            assert self.pushed == [f4], self.pushed
        finally:
            SCons.CacheDir.CachePush = save_CachePush

    def test_cachepath(self):
        """Test the cachepath() method"""

        # Verify how the cachepath() method determines the name
        # of the file in cache.
        def my_collect(list):
            return list[0]
        save_collect = SCons.Sig.MD5.collect
        SCons.Sig.MD5.collect = my_collect

        try:
            f5 = self.fs.File("cd.f5")
            f5.binfo = f5.BuildInfo(f5)
            f5.binfo.ninfo.bsig = 'a_fake_bsig'
            result = self.cp.cachepath(f5)
            dirname = os.path.join('cache', 'A')
            filename = os.path.join(dirname, 'a_fake_bsig')
            assert result == (dirname, filename), result
        finally:
            SCons.Sig.MD5.collect = save_collect

    def test_no_bsig(self):
        """Test that no bsig raises an InternalError"""

        f6 = self.fs.File("cd.f6")
        f6.binfo = f6.BuildInfo(f6)
        exc_caught = 0
        try:
            cp = self.cp.cachepath(f6)
        except SCons.Errors.InternalError:
            exc_caught = 1
        assert exc_caught

    def test_xxx(self):
        """Test raising a warning if we can't copy a file to cache."""

        test = TestCmd(workdir='')

        save_copy2 = shutil.copy2
        def copy2(src, dst):
            raise OSError
        shutil.copy2 = copy2
        save_mkdir = os.mkdir
        def mkdir(dir, mode=0):
            pass
        os.mkdir = mkdir
        old_warn_exceptions = SCons.Warnings.warningAsException(1)
        SCons.Warnings.enableWarningClass(SCons.Warnings.CacheWriteErrorWarning)

        try:
            cd_f7 = self.test.workpath("cd.f7")
            self.test.write(cd_f7, "cd.f7\n")
            f7 = self.fs.File(cd_f7)
            f7.binfo = f7.BuildInfo(f7)
            f7.binfo.ninfo.bsig = 'f7_bsig'

            warn_caught = 0
            try:
                f7.built()
            except SCons.Warnings.CacheWriteErrorWarning:
                warn_caught = 1
            assert warn_caught
        finally:
            shutil.copy2 = save_copy2
            os.mkdir = save_mkdir
            SCons.Warnings.warningAsException(old_warn_exceptions)
            SCons.Warnings.suppressWarningClass(SCons.Warnings.CacheWriteErrorWarning)

    def test_no_strfunction(self):
        """Test handling no strfunction() for an action."""

        save_CacheRetrieveSilent = SCons.CacheDir.CacheRetrieveSilent

        act = Action()
        act.strfunction = None
        f8 = self.fs.File("cd.f8")
        f8.binfo = f8.BuildInfo(f8)
        f8.binfo.ninfo.bsig = 'f8_bsig'
        f8.builder_set(Builder())
        try:
            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_succeed
            self.retrieved = []
            built_it = None

            r = f8.retrieve_from_cache()
            assert r == 1, r
            assert self.retrieved == [f8], self.retrieved
            assert built_it is None, built_it

            SCons.CacheDir.CacheRetrieveSilent = self.retrieve_fail
            self.retrieved = []
            built_it = None

            r = f8.retrieve_from_cache()
            assert r is False, r
            assert self.retrieved == [f8], self.retrieved
            assert built_it is None, built_it
        finally:
            SCons.CacheDir.CacheRetrieveSilent = save_CacheRetrieveSilent

if __name__ == "__main__":
    suite = unittest.TestSuite()
    tclasses = [
        CacheDirTestCase,
    ]
    for tclass in tclasses:
        names = unittest.getTestCaseNames(tclass, 'test_')
        suite.addTests(map(tclass, names))
    if not unittest.TextTestRunner().run(suite).wasSuccessful():
        sys.exit(1)

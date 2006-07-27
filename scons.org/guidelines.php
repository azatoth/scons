<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("Developer's Guidelines", "guidelines");
?>

<div id="bodycontent">
<h2> SCons Developer's Guidelines </h2>

<center>22 May 2006</center>
<ol class="upper-roman">
<li>
General

<p>
<ol class="decimal">
<li>
All SCons software (SCons itself, tests, supporting utilities) will be
written to work with Python version 1.5.2.
</li>
<li>
SCons will be tested against Python versions 1.5.2 and some version of 2.x.
</li>
<li>
The SCons distribution will be generated
by the <code>distutils</code> package.
</li>
<li>
SCons will not require installation of any additional Python modules or
packages.  All modules or packages used by SCons must either be part of
the standard Python 1.5.2 release or be part of the SCons distribution.
</li>
<li>
SCons installation will be atomic, and will install all necessary
non-standard modules and/or packages.
</li>
<li>
At a minimum, SCons will be tested on Linux and Windows XP.  We will add
other platforms as they become available.  All tests must be written
portably.
</li>
<li>
SCons software will be written to a separately-defined set of
conventions (variable naming, class naming, etc.).  We won't be dogmatic
about these, and will use discretion when deciding whether a naming
violation is significant enough to require a fix.
</li>
<li>
SCons is being developed using the Aegis change management system
to control the development process and manage test creation and
maintenance.
</li>
<li>
A public CVS copy of the source tree is maintained at SourceForge for
archival purposes, for public availability, and to support read-only
CVS development for developers who can't (or really prefer not to) use
Aegis.
</li>
<li>
SCons infrastructure module tests are written using PyUnit.
</li>
<li>
Tests of SCons packaging are written using subclasses of the
TestCmd.py module.
</li>
<li>
Tests of full SCons script functionality are written using subclasses
of the TestCmd.py module.
</li>
</ol>
</p>
</li>



<li>
Development philosophy

<p>
In a word (x3):  Testing, testing, testing.
</p>
<p>
We're growing a rich set of regression tests incrementally, while
SCons is being developed.  The goal is to produce an exceptionally
stable, reliable tool of known, verifiable quality right from the
start.
</p>
<p>
A strong set of tests allows us to guarantee that everything works
properly even when we have to refactor internal subsystems, which we
expect to have to do fairly often as SCons grows and develops.  It's
also great positive feedback in the development cycle to make a change,
see the test(s) work, make another change, see the test(s) work...
</p>
</li>



<li>
Testing methodology
<p>
The specific testing rules we're using for SCons are as follows:
</p>
<ol class="decimal">
	<li>
        Every functional change must have one or more new tests, or
        modify one or more existing tests.
	</li>
	<li>
        The new or modified test(s) must pass when run against your new
        code (of course).
	</li>
	<li>
	The new code must also pass all unmodified, checked-in tests
	(regression tests).
	</li>
	<li>
        The new or modified test(s) must fail when run against the
        currently checked-in code.  This verifies that your new or
        modified test does, in fact, test what you intend it to.  If
        it doesn't, then either there's a bug in your test, or you're
        writing code that duplicates functionality that already exists.
	</li>
	<li>
        Changes that don't affect functionality (documentation changes,
        code cleanup, adding a new test for existing functionality,
        etc.) can relax these restrictions as appropriate.
	</li>
</ol>
<p>
These rules are taken from the Aegis change management system, which is
being used behind the scenes to manage the SCons development process.
</p>
<p>
The SCons testing infrastructure is largely in place, and is intended
to make writing tests as easy and painless as possible.  We will change
the infrastructure as needed to continue to make testing even easier, so
long as it still does the job.
</p>
<p>
SCons development uses three (!) testing harnesses, one for unit tests,
one for end-to-end functional tests, and one for test execution:
</p>
<ul>
	<li>
        The infrastructure modules (under the <code>src/scons</code>
	subdirectory) all have individual unit tests that use PyUnit.
	The naming convention is to append <code>"Tests"</code> to the
	module name.  For example, the unit tests for the
	<code>src/scons/Foo.py</code> module can be
        found in the <code>src/scons/FooTests.py</code> file.
	</li>
	<li>
        The packaging is tested by test scripts
        that live in the <code>src/</code> subdirectory
        and use a prefix of <code>"test_"</code>.
	</li>
	<li>
        The scons utility itself is tested by end-to-end tests that
        live in the <code>test/</code> subdirectory and which use the
	TestCmd.py infrastructure.
	</li>
        <li>
        Execution of these tests will be handled by the
        <a href="http://www.codesourcery.com/qmtest/">QMTest</a>
        infrastructure, as wrapped by an execution script.
        <strong>Note:</strong>  The transition to using
        QMTest is still in progress.  The wrapper execution script
        currently executes the test scripts directly.
        </li>
</ul>
<p>
The end-to-end tests in the <code>test/</code> subdirectory are
not substitutes for module unit tests.  If you modify a module
under the <code>src/scons/</code> subdirectory, you generally
<emphasis>must</emphasis>modify its <code>*Tests.py</code> script to
validate your change.  This can be (and probably should be) in addition to
a <code>test/*</code> test of how the modification affects the end-to-end
workings of SCons.
</p>
</li>



<li>
General developer requirements
<p>
<ol class="decimal">
<li>
All project developers must subscribe to the dev@scons.tigris.org
mailing list.
</li>
<li>
All project developers must register at Tigris.org and be added to the
SCons developer list, so that the number of active developers can be
accurately represented on the SCons project page.
</li>
<li>
We will accept patches from developers not actually registered on
the project, so long as the patches conform to our normal requirements.
</li>
</ol>
</p>
</li>



<li>
Using Aegis for SCons development
<p>
<ol class="decimal">
<li>
The main line of SCons development will be under the control of the
Aegis change management system, as administered by Knight on his system.
</li>
<li>
We will use <code>aedist</code> to generate change sets for each change
checked in to the main Aegis repository.  These change sets will be
either distributed by a mailing list or made available via the web, or both.
</li>
<li>
Remote developers using Aegis will send <code>aedist</code> output for
their changes to Knight for review and integration.
</li>
<li>
The <code>aedist</code> output should be sent to Knight
after the change has completed its local <code>aede</code>,
but before <code>aerpass</code>.
</li>
<li>
If the change is rejected, the developer can <code>aedeu</code>
to reopen the change and fix whatever problems
caused the review to not pass.
</li>
<li>
A baseline snapshot <code>(aedist -bl)</code> of the main Aegis
repository will be generated at least daily and placed on the
SCons web site to provide a central location for synchronizing
remote Aegis repositories.
</li>
<li>
Changes to the main Aegis repository will also be propagated
automatically to the Tigris.org and SourceForge CVS repositories.
</li>
</ol>
</p>
</li>



<li>
Using Subversion for SCons development
<p>
<ol class="decimal">
<li>
Developers using CVS may, but need not,
be registered as Tigris.org or SourceForge developers.
</li>
<li>
Remote developers using CVS will send patches (cvs -diff output)
to Knight for integration into the main Aegis repository.  This allows
anonymous CVS access to be used for SCons development by developers who
aren't registered at Tigris.org or SourceForge.
</li>
<li>
Tigris.org- and SourceForge-registered developers using CVS
must not check in their
changes directly to either CVS repository.
Any such changes will be overwritten by
future automatic changes from the main Aegis repository.
</li>
</ol>
</p>
</li>
</ol>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>

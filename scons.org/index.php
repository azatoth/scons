<?
	include "includes/templates.php";
        include "includes/versions.php";

	error_reporting(E_ALL);

	make_top("A software construction tool", "home");

	$downloadpage = "http://prdownloads.sourceforge.net/scons";
	$listpage = "http://scons.tigris.org/servlets/SummarizeList";
?>

<div id="bodycontent">
<h2 class="pagetitle"> Latest News </h2>

<h3>SCons awarded Google Summer of Code project</h3>
<div class="date">24 May 2006</div>
<div class="newsitem">
Google's <a href="http://code.google.com/soc/">Summer of Code</a>
will fund a
<a href="http://www.scons.org/wiki/PhilippSchollProposal">project</a>
proposed by Philipp Scholl
to add support for packaging and release dependencies to SCons.
Stefan Seefeld will be mentoring Philipp's proposal for
the next several months.
Congratulations to Philipp,
and thanks to Stefan for mentoring.
</div>

<h3>Tracking of SCons bug reports, patches and feature requests
has moved to <a href="http://www.tigris.org">tigris.org</a>.</h3>
<div class="date">21 May 2006</div>
<div class="newsitem">
After five years of tracking bug reports, patches and feature requests
at our <a href="http://sourceforge.net/projects/scons/">SourceForge project page</a>,
we've converted them all to our project
<a href="http://scons.tigris.org/servlets/ProjectIssues">Issue Tracker</a>
at
<a href="http://www.tigris.org">tigris.org</a>.
The goal is for this to provide improved management of work on the project.
Many thanks to Greg Noel and Kevin Maples for making this happen.
</div>

<p>
<strong>27 April 2006:</strong>
SCons has been accepted as a Google
<a href="http://code.google.com/soc/">Summer of Code</a> project.
Check out the
<a href="http://www.scons.org/cgi-sys/cgiwrap/scons/moin.cgi/SummerOfCodeIdeas">list of project ideas</a>
over at the SCons
<a href="http://www.scons.org/wiki/">wiki</a>.
</p>

<h3> SCons 0.96.92 (testing pre-release for 0.97) is available </h3>
<div class="date">10 April 2006</div>
<div class="newsitem">
Another testing pre-release has been made available.
This is intended as the last testing pre-release before
the .sconsign file changes significantly
to (among other things)
handle builds consistently
when only a subset of a tree's
dependency graph is used,
as well as
supporting more flexible detection of file changes.
This pre-release
also makes available more features and bug fixes
that have accumulated since 0.96.91.
Download it directly from the
<a href="http://sourceforge.net/project/showfiles.php?group_id=30337">download page</a>
at SourceForge.
</div>

<div class="quote">
<div class="quotetext">
"Doom3's Linux build system uses SCons. <tt>CC="ccache distcc g++-3.3"
JOBS=8</tt> rocks!"
</div>
<div class="quoteauthor">&mdash;Timothee Besset, <a
href="http://www.idsoftware.com">id Software</a></div>
</div>

<h2> What is SCons?</h2>

SCons is an Open Source software construction tool&mdash;that is, a
next-generation build tool. Think of SCons as an improved, cross-platform
substitute for the classic <tt>Make</tt>
utility with integrated functionality similar
to <tt>autoconf/automake</tt> and compiler caches such as <tt>ccache</tt>.
In short, SCons is an
easier, more reliable and faster way to build software. 

<div class="quote">
<div class="quotetext">
"<span class="sconslogo">SCons</span> is a fantastic build system, written in Python (1.5.2) that does lots of nice things like automated dependencies, cross platform operation, configuration, and other great stuff. I would have to say that it is probably going to be the best thing for building C/C++ projects in the near future." 
</div>
<div class="quoteauthor">&mdash; Zed A. Shaw, Bombyx project lead </div>
</div>

<h2> What makes SCons better? </h2>

<ul>
<li>Configuration files are Python scripts--use the power of a real programming language to solve build problems.</li>
<li>Reliable, automatic dependency analysis built-in for C, C++ and Fortran--no more <tt>"make depend"</tt> or <tt>"make clean"</tt> to get all of the dependencies.  Dependency analysis is easily extensible through user-defined dependency Scanners for other languages or file types.</li>
<li>Built-in support for C, C++, D, Java, Fortran, Yacc, Lex, Qt and SWIG, and building TeX and LaTeX documents.  Easily extensible through user-defined Builders for other languages or file types.</li>
<li>Building from central repositories of source code and/or pre-built targets.</li>
<li>Built-in support for fetching source files from SCCS, RCS, CVS, BitKeeper and Perforce.</li>
<li>Built-in support for Microsoft Visual Studio .NET and past Visual Studio versions, including generation of <tt>.dsp</tt>, <tt>.dsw</tt>, <tt>.sln</tt> and <tt>.vcproj</tt> files.</li>
<li>Reliable detection of build changes using MD5 signatures; optional, configurable support for traditional timestamps.</li>
<li>Improved support for parallel builds--like <tt>make -j</tt> but keeps N jobs running simultaneously regardless of directory hierarchy.</li>
<li>Integrated <tt>Autoconf</tt>-like support for finding <tt>#include</tt> files, libraries, functions and typedefs.</li>
<li>Global view of <i>all</i> dependencies--no more multiple build passes or reordering targets to build everything.</li>
<li>Ability to share built files in a cache to speed up multiple builds--like <tt>ccache</tt> but for any type of target file, not just C/C++ compilation.</li>
<li>Designed from the ground up for cross-platform builds, and known to work on Linux, other POSIX systems (including AIX, *BSD systems, HP/UX, IRIX and Solaris), Windows NT, Mac OS X, and OS/2.</li>
</ul>

<p>
("So why the beta status if it's stable?" I hear you ask. Until recently, we
were still tweaking corners of the interface as we found ways to make building
software even easier. We're on track for an official
1.0 production release in the near future. Regardless of status, every release
of SCons goes out only if it passes all of our tests on multiple platforms.)
</p>

<div class="quote">
<div class="quotetext">
"We are using [SCons] on Windows (MSVC and Intel compilers), Linux, IRIX and
Mac OS X (gcc and two versions of CodeWarrior). Handles all of those with ease.
It can do things like properly handle dependencies on auto-generated source and
header files, which would be a nightmare in make." 
</div>
<div class="quoteauthor">&mdash;SilentTristero (Slashdot user), 10 July 2003 post</div>
</div>

<h2>Where did SCons come from?</h2>

<p> <span class="sconslogo">SCons</span> began life as the <i>ScCons</i> build
tool design which won the <a
href="http://software-carpentry.codesourcery.com/">Software Carpentry</a> SC
Build competition in August 2000.  That design was in turn based on the <a
href="http://www.dsmit.com/cons/">Cons</a> software construction utility.  This
project has been renamed <span class="sconslogo">SCons</span> to reflect that
it is no longer directly connected with Software Carpentry (well, that, and to
make it slightly easier to type...).  </p>

</div> <!-- End bodycontent -->

<?
	make_bottom();
?>

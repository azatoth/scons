<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("Development", "dev");
?>

<div id="bodycontent">
<h2> Development </h2>

<p> <span class="sconslogo">SCons</span> is actively looking for developers.
If you're interested, we'd love to hear from you at <a
href="mailto:dev@scons.tigris.org">dev@scons.tigris.org</a>.  </p>

<p> It's only fair that you get an idea of how we develop <span
class="sconslogo">SCons</span> before deciding if you'd like to help.  There is
a complete and evolving set of <a href="guidelines.php">Developer's
Guidelines</a> that go into reasonable detail about how we're guaranteeing that
<span class="sconslogo">SCons</span> is always an exceptionally stable and
reliable tool for building software.  Here are the key points: </p>

<ul>
<li>We write a lot of automated tests to test the daylights out of <span
class="sconslogo">SCons</span>.
Lines of test code currently outnumber lines of code in SCons itself
by more than 2.5 to one.
<li>We use the Aegis change management system to control the development and
testing process.
<li>You can still use Subversion or CVS as a front end
for submitting patches.
</ul>

</p>
Please take a look at the complete guidelines
before deciding to hop on board.
</p>

<p>
That said, here are resources for <span class="sconslogo">SCons</span> developers
(or onlookers):
</p>

<div class="link">
<div class="linkname">
<a href="guidelines.php">Developer's&nbsp;Guidelines</a>
</div>
<div class="linkdesc">
The complete statement of guiding principles and procedures
for <span class="sconslogo">SCons</span> development.
Subject to change and improvement.
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://scons.tigris.org">Project&nbsp;Page</a>
</div>
<div class="linkdesc">
The <span class="sconslogo">SCons</span> project page at
<a href="http://www.tigris.org">Tigris.org</a>.
This is the center of active SCons development,
hosting the main source code repository
and issue tracker (bugs, patches, tasks, etc.).
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://sourceforge.net/projects/scons/">Project&nbsp;Page</a>
</div>
<div class="linkdesc">
The <span class="sconslogo">SCons</span> project page at
<a href="http://sourceforge.net">SourceForge</a>.
This is where we used to development, but no longer.
It's now mostly of historic interest,
although it's also the origination site for downloads.
</div>
</div>

<div class="link">
<div class="linkname">
Archive of the latest checked-in source in
<a href="ftp://ftp.scons.org/scons-src-latest.tar.gz">.tar.gz</a>
or
<a href="ftp://ftp.scons.org/scons-src-latest.tar.zip">.zip</a>
</div>
<div class="linkdesc">
The whole source tree in easy-to-download form.
Updated whenever a change is made to <span class="sconslogo">SCons</span>.
(Note that the source tree in these archives
is mostly for packaging and testing of SCons;
consult the <tt>README</tt> file for
information about how to build packages and
install SCons from the source tree.
It's <emphasis>not</emphasis> handled by
executing <tt>python setup.py</tt> directly
from this package.)
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://scons.tigris.org/source/browse/scons/">Subversion&nbsp;repository</a></td>
</div>
<div class="linkdesc">
The browsable Subversion repository at
<a href="http://www.tigris.org">Tigris.org</a>.
Most active development is carried out on subsidiary
<tt>branches/</tt>.
The <tt>trunk/</tt> contains whatever approved changes
have been promoted from the
See the 
<a href="http://scons.tigris.org/branching.html">Branching</a></td>
page at our tigris.org project page
for a description of the different
branches
and how we handle branch management.
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://scons.cvs.sourceforge.net/scons/">CVS&nbsp;repository</a></td>
</div>
<div class="linkdesc">
The browsable CVS repository at
<a href="http://sourceforge.net">SourceForge</a>.
Updated whenever a change is made to <span class="sconslogo">SCons</span>.
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://sc-archive.codesourcery.com/entries/build/ScCons/ScCons.html">ScCons design documents</a>
</div>
<div class="linkdesc">
The original design, from the
<a href="http://software-carpentry.codesourcery.com/">Software Carpentry</a>
build tool contest,
on which <span class="sconslogo">SCons</span> itself was based.
This is now of more interest as an historical document,
since the current design has changed significantly
as we figured out how to make things easier.
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://aegis.sourceforge.net/cgi-bin/aeget">Aegis&nbsp;repository</a>
</div>
<div class="linkdesc">
The browsable Aegis repository at
<a href="http://sourceforge.net">SourceForge</a>,
with listing service provided by Peter Miller, the author of Aegis.
Click through to the <emphasis>scons</emphasis>
project and branches to get a view of what's going on
with <span class="sconslogo">SCons</span> development.
Updated whenever a change is made to <span class="sconslogo">SCons</span>.
</div>
</div>

<div class="link">
<div class="linkname">
<a href="ftp://ftp.scons.org/scons.ae">Current&nbsp;aedist&nbsp;baseline</a>
</div>
<div class="linkdesc">
The Aegis snapshot of the current <span
class="sconslogo">SCons</span> baseline.
Updated whenever a change is made to <span class="sconslogo">SCons</span>.
</div>
</div>

<div class="link">
<div class="linkname">
<a href="http://www.pcug.org.au/~millerp/aegis/aegis.html">Aegis</a>
</div>
<div class="linkdesc">
The Aegis home page.
</div>
</div>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>

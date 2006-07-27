<?
	include "includes/templates.php";
	include "includes/versions.php";

	error_reporting(E_ALL);

	make_top("Documentation", "docs");

	$downloadpage = "http://prdownloads.sourceforge.net/scons";
	$listpage = "http://scons.tigris.org/servlets/SummarizeList";
?>

<div id="bodycontent">
<h2 class="pagetitle"> Documentation </h2>

<p>
This page contains links to general SCons documentation,
and to documentation (man page and User's Guide)
for the current stable release of SCons:  <?echo $currentrelease;?>.
Man pages and User's Guides for other releases
of SCons are available at the
<a href="docversions.php">Version-Specific SCons Documentation</a>
page.
</p>


<h3> SCons <?echo $currentrelease;?> man page </h3>
<p>
The man page for the current stable release of
<span class="sconslogo">SCons</span>.
We're meticulous about updating the man page
whenever new functionality is added or something changes,
so this covers everything that the current
version of <span class="sconslogo">SCons</span>
can do (modulo oversights).
</p>

<ul>
<li><a href="doc/production/HTML/scons-man.html">HTML</a></li>
<li><a href="doc/production/PS/scons-man.ps">PostScript</a></li>
<li><a href="doc/production/TEXT/scons-man.txt">Plain text</a></li>
</ul>


<h3> SCons <?echo $currentrelease;?> User Guide </h3>

<p>
The User's Guide for the current stable release of
<span class="sconslogo">SCons</span>.
<b>This is very much a work in progress.</b> This covers the basics,
but there is a lot in <span class="sconslogo">SCons</span> that hasn't been
covered yet in this Guide,
so check the man page before assuming that
<span class="sconslogo">SCons</span> can't do something
you don't find covered here.
Please help improve this document by letting the
<span class="sconslogo">SCons</span> maintainers know about anything you find
that's incorrect, or about missing pieces in which you're especially interested
(or to which you can contribute yourself).</p>

<ul>
<li><a href="doc/production/HTML/scons-user.html">HTML (single page)</a></li>
<li><a href="doc/production/HTML/scons-user/book1.html">HTML (multiple pages)</a></li>
<li><a href="doc/production/PDF/scons-user.pdf">PDF</a></li>
<li><a href="doc/production/PS/scons-user.ps">PostScript</a></li>
<li><a href="doc/production/TEXT/scons-user.txt">Plain text</a></li>
</ul>

<h3> SCons Design </h3>

The ongoing <span class="sconslogo">SCons</span> design document,
based largely on the
<a href="http://software-carpentry.codesourcery.com/entries/second-round/build/ScCons/">ScCons design</a>
from the second round of the
<a href="http://software-carpentry.codesourcery.com/">Software Carpentry</a>
contest.
<b>This is out of date at the moment</b>, and needs to be updated
for the changes made to the <span class="sconslogo">SCons</span> interface
during alpha development.

<ul>
<li><a href="doc/production/HTML/scons-design/book1.html">HTML</a></li>
<li><a href="doc/production/PDF/scons-design.pdf">PDF</a></li>
<li><a href="doc/production/PS/scons-design.ps">PostScript</a></li>
</ul>

<h3>SCons Design and Implementation</h3>
The paper about <span class="sconslogo">SCons</span> presented at the Python 10 conference
in February 2002, a nominee for the best paper award at the conference.
<ul>
<li><a href="doc/production/HTML/scons-python10/t1.html">HTML</a></li>
<li><a href="doc/production/PS/scons-python10.ps">PostScript</a></li>
</ul>

<p>
Please subscribe to the low-volume <a
href="mailto:announce-subscribe@scons.tigris.org">announce@scons.tigris.org</a>
mailing list to receive news and announcements about new documentation.
</p>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>

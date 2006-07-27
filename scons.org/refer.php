<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("References", "references");
?>

<div id="bodycontent">
<h2 class="pagetitle"> References </h2>

There are lots of people
and projects using
<span class="sconslogo">SCons</span>;
here's what some of them have to say about it.

<?

include "refer-raw.xhtml";

?>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>

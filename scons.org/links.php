<?
	include "includes/templates.php";

	error_reporting(E_ALL);

	make_top("Links", "links");
?>

<div id="bodycontent">
<h2 class="pagetitle"> Links </h2>

<?

include "links-raw.xhtml";

?>

</div> <!-- End bodycontent -->
<?
	make_bottom();
?>

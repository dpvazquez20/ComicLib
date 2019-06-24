/* JS USED IN COLLECTION PAGES (/templates/collection) */


// Activate the selectpickers
$(document).ready(function(){
	$('.selectpicker').selectpicker({
		// Text showed when no matches were found (it uses a language string used as the select (search) id
		noneResultsText: document.getElementsByName("search").item(0).getAttribute("id"),
	});
});


// Show toasts
$(function () {
  	var toast = document.getElementById("toast");
	if (toast !== null) {
		$('.toast').toast('show');
	}
	toast = null
});

// Activate tooltips in the management buttons and toast messages
$(function () {
  	$('[data-toggle="tooltip"]').tooltip();
	$('.toast').toast();
});

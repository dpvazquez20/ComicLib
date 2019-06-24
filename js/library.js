/* JS USED IN COLLECTION PAGES (/templates/comics) */


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


// Validate the shelving name field in the shelving add form
function validate_shelving_name(){
	// Variable that allows or not the submit of the form
	var submit = true;

	// Check if there is some shelving name
	var name = $('#add_form #name').val();
	if (name === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("name").className = "form-control is-invalid";
		submit = false;
	} else {
		document.getElementById("name").className = "form-control is-valid";
	}
	name = null;

	// Color the picture input
	document.getElementById("picture").className = "form-control is-valid";

	return submit;
}


// Validate the shelving select in the move comic form
function check_shelving(){
	// Variable that allows or not the submit of the form
	var submit = true;

	// Check if there is some shelving selected
	var shelving = $('#move_form #shelving_key').val();
	if (shelving === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("shelving_key").className = "form-control is-invalid";
		submit = false;
	} else {
		document.getElementById("shelving_key").className = "form-control is-valid";
	}
	shelving = null;

	return submit;
}
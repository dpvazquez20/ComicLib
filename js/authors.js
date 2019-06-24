/* JS USED IN AUTHORS PAGES (/templates/authors) */


// Activate the selectpickers
$(document).ready(function(){
	$('.selectpicker').selectpicker({
		// Text showed when no matches were found (it uses a language string used as the select (search) id
		noneResultsText: document.getElementsByName("search").item(0).getAttribute("id"),
	});
});


// Activate tooltips in the management buttons
$(function () {
  	$('[data-toggle="tooltip"]').tooltip()
});


// Validate the author name field in the author add form
function validate_author_name(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if there is some author name
	var name = $('#add_form #add_name').val();
	if (name === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("add_name").className = "form-control is-invalid";
		submit = false;
	} else {
		document.getElementById("add_name").className = "form-control";
	}
	name = null;

	return submit;
}
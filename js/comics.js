/* JS USED IN COMICS PAGES (/templates/comics) */


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


// Validate the fields in the add form
function validate_fields(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if the isbn exists and if its length is 13 characters
	var isbn = $('#add_form #isbn').val();
	if (isbn !== "") {				// If the isbn exists, checks the length
		if (isbn.length !== 13) {	// If the length isn't 13 characters show an error message and ban the submit of the form
			document.getElementById("isbn").className = "form-control is-invalid";
		} else {
			document.getElementById("isbn").className = "form-control";
		}
	}
	isbn = null;

	// Check if there is some title
	var title = $('#add_form #title').val();
	if (title === "") {			// If there isn't shows an error message and ban the submit of the form
		document.getElementById("title").className = "form-control is-invalid";
		submit = false;
	} else {
		document.getElementById("title").className = "form-control";
	}
	title = null;

	// Check if there is some edition and if its above 0
	var edition = $('#add_form #edition').val();
	if (edition !== "") {
		if (edition <= 0){
			document.getElementById("edition").className = "form-control is-invalid";
			submit = false;
		} else {
			document.getElementById("edition").className = "form-control";
		}
	}
	edition = null;

	// Check if there is some type
	var type = $('#add_form #type').val();
	if (type === "" || type === null) {			// If there isn't shows an error message and ban the submit of the form
		document.getElementById("type").className = "custom-select is-invalid";
		submit = false;
	} else {
		document.getElementById("type").className = "custom-select";
	}
	type = null;

	// Check if there is some value and if its above or equal 0
	var value = $('#add_form #value').val();
	if (value !== "") {
		if (Math.round(value.toNumber() * 100) < 0 || value.includes(".")){
			document.getElementById("value").className = "form-control is-invalid";
			submit = false;
		} else {
			document.getElementById("value").className = "form-control";
		}
	}
	value = null;

	return submit;
}


// Validate the fields in the modify form
function validate_fields2(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if the isbn exists and if its length is 13 characters
	var isbn = $('#modify_form #m_isbn').val();
	if (isbn !== "") {				// If the isbn exists, checks the length
		if (isbn.length !== 13) {	// If the length isn't 13 characters show an error message and ban the submit of the form
			document.getElementById("m_isbn").className = "form-control is-invalid";
		} else {
			document.getElementById("m_isbn").className = "form-control";
		}
	}
	isbn = null;

	// Check if there is some edition and if its above 0
	var edition = $('#modify_form #m_edition').val();
	if (edition !== "") {
		if (edition <= 0){
			document.getElementById("m_edition").className = "form-control is-invalid";
			submit = false;
		} else {
			document.getElementById("m_edition").className = "form-control";
		}
	}
	edition = null;

	// Check if there is some value and if its above or equal 0
	var value = $('#modify_form #m_value').val();
	if (value !== "") {
		if (Math.round(value.toNumber() * 100) < 0 || value.includes(".")){
			document.getElementById("m_value").className = "form-control is-invalid";
			submit = false;
		} else {
			document.getElementById("m_value").className = "form-control";
		}
	}
	value = null;

	return submit;
}


/* JS USED IN USERS PAGES (/templates/users) */


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


// Function that allows the user to see the password text in the add form
function show_passwords(){
	var x = document.getElementById("password");
	var y = document.getElementById("r_password");
	if (x.type === "password" && y.type === "password") {
		x.type = "text";
		y.type = "text";
	} else {
		x.type = "password";
		y.type = "password";
	}
}


// Validate the fields in the add form
function validate_fields(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if there is some email
	var email = $('#add_form #email').val();
	if (email === "") {			// If there isn't shows an error message and ban the submit of the form
		document.getElementById("email").className = "form-control is-invalid";
		submit = false;
	} else {
		document.getElementById("email").className = "form-control";
	}
	email = null;

	// Check if the passwords are equals
	var pass1 = $('#add_form #password').val();
	var pass2 = $('#add_form #r_password').val();
	if (pass1 !== pass2 || pass1 === "" || pass2 === "") {		// If not equals or empty, show an error message and ban the submit of the form
		document.getElementById("password").className = "form-control is-invalid";
		document.getElementById("r_password").className = "form-control is-invalid";
		submit = false
	} else {
		document.getElementById("password").className = "form-control";
		document.getElementById("r_password").className = "form-control";
	}
	pass1 = null;
	pass2 = null;

	// Check if the username exists and if its length is lower than 20 characters
	var username = $('#add_form #username').val();
	if (username !== "") {				// If the username exists, checks the length
		if (username.length > 20) {	// If the length is above 20 characters show an error message and ban the submit of the form
			document.getElementById("username").className = "form-control is-invalid";
		} else {
			document.getElementById("username").className = "form-control";
		}
	}
	username = null;

	// Check if some role was selected
	var admin = $('#add_form #admin_radio').prop("checked");
	var client = $('#add_form #client_radio').prop("checked");
	if (admin === false && client === false) {	// If role wasn't selected shows an error field form in the role input
		document.getElementById("admin_radio").className = "custom-control-input is-invalid";
		document.getElementById("client_radio").className = "custom-control-input is-invalid";
		submit = false
	} else {
		document.getElementById("admin_radio").className = "custom-control-input";
		document.getElementById("client_radio").className = "custom-control-input";
	}
	admin = null;
	client = null;

	return submit;
}


// Function that allows the user to see the password text in the modify form
function show_passwords2(){
	var x = document.getElementById("m_password");
	var y = document.getElementById("m_r_password");
	if (x.type === "password" && y.type === "password") {
		x.type = "text";
		y.type = "text";
	} else {
		x.type = "password";
		y.type = "password";
	}
}


// Validate the fields in the modify form
function validate_fields2() {
	// Variable that allows or not the submit of the form
	var submit = true;

	// Check if the passwords are equals
	var pass1 = $('#modify_form #m_password').val();
	var pass2 = $('#modify_form #m_r_password').val();
	if (pass1 !== "" && pass2 !== "")  {
		if (pass1 !== pass2) {		// If not equals, show an error message and ban the submit of the form
			document.getElementById("m_password").className = "form-control is-invalid";
			document.getElementById("m_r_password").className = "form-control is-invalid";
			submit = false
		} else {
			document.getElementById("m_password").className = "form-control";
			document.getElementById("m_r_password").className = "form-control";
		}
	}
	pass1 = null;
	pass2 = null;

	// Check if the username exists and if its length is lower than 20 characters
	var username = $('#modify_form #m_username').val();
	if (username.length > 20) {	// If the length is above 20 characters show an error message and ban the submit of the form
		document.getElementById("m_username").className = "form-control is-invalid";
	} else {
		document.getElementById("m_username").className = "form-control";
	}
	username = null;

	return submit;
}
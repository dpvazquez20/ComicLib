/* LOGIN AND SIGN IN PAGE (index.html) */

// Activate tooltips in the new acount form
$(function () {
  	$('[data-toggle="tooltip"]').tooltip()
});


// Function that allows the user to see the password text in the log in
function show_password(){
	var x = document.getElementById("pwd");
	if (x.type === "password") {
		x.type = "text";
	} else {
		x.type = "password";
	}
}


// Function that allows the user to see the password text in the sign in
function show_passwords(){
	var x = document.getElementById("s_password");
	var y = document.getElementById("rs_password");
	if (x.type === "password" && y.type === "password") {
		x.type = "text";
		y.type = "text";
	} else {
		x.type = "password";
		y.type = "password";
	}
}


// Validate the email field in the sign in form
function validate_email2() {
	// Check if there is some email
	var email = $('#signin_form #s_email').val();
	if (email !== "") {			// If there is, shows an ok form field
		document.getElementById("s_email").className = "form-control is-valid";
	} else {						// Else shows an error message and ban the submit of the form
		document.getElementById("s_email").className = "form-control is-invalid";
	}
	email = null;
}


// Validate the passwords fields in the sign in form
function validate_pass() {
	// Check if the passwords are equals
	var pass1 = $('#signin_form #s_password').val();
	var pass2 = $('#signin_form #rs_password').val();
	if (pass1 !== pass2 || pass1 === "" || pass2 === "") {		// If not equals or empty, show an error message and ban the submit of the form
		document.getElementById("s_password").className = "form-control is-invalid";
		document.getElementById("rs_password").className = "form-control is-invalid";
	} else {					// If equals, shows an ok form field
		document.getElementById("s_password").className = "form-control is-valid";
		document.getElementById("rs_password").className = "form-control is-valid";
	}
	pass1 = null;
	pass2 = null;
}


// Validate the username field in the sign in form
function validate_username() {
	// Check if the username exists and if its length is lower than 20 characters
	var username = $('#signin_form #s_username').val();
	if (username.length <= 20) {	// If length is above 20, shows an ok form field
		document.getElementById("s_username").className = "form-control is-valid";
	} else {						// Else show an error message and ban the submit of the form
		document.getElementById("s_username").className = "form-control is-invalid";
	}
	username = null;
}


// Validate the genre fields in the sign in form
function validate_genre(){
	// Genre is an optional field so it's always valid
	document.getElementById("man_radio").className = "custom-control-input is-valid";
	document.getElementById("woman_radio").className = "custom-control-input is-valid";
}


// Validate the fields in the sign in form
function validate_fields(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if there is some email
	var email = $('#signin_form #s_email').val();
	if (email !== "") {			// If there is, shows an ok form field
		document.getElementById("s_email").className = "form-control is-valid";
	} else {						// Else shows an error message and ban the submit of the form
		document.getElementById("s_email").className = "form-control is-invalid";
		submit = false;
	}
	email = null;

	// Check if the passwords are equals
	var pass1 = $('#signin_form #s_password').val();
	var pass2 = $('#signin_form #rs_password').val();
	if (pass1 !== pass2 || pass1 === "" || pass2 === "") {		// If not equals or empty, show an error message and ban the submit of the form
		document.getElementById("s_password").className = "form-control is-invalid";
		document.getElementById("rs_password").className = "form-control is-invalid";
		submit = false
	} else {					// If equals, shows an ok form field
		document.getElementById("s_password").className = "form-control is-valid";
		document.getElementById("rs_password").className = "form-control is-valid";
	}
	pass1 = null;
	pass2 = null;

	// Check if the username exists and if its length is lower than 20 characters
	var username = $('#signin_form #s_username').val();
	if (username.length <= 20) {	// If length is above 20, shows an ok form field
		document.getElementById("s_username").className = "form-control is-valid";
	} else {						// Else show an error message and ban the submit of the form
		document.getElementById("s_username").className = "form-control is-invalid";
		submit = false;
	}
	username = null;

	// Genre is an optional field so it's always valid
	document.getElementById("man_radio").className = "custom-control-input is-valid";
	document.getElementById("woman_radio").className = "custom-control-input is-valid";

	return submit;
}


// Validate the email field in the forget password form
function validate_email(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if there is some email
	var email = $('#forget_form #f_email').val();
	if (email === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("f_email").className = "form-control is-invalid";
		submit = false;
	} else {						// Else shows an error message and ban the submit of the form
		document.getElementById("f_email").className = "form-control is-valid";
	}
	email = null;

	return submit;
}


// Validate the email field in the forget password form
function validate_email3(){
	// Check if there is some email
	var email = $('#forget_form #f_email').val();
	if (email === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("f_email").className = "form-control is-invalid";
	} else {
		document.getElementById("f_email").className = "form-control is-valid";
	}
	email = null;
}
/* PROFILE PAGES (profile directory) */


// Activate tooltips and toasts
$(function () {
  	$('[data-toggle="tooltip"]').tooltip();
  	$('.toast').toast();
});


// Show toasts
$(function () {
  	var toast = document.getElementById("toast");
	if (toast !== null) {
		$('.toast').toast('show');
	}
	toast = null
});

// Validate the name field in the profile modify username form
function validate_username(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if there is some name and it has less than 20 characters
	var name = $('#modify_username #username').val();
	if (name === "" || name.length > 20) {			// If not, shows an error message and ban the submit of the form
		document.getElementById("username").className = "form-control is-invalid";
		submit = false;
	} else {
	    document.getElementById("username").className = "form-control is-valid";
    }
	name = null;

	return submit;
}


// Validate the name field in the profile modify username form
function validate_username2(){
	// Check if there is some name and it has less than 20 characters
	var name = $('#modify_username #username').val();
	if (name === "" || name.length > 20) {			// If not, shows an error message and ban the submit of the form
		document.getElementById("username").className = "form-control is-invalid";
	} else {
	    document.getElementById("username").className = "form-control is-valid";
    }
	name = null;
}


// Function that allows the user to see the passwords text in change password form
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


// Validate the passwords fields in the change password form
function validate_passwords() {
    // Variable that allow or not the submit of the form
	var submit = true;

    // Check if the passwords are equals
    var pass1 = $('#pass_form #password').val();
    var pass2 = $('#pass_form #r_password').val();
    if (pass1 !== pass2 || pass1 === "" || pass2 === "") {		// If not equals, show an error message and ban the submit of the form
        document.getElementById("password").className = "form-control is-invalid";
        document.getElementById("r_password").className = "form-control is-invalid";
        submit = false
    } else {					// If equals, shows an ok form field
        document.getElementById("password").className = "form-control is-valid";
        document.getElementById("r_password").className = "form-control is-valid";
    }
    pass1 = null;
    pass2 = null;

    return submit
}


// Validate the passwords fields in the change password form
function validate_passwords2() {
    // Check if the passwords are equals
    var pass1 = $('#pass_form #password').val();
    var pass2 = $('#pass_form #r_password').val();
    if (pass1 !== pass2 || pass1 === "" || pass2 === "") {		// If not equals, show an error message and ban the submit of the form
        document.getElementById("password").className = "form-control is-invalid";
        document.getElementById("r_password").className = "form-control is-invalid";
    } else {					// If equals, shows an ok form field
        document.getElementById("password").className = "form-control is-valid";
        document.getElementById("r_password").className = "form-control is-valid";
    }
    pass1 = null;
    pass2 = null;
}


// Validate the email field in the profile modify email form
function validate_email(){
	// Variable that allow or not the submit of the form
	var submit = true;

	// Check if there is some email
	var email = $('#email_form #email').val();
	if (email === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("email").className = "form-control is-invalid";
		submit = false;
	} else {
	    document.getElementById("email").className = "form-control is-valid";
    }
	email = null;

	return submit;
}


// Validate the email field in the profile modify email form
function validate_email2(){
	// Check if there is some email
	var email = $('#email_form #email').val();
	if (email === "") {			// If not, shows an error message and ban the submit of the form
		document.getElementById("email").className = "form-control is-invalid";
	} else {
	    document.getElementById("email").className = "form-control is-valid";
    }
	email = null;
}


// Validate the genre fields in the sign in form
function validate_genre(){
	// Genre is an optional field so it's always valid
	document.getElementById("man_radio").className = "custom-control-input is-valid";
	document.getElementById("woman_radio").className = "custom-control-input is-valid";
}

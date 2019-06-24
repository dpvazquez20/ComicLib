#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time
import random

from google.appengine.api import mail
from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.functions import get_default_language
from handlers.elements.function import encryptPassword
from handlers.lang.spa import lang as spa
from handlers.lang.spa import lang as eng
from models.db import User


""" Handler used in the index page (Sign in)
    get: redirect to the login page
    post: it's responsible for doing the user sign in"""
class SigninHandler(BaseHandler):

    # Redirect to the login page
    def get(self):
        self.redirect("/login")

    # Login authentication
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)
        # Retrieve the fields written in the sign in form
        email = self.request.get("s_email", "")              # New user email
        email = email.encode("utf8")
        password1 = self.request.get("s_password", "")       # New user password
        password1 = password1.encode("utf8")
        password2 = self.request.get("rs_password", "")      # New user password
        password2 = password2.encode("utf8")
        name = self.request.get("s_name", "")                # New user name
        name = name.encode("utf8")
        genre = self.request.get("s_genre", "not_defined")   # New user genre
        genre = genre.encode("utf8")

        # Set the default language of the app
        lang = get_default_language()  # Get the default language of the app

        # Set the language strings dictionary
        if lang == "spa":
            lang = spa  # Spanish strings
        elif lang == "eng":
            lang = eng  # English strings

        # Default values to be sent to the HTML page
        values = {
            "lang": lang,  # Strings
        }

        # Check if the email or password fields are empty (HTML shouldn't allow this). Show an error message if they are empty
        if len(email) == 0 or len(password1) == 0 or len(password2) == 0:
            # Values to be sent to the HTML page
            values["error_message"] = lang["needs_email_pass"]  # Error message (Email and password required)

            del email, password1, password2, name, genre    # Delete variables to free memory
            self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

        # If not empty
        else:
            # Check if the user already exists
            user = User.query(User.email == email)

            # If the user exists, show an error message
            if user and user.count() > 0:
                # Values to be sent to the HTML page
                values["error_message"] = lang["user_already_exists"]   # Error message (This user already exists)

                del user, email, password1, password2, name, genre  # Delete variables to free memory
                self.response.write(jinja.render_template("index.html", **values))  # Go the login page

            # If the user doesn't exist, create a new user
            else:
                # Check if the username already exists
                username = User.query(User.name == name)

                # If the username already exists, shows an error message
                if username.count() > 0:
                    # Values to be sent to the HTML page
                    values["error_message"] = lang["username_already_exists"]   # Error message (Username already used by other)

                    del username        # Delete variable to free memory
                    self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

                # If the username doesn't exist
                else:
                    # If the passwords are equals
                    if self.check_passwords(password1, password1):
                        # Create an username if the user didn't write one
                        if len(name) == 0:
                            pos = email.find("@")
                            name = email[:pos]
                            # Check if the new user name already exists
                            aux_user = User.query(User.name == name).fetch()
                            aux_name = name
                            while len(aux_user) > 0:
                                aux_name = name + str(random.randint(0, 999))
                                aux_user = User.query(User.name == aux_name).fetch()
                            name = aux_name  # Setting the new user name
                            del pos, aux_user, aux_name  # Delete variables to free memory

                        # Codify the password
                        hash = encryptPassword(password1)

                        # Check the genre
                        if genre != "male" and genre != "female" and genre != "female":
                            genre = "not_defined"

                        # Get the default language
                        idiom = get_default_language()

                        # Create the user and put it in in the database
                        user = User(email=email, password=hash, name=name, genre=genre, role="client", language=idiom)
                        aux = user.put()
                        time.sleep(1)

                        # It the user was successfully added
                        if aux is not None:
                            # Setting the session variables
                            self.session['session_name'] = user.name        # User name
                            self.session['session_role'] = user.role        # User role
                            self.session['session_idiom'] = user.language   # User language
                            self.session['session_genre'] = user.genre      # User genre
                            self.session['num_elems_page'] = 10             # Number of elements per page
                            self.session['current_number_page'] = 1         # Current number page
                            self.session['pages'] = list()                  # Pages for the pagination
                            self.session['last_page'] = 1                   # Last page number
                            self.session['pages_to_show'] = 3               # Number of pages that shows the pagination
                            self.session['page_name'] = ""                  # Name of the current page in wich user is

                            # Create a welcome email
                            message = mail.EmailMessage(
                                sender="noreply@gmail.com",  # Email sender, it has to be a Google account
                                subject=lang["welcome_subject"])  # Email subject

                            message.to = email  # Email receiver
                            message.body = lang["welcome_mail"]  # Email body

                            # Send the email
                            message.send()

                            del user, email, password1, password2, name, genre, hash, username, idiom, message, aux    # Delete variables to free memory
                            self.redirect("/home")  # Redirect to the home page

                        # Else show an error message
                        else:
                            # Variables to be sent to the HTML page
                            values["error_message"] = lang["error_sign_in"]  # Error message (The client couldn't be added)

                            del user, email, password1, password2, name, genre, hash, username, idiom, aux  # Delete variables to free memory
                            self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

                    # If password not equals
                    else:
                        # Variables to be sent to the HTML page
                        values["error_message"] = lang["invalid_password"]  # Error message (Password not equals)

                        del user, email, password1, password2, name, genre, username   # Delete variables to free memory
                        self.response.write(jinja.render_template("index.html", **values))  # Go to the login page


    # Check the password given by HTML
    def check_passwords(self, pass1, pass2):
        toret = True
        if len(pass1) < 8 or len(pass1) > 20:   # Password length
            toret = False
        if len(pass2) < 8 or len(pass2) > 20:   # Password length
            toret = False
        if pass1 != pass2:                      # Passwords equals
            toret = False
        return toret


app = webapp2.WSGIApplication([], debug=True)
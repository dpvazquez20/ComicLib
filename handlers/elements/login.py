#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from datetime import date, timedelta
from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.functions import get_default_language
from handlers.elements.function import encryptPassword
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User


""" Handler used in the index page (Log in)
    get: redirect to the login page
    post: it's responsible for doing the user login"""
class LoginHandler(BaseHandler):

    # Redirect to the login page
    def get(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Set the default language of the app
        lang = get_default_language()           # Get the default language of the app

        # Set the language strings dictionary
        if lang == "spa":
            lang = spa              # Spanish strings
        elif lang == "eng":
            lang = eng              # English strings

        # Values to be sent to the html
        values = {
            "lang": lang,    # Strings
        }

        self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

    # Login authentication
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)
        # Retrieve the email and password written in the login
        email = self.request.get("email", "")           # Email
        email = email.encode("utf8")
        password = self.request.get("password", "")     # Password
        password = password.encode("utf8")

        # Set the default language of the app
        lang = get_default_language()  # Get the default language of the app

        # Set the language strings dictionary
        if lang == "spa":
            lang = spa  # Spanish strings
        elif lang == "eng":
            lang = eng  # English strings

        # Set the default values to be sent to the HTML page
        values = {
            "lang": lang    # Strings
        }

        # Check if the email or password fields are empty (HTML shouldn't allow this). Show an error message if they are empty
        if len(email) == 0 or len(password) == 0:
            # Value to be sent to the HTML page
            values["error_message"] = lang["needs_email_pass"]     # Error message (Password and email required)

            del email, password         # Delete variables to free memory
            self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

        # If not empty
        else:
            # Check if the user exists
            user = User.query(User.email == email)

            if user and user.count() > 0:
                # Codify the password
                hash = encryptPassword(password)

                # If the user exists, check the email and password. If they are correct, set session variables and redirect tho the home page
                user = User.query(User.email == email, User.password == hash)
                if user and user.count() == 1:
                    user = user.fetch()
                    user = user[0]

                    # If the user isn't blocked
                    if user.blocked == False:
                        # Setting the session variable
                        self.session['session_name'] = user.name             # User name
                        self.session['session_role'] = user.role             # User role
                        self.session['session_idiom'] = user.language        # User language strings
                        self.session['session_genre'] = user.genre           # User genre
                        self.session['num_elems_page'] = 10                  # Number of elements per page
                        self.session['current_number_page'] = 1              # Current number page
                        self.session['pages'] = list()                       # Pages for the pagination
                        self.session['last_page'] = 1                        # Last page number
                        self.session['pages_to_show'] = 3                    # Number of pages that shows the pagination
                        self.session['page_name'] = ""                       # Name of the current page in wich user is

                        del user, email, password, hash     # Delete variables to free memory
                        self.redirect("/home")      # Redirect to the home page

                    # If the user continue with a block
                    else:
                        now = date.today()
                        # If the block is not over
                        if user.blocked == True:
                            if now <= user.end_block:
                                # Value to be sent to the HTML page
                                # Error message (User blocked)
                                values["error_message"] = lang["blocked_" + user.genre] + lang["until"] + str(user.end_block + timedelta(days=1))

                                del user, email, password, hash, now  # Delete variables to free memory
                                self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

                        # Else
                        else:
                            # Unblocking the user
                            user.end_block = None
                            user.blocked = False

                            user.put()  # Setting the user

                            # Setting the session variable
                            self.session['session_name'] = user.name  # User name
                            self.session['session_role'] = user.role  # User role
                            self.session['session_idiom'] = user.language  # User language strings
                            self.session['session_genre'] = user.genre  # User genre
                            self.session['num_elems_page'] = 10  # Number of elements per page
                            self.session['current_number_page'] = 1  # Current number page
                            self.session['pages'] = list()  # Pages for the pagination
                            self.session['last_page'] = 1  # Last page number
                            self.session['pages_to_show'] = 3  # Number of pages that shows the pagination
                            self.session['page_name'] = ""  # Name of the current page in wich user is

                            del user, email, password, hash  # Delete variables to free memory
                            self.redirect("/home")  # Redirect to the home page

                # If they aren't correct show an error message
                else:
                    # Value to be sent to the HTML page
                    values["error_message"] = lang["email_pass_incorrect"]     # Error message (Email or password are wrong)

                    del user, email, password, hash     # Delete variables to free memory
                    self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

            # If the user doesn't exist, show an error message
            else:
                # Value to be sent so the HTML page
                values["error_message"] = lang["user_not_exist"]     # Error message (That user doesn't exist)

                del user, email, password       # Delete variables to free memory
                self.response.write(jinja.render_template("index.html", **values))  # Go to the login page


app = webapp2.WSGIApplication([], debug=True)
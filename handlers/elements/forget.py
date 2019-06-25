#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from google.appengine.api import mail
from handlers.elements.function import randomPassword, encryptPassword
from handlers.lang.spa import lang
from models.db import User


""" Forget password handler
    get: sends an email to the user that allows him/her to recover the password. This password will be a new password generated randomly"""
class ForgetHandler(BaseHandler):

    # Redirect to the login page
    def get(self):
        self.redirect("/login")

    # Allows the user to recover the password
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)
        # Retrieve the email written in the form
        email = self.request.get("email", "")
        email = email.encode("utf8")

        # Default values to be sent to the HTML page
        values = {
            "lang": lang,  # Strings
        }

        # Check if the client sent an email, if not shows an error message (HTML and JS shouldn't allow this)
        if len(email) == 0:
            # Values to be sent to the HTML page
            values["error_message"] = lang["must_email"]    # Error message (An email is required)

            del email       # Delete variables to free memory
            self.response.write(jinja.render_template("index.html", **values))  # Go to the login page

        # If client sent an email
        else:
            # Check if the user exists
            user = User.query(User.email == email)

            # It the user exists
            if user and user.count() > 0:
                user = list(user.fetch())
                user = user[0]

                # Creating and encrypting a random password
                password = randomPassword()

                # Create the email to recuperate the password
                message = mail.EmailMessage(
                    sender="noreplycomiclib@gmail.com",     # Email sender, it has to be a Google account
                    subject=lang["subject"])                # Email subject

                message.to = email                          # Email receiver
                message.body = lang["greeting"] + user.name + lang["body"] + password + lang["end"]     # Email body

                # Set the user new password in the db
                user.password = encryptPassword(password)
                user.put()
                time.sleep(1)

                # Send the email
                message.send()

                del user, email, message, password      # Delete variables to free memory
                self.redirect("/login")     # Redirect to the login page

            # If the user doesn't exist, show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["email_not_exist"]   # Error message (Email doesn't exist)

                del user, email     # Delete variables to free memory
                self.response.write(jinja.render_template("index.html", **values))  # Go to the login page


app = webapp2.WSGIApplication([], debug=True)

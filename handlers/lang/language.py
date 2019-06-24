#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time

from handlers.elements.sessions import BaseHandler
from models.db import User


""" Language handler in the app 
    Get: it's responsible for changing the language in the app"""
class LanguageHandler(BaseHandler):

    # Redirect to the login page
    def get(self):
        self.redirect("/login")

    # Change the language inside the app (all pages except login)
    def post(self):
        # Retrieve the language
        language = self.request.get("lang", "")
        language = language.encode("utf8")

        # If the user selects a language, do the change
        if len(language) > 0:
            # Change the session variable language
            if language == "spa":
                self.session['session_idiom'] = "spa"    # Spanish
            elif language == "eng":
                self.session['session_idiom'] = "eng"    # English
            else:
                self.session['session_idiom'] = "eng"    # Default english

            # Set the new language in the database
            if len(self.session['session_name']) > 0:
                user = User.query(User.name == self.session['session_name'])
                user = user.get()
                user.language = language
                user.put()
                time.sleep(1)
                del user

            del language      # Delete variables to free memory

            self.session_store.save_sessions(self.response)  # Save sessions

            # If there is an user in the app return to the home page, else return to the login page
            if len(self.session['session_name']) > 0:
                self.redirect(self.session.get('page_name'))    # Redirect to the last main page the user visited
            else:
                self.redirect("/login")     # Redirect to the login page

        # Else return to the home page
        else:
            del language    # Delete variables to free memory
            self.redirect("/home")


app = webapp2.WSGIApplication([], debug=True)

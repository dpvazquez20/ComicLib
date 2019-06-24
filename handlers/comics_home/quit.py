#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time

from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User


""" Quit comic handler in the home page
    Get: redirect to the home page 
    Post: it's responsible for quitting a comic to the user collection"""
class HomeQuitComicHandler(BaseHandler):

    # Redirect to the home page
    def get(self):
        self.redirect("/home")

    # Quit a comic
    def post(self):
        # Check if the client is logged in
        if self.session.get('session_role') == 'client':
            # If it's logged in, get the session variables, show the home page
            # Get the comic attributes
            comic_key = self.request.get("comic_key", "")  # Comic key
            comic_key = ndb.Key(urlsafe=comic_key)
            comic = comic_key.get()

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            # If the key is from an comic
            if comic and comic is not None and comic_key is not None:
                # Delete the association in the Comic class
                aux4 = list()
                for user_comic in comic.users:
                    if user_comic.username != self.session.get("session_name"):
                        aux4.append(user_comic)
                    del user_comic

                comic.users = aux4
                comic.put()
                del aux4
                time.sleep(1)

            del lang     # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.redirect("/home")      # Redirect to the home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture

app = webapp2.WSGIApplication([], debug=True)
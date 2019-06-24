#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time

from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, User_ComicBook


""" Add comic handler in the home page
    Get: redirect to the home page 
    Post: it's responsible for adding a comic to the user collection"""
class HomeAddComicHandler(BaseHandler):

    # Redirect to the home page
    def get(self):
        self.redirect("/home")

    # Add a comic
    def post(self):
        # Check if the client is logged in
        if self.session.get('session_role') == 'client':
            # If it's logged in, get the session variables, show the home page
            # Get the comic attributes
            comic_key = self.request.get("comic_key", "")         # Comic key
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
                # Adding the comic
                user_comic = User_ComicBook(username=self.session.get("session_name"), id_aux=comic.key)
                user_comic.put()

                if len(comic.users) > 0:
                    comic.users.append(user_comic)
                else:
                    comic.users = [user_comic]

                comic.put()
                time.sleep(1)

                del user_comic    # Delete variables to free memory

            del lang, comic, comic_key     # Delete variables to free memory
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
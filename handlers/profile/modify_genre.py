#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time

from webapp2_extras import jinja2
from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook

""" Modify genre handler in the profile home page
    Get: redirect to the profile home page 
    Post: it's responsible for modifying the user genre in the database"""
class ProfileModifyGenreHandler(BaseHandler):

    # Redirect to the profile home page
    def get(self):
        self.redirect("/profile")

    # Modify the genre
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin or client are logged in
        if self.session.get('session_role') == 'admin' or self.session.get('session_role') == 'client':
            # If it's logged in, modify
            # Get the user attributes
            genre = self.request.get("genre", "not_defined")               # User genre
            genre = genre.encode("utf8")
            key = self.request.get("key", "")                              # User key
            key = ndb.Key(urlsafe=key)

            user = key.get()      # Get the user with that key

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            # Variables to be sent to the HTML page
            values = {
                "lang": lang,                                                                   # Language strings
                "session_name": self.session.get('session_name'),                               # User name
                "session_role": self.session.get('session_role'),                               # User role
                "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                "user_email": user.email,                                                       # User email
                "user_key": user.key.urlsafe(),                                                 # User key
                "user_genre": self.session.get('session_genre'),                                # User genre
                "statistics": self.get_statistics()                                             # Client statistics
            }

            # If the user exists
            if user is not None:
                # Set the new genre
                if genre != "male" and genre != "female" and genre != "not_defined":
                    genre = "not_defined"

                user.genre = genre
                aux = user.put()
                time.sleep(1)

                # If the modification was successful
                if aux is not None:
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["genre_modified_successfully"]     # Ok message (Genre modified successfully)
                    values["user_genre"] = genre
                    self.session['session_genre'] = genre                          # Setting the session variable

                # Else show an error message
                else:
                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_modify"]  # Error message (The modification couldn't be done)

                del aux    # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["genre_not_modified"]     # Error message (Genre  couldn't be modified)

            del lang, genre, key, user        # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/profile/default.html", **values))  # Go to the profile home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture

    # Get the client statistics
    def get_statistics(self):
        statistics = dict()
        statistics["read"] = 0
        statistics["unread"] = 0
        statistics["comic"] = 0
        statistics["manga"] = 0
        statistics["anthology"] = 0
        statistics["american"] = 0
        statistics["european"] = 0
        statistics["other"] = 0
        statistics["value"] = 0

        comics = ComicBook.query(ComicBook.users.username == self.session.get("session_name"))
        for comic in comics:
            for user_comic in comic.users:
                if user_comic.username == self.session.get('session_name'):
                    # Already read or not
                    if user_comic.state == "read":
                        statistics["read"] += 1
                    else:
                        statistics["unread"] += + 1
                    # Comics by type
                    if comic.type == "comic":
                        statistics["comic"] += 1
                    elif comic.type == "manga":
                        statistics["manga"] += 1
                    else:
                        statistics["anthology"] += 1
                    # Comics by origin
                    if comic.origin == "american":
                        statistics["american"] += 1
                    elif comic.origin == "european":
                        statistics["european"] += 1
                    else:
                        statistics["other"] += 1
                del user_comic
            statistics["value"] += comic.value
            del comic

        del comics  # Delete variables to free memory
        return statistics


app = webapp2.WSGIApplication([], debug=True)
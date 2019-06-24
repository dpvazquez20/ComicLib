#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook


""" Main handler in the profile home page 
    Get: it's responsible for showing the profile home page
    Post: redirect to the profile home page"""
class ProfileHomeHandler(BaseHandler):

    # Show the profile home page
    def get(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin and client are logged in
        if self.session.get('session_role') == 'admin' or self.session.get('session_role') == 'client':
            # Get the user
            user = User.query(User.name == self.session.get('session_name')).fetch()    # Username is unique (teorically)

            # Check the user data
            if user and len(user) == 1:
                # Set the default language of the app
                if self.session['session_idiom'] == "spa":
                    lang = spa  # Spanish strings
                elif self.session['session_idiom'] == "eng":
                    lang = eng  # English strings
                else:
                    lang = eng  # Default english

                self.session['page_name'] = "/profile"  # Current page name

                # Variables to be sent to the HTML page
                values = {
                    "lang": lang,                                                       # Language strings
                    "session_name": self.session.get('session_name'),                   # User name
                    "session_role": self.session.get('session_role'),                   # User role
                    "session_picture": user[0].picture,                                 # User picture
                    "user_email": user[0].email,                                        # User email
                    "user_key": user[0].key.urlsafe(),                                  # User key
                    "user_genre": self.session.get('session_genre'),                    # User genre
                    "statistics": self.get_statistics()                                 # Client statistics
                }

                del lang  # Delete variables to free memory

                self.session_store.save_sessions(self.response)     # Save sessions
                self.response.write(jinja.render_template("/profile/default.html", **values))   # Go to the profile home page

            # If the user doesn't exist or there more than 1 user with the same name, redirect to the login page
            else:
                self.redirect("/login")

        # If they aren't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Redirect to the profile home page
    def post(self):
        self.redirect("/profile")

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

        del comics      # Delete variables to free memory
        return statistics


app = webapp2.WSGIApplication([], debug=True)

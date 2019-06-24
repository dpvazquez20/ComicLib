#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time
import copy

from webapp2_extras import jinja2
from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook, User_ComicBook, Shelving


""" Modify username handler in the profile home page
    Get: redirect to the profile home page 
    Post: it's responsible for modifying the user name in the database"""
class ProfileModifyUsernameHandler(BaseHandler):

    # Redirect to the profile home page
    def get(self):
        self.redirect("/profile")

    # Modify the username
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin' or self.session.get('session_role') == 'client':
            # If it's logged in, get the session variables
            # Get the user attributes
            username = self.request.get("username", "")     # Username
            username = username.encode("utf8")
            key = self.request.get("key", "")               # User key
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

            # If the user exists and there is an username to change
            if user is not None and len(username) > 0:
                repeated_user = User.query(User.name == username)

                # If it doesn't exist an user with the name provided
                if repeated_user.count() == 0:
                    # Set the new username
                    username_aux = copy.copy(user.name)
                    user.name = username
                    aux = user.put()
                    time.sleep(1)

                    # If the modification was successful
                    if aux is not None:
                        # Variables to be sent to the HTML page
                        # Ok message (Username modified successfully)
                        values["ok_message"] = lang["username_modified_successfully_" + str(self.session.get("session_genre"))]

                        # Change the username in the comics
                        comics = ComicBook.query(ComicBook.users.username == username_aux)
                        for comic in comics:
                            for user_comic in comic.users:
                                if user_comic.username == username_aux:
                                    user_comic.username = user.name
                                del user_comic
                            comic.put()
                            del comic

                        # Change the username in the User_ComicBook rows
                        user_comics = User_ComicBook.query(User_ComicBook.username == username_aux)
                        for user_comic in user_comics:
                            if user_comic.username == username_aux:
                                user_comic.username = user.name
                            user_comic.put()
                            del user_comic

                        # Change the username in the shelves and shelvings
                        shelvings = Shelving.query(Shelving.username == username_aux)
                        for shelving in shelvings:
                            shelving.username = user.name
                            shelving.put()
                            del shelving

                        del user_comics, shelvings  # Delete variables to free memory
                        self.session['session_name'] = user.name    # Setting the new session username
                        values["session_name"] = user.name

                    # Else show an error message
                    else:
                        # Variables to be sent to the HTML page
                        values["error_message"] = lang["error_modify"]  # Error message (The modification couldn't be done)

                    del aux, username_aux    # Delete variables to free memory

                # If already exists show an error message
                else:
                    # Values to be sent to the HTML page
                    values["error_message"] = lang["username_already_exists"]  # Error message (Username already used by other)

                del repeated_user       # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                # Error message (Username couldn't be modified)
                values["error_message"] = lang["username_not_modified_" + str(self.session.get("session_genre"))]

            del lang, username, key, user     # Delete variables to free memory
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

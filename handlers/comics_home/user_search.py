#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook


""" Search handler in the home page 
    Get: redirect to the home page
    Post: it's responsible for searching the field given by the user"""
class UserSearchHandler(BaseHandler):

    # Redirect to the home page
    def get(self):
        self.post()

    # Search an comic or more
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in
        if self.session.get('session_role') == 'client':
            # If it's logged in, get the session variables, show the home page
            # Get the search field
            search = self.request.get("search", "")     # Comic
            search = search.encode("utf8")

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            self.session['page_name'] = "/user_search"  # Current page name

            # Initializing variables
            comics = list()

            all_comics = ComicBook.query()

            # Variables to be sent to the HTML page
            values = {
                "lang": lang,                                                                   # Language strings
                "session_name": self.session.get('session_name'),                               # User name
                "session_role": self.session.get('session_role'),                               # User role
                "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                "session_genre": self.session.get('session_genre'),                             # User genre
                "comics": comics,                                                               # Comics
                "all_comics": all_comics                                                        # All comics (for the user search)
            }

            # Check if there is a field to search
            if search != "" and len(search) > 0:
                # Get the key sent in the search field
                key = ndb.Key(urlsafe=search)

                # Get the comics with that key
                comic = key.get()

                # Check if the comics exists
                if comic and comic is not None:
                    comics.append(comic)                                                            # Comics list
                    self.get_own_comics(comics)                                                     # Get the comics added by the user
                    values["comics"] = comics                                                       # Search results

                # If not exists, shows a message
                else:
                    values["ok_message"] = lang["search_not_results"]  # Ok message (No matches found)

                del key, comic     # Delete variables to free memory

            # If not exists, shows a message
            else:
                values["ok_message"] = lang["search_not_results"]  # Ok message (No matches found)

            del search, comics, lang        # Delete variables to free memory
            self.response.write(jinja.render_template("/elements/user_search_results.html", **values))  # Go to the comics home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture

    # Add a attribute in the comics that the current user has added previosly
    def get_own_comics(self, comics):
        for comic in comics:
            for user_comic in comic.users:
                if self.session.get('session_name') == user_comic.username:
                    comic.owned = True
                del user_comic
            del comic

app = webapp2.WSGIApplication([], debug=True)

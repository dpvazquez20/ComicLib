#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import Author, User


""" Search handler in the authors home page 
    Get: redirect to the authors home page
    Post: it's responsible for searching the field given by the user"""
class SearchAuthorHandler(BaseHandler):

    # Redirect to the authors home page
    def get(self):
        self.redirect("/authors")

    # Search an author or more
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the search field
            search = self.request.get("search", "")     # Sort option
            search = search.encode("utf8")

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            # Initializing variables
            all_keys = list()
            authors = list()
            pages = list()
            keys_page_list = list()
            all_authors = Author.query().fetch()

            # Variables to be sent to the HTML page
            values = {
                "lang": lang,                                                                   # Language strings
                "session_name": self.session.get('session_name'),                               # User name
                "session_role": self.session.get('session_role'),                               # User role
                "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                "session_genre": self.session.get('session_genre'),                             # User genre
                "authors": authors,                                                             # Authors
                "current_number_page": self.session.get('current_number_page'),                 # Current number page
                "pages": pages,                                                                 # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # Authors keys that are currently in the page
                "all_keys": all_keys,                                                           # All author keys
                "all_authors": all_authors                                                      # ALL author (for the search field)
            }

            # Check if there is a field to search
            if search != "" and len(search) > 0:
                # Get the key sent in the search field
                key = ndb.Key(urlsafe=search)

                # Get the authors with that key
                author = key.get()

                # Check if the authors exists
                if author and author is not None:
                    authors.append(author)             # Authors list
                    values["authors"] = authors        # Search results

                    # Setting all the author keys
                    all_keys.append(author.key.urlsafe())
                    values["all_keys"] = all_keys
                    # Setting the keys list to allow the use of the "Delete page" button
                    keys_page_list.append(author.key.urlsafe())
                    values["keys_page_list"] = keys_page_list

                # If not exists, shows a message
                else:
                    values["ok_message"] = lang["search_not_results"]  # Ok message (No matches found)

                del key, author     # Delete variables to free memory

            # If not exists, shows a message
            else:
                values["ok_message"] = lang["search_not_results"]  # Ok message (No matches found)

            del search, authors, pages, keys_page_list, all_keys, lang, all_authors        # Delete variables to free memory
            self.response.write(jinja.render_template("/authors/default.html", **values))  # Go to the authors home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture


app = webapp2.WSGIApplication([], debug=True)

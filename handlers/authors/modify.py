#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import copy

from webapp2_extras import jinja2
from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import Author, User, ComicBook, ComicBook_Author


""" Modify handler in the authors home page
    Get: redirect to the authors home page 
    Post: it's responsible for modifying the author data in the database"""
class ModifyAuthorHandler(BaseHandler):

    # Redirect to the authors home page
    def get(self):
        self.redirect("/authors")

    # Modify an author
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the author attributes
            name = self.request.get("name", "")
            name = name.encode("utf8")
            key = self.request.get("key", "")
            key = ndb.Key(urlsafe=key)
            author = key.get()      # Get the author with that key

            keys_page_list = self.request.get("keys_page_list", "")     # Author keys (only authors in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the author keys (for the order field)

            # Initialize variables
            aux = list()            # Support variable
            aux3 = list()           # Support variable
            all_authors = list()    # List with all authors (for the search field)

            # Transform the HTML string in a list
            all_keys = copy.copy(aux_all_keys)
            aux_all_keys = self.transform_keys(aux_all_keys)

            authors = Author.query()
            for author2 in authors:  # Get ALL the keys
                aux.append(author2.key.urlsafe())
                del author2

            for key3 in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                for key2 in aux:
                    if key3 == str(key2):
                        key2 = ndb.Key(urlsafe=key2)
                        aux3.append(key2)
                        break
                    del key2
                del key3

            # Get all db authors
            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')
            authors = Author.query(Author.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

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
                "session_genre": self.session.get('session_genre'),                             # User genre
                "authors": authors,                                                             # Authors
                "current_number_page": self.session.get('current_number_page'),                 # Current number page
                "pages": self.session.get('pages'),                                             # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # Authors keys that are currently in the page
                "all_keys": all_keys,                                                           # All author keys
                "all_authors": all_authors                                                      # ALL author (for the search field)
            }

            # If the key is from an author
            if author and author is not None:
                # If there is some attribute to modify
                if len(name) > 0:
                    old_name = author.name  # Save the old author name for the modify method
                    # Set the author attributes
                    author.name = name
                    aux2 = author.put()

                    # If the modification was successful
                    if aux2 is not None:
                        # Modify the author in other db models (author must be modified in all db models that use it)
                        self.modify_author_everywhere(old_name, author.name)

                        # Variables to be sent to the HTML page
                        values["ok_message"] = lang["author_modified_successfully"]    # Ok message (Author modified successfully)

                        # Get all db authors (Limited to the number given by the session variable [10 by default])
                        authors = Author.query(Author.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)
                        values["authors"] = authors

                    # Else show an error message
                    else:
                        # Variables to be sent to the HTML page
                        values["error_message"] = lang["error_modify"]  # Error message (The modification couldn't be done)

                    del aux2, old_name    # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["author_not_modified"]   # Error message (Author couldn't be modified)

            all_authors = Author.query().fetch()  # ALL authors (for the search field)
            values["all_authors"] = all_authors

            del lang, name, key, author, keys_page_list, aux_all_keys, aux, aux3, authors, \
                all_authors, offset, all_keys     # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/authors/default.html", **values))  # Go to the authors home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Transform the HTML string in a list
    def transform_keys(self, keys):
        keys = keys.replace("[", "")
        keys = keys.replace("]", "")
        keys = keys.replace("'", "")
        keys = keys.replace('"', '')
        keys = keys.split(", ")
        return keys

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture

    # Modify the author in the other db models
    def modify_author_everywhere(self, old_name, new_name):
        # Modify the author in the ComicBook model
        comics = ComicBook.query().fetch()
        if len(comics) > 0:
            for comic in comics:
                if len(comic.authors) > 0:
                    for comic_author in comic.authors:
                        if old_name == comic_author.author.name:
                            comic_author.author.name = new_name
                            comic.put()
                        del comic_author
                del comic

        # Modify the author in the ComicBook_Author model
        comic_authors = ComicBook_Author.query().fetch()
        if len(comic_authors) > 0:
            for comic_author in comic_authors:
                if old_name == comic_author.author.name:
                    comic_author.author.name = new_name
                    comic_author.put()
                del comic_author

        del comics, comic_authors


app = webapp2.WSGIApplication([], debug=True)
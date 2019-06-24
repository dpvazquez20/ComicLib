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
from models.db import User, ComicBook, Author, ComicBook_Author


""" Add author handler in the comics home page
    Get: redirect to the comics home page 
    Post: it's responsible for adding an author to the comic data in the database"""
class AddAuthorComicHandler(BaseHandler):

    # Redirect to the comics home page
    def get(self):
        self.redirect("/comics")

    # Add an author
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the comic attributes
            author_key = self.request.get("author", "")         # Author key
            author_key = ndb.Key(urlsafe=author_key)
            role = self.request.get_all("role[]")               # Author roles

            key = self.request.get("key", "")
            key = ndb.Key(urlsafe=key)
            comic = key.get()      # Get the comic with that key

            keys_page_list = self.request.get("keys_page_list", "")     # Comic keys (only comics in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the comic keys (for the order field)

            # Initialize variables
            aux = list()              # Support variable
            aux3 = list()             # Support variable
            all_comics = list()       # List with all comics (for the search field)

            # Transform the HTML string in a list
            all_keys = copy.copy(aux_all_keys)
            aux_all_keys = self.transform_keys(aux_all_keys)

            comics = ComicBook.query()
            for comic2 in comics:  # Get ALL the keys
                aux.append(comic2.key.urlsafe())
                del comic2

            for key3 in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                for key2 in aux:
                    if key3 == str(key2):
                        key2 = ndb.Key(urlsafe=key2)
                        aux3.append(key2)
                        break
                    del key2
                del key3

            # Get all db comics
            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')
            comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

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
                "comics": comics,                                                               # Comics
                "current_number_page": self.session.get('current_number_page'),                 # Current number page
                "pages": self.session.get('pages'),                                             # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # Comics keys that are currently in the page
                "all_keys": all_keys,                                                           # All comic keys
                "all_comics": all_comics,                                                       # ALL comic (for the search field)
                "authors": self.get_authors()                                                   # Authors for adding them to the comics
            }

            # If the key is from an comic
            if comic and comic is not None and len(role) > 0 and author_key is not None:
                # Adding the author
                roles = ""
                if str(role).find("all") == -1:
                    for i in range(0, len(role)):
                        roles += lang[role[i]] + ", "
                    roles = roles[:len(roles) - 2]
                    roles = roles.capitalize()
                else:
                    roles = lang["script"] + ", " + lang["drawing"] + ", " + lang["labels"] + ", " + lang["inked"] + ", " + lang["colors"] + ", " + lang["cover"]
                    roles = roles.capitalize()

                id = ComicBook_Author.query().order(-ComicBook_Author.id_aux).fetch(1)
                if len(id) > 0:
                    id = id[0].id_aux + 1
                else:
                    id = 1

                comic_author = ComicBook_Author(author=author_key.get(), role=roles, id_aux=id)
                comic_author.put()

                if len(comic.authors) > 0:
                    comic.authors.append(comic_author)
                else:
                    comic.authors = [comic_author]

                aux2 = comic.put()
                time.sleep(1)

                # If the modification was successful
                if aux2 is not None:
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["author_added_successfully"]    # Ok message (Author added successfully)

                    # Get all db Comics (Limited to the number given by the session variable [10 by default])
                    comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)
                    values["comics"] = comics

                # Else show an error message
                else:
                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_add"]  # Error message (The addition couldn't be done)

                del aux2, comic_author, roles, id    # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["must_insert_all_author_attributes"]   # Error message (You must insert all author attributes)

            all_comics = ComicBook.query().fetch()  # ALL comics (for the search field)
            values["all_comics"] = all_comics

            del lang, key, comic, keys_page_list, aux_all_keys, aux, aux3, \
                all_comics, offset, all_keys, author_key, role, comics     # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/comics/default.html", **values))  # Go to the comics home page

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

    # Get all authors for the add author
    def get_authors(self):
        authors = Author.query().fetch()
        return authors


app = webapp2.WSGIApplication([], debug=True)
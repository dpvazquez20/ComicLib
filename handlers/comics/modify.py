#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time
import copy

from datetime import datetime
from webapp2_extras import jinja2
from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook, Author
from google.appengine.api import images


""" Modify handler in the comics home page
    Get: redirect to the comics home page 
    Post: it's responsible for modifying the comic data in the database"""
class ModifyComicHandler(BaseHandler):

    # Redirect to the comics home page
    def get(self):
        self.redirect("/comics")

    # Modify an comic
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the comic attributes
            isbn = self.request.get("m_isbn", "")                 # Comic ISBN
            isbn = isbn.encode("utf8")
            title = self.request.get("m_title", "")               # Comic title
            title = title.encode("utf8")
            publisher = self.request.get("m_publisher", "")       # Comic publisher
            publisher = publisher.encode("utf8")
            edition = self.request.get("m_edition", "")           # Comic edition
            edition = edition.encode("utf8")
            plot = self.request.get("m_plot", "")                 # Comic plot
            plot = plot.encode("utf8")
            type = self.request.get("m_type", "")                 # Comic type
            type = type.encode("utf8")
            origin = self.request.get("m_origin", "")             # Comic origin
            origin = origin.encode("utf8")
            value = self.request.get("m_value", "")               # Comic value
            value = value.encode("utf8")
            cover = self.request.get("m_cover", "")               # Comic picture
            save_date = self.request.get("m_save_date", "")       # Comic save date
            save_date = save_date.encode("utf8")

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
            if comic and comic is not None:
                # Check the comic attributes
                if len(isbn) > 0:  # Create the ISBN string
                    isbn = isbn[0: 3] + "-" + isbn[3] + "-" + isbn[4:6] + "-" + isbn[6:12] + "-" + isbn[12]
                    comic.isbn = isbn

                if len(title) > 0:
                    comic.title = title

                if len(publisher) > 0:
                    comic.publisher = publisher

                if len(edition) > 0:
                    comic.edition = edition

                if len(plot) > 0:
                    comic.plot = plot

                if len(type) > 0:
                    if type == "comic" or type == "manga" or type == "anthology":
                        comic.type = type

                if len(origin) > 0:
                    if origin == "american" or origin == "european" or type == "other":
                        comic.origin = origin

                if len(edition) > 0:
                    edition = int(edition)
                    if edition >= 1:
                        comic.edition = edition

                if len(value) > 0:
                    value = float(value)
                    if value >= 0:
                        comic.value = value

                if cover != "":
                    comic.cover = images.resize(cover, 300, 250)

                if save_date != "":
                    save_date = datetime.strptime(save_date, '%Y-%m-%d')
                    comic.save_date = save_date

                aux2 = comic.put()
                time.sleep(1)

                # If the modification was successful
                if aux2 is not None:
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["comic_modified_successfully"]    # Ok message (Comic modified successfully)

                    # Get all db Comics (Limited to the number given by the session variable [10 by default])
                    comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)
                    values["comics"] = comics

                # Else show an error message
                else:
                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_modify"]  # Error message (The modification couldn't be done)

                del aux2    # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["comic_not_modified"]   # Error message (Comic couldn't be modified)

            all_comics = ComicBook.query().fetch()  # ALL comics (for the search field)
            values["all_comics"] = all_comics

            del lang, isbn, key, comic, keys_page_list, aux_all_keys, aux, aux3, title, \
                all_comics, offset, all_keys, publisher, edition, cover, type, origin, plot     # Delete variables to free memory
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
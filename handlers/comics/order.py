#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook, Author


""" Order handler in the comics home page 
    Get: redirect to the comics home page
    Post: it's responsible for ordering the comics list"""
class OrderComicHandler(BaseHandler):

    # Redirect to the comics home page
    def get(self):
        self.redirect("/comics")

    # Order an comic list
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # Initialize variables
            all_keys = list()        # New comic keys list
            comics = None            # Comics list
            all_comics = list()      # ALL comics (for the search field)
            pages = list()           # Pages for the pagination

            # If it's logged in, get the session variables, show the home page
            # Get the order attributes
            order_by = self.request.get("order_by", "")     # Sort option
            order_by = order_by.encode("utf8")
            aux_all_keys = self.request.get("all_keys", "")  # All comic keys list

            if len(aux_all_keys) > 2:
                # Transform the HTML string in a list
                aux_all_keys = self.transform_keys(aux_all_keys)

                # It's necessary to compare the HTML with the query list in order to obtain the desired list, like I said
                comics = ComicBook.query()
                all_comics = copy.copy(comics)        # ALL comics (for the search field)
                all_comics = all_comics.fetch()

                aux = list()
                for comic in comics:  # Get ALL the keys
                    aux.append(comic.key.urlsafe())
                    del comic

                for key in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                    for key2 in aux:
                        if key == str(key2):
                            key2 = ndb.Key(urlsafe=key)
                            all_keys.append(key2)
                            break
                        del key2
                    del key

                del aux  # Delete variables to free memory

                # Get all db comics (Limited to the number given by the session variable [10 by default])
                # Not ordered because it has to respect if the comic used some ordination or filter
                comics = ComicBook.query(ComicBook.key.IN(all_keys))

            # If there is a list of comics and a sort option
            if order_by != "" and comics is not None:
                # Get the number of pages for the pagination
                num_total = len(all_keys)
                num_elems_page = self.session.get('num_elems_page')     # Number of elements (comics) per page
                num_pages = num_total / num_elems_page                  # Number of pages

                if num_pages > 0:
                   # If the rest of the division is above 0
                    if (num_total % num_elems_page) > 0:
                        num_pages = (num_total / num_elems_page) + 1  # It's necessary other page
                    else:
                        num_pages = (num_total / num_elems_page)  # It doesn't need other page

                    # Set the pages for the pagination
                    if num_pages >= self.session.get('pages_to_show'):
                        for i in range(1, self.session.get('pages_to_show') + 1):
                            pages.append(i)
                    else:
                        for i in range(1, num_pages + 1):
                            pages.append(i)

                # Order the comic list
                if order_by == "title":
                    comics = comics.order(ComicBook.title)                           # Title A-Z

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))
                elif order_by == "-title":
                    comics = comics.order(-ComicBook.title)                          # Title Z-A

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))
                elif order_by == "save_date":
                    comics = comics.order(ComicBook.save_date)                       # Older first

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))
                elif order_by == "-save_date":
                    comics = comics.order(-ComicBook.save_date)                      # Newest first

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))
                elif order_by == "value":
                    comics = comics.order(ComicBook.value)                          # Value ascendant

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))
                elif order_by == "-value":
                    comics = comics.order(-ComicBook.value)                         # Value descendant

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))
                else:
                    comics = comics.order(-ComicBook.save_date)                      # Newest first

                    # Setting the all comic keys list
                    all_keys = list()
                    for comic in comics:
                        all_keys.append(comic.key.urlsafe())
                        del comic

                    comics = comics.fetch(self.session.get('num_elems_page'))   # Name ascendant

                # Setting the comic keys list (only on the current page)
                keys_page_list = list()
                for comic in comics:
                    keys_page_list.append(comic.key.urlsafe())
                    del comic

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
                    "current_number_page": 1,                                                       # Current number page
                    "pages": pages,                                                                 # Pages for the pagination
                    "last_page": self.session.get('last_page'),                                     # Last page number
                    "keys_page_list": keys_page_list,                                               # Comics keys that are currently in the page
                    "all_keys": all_keys,                                                           # All comic keys
                    "all_comics": all_comics,                                                       # ALL comic (for the search field)
                    "authors": self.get_authors()                                                   # Authors for adding them to the comics
                }

                del order_by, aux_all_keys, all_keys, comics, lang, keys_page_list, pages,\
                    num_total, num_pages, num_elems_page, all_comics    # Delete variables to free memory

                self.session_store.save_sessions(self.response)     # Save sessions
                self.response.write(jinja.render_template("/comics/default.html", **values))   # Go to the comics home page

            # Else redirect to the comics home page
            else:
                del order_by, aux_all_keys, all_keys, comics       # Delete variables to free memory
                self.redirect("/comics")

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

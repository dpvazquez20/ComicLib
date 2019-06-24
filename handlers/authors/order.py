#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import Author, User


""" Order handler in the authors home page 
    Get: redirect to the authors home page
    Post: it's responsible for ordering the authors list"""
class OrderAuthorHandler(BaseHandler):

    # Redirect to the authors home page
    def get(self):
        self.redirect("/authors")

    # Order an author list
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # Initialize variables
            all_keys = list()       # New author keys list
            authors = None          # Authors list
            all_authors = list()    # ALL authors (for the search field)
            pages = list()          # Pages for the pagination

            # If it's logged in, get the session variables, show the home page
            # Get the order attributes
            order_by = self.request.get("order_by", "")     # Sort option
            order_by = order_by.encode("utf8")
            aux_all_keys = self.request.get("all_keys", "")  # All author keys list

            if len(aux_all_keys) > 2:
                # Transform the HTML string in a list
                aux_all_keys = self.transform_keys(aux_all_keys)

                # It's necessary to compare the HTML with the query list in order to obtain the desired list, like I said
                authors = Author.query()
                all_authors = copy.copy(authors)        # ALL authors (for the search field)
                all_authors = all_authors.fetch()

                aux = list()
                for author in authors:  # Get ALL the keys
                    aux.append(author.key.urlsafe())
                    del author

                for key in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                    for key2 in aux:
                        if key == str(key2):
                            key2 = ndb.Key(urlsafe=key)
                            all_keys.append(key2)
                            break
                        del key2
                    del key

                del aux  # Delete variables to free memory

                # Get all db authors (Limited to the number given by the session variable [10 by default])
                # Not ordered because it has to respect if the user used some ordination or filter
                authors = Author.query(Author.key.IN(all_keys))

            # If there is a list of authors and a sort option
            if order_by != "" and authors is not None:
                # Get the number of pages for the pagination
                num_total = len(all_keys)
                num_elems_page = self.session.get('num_elems_page')     # Number of elements (authors) per page
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

                # Order the author list
                if order_by == "name":
                    authors = authors.order(Author.name)  # Name ascendant

                    # Setting the all author keys list
                    all_keys = list()
                    for author in authors:
                        all_keys.append(author.key.urlsafe())
                        del author

                    authors = authors.fetch(self.session.get('num_elems_page'))   # Name ascendant
                elif order_by == "-name":
                    authors = authors.order(-Author.name)  # Name ascendant

                    # Setting the all author keys list
                    all_keys = list()
                    for author in authors:
                        all_keys.append(author.key.urlsafe())
                        del author

                    authors = authors.fetch(self.session.get('num_elems_page'))  # Name descendant
                else:
                    authors = authors.order(Author.name)  # Name ascendant

                    # Setting the all author keys list
                    all_keys = list()
                    for author in authors:
                        all_keys.append(author.key.urlsafe())
                        del author

                    authors = authors.fetch(self.session.get('num_elems_page'))   # Name ascendant

                # Setting the author keys list (only on the current page)
                keys_page_list = list()
                for author in authors:
                    keys_page_list.append(author.key.urlsafe())
                    del author

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
                    "current_number_page": 1,                                                       # Current number page
                    "pages": pages,                                                                 # Pages for the pagination
                    "last_page": self.session.get('last_page'),                                     # Last page number
                    "keys_page_list": keys_page_list,                                               # Authors keys that are currently in the page
                    "all_keys": all_keys,                                                           # All author keys
                    "all_authors": all_authors                                                      # ALL author (for the search field)
                }

                del order_by, aux_all_keys, all_keys, authors, lang, keys_page_list, pages,\
                    num_total, num_pages, num_elems_page, all_authors    # Delete variables to free memory

                self.session_store.save_sessions(self.response)     # Save sessions
                self.response.write(jinja.render_template("/authors/default.html", **values))   # Go to the authors home page

            # Else redirect to the authors home page
            else:
                del order_by, aux_all_keys, all_keys, authors       # Delete variables to free memory
                self.redirect("/authors")

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


app = webapp2.WSGIApplication([], debug=True)

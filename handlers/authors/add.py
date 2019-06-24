#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import Author, User
from google.appengine.ext import ndb


""" Add handler in the authors home page
    Get: redirect to the authors home page 
    Post: it's responsible for adding an author to the database"""
class AddAuthorHandler(BaseHandler):

    # Redirect to the authors home page
    def get(self):
        self.redirect("/authors")

    # List all authors
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the author attributes
            name = self.request.get("name", "")                         # Author name
            name = name.encode("utf8")
            keys_page_list = self.request.get("keys_page_list", "")     # Author keys (only authors in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the author keys (for the order field)

            # Initialize variables
            all_keys = list()                                           # All the author keys (for the order field)
            all_authors = list()                                        # All authors (for the search field)
            aux = list()                                                # Support list
            aux3 = list()                                               # Support list

            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')  # Number of elements to ignore in the query

            # If the current page isn't empty
            if len(keys_page_list) > 2:
                # Transform the HTML string in a list
                aux_all_keys = self.transform_keys(aux_all_keys)

                authors = Author.query()
                all_authors = copy.copy(authors)  # ALL authors (for the search field)
                all_authors = all_authors.fetch()

                for author in authors:  # Get ALL the keys
                    aux.append(author.key.urlsafe())
                    del author

                for key in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                    for key2 in aux:
                        if key == str(key2):
                            key2 = ndb.Key(urlsafe=key)
                            aux3.append(key2)
                            all_keys.append(key2.urlsafe())
                            break
                        del key2
                    del key

                # Get db authors
                authors = Author.query(Author.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

            # If empty
            else:
                authors = list()

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            keys_page_list = list()

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
                "keys_page_list": keys_page_list,                                               # Author keys that are currently in the page
                "all_keys": all_keys,                                                           # All author keys
                "all_authors": all_authors                                                      # ALL author (for the search field)
            }

            # If the user enters all the attributes (the database can have more than one author with the same name)
            if len(name) > 0:
                # Add the new author to the home page
                author = Author(name=name)
                aux2 = author.put()
                time.sleep(1)

                # If the author was successfully added
                if aux2 is not None:
                    # Adding the new author and its key to the lists
                    aux3.append(author.key)
                    all_keys.append(author.key.urlsafe())
                    all_authors.append(author)

                    # Setting pagination
                    ##############################################################################################
                    pages_to_show = self.session.get('pages_to_show')   # Number of pages that shows the pagination
                    pages = list()  # Pages for the pagination (it's a list because of django for templates)

                    # Get all db authors (Limited to the number given by the session variable [10 by default])
                    authors = Author.query(Author.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

                    # Setting the new keys list for the authors currently in the page (allows to use the "Delete page" button)
                    for author in authors:
                        keys_page_list.append(author.key.urlsafe())
                        del author

                    num_total = len(all_authors)  # Total number of elements

                    # If the total number of elements is above 0 do the pagination
                    if num_total > 0:
                        # Get the number of pages for the pagination
                        num_elems_page = self.session.get('num_elems_page')  # Number of elements (authors) per page
                        num_pages = num_total / num_elems_page               # Number of pages

                        # If there are less elements than session["num_elems_page"]
                        if num_pages == 0:
                            num_pages = 1  # At least one page
                        # Else
                        else:
                            # If the rest of the division is above 0
                            if (num_total % num_elems_page) > 0:
                                num_pages = (num_total / num_elems_page) + 1    # It's necessary other page
                            else:
                                num_pages = (num_total / num_elems_page)        # It doesn't need other page

                        self.session['last_page'] = num_pages  # Last page

                        # Set the pages for the pagination
                        for i in range(1, num_pages + 1):
                            pages.append(i)

                        # Set number of pages for the pagination (pagination only shows 3 pages)
                        current_number_page = self.session.get('current_number_page')
                        # If the current page is 1
                        if current_number_page == 1:
                            pages = pages[0:pages_to_show]  # Shows pages 1,2,3
                        # If the current page is the final page
                        elif current_number_page == num_pages:  # Shows the last three pages
                            if (num_pages - pages_to_show) >= 0:
                                pages = pages[(num_pages - pages_to_show):]
                            else:
                                pages = pages[0:pages_to_show]
                        # Else
                        else:
                            pages = pages[(current_number_page - 2):(current_number_page + 1)]  # Show the current, last and next pages

                        self.session['pages'] = pages  # Pages for the pagination

                        # Variables to be sent to the HTML page
                        values["authors"] = authors                             # Authors
                        values["pages"] = self.session.get('pages')             # Pages for the pagination
                        values["last_page"] = self.session.get('last_page')     # Last page number

                        del num_elems_page, num_pages, current_number_page  # Delete variables to free memory
                    ###########################################################################################
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["author_added_successfully"]   # Ok message (Author added successfully)
                    values["keys_page_list"] = keys_page_list                  # Authors keys that are currently in the page
                    values["all_keys"] = all_keys                              # All author keys
                    values["all_authors"] = all_authors                        # ALL author (for the search field)

                    del pages_to_show, pages, authors, num_total    #  Delete variables to free memory

                # If wasn't successfully added
                else:
                    del author, aux2        # Delete variables to free memory

                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_add"]  # Error message (The addition failed)

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["must_insert_all_author_attributes"]   # Error message (You must enter all author data)

            del lang, name, offset, keys_page_list, aux_all_keys, all_keys, all_authors, aux, aux3    # Delete variables to free memory
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


app = webapp2.WSGIApplication([], debug=True)
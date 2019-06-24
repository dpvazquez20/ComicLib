#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import ComicBook, User, Author


""" Main handler in the comics home page 
    Get: it's responsible for showing the comic home page with a comic list (always check if an admin is logged in)
    Post: it's responsible for moving the comics list with the pagination"""
class ComicHomeHandler(BaseHandler):

    # List all comics
    def get(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in. If it's logged in, show the home page
        if self.session.get('session_role') == 'admin':
            # Initialize variables
            pages_to_show = self.session.get('pages_to_show')       # Number of pages that shows the pagination
            pages = list()                                          # Pages for the pagination (it's a list because of django for templates)
            self.session['current_number_page'] = 1                 # Session current number page
            all_keys = list()                                       # All comic keys
            keys_page_list = list()                                 # Comic keys currently in the page

            # Get all db comics (Limited to the number given by the session variable [10 by default])
            comics = ComicBook.query().order(-ComicBook.save_date)                  # All comics ordered by save date
            all_comics = copy.copy(comics)                                          # ALL comics (for the search field)
            all_comics = all_comics.fetch()
            num_total = len(all_comics)                                  # Total number of elements

            self.session['page_name'] = "/comics"  # Current page name
            self.session['num_elems_page'] = 10  # Amount of elements

            # Get ALL the comic keys (they are necessary to do the order and filter)
            for comic in comics:
                all_keys.append(comic.key.urlsafe())
                del comic

            # If the total number of elements is above 0 do the pagination
            if num_total > 0:
                # Get the number of pages for the pagination
                num_elems_page = self.session.get('num_elems_page')     # Number of elements (comics) per page
                num_pages = num_total / num_elems_page                  # Number of pages

                comics = comics.fetch(self.session.get('num_elems_page'))  # Ordered by name

                # If there are less elements than session["num_elems_page"]
                if num_pages == 0:
                    num_pages = 1       # At least one page
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
                current_number_page = 1
                # If the current page is 1
                if current_number_page == 1:
                    pages = pages[0:pages_to_show]          # Shows pages 1,2,3
                # If the current page is the final page
                elif current_number_page == num_pages:      # Shows the last three pages
                    if (num_pages - pages_to_show) >= 0:
                        pages = pages[(num_pages - pages_to_show):]
                    else:
                        pages = pages[0:pages_to_show]
                # Else
                else:
                    pages = pages[(current_number_page - 1):(current_number_page + 1)]    # Show the current, last and next pages

                self.session['pages'] = pages  # Pages for the pagination

                # Setting the keys list to allow the use of the "Delete page" button
                for comic in comics:
                    keys_page_list.append(comic.key.urlsafe())
                    del comic

                del num_elems_page, num_pages, current_number_page, pages      # Delete variables to free memory

            # If num_total < 0
            else:
                comics = all_comics

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
                "pages": self.session.get('pages'),                                             # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # Comics keys that are currently in the page
                "all_keys": all_keys,                                                           # All comic keys
                "all_comics": all_comics,                                                       # ALL comics (for the search field)
                "authors": self.get_authors()                                                   # Authors for adding them to the comics
            }

            del num_total, pages_to_show, keys_page_list, all_keys, lang, comics, all_comics  # Delete variables to free memory

            self.session_store.save_sessions(self.response)     # Save sessions
            self.response.write(jinja.render_template("/comics/default.html", **values))   # Go to the comics home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")


    # Move between the comics list with the pagination
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in. If it's logged in, show the home page
        if self.session.get('session_role') == 'admin':
            pages_to_show = self.session.get('pages_to_show')  # Number of pages that shows the pagination
            pages = list()  # Pages for the pagination (it's a list because of django for templates)

            # Retrieve the page number
            page_number = self.request.get("page", self.session.get('current_number_page'))
            page_number = int(page_number)

            # If the page number sent by HTML is above 0
            if page_number > 0:
                # Initialize variables
                all_keys = list()        # New comic keys list
                comics = list()          # Comics list
                aux3 = list()            # All comic keys support list
                all_comics = list()      # ALL comics (for the search field)

                # Set the offset for the query (offset allows to ignore an amount of query results given by its value)
                num_elems_page = self.session.get('num_elems_page')
                offset = num_elems_page * (page_number - 1)

                # Get ALL keys from ALL comics (I do this because I want to maintain the ordinations and filters done in the list)
                aux_all_keys = self.request.get("all_keys", "")    # All comic keys list

                # Check if the comics keys are empty
                if len(aux_all_keys) > 2:
                    # Transform the HTML string in a list
                    aux_all_keys = self.transform_keys(aux_all_keys)

                    # It's necessary to compare the HTML with the query list in order to obtain the desired list, like I said
                    comics = ComicBook.query()
                    all_comics = copy.copy(comics)  # ALL comics (for the search field)
                    all_comics = all_comics.fetch()

                    aux = list()
                    for comic in comics:      # Get ALL the keys
                        aux.append(comic.key.urlsafe())
                        del comic

                    for key in aux_all_keys:    # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                        for key2 in aux:
                            if key == str(key2):
                                key2 = ndb.Key(urlsafe=key)
                                all_keys.append(key2)
                                aux3.append(key2.urlsafe())
                                break
                            del key2
                        del key

                    del aux     # Delete variables to free memory

                    # Get all db comics (Limited to the number given by the session variable [10 by default])
                    # Not ordered because it has to respect if the comic used some ordination or filter
                    comics = ComicBook.query(ComicBook.key.IN(all_keys)).fetch(num_elems_page, offset=offset)

                num_total = len(aux_all_keys)  # Total number of elements

                # Setting all the comic keys
                all_keys = aux3
                del aux3    # Delete variables to free memory

                # If the total number of elements is above 0 do the pagination
                if num_total > 0:
                    # Get the number of pages for the pagination
                    num_pages = num_total / num_elems_page  # Number of pages

                    # If the page number sent by html is less than the last possible page
                    if page_number <= (num_pages + 1):
                        # Update the session current number page
                        self.session['current_number_page'] = page_number
                        current_number_page = page_number

                        # If there are less elements than session["num_elems_page"]
                        if num_pages == 0:
                            num_pages = 1  # At least one page
                        # Else
                        else:
                            # If the rest of the division is above 0
                            if (num_total % num_elems_page) > 0:
                                num_pages = (num_total / num_elems_page) + 1  # It's necessary other page
                            else:
                                num_pages = (num_total / num_elems_page)  # It doesn't need other page

                        self.session['last_page'] = num_pages  # Last page

                        # Set the pages for the pagination
                        for i in range(1, num_pages + 1):
                            pages.append(i)

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

                        # Set the default language of the app
                        if self.session['session_idiom'] == "spa":
                            lang = spa  # Spanish strings
                        elif self.session['session_idiom'] == "eng":
                            lang = eng  # English strings
                        else:
                            lang = eng  # Default english

                        # Setting the keys list to allow the use of the "Delete page" button
                        keys_page_list = list()
                        for comic in comics:
                            keys_page_list.append(comic.key.urlsafe())
                            del comic

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

                        del pages_to_show, page_number, num_elems_page, num_total, offset, \
                            num_pages, current_number_page, pages, keys_page_list, comics, aux_all_keys, all_keys,\
                            all_comics  # Delete variables to free memory

                        self.session_store.save_sessions(self.response)  # Save sessions
                        self.response.write(jinja.render_template("/comics/default.html", **values))  # Go to the comics home page

                    # If it isn't less redirect to comics home page
                    else:
                        del pages_to_show, page_number, pages, num_elems_page, num_total, offset, comics, num_pages, \
                            aux_all_keys, all_comics   # Delete variables to free memory
                        self.redirect("/comics")

                # If the total number is not above 0, redirect to the comics home page
                else:
                    del pages_to_show, page_number, pages, offset, comics, num_elems_page, aux_all_keys  # Delete variables to free memory
                    self.redirect("/comics")

            # If it isn't above redirect to comics home page
            else:
                del pages_to_show, page_number, pages       # Delete variables to free memory
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
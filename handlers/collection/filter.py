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


""" Filter handler in the collection home page 
    Get: redirect to the collection home page
    Post: it's responsible for filtering the comics list"""
class FilterCollectionHandler(BaseHandler):

    # Redirect to the collection home page
    def get(self):
        self.redirect("/collection")

    # Filter an comic list
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in
        if self.session.get('session_role') == 'client':
            # Initialize variables
            all_keys = list()               # New comic keys list
            comics = None                   # Comics list
            all_comics_user = list()        # ALL comics (for the search field)
            pages = list()                  # Pages for the pagination

            # If it's logged in, get the session variables, show the home page
            # Get the filter attributes
            filter_by = self.request.get_all("filter_by[]")     # Filter option
            aux_all_keys = self.request.get("all_keys", "")     # All comic keys list

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            if len(aux_all_keys) > 2:
                # Transform the HTML string in a list
                aux_all_keys = self.transform_keys(aux_all_keys)

                # It's necessary to compare the HTML with the query list in order to obtain the desired list, like I said
                comics = ComicBook.query(ComicBook.users.username == self.session.get('session_name'))
                all_comics_user = copy.copy(comics)        # ALL comics (for the search field)
                all_comics_user = all_comics_user.fetch()

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
            if len(filter_by) > 0 and comics is not None:
                ok_message = lang["filtered_by"] + ": "        # Ok message (filters applied)

                for i in range(0, len(filter_by)):
                    # Filter the comic list
                    if filter_by[i] == "comic" or filter_by[i] == "manga" or filter_by[i] == "anthology":
                        comics = ComicBook.query(ComicBook.key.IN(all_keys)).filter(ComicBook.type == filter_by[i])           # Type male or female
                    elif filter_by[i] == "american" or filter_by[i] == "european" or filter_by[i] == "other":
                        comics = ComicBook.query(ComicBook.key.IN(all_keys)).filter(ComicBook.origin == filter_by[i])         # Origin admin or client
                    elif filter_by[i] == "read" or filter_by[i] == "unread":
                        comics = ComicBook.query(ComicBook.key.IN(all_keys)).filter(ComicBook.users.username == self.session.get("session_name") and ComicBook.users.state == filter_by[i])  # Comic read or unread

                    # Setting the all comic keys list
                    all_keys = list()
                    aux_all_keys = list()
                    if comics.count() > 0:
                        for comic in comics:
                            aux_all_keys.append(comic.key.urlsafe())
                            all_keys.append(comic.key)
                            del comic

                        comics = comics.fetch(self.session.get('num_elems_page'))     # Setting the first page to show
                    else:
                        comics = list()

                    ok_message += lang[filter_by[i]].lower() + ", "      # Update the ok message (the filter applied)

                ok_message = ok_message[:len(ok_message)-2]     # Update the ok message (remove the last ", ")
                all_keys = aux_all_keys

                # Get the number of pages for the pagination
                num_total = len(all_keys)
                num_elems_page = self.session.get('num_elems_page')  # Number of elements (comics) per page
                num_pages = num_total / num_elems_page  # Number of pages

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

                # Setting the comic keys list (only on the current page)
                keys_page_list = list()
                for comic in comics:
                    keys_page_list.append(comic.key.urlsafe())
                    del comic

                all_comics = ComicBook.query().fetch()
                self.get_read_comics(comics)

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
                    "all_comics_user": all_comics_user,                                             # All user comic (for the search field)
                    "all_comics": all_comics,                                                       # ALL comics (for the user search field)
                    "filter_message": ok_message                                                    # Applied filters message
                }

                del filter_by, aux_all_keys, all_keys, comics, lang, keys_page_list, pages,\
                    num_total, num_pages, num_elems_page, all_comics_user, ok_message    # Delete variables to free memory

                self.session_store.save_sessions(self.response)     # Save sessions
                self.response.write(jinja.render_template("/collection/default.html", **values))   # Go to the comics home page

            # Else redirect to the comics home page
            else:
                del filter_by, aux_all_keys, all_keys, comics       # Delete variables to free memory
                self.redirect("/collection")

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

    # Get the comics read by the user
    def get_read_comics(self, comics):
        for comic in comics:
            for user_comicbook in comic.users:
                if user_comicbook.username == self.session.get('session_name'):
                    if user_comicbook.state == "read":
                        comic.is_read = True
                    else:
                        comic.is_read = False
                del user_comicbook
            del comic

app = webapp2.WSGIApplication([], debug=True)

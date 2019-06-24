#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from google.appengine.ext import ndb
from models.db import User, ComicBook, Author


""" Delete handler in the collection home page
    Get: redirect to the collection home page 
    Post: it's responsible for quiting a comic from the database"""
class QuitCollectionComicHandler(BaseHandler):

    # Redirect to the collection home page
    def get(self):
        self.redirect("/collection")

    # Quit a comic
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # If an client is logged in quit the comic
        if self.session.get('session_role') == 'client':
            # Retrieving the comic key
            key = self.request.get("key", "")
            key = ndb.Key(urlsafe=key)
            comic = key.get()  # Get the db comic with that key

            keys_page_list = self.request.get("keys_page_list", "")     # Comic keys (only comics in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the comic keys (for the order field)

            # Initialize variables
            all_keys = list()   # All the comic keys (for the order field)
            aux = list()        # Support variable
            aux3 = list()       # Support variable

            # Transform the HTML string in a list
            aux_all_keys = self.transform_keys(aux_all_keys)

            comics = ComicBook.query(ComicBook.users.username == self.session.get('session_name'))
            all_comics_user = list()

            for comic2 in comics:  # Get ALL the keys
                aux.append(comic2.key.urlsafe())
                del comic2

            for key3 in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                for key2 in aux:
                    if key3 == str(key2):
                        key2 = ndb.Key(urlsafe=key2)
                        aux3.append(key2)
                        all_keys.append(key2.urlsafe())
                        break
                    del key2
                del key3

            # Get db comics
            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')
            comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

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
                "all_comics": all_comics                                                        # ALL comics (for the user search field)
            }

            # If the comic exists
            if comic and comic is not None:
                # Delete the association in the Comic class
                aux4 = list()
                for user_comic in comic.users:
                    if user_comic.username != self.session.get("session_name"):
                        aux4.append(user_comic)
                    del user_comic

                comic.users = aux4
                comic.put()
                del aux4
                time.sleep(1)

                # Deleting the old comic key to the comic keys lists
                all_keys.remove(comic.key.urlsafe())
                aux3.remove(comic.key)

                values["ok_message"] = lang["comic_quited_successfully"]  # Ok message (comic quited successfully)

                # Setting pagination
                ##############################################################################################
                pages_to_show = self.session.get('pages_to_show')  # Number of pages that shows the pagination
                pages = list()  # Pages for the pagination (it's a list because of django for templates)

                # Get all db comics (Limited to the number given by the session variable [10 by default])
                num_total = len(aux3)   # Total number of elements
                if len(aux3) > 0:
                    comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset) # List not empty
                else:
                    comics = list()

                # If the total number of elements is above 0 do the pagination
                if num_total > 0 and len(comics) > 0:
                    # Get the number of pages for the pagination
                    num_elems_page = self.session.get('num_elems_page')  # Number of elements (comics) per page
                    num_pages = num_total / num_elems_page  # Number of pages

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

                    del num_elems_page, num_pages, current_number_page  # Delete variables to free memory

                # If page is empty do the same, but return to the to the last page next to the current page
                elif num_total > 0 and len(comics) == 0:
                    # Get all db comics (Limited to the number given by the session variable [10 by default])
                    offset = (self.session.get('current_number_page') - 2) * self.session.get('num_elems_page')
                    comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

                    # Get the number of pages for the pagination
                    num_elems_page = self.session.get('num_elems_page')  # Number of elements (comics) per page
                    num_pages = num_total / num_elems_page  # Number of pages

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

                    current_number_page = num_pages  # The previous last page doesn't already exist, so it has to be the last page of the new list
                    self.session['last_page'] = num_pages  # Last page

                    # Set the pages for the pagination
                    for i in range(1, num_pages + 1):
                        pages.append(i)

                    # Set number of pages for the pagination (pagination only shows 3 pages)
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

                    self.session['pages'] = pages                               # Pages for the pagination
                    self.session['current_number_page'] = current_number_page   # Current number page

                    del num_elems_page, num_pages, current_number_page  # Delete variables to free memory
                ###########################################################################################

                # Variables to be sent to the html
                values["comics"] = comics                                                   # Comics
                values["pages"] = self.session.get('pages')                                 # Pages for the pagination
                values["last_page"] = self.session.get('last_page')                         # Last page number
                values["all_keys"] = all_keys                                               # All comic keys
                values["current_number_page"] = self.session.get('current_number_page')     # Current number page

                # Setting the comic keys list that are currently in the page
                keys_page_list = list()
                for comic in comics:
                    keys_page_list.append(comic.key.urlsafe())
                values["keys_page_list"] = keys_page_list

                del pages_to_show, pages, num_total  # Delete variables to free memory

            # Else show an error message
            else:
                values["error_message"] = lang["comic_not_quited"]    # Error message (Comic couldn't be quited)

            # Setting the all comics list
            time.sleep(0.5)
            all_comics_user = ComicBook.query(ComicBook.users.username == self.session.get('session_name')).fetch()
            values["all_comics_user"] = all_comics_user

            del key, comic, keys_page_list, aux_all_keys, all_keys, aux, aux3, all_comics_user, offset, comics,\
                lang  # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/collection/default.html", **values))  # Go to the collection home page

        # Else redirect to the login page
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
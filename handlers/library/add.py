#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, ComicBook, Author, Shelving
from google.appengine.ext import ndb
from google.appengine.api import images


""" Add handler in the library home page
    Get: redirect to the library home page 
    Post: it's responsible for adding a shelving to the database"""
class AddShelvingHandler(BaseHandler):

    # Redirect to the shelving home page
    def get(self):
        self.redirect("/library")

    # Add a shelving
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'client':
            # If it's logged in, get the session variables, show the home page
            # Get the shelving attributes
            name = self.request.get("name", "")                           # Shelving name
            name = name.encode("utf8")
            picture = self.request.get("picture", "")                     # Shelving picture

            keys_page_list = self.request.get("keys_page_list", "")     # Comic keys (only comics in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the comic keys (for the order field)

            # Initialize variables
            all_keys = list()                                           # All the comic keys (for the order field)
            aux = list()                                                # Support list
            aux3 = list()                                               # Support list
            shelving_name = list()                                      # Shelving name

            all_comics = ComicBook.query().fetch()

            # Get the shelvings
            shelvings = Shelving.query(Shelving.username == self.session.get('session_name')).order(Shelving.name).fetch()

            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')  # Number of elements to ignore in the query

            # Transform the HTML string in a list
            aux_all_keys = self.transform_keys(aux_all_keys)

            # Get all comics that belongs to the current user
            if not self.session.get("shelving"):
                comics = ComicBook.query(ComicBook.users.username == self.session.get('session_name')).order(ComicBook.users.addition_date)  # All comics ordered by the addition date
                all_comics_user = copy.copy(comics)  # ALL comics (for the search field)
                all_comics_user = all_comics_user.fetch()
            else:
                key = ndb.Key(urlsafe=self.session.get("shelving"))
                comics = ComicBook.query(ComicBook.users.username == self.session.get('session_name'), ComicBook.users.shelving == key).order(ComicBook.users.addition_date)  # Comics in the shelving ordered by the addition date
                shelving = key.get()
                shelving_name = shelving.name
                del shelving
                all_comics_user = ComicBook.query(ComicBook.users.username == self.session.get('session_name')).fetch()  # ALL comics (for the search field)

            for comic in comics:  # Get ALL the keys
                aux.append(comic.key.urlsafe())
                del comic

            for key in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                for key2 in aux:
                    if key == str(key2):
                        key2 = ndb.Key(urlsafe=key)
                        aux3.append(key2)
                        all_keys.append(key2.urlsafe())
                        break
                    del key2
                del key

            # Get db comics
            comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)
            # Get the comics (if --> default, else --> see shelving)
            if not self.session.get('shelving'):
                comics = self.get_comics_read_and_without_shelving(comics)  # Get read comics and the ones that aren't in a shelving
            else:
                self.get_comics_read(comics)  # Get read comics

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
                "comics": comics,                                                               # Comics
                "current_number_page": self.session.get('current_number_page'),                 # Current number page
                "pages": self.session.get('pages'),                                             # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # Comic keys that are currently in the page
                "all_keys": all_keys,                                                           # All comic keys
                "all_comics": all_comics,                                                       # ALL comic (for the user search field)
                "all_comics_user": all_comics_user,                                             # All user comics (for the search field)
                "authors": self.get_authors(),                                                  # Authors for adding them to the comics
                "shelvings": shelvings,                                                         # Shelvings list
                "shelving_name": shelving_name                                                  # Shelving name
            }

            # If the user enters all the attributes (the database can have more than one shelving with the same name)
            if len(name) > 0:
                # Check the comic attributes
                if picture != "":
                    picture = images.resize(picture, 300, 250)
                else:
                    picture = None

                # Add the new shelving to the home page
                shelving = Shelving(name=name, picture=picture, username=self.session.get('session_name'))

                aux2 = shelving.put()
                time.sleep(1)

                # If the shelving was successfully added
                if aux2 is not None:
                    # Adding the new shelving to the list
                    shelvings.append(shelving)

                    # Setting pagination
                    ##############################################################################################
                    pages_to_show = self.session.get('pages_to_show')   # Number of pages that shows the pagination
                    pages = list()  # Pages for the pagination (it's a list because of django for templates)

                    # Get all db comics (Limited to the number given by the session variable [10 by default])
                    comics = ComicBook.query(ComicBook.key.IN(aux3)).order(-ComicBook.save_date).fetch(self.session.get('num_elems_page'), offset=offset)

                    # Setting the new keys list for the comics currently in the page (allows to use the "Delete page" button)
                    for comic in comics:
                        keys_page_list.append(comic.key.urlsafe())
                        del comic

                    num_total = len(all_comics_user)  # Total number of elements

                    # If the total number of elements is above 0 do the pagination
                    if num_total > 0:
                        # Get the number of pages for the pagination
                        num_elems_page = self.session.get('num_elems_page')  # Number of elements (comics) per page
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
                        # Get the comics (if --> default, else --> see shelving)
                        if not self.session.get('shelving'):
                            values["comics"] = self.get_comics_read_and_without_shelving(comics)  # Get read comics and the ones that aren't in a shelving
                        else:
                            self.get_comics_read(comics)  # Get read comics
                            values["comics"] = comics

                        values["pages"] = self.session.get('pages')                             # Pages for the pagination
                        values["last_page"] = self.session.get('last_page')                     # Last page number

                        del num_elems_page, num_pages, current_number_page  # Delete variables to free memory
                    ###########################################################################################
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["shelving_added_successfully"]    # Ok message (shelving added successfully)
                    values["keys_page_list"] = keys_page_list                     # Comics keys that are currently in the page
                    values["all_keys"] = all_keys                                 # All comic keys
                    values["shelvings"] = shelvings                               # Shelvings list

                    del pages_to_show, pages, comics, num_total, shelving    #  Delete variables to free memory

                # If wasn't successfully added
                else:
                    del shelving, aux2        # Delete variables to free memory

                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_add"]  # Error message (The addition failed)

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["must_insert_all_shelving_attributes"]   # Error message (You must enter all shelving data)

            del lang, offset, keys_page_list, aux_all_keys, all_keys, all_comics, aux, aux3, picture,\
                name, shelvings, all_comics_user, shelving_name     # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/library/default.html", **values))  # Go to the comicss home page

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

    # Get the read comics and the ones that aren't in a shelving
    def get_comics_read_and_without_shelving(self, comics):
        if len(comics) > 0:
            aux = list()
            for i in range(0, len(comics)):
                for user_comic in comics[i].users:
                    if user_comic.username == self.session.get('session_name'):
                        if user_comic.state == "read":
                            comics[i].is_read = True
                        else:
                            comics[i].is_read = False
                        if user_comic.shelving is None:
                            aux.append(comics[i])
                    del user_comic
                del i
            return aux

    # Get the read comics
    def get_comics_read(self, comics):
        if len(comics) > 0:
            for i in range(0, len(comics)):
                for user_comic in comics[i].users:
                    if user_comic.username == self.session.get('session_name'):
                        if user_comic.state == "read":
                            comics[i].is_read = True
                        else:
                            comics[i].is_read = False
                    del user_comic
                del i


app = webapp2.WSGIApplication([], debug=True)
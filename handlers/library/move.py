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
from models.db import User, ComicBook, Author, Shelving, User_ComicBook


""" Move handler in the library home page
    Get: redirect to the library home page 
    Post: it's responsible for moving the comic book data in the database"""
class MoveComicHandler(BaseHandler):

    # Redirect to the library home page
    def get(self):
        self.redirect("/library")

    # Move the comic
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in
        if self.session.get('session_role') == 'client':
            # If it's logged in, get the session variables, show the home page
            # Get the attributes
            key = self.request.get("comic_key", "")
            key = ndb.Key(urlsafe=key)
            comic = key.get()      # Get the comic with that key

            key = self.request.get("shelving_key", "")  # Shelving key
            if key == "None":
                key = None
            elif len(key) > 0 and key != "None":
                key = ndb.Key(urlsafe=key)

            keys_page_list = self.request.get("keys_page_list", "")     # Comic keys (only comics in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the comic keys (for the order field)

            # Initialize variables
            aux = list()                # Support variable
            aux3 = list()               # Support variable
            all_comics = list()         # List with all comics (for the search field)
            shelving_name = list()      # Shelving name

            # Get the user shelvings
            shelvings = Shelving.query(Shelving.username == self.session.get("session_name")).order(Shelving.name).fetch()

            # Transform the HTML string in a list
            all_keys = copy.copy(aux_all_keys)
            aux_all_keys = self.transform_keys(aux_all_keys)

            # Get all comics that belongs to the current user
            if not self.session.get("shelving"):
                comics = ComicBook.query(ComicBook.users.username == self.session.get('session_name')).order(ComicBook.users.addition_date)  # All comics ordered by the addition date
                all_comics_user = copy.copy(comics)  # ALL comics (for the search field)
                all_comics_user = all_comics_user.fetch()
            else:
                key2 = ndb.Key(urlsafe=self.session.get("shelving"))
                comics = ComicBook.query(ComicBook.users.username == self.session.get('session_name'), ComicBook.users.shelving == key2).order(ComicBook.users.addition_date)  # Comics in the shelving ordered by the addition date
                shelving = key2.get()
                shelving_name = shelving.name
                del shelving, key2
                all_comics_user = ComicBook.query(ComicBook.users.username == self.session.get('session_name')).fetch()  # ALL comics (for the search field)

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
                "all_comics": all_comics,                                                       # ALL comic (for the user search field)
                "authors": self.get_authors(),                                                  # Authors for adding them to the comics
                "all_comics_user": all_comics_user,                                             # All user comics (for the user search field)
                "shelvings": shelvings,                                                         # Shelvings
                "shelving_name": shelving_name                                                  # Shelving name
            }

            # If the key is from an shelving
            if comic and comic is not None and key != "":
                # Move the comic book
                user_comics = User_ComicBook.query(User_ComicBook.username == self.session.get("session_name"), User_ComicBook.id_aux == comic.key)
                for user_comic in comic.users:
                    # Update the Comic.users row
                    if user_comic.username == self.session.get("session_name"):
                        user_comic.shelving = key
                        comic.put()
                    break

                # Update the Comic.Users
                for user_comic in user_comics:
                    user_comic.shelving = key
                    user_comic.put()
                    del user_comic
                    break

                aux2 = comic.put()
                time.sleep(1)

                # If the modification was successful
                if aux2 is not None:
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["comic_moved_successfully"]    # Ok message (Comic moved successfully)

                    # Get the comics (if --> default, else --> see shelving)
                    if not self.session.get('shelving'):
                        comics = ComicBook.query(ComicBook.key.IN(aux3)).fetch(self.session.get('num_elems_page'),offset=offset)
                        comics = self.get_comics_read_and_without_shelving(comics)  # Get read comics and the ones that aren't in a shelving
                    else:
                        comics = ComicBook.query(ComicBook.users.username == self.session.get("session_name"), ComicBook.users.shelving == ndb.Key(urlsafe=self.session.get("shelving"))).fetch(self.session.get('num_elems_page'),offset=offset)
                        self.get_comics_read(comics)  # Get read comics

                    values["comics"] = comics

                    # Update the keys_page_list
                    keys_page_list = list()
                    for comic in comics:
                        keys_page_list.append(comic.key.urlsafe())
                    values["keys_page_list"] = keys_page_list

                # Else show an error message
                else:
                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_move"]  # Error message (The modification couldn't be done)

                del aux2, user_comics    # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["comic_not_moved"]   # Error message (Comic couldn't be moved)

            all_comics = ComicBook.query().fetch()  # ALL comics (for the search field)
            values["all_comics"] = all_comics

            del lang, key, keys_page_list, aux_all_keys, aux, aux3, \
                all_comics, offset, all_keys, all_comics_user, shelvings, comic, shelving_name     # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/library/default.html", **values))  # Go to the library home page

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
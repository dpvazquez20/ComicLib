#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import ComicBook, User


""" Main handler in the home page 
    Get: it's responsible for showing the home page (always check if a user is logged in)"""
class HomeHandler(BaseHandler):

    # Default
    def get(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the user is logged in
        if self.session.get('session_role') == 'admin' or self.session.get('session_role') == 'client':
            # Init variables
            comics_to_show = 10         # Amount of new comics to show in the home page
            comics_carousel = 5        # Comics to show in the carousel
            aux = list()

            # If it's logged in, get the session variables, show the home page
            # Set the default language of the app
            if self.session['session_idiom'] == "spa":
                lang = spa  # Spanish strings
            elif self.session['session_idiom'] == "eng":
                lang = eng  # English strings
            else:
                lang = eng  # Default english

            self.session['page_name'] = "/home"      # Current page name

            # Get the comics to show in the home page
            all_comics = ComicBook.query()                                                  # Comics for the search
            comics = all_comics.order(-ComicBook.save_date).fetch(comics_to_show)           # New comics to show
            self.get_own_comics(comics)                                                     # Get the comics added by the user

            # Create a new comic list for the bootstrap carousel
            self.get_new_comics(comics, comics_carousel, comics_to_show, aux)
            comics = aux

            # Variables to be sent to the HTML page
            values = {
                "lang": lang,                                                                   # Language strings
                "session_name": self.session.get('session_name'),                               # User name
                "session_role": self.session.get('session_role'),                               # User role
                "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                "session_genre": self.session.get('session_genre'),                             # User genre
                "all_comics": all_comics,                                                       # All comics
                "carousel": comics,                                                             # New comics
            }

            del lang, comics, all_comics, comics_to_show, comics_carousel, aux    # Delete variables to free memory

            self.session_store.save_sessions(self.response)     # Save sessions
            self.response.write(jinja.render_template("home.html", **values))   # Go to the home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture

    # Create a new comic list for the bootstrap carousel
    def get_new_comics(self, comics, comics_carousel, comics_to_show, aux):
        list_number = len(comics) / comics_carousel    # Amount of lists for the carousel
        mod = len(comics) % comics_carousel            # See if its necessary another list for the carousel
        init = 0                                        # Beginning of a carousel lists
        limit = comics_carousel                        # End of a carousel list

        # Get the carousel lists, each list contains comic_carousel elements
        for i in range(0, list_number):
            aux.append(comics[init:limit])
            init = limit
            limit += comics_to_show
            del i
        if mod > 0:
            aux.append(comics[limit:(limit + mod)])

        del list_number, mod, init, limit

    # Add a attribute in the comics that the current user has added previosly
    def get_own_comics(self, comics):
        for comic in comics:
            for user_comic in comic.users:
                if self.session.get('session_name') == user_comic.username:
                    comic.owned = True
                del user_comic
            del comic

app = webapp2.WSGIApplication([], debug=True)

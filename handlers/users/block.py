#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import copy
from datetime import date, timedelta
import time

from webapp2_extras import jinja2
from google.appengine.ext import ndb
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User


""" Block handler in the users home page
    Get: redirect to the users home page 
    Post: it's responsible for blocking the user in the database"""
class BlockUserHandler(BaseHandler):

    # Redirect to the users home page
    def get(self):
        self.redirect("/users")

    # Block an user
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the user attributes
            days = self.request.get("days", 0)              # Block days
            days = int(days)

            key = self.request.get("key", "")
            key = ndb.Key(urlsafe=key)
            user = key.get()      # Get the user with that key

            keys_page_list = self.request.get("keys_page_list", "")     # User keys (only users in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the user keys (for the order field)

            # Initialize variables
            aux = list()             # Support variable
            aux3 = list()            # Support variable
            all_users = list()       # List with all users (for the search field)

            # Transform the HTML string in a list
            all_keys = copy.copy(aux_all_keys)
            aux_all_keys = self.transform_keys(aux_all_keys)

            users = User.query()
            for user2 in users:  # Get ALL the keys
                aux.append(user2.key.urlsafe())
                del user2

            for key3 in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                for key2 in aux:
                    if key3 == str(key2):
                        key2 = ndb.Key(urlsafe=key2)
                        aux3.append(key2)
                        break
                    del key2
                del key3

            # Get all db users
            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')
            users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

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
                "users": users,                                                                 # Users
                "current_number_page": self.session.get('current_number_page'),                 # Current number page
                "pages": self.session.get('pages'),                                             # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # Users keys that are currently in the page
                "all_keys": all_keys,                                                           # All user keys
                "all_users": all_users                                                          # ALL user (for the search field)
            }

            # If the key is from an user
            if user and user is not None:
                # If block days are correct (between 1 and 365)
                if days > 0 and days < 366:
                    user.blocked = True
                    user.end_block = self.get_block_end_date(days)   # Set the block end date

                    # Set the user
                    aux2 = user.put()
                    time.sleep(1)

                    # If the modification was successful
                    if aux2 is not None:
                        # Variables to be sent to the HTML page
                        values["ok_message"] = lang["user_blocked_successfully"]    # Ok message (User blocked successfully)

                        # Get all db users (Limited to the number given by the session variable [10 by default])
                        users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)
                        values["users"] = users

                    # Else show an error message
                    else:
                        # Variables to be sent to the HTML page
                        values["error_message"] = lang["error_block"]  # Error message (The block couldn't be done)

                    del aux2    # Delete variables to free memory

                # Else show an error message
                else:
                    # Values to be sent to the HTML page
                    values["error_message"] = lang["invalid_block_days"]  # Error message (Days have to be between 1 and 365)

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["user_not_blocked"]   # Error message (User couldn't be blocked)

            all_users = User.query().fetch()  # ALL users (for the search field)
            values["all_users"] = all_users

            del lang, key, user, keys_page_list, aux_all_keys, aux, aux3, users, \
                all_users, offset, all_keys, days     # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/users/default.html", **values))  # Go to the users home page

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

    # Get the block end date
    def get_block_end_date(self, num_days):
        now = date.today()      # Current date
        toret = now + timedelta(days=num_days)  # Adding the days provided by HTML
        del now     # Delete variables to free memory
        return toret

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture

app = webapp2.WSGIApplication([], debug=True)
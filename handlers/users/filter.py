#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User


""" Filter handler in the users home page 
    Get: redirect to the users home page
    Post: it's responsible for filtering the users list"""
class FilterUserHandler(BaseHandler):

    # Redirect to the users home page
    def get(self):
        self.redirect("/users")

    # Filter an user list
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # Initialize variables
            all_keys = list()       # New user keys list
            users = None            # Users list
            all_users = list()      # ALL users (for the search field)
            pages = list()          # Pages for the pagination

            # If it's logged in, get the session variables, show the home page
            # Get the filter attributes
            filter_by = self.request.get_all("filter_by[]")     # Filter option
            aux_all_keys = self.request.get("all_keys", "")     # All user keys list

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
                users = User.query()
                all_users = copy.copy(users)        # ALL users (for the search field)
                all_users = all_users.fetch()

                aux = list()
                for user in users:  # Get ALL the keys
                    aux.append(user.key.urlsafe())
                    del user

                for key in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                    for key2 in aux:
                        if key == str(key2):
                            key2 = ndb.Key(urlsafe=key)
                            all_keys.append(key2)
                            break
                        del key2
                    del key

                del aux  # Delete variables to free memory

                # Get all db users (Limited to the number given by the session variable [10 by default])
                # Not ordered because it has to respect if the user used some ordination or filter
                users = User.query(User.key.IN(all_keys))

            # If there is a list of users and a sort option
            if len(filter_by) > 0 and users is not None:
                ok_message = lang["filtered_by"] + ": "        # Ok message (filters applied)

                for i in range(0, len(filter_by)):
                    # Filter the user list
                    if filter_by[i] == "male" or filter_by[i] == "female" or filter_by[i] == "not_defined":
                        users = User.query(User.key.IN(all_keys)).filter(User.genre == filter_by[i])        # Genre male or female
                    elif filter_by[i] == "admin" or filter_by[i] == "client":
                        users = User.query(User.key.IN(all_keys)).filter(User.role == filter_by[i])         # Role admin or client

                    # Setting the all user keys list
                    all_keys = list()
                    aux_all_keys = list()
                    if users.count() > 0:
                        for user in users:
                            aux_all_keys.append(user.key.urlsafe())
                            all_keys.append(user.key)
                            del user

                        users = users.fetch(self.session.get('num_elems_page'))     # Setting the first page to show
                    else:
                        users = list()

                    ok_message += lang[filter_by[i]].lower() + ", "      # Update the ok message (the filter applied)

                ok_message = ok_message[:len(ok_message)-2]     # Update the ok message (remove the last ", ")
                all_keys = aux_all_keys

                # Get the number of pages for the pagination
                num_total = len(all_keys)
                num_elems_page = self.session.get('num_elems_page')  # Number of elements (users) per page
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

                # Setting the user keys list (only on the current page)
                keys_page_list = list()
                for user in users:
                    keys_page_list.append(user.key.urlsafe())
                    del user

                # Variables to be sent to the HTML page
                values = {
                    "lang": lang,                                                                   # Language strings
                    "session_name": self.session.get('session_name'),                               # User name
                    "session_role": self.session.get('session_role'),                               # User role
                    "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                    "session_genre": self.session.get('session_genre'),                             # User genre
                    "users": users,                                                                 # Users
                    "current_number_page": 1,                                                       # Current number page
                    "pages": pages,                                                                 # Pages for the pagination
                    "last_page": self.session.get('last_page'),                                     # Last page number
                    "keys_page_list": keys_page_list,                                               # Users keys that are currently in the page
                    "all_keys": all_keys,                                                           # All user keys
                    "all_users": all_users,                                                         # ALL user (for the search field)
                    "ok_message": ok_message                                                        # Ok message (filters applied)
                }

                del filter_by, aux_all_keys, all_keys, users, lang, keys_page_list, pages,\
                    num_total, num_pages, num_elems_page, all_users, ok_message    # Delete variables to free memory

                self.session_store.save_sessions(self.response)     # Save sessions
                self.response.write(jinja.render_template("/users/default.html", **values))   # Go to the users home page

            # Else redirect to the users home page
            else:
                del filter_by, aux_all_keys, all_keys, users       # Delete variables to free memory
                self.redirect("/users")

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

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
from models.db import User
from google.appengine.api import images


""" Modify handler in the users home page
    Get: redirect to the users home page 
    Post: it's responsible for modifying the user data in the database"""
class ModifyUserHandler(BaseHandler):

    # Redirect to the users home page
    def get(self):
        self.redirect("/users")

    # Modify an user
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the user attributes
            email = self.request.get("m_email", "")               # User email
            email = email.encode("utf8")
            password1 = self.request.get("m_password", "")        # User password
            password1 = password1.encode("utf8")
            password2 = self.request.get("m_r_password", "")      # User password
            password2 = password2.encode("utf8")
            name = self.request.get("m_username", "")             # User name
            name = name.encode("utf8")
            genre = self.request.get("m_genre", "")               # User genre
            genre = genre.encode("utf8")
            role = self.request.get("m_role", "")                 # User role
            role = role.encode("utf8")
            picture = self.request.get("m_picture", "")           # User picture

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
                # If there is a genre to modify
                if genre == "male" or genre == "female":
                    user.genre = genre
                # If there is a role to modify
                if role == "admin" or role == "client":
                    user.role = role
                # If there is a picture to modify
                if picture != "":
                    user.picture = images.resize(picture, 250, 250)

                # If there is a name or email to modify
                if len(name) > 0 or len(email) > 0:
                    aux_user = User.query(ndb.OR(User.email == email, User.name == name)).fetch()
                    # Check if the user name already exists
                    if len(aux_user) > 0:
                        values["error_message"] = lang["user_already_exists"]
                    else:
                        if len(email) > 0:
                            user.email = email
                        if len(name) > 0:
                            user.name = name
                    del aux_user     # Delete variables to free memory

                # If there is a password to modify
                if len(password1) > 0 and len(password2) > 0:
                    if self.check_passwords(password1, password2):
                        user.password = password1

                # Set the user
                aux2 = user.put()
                time.sleep(1)

                # If the modification was successful
                if aux2 is not None:
                    # Variables to be sent to the HTML page
                    values["ok_message"] = lang["user_modified_successfully"]    # Ok message (User modified successfully)

                    # Get all db users (Limited to the number given by the session variable [10 by default])
                    users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)
                    values["users"] = users

                # Else show an error message
                else:
                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["error_modify"]  # Error message (The modification couldn't be done)

                del aux2    # Delete variables to free memory

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["user_not_modified"]   # Error message (User couldn't be modified)

            all_users = User.query().fetch()  # ALL users (for the search field)
            values["all_users"] = all_users

            del lang, name, key, user, keys_page_list, aux_all_keys, aux, aux3, users, \
                all_users, offset, all_keys, email, role, picture, genre, password1, password2     # Delete variables to free memory
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

    # Check the password given by HTML
    def check_passwords(self, pass1, pass2):
        toret = True
        if len(pass1) < 8 or len(pass1) > 20:  # Password length
            toret = False
        if len(pass2) < 8 or len(pass2) > 20:  # Password length
            toret = False
        if pass1 != pass2:  # Passwords equals
            toret = False
        return toret

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture


app = webapp2.WSGIApplication([], debug=True)
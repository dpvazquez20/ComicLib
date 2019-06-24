#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import time
import copy
import random

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from handlers.elements.function import encryptPassword
from models.db import User
from google.appengine.ext import ndb
from google.appengine.api import images


""" Add handler in the users home page
    Get: redirect to the users home page 
    Post: it's responsible for adding an user to the database"""
class AddUserHandler(BaseHandler):

    # Redirect to the users home page
    def get(self):
        self.redirect("/users")

    # List all users
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the user attributes
            email = self.request.get("email", "")                           # User email
            email = email.encode("utf8")
            password1 = self.request.get("password", "")                    # User password
            password1 = password1.encode("utf8")
            password2 = self.request.get("r_password", "")                  # User password
            password2 = password2.encode("utf8")
            name = self.request.get("username", "")                         # User name
            name = name.encode("utf8")
            genre = self.request.get("genre", "")                           # User genre
            genre = genre.encode("utf8")
            role = self.request.get("role", "")                             # User role
            role = role.encode("utf8")
            picture = self.request.get("picture", "")                       # User picture

            keys_page_list = self.request.get("keys_page_list", "")     # User keys (only Users in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the user keys (for the order field)

            # Initialize variables
            all_keys = list()                                           # All the user keys (for the order field)
            all_users = list()                                          # All users (for the search field)
            aux = list()                                                # Support list
            aux3 = list()                                               # Support list

            offset = (self.session.get('current_number_page') - 1) * self.session.get('num_elems_page')  # Number of elements to ignore in the query

            # If the current page isn't empty
            if len(keys_page_list) > 2:
                # Transform the HTML string in a list
                aux_all_keys = self.transform_keys(aux_all_keys)

                users = User.query()
                all_users = copy.copy(users)  # ALL users (for the search field)
                all_users = all_users.fetch()

                for user in users:  # Get ALL the keys
                    aux.append(user.key.urlsafe())
                    del user

                for key in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                    for key2 in aux:
                        if key == str(key2):
                            key2 = ndb.Key(urlsafe=key)
                            aux3.append(key2)
                            all_keys.append(key2.urlsafe())
                            break
                        del key2
                    del key

                # Get db users
                users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

            # If empty
            else:
                users = list()

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
                "users": users,                                                                 # Users
                "current_number_page": self.session.get('current_number_page'),                 # Current number page
                "pages": self.session.get('pages'),                                             # Pages for the pagination
                "last_page": self.session.get('last_page'),                                     # Last page number
                "keys_page_list": keys_page_list,                                               # User keys that are currently in the page
                "all_keys": all_keys,                                                           # All user keys
                "all_users": all_users                                                          # ALL user (for the search field)
            }

            # If the user enters all the attributes (the database can have more than one user with the same name)
            if len(email) > 0 and self.check_passwords(password1, password2) and len(role) > 0:
                user = User.query(ndb.OR(User.email == email, User.name == name)).fetch()

                # If an user already exists, show an error message
                if len(user) == 0:
                    # Check the user attributes
                    if len(name) == 0:      # Create an username if the user didn't write one
                        pos = email.find("@")
                        name = email[:pos]
                        # Check if the new user name already exists
                        aux_user = User.query(User.name == name).fetch()
                        aux_name = name
                        while len(aux_user) > 0:
                            aux_name = name + str(random.randint(0,999))
                            aux_user = User.query(User.name == aux_name).fetch()
                            print(aux_name)
                        name = aux_name                 # Setting the new user name
                        del pos, aux_user, aux_name     # Delete variables to free memory
                    elif len(name) > 20:
                        name = name[0:20]

                    if role != "admin" and role != "client":
                        role = "client"

                    if len(genre) == 0 and genre != "male" and genre != "female":
                        genre = "not_defined"

                    if picture != "":
                        picture = images.resize(picture, 250, 250)
                    else:
                        picture = None

                    # Add the new user to the home page
                    user = User(email=email, password=encryptPassword(password1), name=name, genre=genre, role=role, picture=picture)
                    aux2 = user.put()
                    time.sleep(1)

                    # If the user was successfully added
                    if aux2 is not None:
                        # Adding the new user and its key to the lists
                        aux3.append(user.key)
                        all_keys.append(user.key.urlsafe())
                        all_users.append(user)

                        # Setting pagination
                        ##############################################################################################
                        pages_to_show = self.session.get('pages_to_show')   # Number of pages that shows the pagination
                        pages = list()  # Pages for the pagination (it's a list because of django for templates)

                        # Get all db users (Limited to the number given by the session variable [10 by default])
                        users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

                        # Setting the new keys list for the users currently in the page (allows to use the "Delete page" button)
                        for user in users:
                            keys_page_list.append(user.key.urlsafe())
                            del user

                        num_total = len(all_users)  # Total number of elements

                        # If the total number of elements is above 0 do the pagination
                        if num_total > 0:
                            # Get the number of pages for the pagination
                            num_elems_page = self.session.get('num_elems_page')  # Number of elements (users) per page
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
                            values["users"] = users                                 # Users
                            values["pages"] = self.session.get('pages')             # Pages for the pagination
                            values["last_page"] = self.session.get('last_page')     # Last page number

                            del num_elems_page, num_pages, current_number_page  # Delete variables to free memory
                        ###########################################################################################
                        # Variables to be sent to the HTML page
                        values["ok_message"] = lang["user_added_successfully"]     # Ok message (user added successfully)
                        values["keys_page_list"] = keys_page_list                  # Users keys that are currently in the page
                        values["all_keys"] = all_keys                              # All user keys
                        values["all_users"] = all_users                            # ALL user (for the search field)

                        del pages_to_show, pages, users, num_total    #  Delete variables to free memory

                    # If wasn't successfully added
                    else:
                        del user, aux2        # Delete variables to free memory

                        # Variables to be sent to the HTML page
                        values["error_message"] = lang["error_add"]  # Error message (The addition failed)

                # If not exists
                else:
                    del user    # Delete variables to free memory

                    # Variables to be sent to the HTML page
                    values["error_message"] = lang["user_already_exists"]  # Error message (User already exists)

            # Else show an error message
            else:
                # Values to be sent to the HTML page
                values["error_message"] = lang["must_insert_all_user_attributes"]   # Error message (You must enter all user data)

            del lang, name, offset, keys_page_list, aux_all_keys, all_keys, all_users, aux, aux3, email, \
                password1, password2, genre, role, picture       # Delete variables to free memory
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
        if len(pass1) < 8 or len(pass1) > 20:   # Password length
            toret = False
        if len(pass2) < 8 or len(pass2) > 20:   # Password length
            toret = False
        if pass1 != pass2:                      # Passwords equals
            toret = False
        return toret

    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture


app = webapp2.WSGIApplication([], debug=True)
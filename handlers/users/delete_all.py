#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from google.appengine.ext import ndb
from models.db import User


""" Delete handler in the users home page
    Get: redirect to the users home page 
    Post: it's responsible for deleting all the users that are shown in the page"""
class DeleteAllUserHandler(BaseHandler):

    # Redirect to the users home page
    def get(self):
        self.redirect("/users")

    # Delete the users
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # If an admin is logged in delete the user
        if self.session.get('session_role') == 'admin':
            # Retrieving the user key
            keys_page_list = self.request.get("keys_page_list", "")     # User keys (only users in the current page)
            aux_all_keys = self.request.get("all_keys", "")             # All the user keys (for the order field)

            # Initialize variables
            all_keys = list()   # All the user keys (for the order field)
            aux = list()        # Support variable
            aux3 = list()       # Support variable
            aux2 = list()       # Support variable

            # Transform the HTML strings in a list
            aux_all_keys = self.transform_keys(aux_all_keys)
            keys_page_list = self.transform_keys(keys_page_list)

            users = User.query()
            all_users = copy.copy(users)  # ALL users (for the search field)
            all_users = all_users.fetch()

            for user2 in users:  # Get ALL the keys
                aux.append(user2.key.urlsafe())
                del user2

            for key3 in aux_all_keys:  # Compare the "list" given by HTML with aux for making the new all keys list (all_keys)
                for key2 in aux:
                    if key3 == str(key2):
                        key2 = ndb.Key(urlsafe=key2)
                        aux3.append(key2)
                        all_keys.append(key2.urlsafe())
                        break
                    del key2
                del key3

            for key3 in keys_page_list:     # Compare the "list" given by HTML with aux for making the new keys page list (keys_page_list)
                for key2 in aux:
                    if key3 == str(key2):
                        key2 = ndb.Key(urlsafe=key2)
                        aux2.append(key2)
                    del key2
                del key3

            # Get db users
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

            # If the user exists
            if aux3 and len(aux3):
                # Deleting the old user keys to the user keys lists and delete the db users
                for key in aux2:
                    user = key.get()
                    all_keys.remove(user.key.urlsafe())
                    aux3.remove(user.key)
                    user.key.delete()     # Delete db user
                    del key

                values["ok_message"] = lang["users_deleted_successfully"]  # Ok message (users deleted successfully)

                # Setting pagination
                ##############################################################################################
                pages_to_show = self.session.get('pages_to_show')  # Number of pages that shows the pagination
                pages = list()  # Pages for the pagination (it's a list because of django for templates)

                # Get all db users (Limited to the number given by the session variable [10 by default])
                num_total = len(aux3)   # Total number of elements
                if len(aux3) > 0:
                    users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset) # List not empty
                else:
                    users = list()

                # If the total number of elements is above 0 do the pagination
                if num_total > 0 and len(users) > 0:
                    # Get the number of pages for the pagination
                    num_elems_page = self.session.get('num_elems_page')  # Number of elements (users) per page
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
                elif num_total > 0 and len(users) == 0:
                    # Get all db users (Limited to the number given by the session variable [10 by default])
                    offset = (self.session.get('current_number_page') - 2) * self.session.get('num_elems_page')
                    users = User.query(User.key.IN(aux3)).fetch(self.session.get('num_elems_page'), offset=offset)

                    # Get the number of pages for the pagination
                    num_elems_page = self.session.get('num_elems_page')  # Number of elements (users) per page
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
                values["users"] = users                                                     # Users
                values["pages"] = self.session.get('pages')                                 # Pages for the pagination
                values["last_page"] = self.session.get('last_page')                         # Last page number
                values["all_keys"] = all_keys                                               # All user keys
                values["current_number_page"] = self.session.get('current_number_page')     # Current number page

                # Setting the all users list
                all_users = User.query().fetch()
                values["all_users"] = all_users

                # Setting the user keys list that are currently in the page
                keys_page_list = list()
                for user in users:
                    keys_page_list.append(user.key.urlsafe())
                    del user
                values["keys_page_list"] = keys_page_list

                del pages_to_show, pages, num_total  # Delete variables to free memory

            # Else show an error message
            else:
                values["error_message"] = lang["users_not_deleted"]    # Error message (user couldn't be deleted)

            del keys_page_list, aux_all_keys, all_keys, aux, aux3, all_users, offset, users,\
                lang, aux2  # Delete variables to free memory
            self.session_store.save_sessions(self.response)  # Save sessions
            self.response.write(jinja.render_template("/users/default.html", **values))  # Go to the users home page

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


app = webapp2.WSGIApplication([], debug=True)
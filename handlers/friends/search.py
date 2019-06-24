#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, Friend, ComicBook


""" Search handler in the friends home page 
    Get: redirect to the friends home page
    Post: it's responsible for searching an user"""
class SearchFriendHandler(BaseHandler):

    # List all friends
    def get(self):
        self.redirect("/friends")

    # Search an user
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in. If it's logged in, show the home page
        if self.session.get('session_role') == 'client':
            user = User.query(User.name == self.session.get("session_name")).fetch()        # Current user
            # Get the friend id
            search = self.request.get("search", "")

            # If users exists, get friends and friends requests
            if user and len(user) > 0:
                user = user[0]
                all_comics = ComicBook.query()
                comics = copy.copy(all_comics)
                comics = comics.filter(ComicBook.users.username == self.session.get("session_name")).fetch()
                all_comics = all_comics.fetch()
                all_users = User.query(User.role == "client").fetch()

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
                    "all_comics": all_comics,                                                       # ALL comic (for the users search field)
                    "all_users": all_users,                                                         # ALL users (for the search field)
                    "comics": comics,                                                               # Current user comics (for the borrowinngs)
                }

                # If the key is valid
                if len(search) > 0:
                    search = ndb.Key(urlsafe=search)
                    search = search.get()

                    # If the user exists, see if it's a friend, request other user
                    if search and search is not None:
                        all = Friend.query(Friend.who_ask == search.key, Friend.who_answer == user.key).fetch()
                        aux = copy.copy(all)
                        all = Friend.query(Friend.who_ask == user.key, Friend.who_answer == search.key).fetch()
                        all += aux
                        is_friend = None
                        aux = None

                        # See if the user is already a friend or has a friend request
                        for elem in all:
                            if elem.who_ask == search.key and elem.who_answer == user.key:
                                is_friend = elem.is_friend
                                aux = True
                                break
                            else:
                                aux = False
                            del elem

                        # Variables to be shown in the HTML page
                        if is_friend is None and aux is None:
                            others = list()
                            others.append(search)
                            values["others"] = others
                            del others
                        else:
                            if is_friend == False and aux == True:
                                requests = list()
                                requests.append(search)
                                values["requests"] = requests
                                del requests
                            elif is_friend == True and aux == True:
                                friends = list()
                                friends.append(search)
                                values["friends"] = friends
                                del friends

                        del all, is_friend, aux      # Delete variables to free memory

                    # Else show a message
                    else:
                        values["ok_message"] = lang["search_not_results"]   # There aren't any search result

                # Else show a message
                else:
                    values["ok_message"] = lang["search_not_results"]       # There aren't any search result


                del lang, user, all_comics, all_users, search
                self.session_store.save_sessions(self.response)  # Save sessions
                self.response.write(jinja.render_template("/friends/default.html", **values))  # Go to the friends home page

            # Else redirect to the login page
            else:
                del user        # Delete variables to free memory
                self.redirect("/login")

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")


    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture


app = webapp2.WSGIApplication([], debug=True)
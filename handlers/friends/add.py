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


""" Add handler in the friends home page 
    Get: redirect to the friends home page
    Post: it's responsible for adding a new friend"""
class AddFriendHandler(BaseHandler):

    # List all friends
    def get(self):
        self.redirect("/friends")

    # Add a new friend
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in. If it's logged in, show the home page
        if self.session.get('session_role') == 'client':
            user = User.query(User.name == self.session.get("session_name")).fetch()        # Current user
            # Get the friend id
            who_ask = self.request.get("who_ask", "")       # Who made the friend request

            # If users exists, get friends and friends requests
            if user and len(user) > 0:
                user = user[0]
                # Get db friends and friend requests
                all = Friend.query().order(-Friend.addition_date)

                # Db friends
                friends = copy.copy(all)
                friends = friends.filter(Friend.is_friend == True)
                friends = friends.filter(ndb.OR(Friend.who_ask == user.key, Friend.who_answer == user.key))
                friends = friends.order(-Friend.addition_date)
                aux = list()
                for friend in friends:
                    if friend.who_answer != user.key:
                        aux.append(friend.who_answer.get())
                    elif friend.who_ask != user.key:
                        aux.append(friend.who_ask.get())
                    del friend
                friends = aux

                # Db friends requests
                requests = copy.copy(all)
                requests = requests.filter(Friend.is_friend == False)
                requests = requests.filter(Friend.who_answer == user.key)
                requests = requests.order(-Friend.addition_date)
                aux = list()
                for request in requests:
                    aux.append(request.who_ask.get())
                    del request
                requests = aux

                # Set the default language of the app
                if self.session['session_idiom'] == "spa":
                    lang = spa  # Spanish strings
                elif self.session['session_idiom'] == "eng":
                    lang = eng  # English strings
                else:
                    lang = eng  # Default english

                all_comics = ComicBook.query()
                comics = copy.copy(all_comics)
                comics = comics.filter(ComicBook.users.username == self.session.get("session_name")).fetch()
                all_comics = all_comics.fetch()
                all_users = User.query(User.role == "client").fetch()

                # Variables to be sent to the HTML page
                values = {
                    "lang": lang,                                                                   # Language strings
                    "session_name": self.session.get('session_name'),                               # User name
                    "session_role": self.session.get('session_role'),                               # User role
                    "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                    "session_genre": self.session.get('session_genre'),                             # User genre
                    "friends": friends,                                                             # User friends
                    "requests": requests,                                                           # User friend requests
                    "all_comics": all_comics,                                                       # ALL comic (for the users search field)
                    "all_users": all_users,                                                         # ALL users (for the search field)
                    "comics": comics,                                                               # Current user comics (for the borrowinngs)
                }

                # If the key is valid
                if len(who_ask) > 0:
                    who_ask = ndb.Key(urlsafe=who_ask)  # User who made the friend request
                    who_ask = who_ask.get()

                    # If user exists
                    if who_ask != None:
                        # Add a new friend
                        requests2 = copy.copy(all)
                        requests2 = requests2.filter(Friend.who_ask == who_ask.key, Friend.who_answer == user.key).fetch()

                        # If the adding if from a friend request
                        if len(requests2) > 0:
                            for request in requests2:
                                if request.who_ask == who_ask.key:
                                    request.is_friend = True
                                    request.put()
                                    break
                                del request

                            if who_ask in requests:
                                requests.remove(who_ask)    # Remove user from the request list
                            friends.append(who_ask)     # Add user to the friend list

                            values["ok_message"] = lang["friend_added_successfully"] + " " + str(who_ask.name)  # Friend added successfully

                        # Else (a new friend request)
                        else:
                            request = Friend(who_ask=user.key, who_answer=who_ask.key)
                            request.put()
                            del request
                            values["ok_message"] = lang["request_added_successfully"] + " " + str(who_ask.name)  # Friend added successfully

                        # Values to be sent to the HTML page
                        values["friends"] = friends
                        values["requests"] = requests

                        del requests2 # Delete variables to free memory

                    # Else show an error message
                    else:
                        values["error_message"] = lang["error_add"]  # The adding couldn't be done

                # Else show an error message
                else:
                    values["error_message"] = lang["friend_not_added"]    # Friend couldn't be added

                del lang, user, all, friends, requests, aux, all_comics, all_users, who_ask
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
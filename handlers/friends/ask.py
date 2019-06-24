#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, Friend, ComicBook, Borrowing


""" Ask for comic handler in the friends home page 
    Get: redirect to the friends home page
    Post: it's responsible for asking for a comic"""
class AskFriendHandler(BaseHandler):

    # List all friend
    def get(self):
        self.redirect("/friends")

    # Ask for a comicbook
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in. If it's logged in, ask for
        if self.session.get('session_role') == 'client':
            user = User.query(User.name == self.session.get("session_name")).fetch()        # Current user

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

                friend = self.request.get("friend", "")         # Friend
                comic = self.request.get("comic_key", "")       # Comic

                # If the friend is valid
                if len(friend) > 0 and len(comic) > 0:
                    friend = ndb.Key(urlsafe=friend)
                    friend = friend.get()
                    comic = ndb.Key(urlsafe=comic)
                    comic = comic.get()

                    # If user exists
                    if friend is not None and comic is not None:
                        borrowing = Borrowing.query(Borrowing.who_want == user.key, Borrowing.who_borrow == friend.key, Borrowing.comic == comic.key).fetch()

                        # If the comic wasn't already asked to this user
                        if len(borrowing) == 0:
                            # Add a new borrowing
                            borrowing = Borrowing(who_want=user.key, who_borrow=friend.key, comic=comic.key)
                            borrowing = borrowing.put()

                            # If the adding was successful
                            if borrowing is not None:
                                values["ok_message"] = lang["ask_for_added_successfully"] + " " + str(friend.name)  # Borrowing added successfully

                            # Else show an error message
                            else:
                                values["error_message"] = lang["error_add"]

                        # Else do nothing
                        else:
                            values["ok_message"] = lang["ask_for_already_added"] + " " + str(friend.name)  # Borrowing already added

                        del borrowing  # Delete variables to free memory

                    # Else show an error message
                    else:
                        values["error_message"] = lang["error_add"]  # The adding couldn't be done

                # Else show an error message
                else:
                    values["error_message"] = lang["ask_for_not_added"]    # Borrowing couldn't be added

                del lang, user, all, friends, requests, aux, all_comics, all_users, friend, comic
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
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import google.appengine.ext.ndb as ndb
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, Borrowing, ComicBook


""" Quit handler in the borrowings home page 
    Get: it's responsible for deleting a borrowing
    Post: it's responsible for showing the borrowings home page"""
class BorrowingsQuitHandler(BaseHandler):

    # List all borrowings
    def get(self):
        self.redirect("/borrowings")

    # Add a new borrowing
    def post(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in. If it's logged in, delete a borrowing
        if self.session.get('session_role') == 'client':
            user = User.query(User.name == self.session.get("session_name")).fetch()        # Current user

            # If users exists, get borrowings
            if user and len(user) > 0:
                user = user[0]
                # Get db borrowings
                all = Borrowing.query()

                # Db borrowed comics
                borrow_comics = copy.copy(all)
                borrow_comics = borrow_comics.filter(Borrowing.is_borrowed == True)
                borrow_comics = borrow_comics.filter(Borrowing.who_borrow == user.key)
                aux = list()
                for borrow_comic in borrow_comics:
                    aux2 = borrow_comic.comic.get()
                    aux3 = borrow_comic.who_want.get()
                    aux2.owner_name = aux3.name
                    aux.append(aux2)
                    del borrow_comic, aux2, aux3
                borrow_comics = aux

                # Db asked comics
                orders = copy.copy(all)
                orders = orders.filter(Borrowing.is_borrowed == False)
                orders = orders.filter(Borrowing.who_borrow == user.key)
                aux = list()
                for order in orders:
                    aux2 = order.comic.get()
                    aux3 = order.who_want.get()
                    aux2.owner_name = aux3.name
                    aux.append(aux2)
                    del order, aux2, aux3
                orders = aux

                # Db comics that user ask for
                own = copy.copy(all)
                own = own.filter(Borrowing.is_borrowed == True)
                own = own.filter(Borrowing.who_want == user.key)
                aux = list()
                for elem in own:
                    aux2 = elem.comic.get()
                    aux3 = elem.who_borrow.get()
                    aux2.owner_name = aux3.name
                    aux.append(aux2)
                    del elem, aux2, aux3
                own = aux

                # Set the default language of the app
                if self.session['session_idiom'] == "spa":
                    lang = spa  # Spanish strings
                elif self.session['session_idiom'] == "eng":
                    lang = eng  # English strings
                else:
                    lang = eng  # Default english

                all_comics = ComicBook.query().fetch()

                # Variables to be sent to the HTML page
                values = {
                    "lang": lang,                                                                   # Language strings
                    "session_name": self.session.get('session_name'),                               # User name
                    "session_role": self.session.get('session_role'),                               # User role
                    "session_picture": self.get_session_image(self.session.get('session_name')),    # User picture
                    "session_genre": self.session.get('session_genre'),                             # User genre
                    "borrow_comics": borrow_comics,                                                 # Borrowed comics
                    "orders": orders,                                                               # Asked comics
                    "own": own,                                                                     # Comics that current user ask for
                    "all_comics": all_comics,                                                       # ALL comic (for the users search field)
                }

                friend = self.request.get("friend_name", "")    # Friend
                friend = User.query(User.name == friend).fetch()
                comic = self.request.get("comic_key", "")       # Comic
                message = self.request.get("message", "")       # Auxiliar variable
                message = message.encode("utf8")

                # If the friend is valid
                if len(friend) > 0 and len(comic) > 0 and len(message):
                    friend = friend[0]
                    comic = ndb.Key(urlsafe=comic)
                    comic = comic.get()

                    # If user exists
                    if friend is not None and comic is not None:
                        # Delete borrowing
                        borrowing = list()
                        if message == "order":
                            borrowing = Borrowing.query(Borrowing.who_want == friend.key, Borrowing.who_borrow == user.key, Borrowing.comic == comic.key).fetch()
                        elif message == "borrowing":
                            borrowing = Borrowing.query(Borrowing.who_want == user.key, Borrowing.who_borrow == friend.key, Borrowing.is_borrowed == True, Borrowing.comic == comic.key).fetch()

                        # If the borrowing exists
                        if len(borrowing) > 0:
                            borrowing = borrowing[0]

                            if message == "borrowing":
                                if borrowing.comic.get() in own:
                                    own.remove(borrowing.comic.get())
                                aux2 = message + "_deleted_successfully"

                                # Values to be sent to the HTML page
                                values["own"] = own
                                values["ok_message"] = lang[aux2] + " " + friend.name   # Borrowing deleted successfully
                                del aux2

                            elif message == "order":
                                if borrowing.comic.get() in orders:
                                    orders.remove(borrowing.comic.get())
                                aux2 = message + "_deleted_successfully"

                                # Values to be sent to the HTML page
                                values["orders"] = orders
                                values["ok_message"] = lang[aux2] + " " + friend.name  # Borrowing deleted successfully
                                del aux2
                            else:
                                values["ok_message"] = lang["delete_done"]  # The deletion could be done

                            borrowing.key.delete()

                        # Else show an error message
                        else:
                            if message == "borrowing" or message == "order":
                                aux2 = message + "_not_deleted"
                                values["error_message"] = lang[aux2] + " " + friend.name     # The deletion couldn't be done
                                del aux2
                            else:
                                values["error_message"] = lang["error_delete"]  # The deletion couldn't be done

                        del borrowing  # Delete variables to free memory

                    # Else show an error message
                    else:
                        if message == "borrowing" or message == "order":
                            aux2 = message + "_not_deleted2"
                            values["error_message"] = lang[aux2]  # The deletion couldn't be done
                            del aux2
                        else:
                            values["error_message"] = lang["error_delete"]  # The deletion couldn't be done

                # Else show an error message
                else:
                    values["error_message"] = lang["error_delete"]  # The deletion couldn't be done

                del lang, user, all, borrow_comics, orders, aux, all_comics, own, friend, comic
                self.session_store.save_sessions(self.response)  # Save sessions
                self.response.write(jinja.render_template("/borrowings/default.html", **values))  # Go to the borrowings home page

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
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import copy

from webapp2_extras import jinja2
from handlers.elements.sessions import BaseHandler
from handlers.lang.spa import lang as spa
from handlers.lang.eng import lang as eng
from models.db import User, Borrowing, ComicBook


""" Main handler in the borrowings home page 
    Get: it's responsible for showing the borrowings home page (always check if an admin is logged in)
    Post: it's responsible for showing the borrowings home page"""
class BorrowingsHomeHandler(BaseHandler):

    # List all borrowings
    def get(self):
        jinja = jinja2.get_jinja2(app=self.app)

        # Check if the client is logged in. If it's logged in, show the home page
        if self.session.get('session_role') == 'client':
            user = User.query(User.name == self.session.get("session_name")).fetch()        # Current user

            # If users exists, get borrowings
            if user and len(user) > 0:
                self.session['page_name'] = "/borrowings"  # Current page name

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

                del lang, user, all, borrow_comics, orders, aux, all_comics, own
                self.session_store.save_sessions(self.response)  # Save sessions
                self.response.write(jinja.render_template("/borrowings/default.html", **values))  # Go to the borrowings home page

            # Else redirect to the login page
            else:
                del user        # Delete variables to free memory
                self.redirect("/login")

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")

    # List all borrowings
    def post(self):
        self.redirect("/borrowings")


    # Get the session user image
    def get_session_image(self, name):
        user = User.query(User.name == name).fetch()
        return user[0].picture


app = webapp2.WSGIApplication([], debug=True)
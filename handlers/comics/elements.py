#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from handlers.elements.sessions import BaseHandler


""" Handler that allows the user to change the number of elements shown in the page
    Get: redirect to the comics home page 
    Post: it's responsible for changing the number of elements"""
class ChangeNumElemsComicHandler(BaseHandler):

    # Redirect to the comics home page
    def get(self):
        self.redirect("/comics")

    # Change the number of elements
    def post(self):
        # Check if the admin is logged in
        if self.session.get('session_role') == 'admin':
            # If it's logged in, get the session variables, show the home page
            # Get the comic attributes
            num_elems = self.request.get("num_elems", 0)
            num_elems = int(num_elems)

            # Setting the session variable according to the new value
            if num_elems > 0:
                self.session['num_elems_page'] = num_elems

            del num_elems    # Delete variables to free memory
            self.redirect("/comics")       # Redirect to the comics home page

        # If it isn't logged in, redirect to the login page
        else:
            self.redirect("/login")


app = webapp2.WSGIApplication([], debug=True)
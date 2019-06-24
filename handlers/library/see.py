#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from handlers.elements.sessions import BaseHandler


""" See handler in the library home page 
    Get: redirect to the library home page
    Post: redirect to the library home page"""
class SeeLibraryHandler(BaseHandler):

    # Redirect to the library home page
    def get(self):
        # Get the shelving key
        key = self.request.get("shelving_key", "")

        # Setting the new session variable
        if len(key) > 0:
            self.session['shelving'] = key
            self.session_store.save_sessions(self.response)     # Save sessions

        # Redirect to the library home page
        self.redirect("/library")

    # Redirect to the library home page
    def post(self):
        self.redirect("/library_see")


app = webapp2.WSGIApplication([], debug=True)

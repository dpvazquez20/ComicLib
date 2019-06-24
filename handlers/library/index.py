#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from handlers.elements.sessions import BaseHandler


""" Index handler in the library home page 
    Get: redirect to the library home page after resetting the shelving session variable
    Post: redirect to the library home page after resetting the shelving session variable"""
class IndexLibraryHandler(BaseHandler):

    # Redirect to the library home page
    def get(self):
        self.session['shelving'] = None
        self.session_store.save_sessions(self.response)     # Save sessions

        # Redirect to the library home page
        self.redirect("/library")

    # Redirect to the library home page
    def post(self):
        self.session['shelving'] = None
        self.session_store.save_sessions(self.response)  # Save sessions

        # Redirect to the library home page
        self.redirect("/library")


app = webapp2.WSGIApplication([], debug=True)

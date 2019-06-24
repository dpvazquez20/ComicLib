#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from handlers.elements.sessions import BaseHandler


""" Logout handler
    get: destroy the user session and redirect to the login page"""
class LogoutHandler(BaseHandler):

    # Destroy the user session and redirect to the login page
    def get(self):
        self.session.clear()
        self.redirect("/login")


app = webapp2.WSGIApplication([], debug=True)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from webapp2_extras import sessions


""" Base handler that allows to use session variables 
    dispatch: initialize a session variable
    session: property that allows to access and set the session variable"""
class BaseHandler(webapp2.RequestHandler):

    # Initialize the session variable
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    # Session main property
    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        session = self.session_store.get_session()
        return session

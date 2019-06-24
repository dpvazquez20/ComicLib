#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

from handlers.elements.sessions import BaseHandler
from models import db

""" Handler used in the home page
    get: reset the db
    post: reset the db"""
class ResetHandler(BaseHandler):

    # Reset the database
    def get(self):
        install = db.Install.query()
        for ins in install:
            ins.key.delete()
            del ins
        users = db.User.query()
        for user in users:
            user.key.delete()
            del user
        authors = db.Author.query()
        for author in authors:
            author.key.delete()
            del author
        comics = db.ComicBook.query()
        for comic in comics:
            comic.key.delete()
            del comic
        shelvings = db.Shelving.query()
        for shelving in shelvings:
            shelving.key.delete()
            del shelving
        user_comics = db.User_ComicBook.query()
        for user_comic in user_comics:
            user_comic.key.delete()
            del user_comic
        comic_authors = db.ComicBook_Author.query()
        for comic_author in comic_authors:
            comic_author.key.delete()
            del comic_author
        friends = db.Friend.query()
        for friend in friends:
            friend.key.delete()
            del friend
        borrowings = db.Borrowing.query()
        for borrowing in borrowings:
            borrowing.key.delete()
            del borrowing
        del install, users, authors, comics, shelvings, user_comics, comic_authors, friends, borrowings

        self.redirect("/")

    # Reset the database
    def post(self):
        self.redirect("/")


app = webapp2.WSGIApplication([], debug=True)
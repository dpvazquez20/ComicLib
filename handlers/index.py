#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import models.install as d

############# GENERAL
from handlers.elements.function import randomSecretKey
from handlers.elements.sessions import BaseHandler
from handlers.elements.reset import ResetHandler
from handlers.elements.login import LoginHandler
from handlers.elements.signin import SigninHandler
from handlers.elements.forget import ForgetHandler
from handlers.home import HomeHandler
from handlers.lang.language import LanguageHandler
from handlers.elements.logout import LogoutHandler
############# AUTHORS
from handlers.authors.default import AuthorHomeHandler
from handlers.authors.add import AddAuthorHandler
from handlers.authors.delete import DeleteAuthorHandler
from handlers.authors.delete_all import DeleteAllAuthorHandler
from handlers.authors.modify import ModifyAuthorHandler
from handlers.authors.order import OrderAuthorHandler
from handlers.authors.search import SearchAuthorHandler
from handlers.authors.elements import ChangeNumElemsAuthorHandler
############# PROFILE
from handlers.profile.default import ProfileHomeHandler
from handlers.profile.modify_username import ProfileModifyUsernameHandler
from handlers.profile.modify_password import ProfileModifyPasswordHandler
from handlers.profile.modify_email import ProfileModifyEmailHandler
from handlers.profile.modify_genre import ProfileModifyGenreHandler
from handlers.profile.delete_account import ProfileDeleteAccountHandler
from handlers.profile.modify_picture import ProfileModifyPictureHandler
############ USERS
from handlers.users.default import UserHomeHandler
from handlers.users.add import AddUserHandler
from handlers.users.delete import DeleteUserHandler
from handlers.users.delete_all import DeleteAllUserHandler
from handlers.users.modify import ModifyUserHandler
from handlers.users.elements import ChangeNumElemsUserHandler
from handlers.users.order import OrderUserHandler
from handlers.users.filter import FilterUserHandler
from handlers.users.search import SearchUserHandler
from handlers.users.block import BlockUserHandler
from handlers.users.unblock import UnblockUserHandler
############ COMICS
from handlers.comics.default import ComicHomeHandler
from handlers.comics.add import AddComicHandler
from handlers.comics.delete import DeleteComicHandler
from handlers.comics.delete_all import DeleteAllComicHandler
from handlers.comics.modify import ModifyComicHandler
from handlers.comics.elements import ChangeNumElemsComicHandler
from handlers.comics.order import OrderComicHandler
from handlers.comics.search import SearchComicHandler
from handlers.comics.filter import FilterComicHandler
from handlers.comics.add_author import AddAuthorComicHandler
from handlers.comics.delete_author import DeleteAuthorComicHandler
############ COMICS USER HOME
from handlers.comics_home.user_search import UserSearchHandler
from handlers.comics_home.add import HomeAddComicHandler
from handlers.comics_home.quit import HomeQuitComicHandler
############ COLLECTION
from handlers.collection.default import CollectionHomeHandler
from handlers.collection.elements import ChangeNumElemsCollectionHandler
from handlers.collection.filter import FilterCollectionHandler
from handlers.collection.modify import ModifyCollectionHandler
from handlers.collection.order import OrderCollectionHandler
from handlers.collection.quit import QuitCollectionComicHandler
from handlers.collection.quit_all import QuitAllCollectionHandler
from handlers.collection.search import SearchCollectionHandler
############ LIBRARY
from handlers.library.index import IndexLibraryHandler
from handlers.library.default import LibraryHomeHandler
from handlers.library.add import AddShelvingHandler
from handlers.library.delete import DeleteShelvingHandler
from handlers.library.elements import ChangeNumElemsLibraryHandler
from handlers.library.filter import FilterLibraryHandler
from handlers.library.modify import ModifyShelvingHandler
from handlers.library.move import MoveComicHandler
from handlers.library.order import OrderLibraryHandler
from handlers.library.quit import QuitLibraryComicHandler
from handlers.library.quit_all import QuitAllLibraryHandler
from handlers.library.read_unread import ReadUnreadLibraryHandler
from handlers.library.search import SearchLibraryHandler
from handlers.library.see import SeeLibraryHandler
############ FRIENDS
from handlers.friends.default import FriendsHomeHandler
from handlers.friends.add import AddFriendHandler
from handlers.friends.quit import QuitFriendHandler
from handlers.friends.search import SearchFriendHandler
from handlers.friends.see import SeeFriendHandler
from handlers.friends.borrow import BorrowFriendHandler
from handlers.friends.ask import AskFriendHandler
############ BORROWINGS
from handlers.borrowings.default import BorrowingsHomeHandler
from handlers.borrowings.add import BorrowingsAddHandler
from handlers.borrowings.quit import BorrowingsQuitHandler
############ DATABASE
from models.db import Install


""" Main handler used in the index page (Log in)
    get: if it's needed, initializes the database. Always redirect to the login page
    """
class IndexHandler(BaseHandler):

    # Default
    def get(self):
        # Check if the database is already filled up with some default data, else, fill up the database
        is_filled_up = Install.query(Install.filled_up == True)
        if is_filled_up.count() == 0:
            d.install()

        del is_filled_up            # Delete variable to free memory
        self.redirect('/login')     # Redirect to the login page


config = {}
config['webapp2_extras.sessions'] = {       # Configuration of session variable
    'secret_key': randomSecretKey()         # Secret key for session variable
}

app = webapp2.WSGIApplication([
    ('/', IndexHandler),
    ('/login', LoginHandler),
    ('/signin', SigninHandler),
    ('/forget', ForgetHandler),
    ('/home', HomeHandler),
    ('/reset', ResetHandler),
    ('/lang', LanguageHandler),
    ('/logout', LogoutHandler),
    ('/authors', AuthorHomeHandler),
    ('/authors_add', AddAuthorHandler),
    ('/authors_delete', DeleteAuthorHandler),
    ('/authors_delete_all', DeleteAllAuthorHandler),
    ('/authors_modify', ModifyAuthorHandler),
    ('/authors_order', OrderAuthorHandler),
    ('/authors_search', SearchAuthorHandler),
    ('/authors_change_num_elems', ChangeNumElemsAuthorHandler),
    ('/profile', ProfileHomeHandler),
    ('/profile_modify_username', ProfileModifyUsernameHandler),
    ('/profile_modify_password', ProfileModifyPasswordHandler),
    ('/profile_modify_email', ProfileModifyEmailHandler),
    ('/profile_modify_genre', ProfileModifyGenreHandler),
    ('/profile_delete_account', ProfileDeleteAccountHandler),
    ('/profile_modify_picture', ProfileModifyPictureHandler),
    ('/users', UserHomeHandler),
    ('/users_add', AddUserHandler),
    ('/users_delete', DeleteUserHandler),
    ('/users_delete_all', DeleteAllUserHandler),
    ('/users_modify', ModifyUserHandler),
    ('/users_change_num_elems', ChangeNumElemsUserHandler),
    ('/users_order', OrderUserHandler),
    ('/users_filter', FilterUserHandler),
    ('/users_search', SearchUserHandler),
    ('/users_block', BlockUserHandler),
    ('/users_unblock', UnblockUserHandler),
    ('/comics', ComicHomeHandler),
    ('/comics_add', AddComicHandler),
    ('/comics_delete', DeleteComicHandler),
    ('/comics_delete_all', DeleteAllComicHandler),
    ('/comics_modify', ModifyComicHandler),
    ('/comics_change_num_elems', ChangeNumElemsComicHandler),
    ('/comics_order', OrderComicHandler),
    ('/comics_filter', FilterComicHandler),
    ('/comics_search', SearchComicHandler),
    ('/comics_add_author', AddAuthorComicHandler),
    ('/comics_delete_author', DeleteAuthorComicHandler),
    ('/home_search', UserSearchHandler),
    ('/home_add', HomeAddComicHandler),
    ('/home_quit', HomeQuitComicHandler),
    ('/collection', CollectionHomeHandler),
    ('/collection_quit', QuitCollectionComicHandler),
    ('/collection_quit_all', QuitAllCollectionHandler),
    ('/collection_change_num_elems', ChangeNumElemsCollectionHandler),
    ('/collection_read', ModifyCollectionHandler),
    ('/collection_unread', ModifyCollectionHandler),
    ('/collection_order', OrderCollectionHandler),
    ('/collection_filter', FilterCollectionHandler),
    ('/collection_order', OrderCollectionHandler),
    ('/collection_search', SearchCollectionHandler),
    ('/library_index', IndexLibraryHandler),
    ('/library', LibraryHomeHandler),
    ('/library_add', AddShelvingHandler),
    ('/library_change_num_elems', ChangeNumElemsLibraryHandler),
    ('/library_delete', DeleteShelvingHandler),
    ('/library_quit', QuitLibraryComicHandler),
    ('/library_quit_all', QuitAllLibraryHandler),
    ('/library_filter', FilterLibraryHandler),
    ('/library_modify', ModifyShelvingHandler),
    ('/library_move', MoveComicHandler),
    ('/library_order', OrderLibraryHandler),
    ('/library_read', ReadUnreadLibraryHandler),
    ('/library_unread', ReadUnreadLibraryHandler),
    ('/library_search', SearchLibraryHandler),
    ('/library_see', SeeLibraryHandler),
    ('/friends', FriendsHomeHandler),
    ('/friends_add', AddFriendHandler),
    ('/friends_refuse', QuitFriendHandler),
    ('/friends_quit', QuitFriendHandler),
    ('/friends_search', SearchFriendHandler),
    ('/friends_see', SeeFriendHandler),
    ('/friends_borrow', BorrowFriendHandler),
    ('/friends_ask_for', AskFriendHandler),
    ('/borrowings', BorrowingsHomeHandler),
    ('/borrowings_add', BorrowingsAddHandler),
    ('/borrowings_refuse', BorrowingsQuitHandler),
    ('/borrowings_give_back', BorrowingsQuitHandler)
], debug=True, config=config)

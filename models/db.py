""" Database """
import google.appengine.ext.ndb as ndb
import datetime


# Class that represents if the database is filled up or not
class Install(ndb.Model):
    filled_up = ndb.BooleanProperty(required=True)  # It allows to know if the database is installed


# Class that represents an user
class User(ndb.Model):
    name = ndb.StringProperty(required=True)                                                        # User name
    email = ndb.StringProperty(required=True)                                                       # User email
    password = ndb.StringProperty(required=True)                                                    # User password
    role = ndb.StringProperty(required=True, choices=["admin", "client"])                           # User role [admin or client]
    picture = ndb.BlobProperty(default=None)                                                        # User profile picture (not required)
    genre = ndb.StringProperty(choices=["male", "female", "not_defined"], default="not_defined")    # User genre (not required)
    language = ndb.StringProperty(choices=["spa", "eng"], default="eng")                            # Application language for this user [spanish or english]
    blocked = ndb.BooleanProperty(required=True, default=False)                                     # If this user is blocked or not
    end_block = ndb.DateProperty(default=None)                                                      # Block end date


# Class that represents an author
class Author(ndb.Model):
    name = ndb.StringProperty(required=True)    # Author name


# Class that represents a many to many relation ComicBook_Author
class ComicBook_Author(ndb.Model):
    author = ndb.StructuredProperty(Author, required=True)      # Author
    role = ndb.StringProperty(required=True)                    # Author roles
    id_aux = ndb.IntegerProperty(required=True)                 # Auxiliar id


# Class that represents a many to many relation between an user and his comic books
class User_ComicBook(ndb.Model):
    addition_date = ndb.DateProperty(default=datetime.date.today())                 # Date in which user added the comic book
    state = ndb.StringProperty(choices=["read", "unread"], default="unread")        # If the comic is read or unread
    username = ndb.StringProperty(required=True)                                    # User that have this comic book
    shelving = ndb.KeyProperty(default=None)                                        # In which shelving is the comic book
    id_aux = ndb.KeyProperty(required=True)                                         # Auxiliar id


# Class that represents a comic book
class ComicBook(ndb.Model):
    isbn = ndb.StringProperty(default="")                                                   # Comic book ISBN
    title = ndb.StringProperty(required=True)                                               # Comic book title
    publisher = ndb.StringProperty(default="")                                              # Publisher company of the comic book
    edition = ndb.IntegerProperty(default=1)                                                # Number of the comic book edition
    plot = ndb.StringProperty(default="")                                                   # Comic book plot
    type = ndb.StringProperty(choices=["comic", "manga", "anthology"], required=True)       # Comic book type (comic, manga, anthology)
    origin = ndb.StringProperty(choices=["american", "european", "other"], default="other") # Comic book origin (american, european, other)
    value = ndb.FloatProperty(default=0)                                                    # Comic value
    cover = ndb.BlobProperty(default=None)                                                  # Comic book cover
    save_date = ndb.DateProperty(default=datetime.date.today())                             # When the comic book was saved
    authors = ndb.StructuredProperty(ComicBook_Author, repeated=True)                       # Comic authors
    users = ndb.StructuredProperty(User_ComicBook, repeated=True)                           # Users that have this comic book
    owned = ndb.BooleanProperty(default=False)                                              # Interface auxiliar variable
    is_read = ndb.BooleanProperty(default=False)                                            # Interface auxiliar variable
    owner_name = ndb.StringProperty()                                                       # Interface auxiliar variable


# Class that represents a comic book shelving
class Shelving(ndb.Model):
    name = ndb.StringProperty(required=True)                 # Shelving name
    picture = ndb.BlobProperty(default=None)                 # Shelving picture
    username = ndb.StringProperty(required=True)             # Shelving owner


# Class that represents the borrowed comic books
class Borrowing(ndb.Model):
    who_want = ndb.KeyProperty(required=True)               # Who wants the comic
    who_borrow = ndb.KeyProperty(required=True)             # Who borrows the comic
    is_borrowed = ndb.BooleanProperty(default=False)        # State of request
    comic = ndb.KeyProperty(required=True)                  # Comic id


# Class that represents the user friends
class Friend(ndb.Model):
    who_ask = ndb.KeyProperty(required=True)                            # Who made the request
    who_answer = ndb.KeyProperty(required=True)                         # Who answers the request
    addition_date = ndb.DateProperty(default=datetime.date.today())     # The friendship begin data
    is_friend = ndb.BooleanProperty(required=True, default=False)       # State of request



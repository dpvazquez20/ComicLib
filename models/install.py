""" File that contains a method for initializing the database """
import models.db as db
import string
import random
import datetime
import time

from Crypto.Hash import SHA256
from handlers.lang.functions import get_default_language

""" Method for filling up the data base """
def install():

    """INIT (sets the value to false, this means that the database is already filled up)"""
    init = db.Install(filled_up=True)
    init.put()
    del init

    """USERS"""
    # Admin
    hash = SHA256.new()
    hash.update("adminadmin")
    hash = hash.hexdigest()
    user = db.User(name="admin", email="admin@admin", password=hash, role="admin", language=get_default_language())
    user.put()
    # Client
    hash = SHA256.new()
    hash.update("clientclient")
    hash = hash.hexdigest()
    user = db.User(name="client", email="client@client", password=hash, role="client", language=get_default_language())
    user.put()
    # Random users
    genre = ["male", "female", "not_defined"]   # Random genre
    role = ["admin", "client"]                  # Random role
    blocked = [True, False]                     # Random block
    for i in range(1, 14):
        # Random name
        username = "User "
        for i in range(1, random.randint(5, 15)):
            username += random.choice(string.ascii_letters.lower())
        # Random password (only lower letters)
        hash = SHA256.new()
        hash.update(username.replace(" ", "").lower())
        hash = hash.hexdigest()
        email = username.lower().replace(" ", "") + "@email.com"    # Random email
        user = db.User(name=username, email=email, password=hash, role=role[random.randint(0, 1)], genre=genre[random.randint(0, 2)], language=get_default_language(), blocked=blocked[random.randint(0, 1)])
        if user.blocked == True:
            user.end_block = datetime.datetime.now()
        user.put()
        del username, email, user, hash, i
    del genre, role, blocked
    time.sleep(1)


    """AUTHORS"""
    for i in range(1, 16):
        author = "Author " + random.choice(string.ascii_letters.upper())    # Random name
        author = db.Author(name=author)
        author.put()
        del i, author
    time.sleep(1)


    """COMIC BOOKS"""
    authors = db.Author.query().fetch()                                                     # Authors
    name = ["Comic ", "Manga ", "Anthology "]                                       # Random head title
    roles = ["script", "drawing", "labels", "inked", "colors", "cover"]             # Random role
    publisher = ["Publisher ABC", "Publisher DEF", "Publisher GHI", ""]             # Random publisher
    type = ["comic", "manga", "anthology"]                                          # Random type
    origin = ["american", "european", "other"]                                      # Random origin
    plot = [
        "",
        "The history of overcoming an athlete to reach the top of the world ranking",
        "A love story between two young people whose families have maintained an enmity over many generations",
        "The revenge story of a daughter who has lost her parents to one of the most dangerous mafias in the world",
    ]                                                                               # Random plot
    for i in range(1, 16):
        isbn = str(random.randint(9780000000000, 9789999999999))
        isbn = isbn[0: 3] + "-" + isbn[3] + "-" + isbn[4:6] + "-" + isbn[6:12] + "-" + isbn[12]     # Random ISBN
        title = name[random.randint(0, 2)]
        for i in range(1, random.randint(5, 25)):
            title += random.choice(string.ascii_letters.lower())                                    # Random title
            del i
        comic = db.ComicBook(isbn=isbn, title=title, publisher=publisher[random.randint(0, 3)], plot=plot[random.randint(0, 3)], edition=random.randint(1, 3), type=type[random.randint(0, 2)], origin=origin[random.randint(0, 2)], value=round(random.uniform(0, 40), 2))

        id_aux = 0
        # Adding random authors to the comic books
        for author in authors:
            choice = random.randint(0, 3)
            if choice == 1:
                choice = random.randint(0, 3)
                if choice == 0:
                    comic_author = db.ComicBook_Author(author=author, role=roles[random.randint(0, 5)], id_aux=id_aux)
                    if len(comic.authors) > 0:
                        comic.authors.append(comic_author)
                    else:
                        comic.authors = [comic_author]
                    comic_author.put()
                    id_aux += 1
                    del comic_author
            del choice
        del id_aux

        comic.put()
        del comic, isbn, title
    del authors, roles, name, publisher, plot, type, origin
    time.sleep(1)


    """SHELVINGS FOR THE 'client' USER"""
    for i in range(0, 3):
        shelving = db.Shelving(name=("Shelving " + str(i)), username="client")
        shelving.put()
        del i, shelving
    time.sleep(1)


    """COMIC COLLECTION AND LIBRARY FOR THE 'client' USER"""
    state = ["read", "unread"]
    comics = db.ComicBook.query().fetch()
    shelvings = db.Shelving.query().fetch()
    for comic in comics:
        choice = random.randint(0, 1)
        if choice == 1:
            user_comic = db.User_ComicBook(addition_date=datetime.datetime.now(), state=state[random.randint(0, 1)], username="client", id_aux=comic.key)
            choice = random.randint(0, 1)
            if choice == 1:
                current = shelvings[random.randint(0, 2)]
                user_comic.shelving = current.key
                current.put()
                del current
            user_comic.put()
            if len(comic.users) > 0:
                comic.users.append(user_comic)
            else:
                comic.users = [user_comic]
            comic.put()
            del user_comic
        del choice, comic
    del state, shelvings
    time.sleep(1)


    """RANDOM FRIENDS AND BORROWINGS FOR THE 'client' USER"""
    client = db.User.query(db.User.name == "client").fetch()
    client = client[0]
    users = db.User.query(db.User.name != "client")
    is_friend = [True, False]
    for user in users:
        choice = random.randint(0, 1)
        if choice == 1 and user.role == "client":
            friend = db.Friend(who_ask=user.key, who_answer=client.key, is_friend=is_friend[random.randint(0, 1)])
            friend.put()
            choice = random.randint(0, 1)
            # Borrowed comics user are ALL, not the ones in the users collection
            if choice == 0 and friend.is_friend == True:
                borrowing = db.Borrowing(who_want=user.key, who_borrow=client.key, is_borrowed=is_friend[random.randint(0, 1)], comic=comics[random.randint(0, len(comics) - 1)].key)
                borrowing.put()
                del borrowing
            elif choice == 1 and friend.is_friend == True:
                borrowing = db.Borrowing(who_want=client.key, who_borrow=user.key, is_borrowed=is_friend[random.randint(0, 1)], comic=comics[random.randint(0, len(comics) - 1)].key)
                borrowing.put()
                del borrowing
            del friend
        del choice, user
    del client, users, is_friend, comics
    time.sleep(1)
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import random

from Crypto.Hash import SHA256


"""Create a random password to send to the user"""
def randomPassword():
    # Random length of the password
    cycles = random.randint(8, 20)      # Between 8 and 20 characters
    password = ""

    # Make the password (it concats numbers and letter randomly)
    for i in range(0, cycles):
        aux = random.randint(0, 1)

        if aux == 1:    # If 1, concat a letter
            password = password + random.choice(string.ascii_letters)
        else:           # if 0, concat a number
            password = password + str(random.randint(0, 9))

        del aux     # Delete variable to free memory

    del cycles      # Delete variable to free memory

    return password


"""Generate a random secret key for the session variable"""
def randomSecretKey():
    key = "-{"
    cycles = random.randint(15, 20)

    # Random body for the key
    for i in range(0, cycles):
        aux = random.randint(0, 1)

        if aux == 1:        # If 1, concat a letter
            key += random.choice(string.ascii_letters)
        else:               # if 0, concat a number
            key += str(random.randint(0, 9))

        del aux  # Delete variable to free memory

    del cycles  # Delete variable to free memory
    key += "}-"
    key = encryptPassword(key)      # SHA 256 encrypt

    return key


"""Encrypt a password in SHA256 sent as argument"""
def encryptPassword(password):
    hash = SHA256.new()         # Create a new SHA256 object
    hash.update(password)       # Create the password hash
    return hash.hexdigest()     # Return the password hash in hexadecimal format
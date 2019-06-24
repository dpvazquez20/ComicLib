#!/usr/bin/env python
# -*- coding: utf-8 -*-

from locale import getdefaultlocale


"""Function that allows to set the default language of the app when a user enter in the login page"""
def get_default_language():
    language, encoding = getdefaultlocale()     # Get the default language and encoding of the OS

    if language != None and len(language) > 0:
        language = language.encode("utf8")

    # Check the language and return a string that represents it
    if language.find("es") != -1:
        return "spa"
    elif language.find("en") != -1:
        return "eng"
    else:
        return "eng"


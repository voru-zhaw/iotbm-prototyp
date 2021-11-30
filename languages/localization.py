import os
import gettext

# list of supported languages
languages = {'de': 'Deutsch', 'en': 'English'}


# method to get the language name by its code
def get_language(code):
    return languages[code]


# method to get the translation function
def get_translation(page, code):
    path = os.getcwd() + '\\languages'
    lang = gettext.translation(page, localedir=path, languages=[code])
    return lang.gettext

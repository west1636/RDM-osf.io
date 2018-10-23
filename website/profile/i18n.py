# coding:utf-8
import gettext
import os

localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
en = gettext.translation('profile', localedir, languages=['en'])
ja = gettext.translation('profile', localedir, languages=['ja'])

# coding:utf-8
import gettext
import os


localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
en = gettext.translation('xattr', localedir, languages=['en'])
ja = gettext.translation('xattr', localedir, languages=['ja'])

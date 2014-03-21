# -*- coding: utf-8 -*-
"""Core functions for the Dropbox addon."""
from framework import db, storage
from framework.mongo import set_up_storage

from website.addons.dropbox import MODELS
from website.addons.dropbox.model import (
    DropboxFile,
    DropboxNodeSettings, DropboxUserSettings
)
from website.addons.dropbox.client import get_client


get_client = get_client


def init_storage():
    set_up_storage(MODELS, storage_class=storage.MongoStorage, db=db)

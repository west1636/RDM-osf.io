# -*- coding: utf-8 -*-
import logging
from flask import current_app as app
from celery.contrib.abortable import AbortableTask
from website.project.decorators import _load_node_or_fail
from addons.wiki import views as wiki_views
from framework.celery_tasks import app as celery_app

__all__ = [
    'run_project_wiki_validate_import',
    'run_project_wiki_copy_import_directory',
    'run_project_wiki_replace',
]
logger = logging.getLogger(__name__)
@celery_app.task(bind=True, base=AbortableTask, track_started=True)
def run_project_wiki_validate_import(self, dir_id, nid):
    node = _load_node_or_fail(nid)
    return wiki_views.project_wiki_validate_import_process(dir_id, node)

@celery_app.task(bind=True, base=AbortableTask, track_started=True)
def run_project_wiki_copy_import_directory(self, data, dir_id, nid):
    node = _load_node_or_fail(nid)
    return wiki_views.project_wiki_copy_import_directory_process(data, dir_id, node)


@celery_app.task(bind=True, base=AbortableTask, track_started=True)
def run_project_wiki_replace(self, data, dir_id, nid):
    node = _load_node_or_fail(nid)
    return wiki_views.project_wiki_replace_process(data, dir_id, node)

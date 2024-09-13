# -*- coding: utf-8 -*-
import logging
import json
from celery.contrib.abortable import AbortableTask
from website.project.decorators import _load_node_or_fail
from website.search.elastic_search import bulk_update_wikis
from addons.wiki import views as wiki_views
from addons.wiki.models import WikiPage
from framework.celery_tasks import app as celery_app
from framework.auth import Auth
from osf.models import OSFUser

__all__ = [
    'run_project_wiki_validate_for_import',
    'run_project_wiki_import',
    'run_update_search_and_bulk_index',
]
logger = logging.getLogger(__name__)
@celery_app.task(bind=True, base=AbortableTask, track_started=True)
def run_project_wiki_validate_for_import(self, dir_id, nid):
    node = _load_node_or_fail(nid)
    return wiki_views.project_wiki_validate_for_import_process(dir_id, node)

@celery_app.task(bind=True, base=AbortableTask, track_started=True)
def run_project_wiki_import(self, data_json, dir_id, current_user_id, nid):
    node = _load_node_or_fail(nid)
    user = OSFUser.load(current_user_id, select_for_update=False)
    auth = Auth.from_kwargs({'user': user}, {})
    data = json.loads(data_json)
    task_id = self.request.id
    return wiki_views.project_wiki_import_process(data, dir_id, task_id, auth, node)

@celery_app.task(bind=True, base=AbortableTask, track_started=True)
def run_update_search_and_bulk_index(self, nid, wiki_id_list, skip_update_search=False):
    node = _load_node_or_fail(nid)
    wiki_pages = WikiPage.objects.filter(id__in=wiki_id_list)
    bulk_update_wikis(wiki_pages)
    if not skip_update_search:
        node.update_search()


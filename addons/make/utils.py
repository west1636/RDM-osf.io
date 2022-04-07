# -*- coding: utf-8 -*-
import json
from django.core import serializers

# widget: ここから
def serialize_make_widget(node):
    make = node.get_addon('make')
    ret = {
        # if True, show widget body, otherwise show addon configuration page link.
        'complete': make.complete,
        'include': False,
        'can_expand': True,
    }
    ret.update(make.config.to_json())
    return ret
# widget: ここまで

def get_guid(node):

    qsGuid = node._prefetched_objects_cache['guids'].only()
    guidSerializer = serializers.serialize('json', qsGuid, ensure_ascii=False)
    guidJson = json.loads(guidSerializer)
    guid = guidJson[0]['fields']['_id']
    return guid

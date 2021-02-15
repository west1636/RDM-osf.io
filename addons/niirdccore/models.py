# -*- coding: utf-8 -*-
import logging
import json

from django.db import models
from django.db.models import Subquery
from django.db.models.signals import post_save
from django.dispatch import receiver

from osf.models import Contributor, RdmAddonOption, AbstractNode
from osf.models.node import Node

from . import settings
from . import SHORT_NAME
from addons.base.models import BaseNodeSettings
from website import settings as ws_settings

logger = logging.getLogger(__name__)

class NodeSettings(BaseNodeSettings):
    """
    プロジェクトにアタッチされたアドオンに関するモデルを定義する。
    """
    dmp_id = models.TextField(blank=True, null=True)
    dmr_api_key = models.TextField(blank=True, null=True)

    def set_dmp_id(self, dmp_id):
        self.dmp_id = dmp_id
        self.save()

    def get_dmp_id(self):
        return self.dmp_id

    def set_dmr_api_key(self, dmr_api_key):
        self.dmr_api_key = dmr_api_key
        self.save()

    def get_dmr_api_key(self):
        return self.dmr_api_key

    @receiver(post_save, sender=Node)
    def add_niirdccore_addon(sender, instance, created, **kwargs):
        if SHORT_NAME not in ws_settings.ADDONS_AVAILABLE_DICT:
            return

        if instance.has_addon(SHORT_NAME):
            # add済みの場合は終了
            return
        # 所属機関によるアドオン追加判定は、adminコンテナの起動が可能になるまでコメントアウトする
        # inst_ids = instance.affiliated_institutions.values('id')
        # addon_option = RdmAddonOption.objects.filter(
        #     provider=SHORT_NAME,
        #     institution_id__in=Subquery(inst_ids),
        #     management_node__isnull=False,
        #     is_allowed=True
        # ).first()
        # if addon_option is None:
        #     return
        # if addon_option.organizational_node is not None and \
        #         not addon_option.organizational_node.is_contributor(instance.creator):
        #     return

        instance.add_addon(SHORT_NAME, auth=None, log=False)

class AddonList(BaseNodeSettings):
    """
    送信先アドオンリストに関するモデルを定義する。
    """
    owner    = models.ForeignKey("NodeSettings", null=True, blank=True, related_name="node")
    node_id = models.CharField(max_length=100, blank=True)
    addon_id = models.CharField(max_length=50, blank=True)
    callback = models.CharField(max_length=100, blank=True)

    def get_owner(self):
        return self.owner

    def set_owner(self, owner):
        self.owner = owner
        self.save()

    def get_node_id(self):
        return node_id

    def set_node_id(self, node_id):
        self.node_id = node_id
        self.save()

    def get_addon_id(self):
        return self.addon_id

    def set_addon_id(self, addon_id):
        self.addon_id = addon_id
        self.save()

    def get_callback(self):
        return self.callback

    def set_callback(self, callback):
        self.callback = callback
        self.save()

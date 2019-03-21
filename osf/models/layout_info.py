from django.db import models
from osf.models.base import BaseModel



class WidgetPosition(BaseModel):
    user_id = models.ForeignKey('OSFUser', on_delete=models.CASCADE)
    node_id = models.ForeignKey('Node', on_delete=models.CASCADE)
    ul_id = models.IntegerField(blank=False, null=False)
    widget_id = models.CharField(max_length=50,blank=False, null=False)
    widget_position = models.IntegerField(blank=False, null=False)

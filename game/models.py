from django.db import models
import json
# Create your models here.

class Table(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    tb = models.CharField(max_length=100)

    """
    b0 = models.IntegerField(default=0)
    b1 = models.IntegerField(default=0)
    b2 = models.IntegerField(default=0)
    b3 = models.IntegerField(default=0)
    b4 = models.IntegerField(default=0)
    b5 = models.IntegerField(default=0)
    b6 = models.IntegerField(default=0)
    b7 = models.IntegerField(default=0)
    b8 = models.IntegerField(default=0)
    """
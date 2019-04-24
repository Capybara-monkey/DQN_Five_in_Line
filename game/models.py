from django.db import models
import json
# Create your models here.

class Table(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    tb = models.CharField(max_length=100)


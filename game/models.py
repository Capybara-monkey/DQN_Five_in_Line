from django.db import models
import json
# Create your models here.

class Table(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    tb = models.CharField(max_length=100)


class PlayNum(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    num = models.IntegerField(default=0)


class Memory(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    memory = models.CharField(max_length = 1000000)


class StateAction(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    state = models.CharField(max_length=100)
    action = models.IntegerField(default=0)


class Epsilon(models.Model):
    data_id = models.IntegerField(default=1, primary_key=True)
    eps = models.FloatField(default=1.0)


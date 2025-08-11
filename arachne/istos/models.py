from django.utils import timezone
from django.db import models
from pathlib import Path

form_type = [
    ("vid", "vid"),
    ("pic", "pic")
]

class Link(models.Model):
    url = models.URLField(max_length=200)
    site = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    dateGrabbed = models.DateField(default=timezone.now)
    #Calls back to another link if scraped from that link
    hasParent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='children')

class Items(models.Model):
    #is link_id in DB
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    url = models.URLField(max_length=100, null=True)
    site = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=50, null=True)
    dateGrabbed = models.DateField(default=timezone.now)
    saved = models.BooleanField(default=False)
    dateSaved = models.DateField(null=True)

class Formats(models.Model):
    type = models.CharField(max_length=3, choices=form_type)
    formName = models.CharField(max_length=4)
    formSave = models.BooleanField(default=True)

class Settings(models.Model):
    settingName = models.CharField(max_length=100)
    on = models.BooleanField(default=False)
    link = models.CharField(max_length=1000, null=True)
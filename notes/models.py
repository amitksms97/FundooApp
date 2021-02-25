from django.db import models
from datetime import datetime
import sys
import os
from colorful.fields import RGBColorField
sys.path.append(os.getcwd() + '/..')
from user.models import User


class Label(models.Model):
    label_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_label_name(self):
        return self.label_name

    def __str__(self):
        return self.label_name


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    is_archive = models.BooleanField("is_archive", default=False)
    is_trashed = models.BooleanField("is_trashed", default=False)
    is_pinned = models.BooleanField(default=False)
    date = models.DateTimeField(default=datetime.now, blank=True)
    color = RGBColorField(colors=['#FF0000', '#00FF00', '#0000FF'], blank=True, null=True)
    label = models.ManyToManyField(Label, blank=True)
    collaborator = models.ManyToManyField(User, related_name="Collaborator_of_note", blank=True)
    trashed_time = models.DateTimeField(default=None, blank=True, null=True)
    reminder = models.DateTimeField(default=None, blank=True, null=True)

    def get_note(self):
        return self.note

    def __str__(self):
        return self.title

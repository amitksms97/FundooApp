from django.db import models
import sys
import os
sys.path.append(os.getcwd() + '/..')
from user.models import User


class Label(models.Model):
    label_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True, null=False, blank=False)

    def get_label_name(self):
        return self.label_name

    def __str__(self):
        return self.label_name


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    collaborator = models.ManyToManyField(to=User, related_name='collaborator')
    label = models.ManyToManyField(to=Label)
    is_trashed = models.BooleanField(default=False)

    def get_note(self):
        return self.note

    def __str__(self):
        return self.title

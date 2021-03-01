from django.db import models
from datetime import datetime
import sys
import os
from colorful.fields import RGBColorField
sys.path.append(os.getcwd() + '/..')
from user.models import User


class Notes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    note = models.CharField(max_length=250)
    date = models.DateTimeField(default=datetime.now, blank=True)

    def get_note(self):
        return self.note

    def __str__(self):
        return self.title

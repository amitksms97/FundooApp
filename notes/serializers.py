from rest_framework import serializers
from .models import Notes
from django.contrib.auth.models import User


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note']


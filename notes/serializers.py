from rest_framework import serializers
from .models import Notes, Label
from django.contrib.auth.models import User


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note', 'label']
        extra_kwargs = {'label': {'read_only': True}}


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['labelframe']

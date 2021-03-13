from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Notes, Label


class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ['title', 'note', 'id', 'user_id']


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['label_name']


class CollaboratorSerializer(ModelSerializer):
    collaborator = serializers.EmailField()

    class Meta:
        model = Notes
        fields = ['collaborator']


class ListNotesSerializer(serializers.ModelSerializer):
    label = serializers.StringRelatedField(many=True, read_only=True)
    collaborator = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Notes
        fields = ['user', 'title', 'note', 'label', 'collaborator', 'reminder']
        extra_kwargs = {'user': {'read_only': True}, 'title': {'read_only': True}, 'content': {'read_only': True},
                        'reminder': {'read_only': True}}


class ReminderSerializer(serializers.ModelSerializer):
    reminder = serializers.DateTimeField()

    class Meta:
        model = Notes
        fields = ['title', 'note', 'user', 'reminder']
        extra_kwargs = {'user': {'read_only': True}, 'title': {'read_only': True}, 'note': {'read_only': True}}


class SearchSerializer(serializers.ModelSerializer):
    value = serializers.CharField()

    class Meta:
        model = Notes
        fields = ['value']

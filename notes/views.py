from rest_framework.generics import GenericAPIView
from .serializers import NotesSerializer, LabelSerializer
from .models import Notes, Label
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework import generics
import logging
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta

import json
from django.core.cache import cache


import logging
from FundooApp.settings import file_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class ListNoteView(generics.ListAPIView):
    """
    Summary:
    --------
        All the notes will be listed for the user.
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    logger.info("Notes listed successfully..!!")

class NoteCreateView(GenericAPIView):
    """
        Summary:
        --------
            Note class will let authorized user to create and get notes.
        --------
        Methods:
            get: User will get all the notes.
            post: User will able to create new note.
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()
    lookup_field = 'id'

    def get(self, request):
        """
                Summary:
                --------
                    All the notes will be fetched for the user.
                --------
                Exception:
                    PageNotAnInteger: object
                    EmptyPage: object.
            """
        user = request.user
        notes = Notes.objects.filter(user_id=user.id, is_archive=False)
        serializer = NotesSerializer(notes, many=True)
        logger.info("Particular Note is obtained, from get()")
        return Response({"response": serializer.data}, status=200)

    def post(self, request):

        data = request.data
        user = request.user
        serializer = NotesSerializer(data=data, partial=True)
        if serializer.is_valid():
            note = serializer.save(user_id=user.id)
            logger.info("New Note is created.")
            logger.info("Data is stored in cache")
            return Response({"response": serializer.data}, status=201)
        logger.error("Something went wrong while creating Note, from post()")
        return Response({"response": serializer.data}, status=400)

@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class NoteUpdateView(GenericAPIView):
    """
        Summary:
        --------
            Existing note can be updated / deleted  by the User.
        Exception:
        ----------
            KeyError: object
    """
    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get_object(self, request, id):
        """
            Summary:
            --------
                Specific note object will be fetched for the user based on id.
            --------
            Exception:
                PageNotAnInteger: object
                EmptyPage: object.
        """
        try:
            user = request.user
            queryset = Notes.objects.filter(user_id=user.id)
            return get_object_or_404(queryset, id=id)
        except Notes.DoesNotExist:
            logger.error("id not present, from get_object()")
            return Response({'response': 'Id not present'})

    def get(self, request, id):
        """
            Summary:
            --------
                Specific note will be fetched for the user based on id.
            --------
            Exception:
                PageNotAnInteger: object
                EmptyPage: object.
        """
        try:
            user = request.user
            if cache.get(str(user.id)+"note"+str(id)):
                note = cache.get(str(user.id)+"note"+str(id))
                serializer = NotesSerializer(note)
                logger.info("data from cache")
                return Response({"response": serializer.data})
            else:
                note = self.get_object(request, id)
                serializer = NotesSerializer(note)
                logger.info("got Note successfully, from get()")
                logger.info("data from db")
                return Response({"response": serializer.data}, status=200)
        except:
            logger.error("something went wrong while getting Note, Enter the right id, from get()")
            return Response(status=404)

    def put(self, request, id):
        """
            Summary:
            --------
                New note will be updated by the User.
            Exception:
            ----------
                KeyError: object
        """
        user = request.user
        try:
            data = request.data
            instance = self.get_object(request, id)
            serializer = NotesSerializer(instance, data=data)
            if serializer.is_valid():
                note_update = serializer.save(user_id=user.id)
                logger.info("Note updated succesfully, from put()")
                cache.set(str(user.id)+"note"+str(id), note_update)
                return Response({'details': 'Note updated succesfully'}, status=200)
            logger.error("Note is not Updated something went wrong, from put()")
            return Response({'deatils': 'Note is not Updated..!!!'}, status=400)
        # except:
        #     logger.error("Something went wrong")
        #     return Response(status=404)
        except Exception as e:
            logger.error("Something went wrong")
            return Response(e)

    def delete(self, request, id):
        """
            Summary:
            --------
                Note will be deleted by the User.
            Exception:
            ----------
                KeyError: object
        """
        user = request.user
        try:
            instance = self.get_object(request, id)
            if instance.is_trashed:
                instance.delete()
                logger.info("Note is Deleted Permanently, from delete()")
                return Response({'response': 'Note is Deleted'}, status=200)
            else:
                instance.is_trashed = True
                instance.trashed_time = datetime.now()
                instance.save()
                logger.info("Note is Trashed")
                return Response({'response': 'Your note is Trashed'}, status=200)
        except:
            logger.error("Note does not exist ")
            return Response({'response': 'Note is not exist'}, status=404)


@method_decorator(login_required(login_url='/auth/login/'), name='dispatch')
class LabelCreateView(GenericAPIView):
    """
        Summary:
        --------
            LabelCreate class will let authorized user to create and get labels.
        --------
        Methods:
            get: User will get all the labels.
            post: User will able to create new label.
    """
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def get(self, request):

        try:
            user = request.user
            labels = Label.objects.filter(user_id=user.id)
            serializer = LabelSerializer(labels, many=True)
            logger.info("Got the Labels, from get()")
            return Response(serializer.data, status=200)
        except Exception as e:
            logger.error("Something went wrong, from get()")
            return Response(e)
    """
        Summary:
        --------
            LabelCreate class will let authorized user to create and get labels.
        --------
        Methods:
            get: User will get all the labels.
            post: User will able to create new label.
    """


from django.db.models import Q
from django.http import HttpResponse
from psycopg2._psycopg import OperationalError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, ListCreateAPIView

from user.models import User
from .token_authorization import TokenAuthorization
from .serializers import NotesSerializer, LabelSerializer, CollaboratorSerializer, ReminderSerializer
from .models import Notes, Label
from rest_framework.response import Response
import logging

from .utils import Utils
from datetime import datetime, timedelta

logger = logging.getLogger('django')


class NoteOperationsView(GenericAPIView):
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
        try:
            user = TokenAuthorization.token_auth(request)
            if user:
                notes = Notes.objects.filter(user=user)
                serializer = NotesSerializer(notes, many=True)
                logger.info("Particular Note is obtained, from get()")
                return Response({"response": serializer.data}, status=200)
            else:
                return Response({'Message': 'You are not logged in'}, status=status.HTTP_400_BAD_REQUEST)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to retrieve note'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):

        try:
            data = request.data
            user = TokenAuthorization.token_auth(request)
            serializer = NotesSerializer(data=data, partial=True)
            if serializer.is_valid():
                serializer.save(user=user)
                logger.info("New Note is created.")
                return Response({"Message": serializer.data}, status=201)
            logger.error("Something went wrong while creating Note, from post()")
            return Response({"response": serializer.data}, status=400)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to update note'}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
            Summary:
            --------
            New note will be updated by the User.
            Exception:
            ----------
                KeyError: object
        """
        try:

            data = request.data
            user = TokenAuthorization.token_auth(request)
            serializer = NotesSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save(user=user)
                logger.info("Note updated successfully, from put()")
                return Response({'details': serializer.data}, status=200)
            logger.error("Note is not Updated something went wrong, from put()")
            return Response({'Message': 'Note is not Updated..!!!'}, status=400)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to update note'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
            Summary:
            --------
                Note will be deleted by the User.
            Exception:
            ----------
                KeyError: object
        """
        try:
            user = TokenAuthorization.token_auth(request)
            note = Notes.objects.filter(user=user)
            note.delete()
            logger.info("Note is Deleted Permanently, from delete()")
            return Response({'response': 'Note is Deleted'}, status=200)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to delete new note,Please try again later'},
                            status=status.HTTP_400_BAD_REQUEST)


class LabelOperationsView(GenericAPIView):
    """
        Summary:
        --------
            Lable class will let authorized user to create and get notes.
        --------
        Methods:
            get: User will get all the notes.
            post: User will able to create new note.
    """
    serializer_class = LabelSerializer
    queryset = Label.objects.all()
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
        user = TokenAuthorization.token_auth(request)
        labels = Label.objects.filter(user=user)
        serializer = LabelSerializer(labels, many=True)
        logger.info("Particular Note is obtained, from get()")
        return Response({"response": serializer.data}, status=200)

    def post(self, request):

        data = request.data
        user = TokenAuthorization.token_auth(request)
        serializer = LabelSerializer(data=data, partial=True)
        if serializer.is_valid():
            serializer.save(user=user)
            logger.info("New Label is created.")
            return Response({"response": serializer.data}, status=201)
        logger.error("Something went wrong while creating Note, from post()")
        return Response({"response": serializer.data}, status=400)

    def put(self, request):
        """
            Summary:
            --------
            New note will be updated by the User.
            Exception:
            ----------
                KeyError: object
        """
        try:
            user = TokenAuthorization.token_auth(request)
            data = request.data
            serializer = LabelSerializer(user, data=data)
            if serializer.is_valid():
                serializer.save(user=user)
                logger.info("Label updated successfully, from put()")
                return Response({'details': serializer.data}, status=200)
            logger.error("Label is not Updated something went wrong, from put()")
            return Response({'details': 'Note is not Updated..!!!'}, status=400)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to update note'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """
            Summary:
            --------
                Label will be deleted by the User.
            Exception:
            ----------
                KeyError: object
        """
        try:
            user = TokenAuthorization.token_auth(request)
            label = Label.objects.filter(user=user)
            label.delete()
            logger.info("Label is Deleted Permanently, from delete()")
            return Response({'response': 'Label is Deleted'}, status=200)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to delete new label,Please try again later'},
                            status=status.HTTP_400_BAD_REQUEST)


class AddCollaboratorForNotes(GenericAPIView):
    """
                This api is for adding collaborator for notes
                @param request: ID of the notes and email id of collaborator
                @return: response of added collaborator
    """
    serializer_class = CollaboratorSerializer
    queryset = Notes.objects.all()
    lookup_field = 'id'

    def get(self, request):
        note_id = request.data.get('note_id')
        return HttpResponse(Notes.objects.get(id=note_id))

    def put(self, request):
        note_id = request.data.get('note_id')
        note = Notes.objects.get(id=note_id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        collaborator_email = serializer.validated_data['collaborator']
        try:
            collaborator = User.objects.get(email=collaborator_email)
        except:
            return Response({'User email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        if collaborator == request.user:
            return Response({'Message': 'This email already exists!!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            note.collaborator.add(collaborator)
            note.save()
            return Response({'collaborator': collaborator_email}, status=status.HTTP_200_OK)


class ListCollaboratorAPIView(GenericAPIView):

    serializer_class = NotesSerializer
    queryset = Notes.objects.all()

    def get(self, request):
        user = request.user
        collaborated_users = []
        collaborator = Notes.objects.filter(collaborator__isnull=False)
        if collaborator:
            collaborator_list = collaborator.values('collaborator')
            for i in range(len(collaborator_list)):
                collab_id = collaborator_list[i]['collaborator']
                collab1 = User.objects.filter(id=collab_id)
                collab_email = collab1.values('email')
                collaborator_list[i].update(collab_email[0])
                collaborated_users = collaborated_users + [collaborator_list[i]]
                return Response({"Collaborated Users": collaborated_users}, status=200)
        else:
            logger.info("No such Note available to have any collaborator Added")
            return Response({"response": "No such Note available to have any collaborator Added"}, status=404)


class SearchAPIView(ListCreateAPIView):
    serializer_class = NotesSerializer

    def get_queryset(self):
        """ Get all notes of particular User """
        try:
            user = self.request.user
            search_key = self.request.data.get('value')
            logger.info("Data Incoming from the database")
            return Notes.objects.filter(Q(title__contains=search_key) | Q(description__contains=search_key),
                                        owner_id=user.id, is_trashed=False)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)


class ArchiveNotes(ListCreateAPIView):
    serializer_class = NotesSerializer

    def post(self, request):
        try:
            note_id = request.data.get('note_id')
            note = Notes.objects.get(id=note_id)
            note.is_archive = True
            note.save()

            return Response({'Message': 'Note is archived successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)

    def get_queryset(self):
        try:
            logger.info("Data Incoming from the database")
            return Notes.objects.filter(is_archive=True)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)

    def put(self, request):
        try:
            note_id = request.data.get('note_id')
            note = Notes.objects.get(id=note_id)
            note.is_archive = False
            note.save()
            return Response({'Message': 'Note is Unarchived successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)


class TrashNotes(ListCreateAPIView):

    def post(self, request):
        try:
            note_id = request.data.get('note_id')
            note = Notes.objects.get(id=note_id)
            note.is_trashed = True
            note.save()
            return Response({'Message': 'Note is trashed successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)

    def get_queryset(self):
        try:
            logger.info("Data Incoming from the database ")
            return Notes.objects.filter(is_trashed=True)
        except Exception as e:
            logger.error(e)


class AddReminderToNotes(ListCreateAPIView):
    serializer_class = ReminderSerializer

    def put(self, request):
        """ To set reminder to notes of particular User """
        note_id = request.data.get('note_id')
        note = Notes.objects.get(id=note_id)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        reminder = serializer.validated_data['reminder']
        if reminder.replace(tzinfo=None) - datetime.now() < timedelta(seconds=0):
            return Response({'response': 'Invalid Time Given'})
        else:
            note.reminder = reminder
            note.save()
            return Response({'response': serializer.data}, status=status.HTTP_200_OK)

    def get_queryset(self):
        """ Get all notes of particular User """
        try:
            user = self.request.user
            logger.info("Data Incoming from the database")
            # return Notes.objects.filter(reminder__isnull=False)
            note = Notes.objects.filter(owner_id=1, reminder__isnull=False)
            reminder = note.values('reminder')
            print(reminder)
            return reminder
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)


class SendReminderEmail(GenericAPIView):
    """
               This api is for registration of new user
              @param request: username,email and password
              @return: it will return the registered user with its credentials
    """
    serializer_class = ReminderSerializer

    def post(self, request):
        """
                This api is for creation of new notes
                @param request: title and description of notes
                @return: response of created notes
        """
        try:
            user = self.request.user
            note = Notes.objects.filter(owner_id=user.id, reminder__isnull=False)
            one_hour = timedelta(hours=1)
            send_mail_time = note.reminder - one_hour
            current_time = datetime.now()
            if current_time == send_mail_time:
                email_body = 'Hi ' + user.username + 'U have a reminder at' + note.reminder
                data = {'email_body': email_body, 'to_email': user.email,
                        'email_subject': 'Reminder'}
                Utils.send_reminder_email(data).delay(10)
                logger.info("Reminder Email Sent Successfully to the user")
                return Response({'Message': 'Reminder Email Sent Successfully to the user'},
                                status=status.HTTP_201_CREATED)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)


'''
Exception handling in code
Include specific exceptions
Methods should be commented
Standard keys for response throughout the applications
Usage of different log levels have to be done
Fix swagger and show API working
Celery for sending emails
Show working test cases
Learn about decorator and how to use custom decorator
Use debugging regularly
Soft delete notes
Response token in header
Use gitignore properly
Understand use of init.py
Remove init dir from git
'''
from django.conf import settings
from psycopg2._psycopg import OperationalError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework_jwt import jwt
from user.models import User
from .serializers import NotesSerializer
from .models import Notes
from rest_framework.response import Response
import logging
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
        key = request.META['HTTP_TOKEN']
        payload = jwt.decode(key, settings.SECRET_KEY, ['HS256'])
        user = User.objects.get(username=payload['username'])
        notes = Notes.objects.filter(user=user)
        serializer = NotesSerializer(notes, many=True)
        logger.info("Particular Note is obtained, from get()")
        return Response({"response": serializer.data}, status=200)

    def post(self, request):

        data = request.data
        key = request.META['HTTP_TOKEN']
        payload = jwt.decode(key, settings.SECRET_KEY, ['HS256'])
        user = User.objects.get(username=payload['username'])
        serializer = NotesSerializer(data=data, partial=True)
        if serializer.is_valid():
            note = serializer.save(user=user)
            logger.info("New Note is created.")
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
            key = request.META['HTTP_TOKEN']
            payload = jwt.decode(key, settings.SECRET_KEY, ['HS256'])
            user = User.objects.get(username=payload['username'])
            data = request.data
            serializer = NotesSerializer(user, data=data)
            if serializer.is_valid():
                note_update = serializer.save(user=user)
                logger.info("Note updated succesfully, from put()")
                return Response({'details': serializer.data}, status=200)
            logger.error("Note is not Updated something went wrong, from put()")
            return Response({'deatils': 'Note is not Updated..!!!'}, status=400)
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            logger.error(e)
            return Response({'Message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Failed to update note'}, status=status.HTTP_400_BAD_REQUEST)
        #todo add exception for token/login check

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
            key = request.META['HTTP_TOKEN']
            payload = jwt.decode(key, settings.SECRET_KEY, ['HS256'])
            user = User.objects.get(username=payload['username'])
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

#Todo lambda and filter and map and reduce


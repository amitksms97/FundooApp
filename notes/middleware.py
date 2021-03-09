import logging

from psycopg2 import OperationalError
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger('django')


class BaseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print("before request")
        try:
            response = self.get_response(request)
            print("after response")
            return response
        except OperationalError as e:
            logger.error(e)
            return Response({'Message': 'Failed to connect with the database'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return Response({'Message': 'Something went wrong please try again'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.response import Response
from rest_framework import status

class StandardResponse:
    @staticmethod
    def success(message="", data=None, status=status.HTTP_200_OK):
        return Response({
            "message": message,
            "data": data
        }, status=status)

    @staticmethod
    def error(message="", errors=None, status=status.HTTP_400_BAD_REQUEST):
        return Response({
            "message": message,
            "errors": errors
        }, status=status)